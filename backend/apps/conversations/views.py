from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.ai_gateway.services import detect_intent, detect_sentiment, find_best_faq
from apps.businesses.models import Business
from apps.conversations.realtime import publish_inbox_event
from .models import Conversation, InternalNote


@api_view(['GET'])
def conversation_history(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    payload = []
    for conv in Conversation.objects.filter(business=business).order_by('-updated_at')[:100]:
        payload.append(
            {
                'id': conv.id,
                'visitor_id': conv.visitor_id,
                'needs_human': conv.needs_human,
                'updated_at': conv.updated_at,
                'messages': [
                    {
                        'id': msg.id,
                        'role': msg.role,
                        'text': msg.text,
                        'created_at': msg.created_at,
                    }
                    for msg in conv.messages.order_by('created_at')
                ],
            }
        )
    return Response(payload)


@api_view(['GET'])
def inbox(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    payload = []
    conversations = Conversation.objects.filter(business=business).order_by('-updated_at')[:200]
    for conv in conversations:
        last_msg = conv.messages.order_by('-created_at').first()
        payload.append(
            {
                'id': conv.id,
                'visitor_id': conv.visitor_id,
                'needs_human': conv.needs_human,
                'assigned_agent_id': conv.assigned_agent_id,
                'last_message': last_msg.text if last_msg else '',
                'last_message_role': last_msg.role if last_msg else '',
                'updated_at': conv.updated_at,
            }
        )
    return Response(payload)


@api_view(['POST'])
def assign_agent(request, conversation_id):
    business = Business.objects.filter(owner=request.user).first()
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
    business = Business.objects.filter(owner=request.user).first()
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
    business = Business.objects.filter(owner=request.user).first()
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
