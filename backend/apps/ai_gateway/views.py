from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.businesses.models import Business
from apps.conversations.models import Conversation, Message
from apps.faqs.models import FAQ
from apps.tickets.models import Ticket


@api_view(['POST'])
@permission_classes([AllowAny])
def website_chat(request):
    business_slug = request.data.get('business_slug', '').strip()
    visitor_id = request.data.get('visitor_id', '').strip()
    user_message = request.data.get('message', '').strip()

    if not business_slug or not visitor_id or not user_message:
        return Response({'detail': 'business_slug, visitor_id, and message are required'}, status=status.HTTP_400_BAD_REQUEST)

    business = Business.objects.filter(slug=business_slug).first()
    if not business:
        return Response({'detail': 'business not found'}, status=status.HTTP_404_NOT_FOUND)

    conversation, _ = Conversation.objects.get_or_create(business=business, visitor_id=visitor_id)
    Message.objects.create(conversation=conversation, role='user', text=user_message)

    lower = user_message.lower()
    wants_human = any(token in lower for token in ['human', 'agent', 'support', 'help me'])

    faq_match = None
    for faq in FAQ.objects.filter(business=business, is_active=True):
        question_tokens = [t for t in faq.question.lower().split() if len(t) > 3]
        if any(token in lower for token in question_tokens):
            faq_match = faq
            break

    if wants_human and business.handover_enabled:
        conversation.needs_human = True
        conversation.save(update_fields=['needs_human', 'updated_at'])
        ticket = Ticket.objects.create(
            business=business,
            conversation=conversation,
            subject='Human handover from website chatbot',
            details=f'Visitor {visitor_id} requested a human agent.',
        )
        reply = f"I have created a support ticket (#{ticket.id}). A human agent will contact you soon."
    elif faq_match:
        reply = faq_match.answer
    else:
        reply = "Thanks for your message. I could not find an exact FAQ answer yet. Our team will follow up soon."

    Message.objects.create(conversation=conversation, role='assistant', text=reply)

    return Response(
        {
            'conversation_id': conversation.id,
            'needs_human': conversation.needs_human,
            'reply': reply,
            'messages': [
                {'role': m.role, 'text': m.text, 'created_at': m.created_at}
                for m in conversation.messages.order_by('created_at')
            ],
        }
    )
