from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q

from apps.ai_gateway.services import detect_intent, detect_sentiment, find_best_faq
from apps.businesses.access import get_user_business
from apps.conversations.realtime import publish_inbox_event
from apps.customers.models import CustomerProfile
from apps.marketplace.permissions import can_manage_marketplace, get_vendor_for_user
from .models import Conversation, InternalNote


@api_view(['GET'])
def conversation_list(request):
    business = get_user_business(request.user)
    if not business:
        return Response([], status=status.HTTP_200_OK)
    vendor = get_vendor_for_user(request.user, business)
    qs = Conversation.objects.filter(business=business)
    if not can_manage_marketplace(request.user, business) and vendor:
        qs = qs.filter(vendor=vendor)
    return Response(
        [
            {
                'id': c.id,
                'visitor_id': c.visitor_id,
                'status': c.status,
                'needs_human': c.needs_human,
                'vendor_id': c.vendor_id,
                'order_id': c.order_id,
                'product_id': c.product_id,
                'updated_at': c.updated_at,
            }
            for c in qs.order_by('-updated_at')[:200]
        ]
    )


@api_view(['GET'])
def conversation_history(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    vendor = get_vendor_for_user(request.user, business)
    qs = Conversation.objects.filter(business=business)
    if not can_manage_marketplace(request.user, business) and vendor:
        qs = qs.filter(vendor=vendor)

    q = str(request.query_params.get('q', '')).strip()
    channel = str(request.query_params.get('channel', 'all')).strip().lower()
    sentiment = str(request.query_params.get('sentiment', 'all')).strip().lower()

    if q:
        qs = qs.filter(Q(visitor_id__icontains=q) | Q(messages__text__icontains=q)).distinct()

    if channel in ['messenger', 'whatsapp', 'website']:
        prefix = {'messenger': 'fb:', 'whatsapp': 'wa:', 'website': 'web:'}[channel]
        qs = qs.filter(visitor_id__startswith=prefix)

    payload = []
    for conv in qs.order_by('-updated_at')[:200]:
        messages = list(conv.messages.order_by('created_at'))
        last_msg = messages[-1] if messages else None
        customer_name = conv.visitor_id
        if ':' in conv.visitor_id:
            external_id = conv.visitor_id.split(':', 1)[1]
            cp = CustomerProfile.objects.filter(business=business, external_id=external_id).first()
            if cp and cp.name:
                customer_name = cp.name

        last_sentiment = (last_msg.sentiment or '').lower() if last_msg else ''
        if last_sentiment not in ['positive', 'neutral', 'negative']:
            last_sentiment = 'negative' if conv.needs_human else 'neutral'
        if sentiment in ['positive', 'neutral', 'negative'] and last_sentiment != sentiment:
            continue

        payload.append(
            {
                'id': conv.id,
                'visitor_id': conv.visitor_id,
                'customer_name': customer_name,
                'channel': (
                    'Messenger' if conv.visitor_id.startswith('fb:')
                    else 'WhatsApp' if conv.visitor_id.startswith('wa:')
                    else 'Website'
                ),
                'needs_human': conv.needs_human,
                'resolved_by': 'Human' if conv.needs_human else 'AI',
                'last_message': last_msg.text if last_msg else '',
                'last_sentiment': last_sentiment,
                'vendor_id': conv.vendor_id,
                'order_id': conv.order_id,
                'product_id': conv.product_id,
                'updated_at': conv.updated_at,
                'messages': [
                    {
                        'id': msg.id,
                        'role': msg.role,
                        'text': msg.text,
                        'sentiment': msg.sentiment,
                        'created_at': msg.created_at,
                    }
                    for msg in messages
                ],
            }
        )
    return Response(payload)


@api_view(['GET'])
def inbox(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    vendor = get_vendor_for_user(request.user, business)
    qs = Conversation.objects.filter(business=business)
    if not can_manage_marketplace(request.user, business) and vendor:
        qs = qs.filter(vendor=vendor)

    payload = []
    conversations = qs.order_by('-updated_at')[:200]
    for conv in conversations:
        last_msg = conv.messages.order_by('-created_at').first()
        payload.append(
            {
                'id': conv.id,
                'visitor_id': conv.visitor_id,
                'needs_human': conv.needs_human,
                'vendor_id': conv.vendor_id,
                'order_id': conv.order_id,
                'product_id': conv.product_id,
                'assigned_agent_id': conv.assigned_agent_id,
                'last_message': last_msg.text if last_msg else '',
                'last_message_role': last_msg.role if last_msg else '',
                'updated_at': conv.updated_at,
            }
        )
    return Response(payload)


@api_view(['POST'])
def assign_agent(request, conversation_id):
    business = get_user_business(request.user)
    conversation = Conversation.objects.filter(id=conversation_id, business=business).first()
    if not conversation:
        return Response({'detail': 'conversation not found'}, status=status.HTTP_404_NOT_FOUND)

    agent_id = request.data.get('agent_id')
    if agent_id and str(agent_id) != str(request.user.id):
        return Response({'detail': 'for now only self-assignment is allowed'}, status=status.HTTP_400_BAD_REQUEST)
    conversation.assigned_agent = request.user
    conversation.save(update_fields=['assigned_agent', 'updated_at'])
    publish_inbox_event(
        business.id,
        {'type': 'conversation_assigned', 'conversation_id': conversation.id, 'assigned_agent_id': conversation.assigned_agent_id},
    )
    return Response({'id': conversation.id, 'assigned_agent_id': conversation.assigned_agent_id})


@api_view(['GET', 'POST'])
def internal_notes(request, conversation_id):
    business = get_user_business(request.user)
    conversation = Conversation.objects.filter(id=conversation_id, business=business).first()
    if not conversation:
        return Response({'detail': 'conversation not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        return Response([
            {
                'id': n.id,
                'author_id': n.author_id,
                'text': n.text,
                'created_at': n.created_at,
            }
            for n in conversation.internal_notes.order_by('created_at')
        ])

    text = request.data.get('text', '').strip()
    if not text:
        return Response({'detail': 'text is required'}, status=status.HTTP_400_BAD_REQUEST)
    note = InternalNote.objects.create(conversation=conversation, author=request.user, text=text)
    publish_inbox_event(
        business.id,
        {'type': 'internal_note_created', 'conversation_id': conversation.id, 'note_id': note.id},
    )
    return Response({'id': note.id, 'author_id': note.author_id, 'text': note.text, 'created_at': note.created_at}, status=201)


@api_view(['POST'])
def ai_suggested_reply(request, conversation_id):
    business = get_user_business(request.user)
    conversation = Conversation.objects.filter(id=conversation_id, business=business).first()
    if not conversation:
        return Response({'detail': 'conversation not found'}, status=status.HTTP_404_NOT_FOUND)

    last_user_message = conversation.messages.filter(role='user').order_by('-created_at').first()
    if not last_user_message:
        return Response({'detail': 'no user message found'}, status=status.HTTP_400_BAD_REQUEST)

    intent = detect_intent(last_user_message.text)
    sentiment = detect_sentiment(last_user_message.text)
    faq_match = find_best_faq(last_user_message.text, business.id)

    if faq_match.faq:
        suggestion = faq_match.faq.answer
    else:
        suggestion = "Thanks for your message. I am checking this and will share an update shortly."

    return Response(
        {
            'conversation_id': conversation.id,
            'suggested_reply': suggestion,
            'intent': intent,
            'sentiment': sentiment,
            'confidence': round(max(0.0, min(1.0, faq_match.score)), 3),
        }
    )
