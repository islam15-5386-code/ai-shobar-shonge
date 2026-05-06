from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.businesses.models import Business
from apps.conversations.models import Conversation, Message
from apps.conversations.realtime import publish_inbox_event
from apps.tickets.models import Ticket
from .models import AIInteractionLog
from .services import (
    confidence_from_similarity,
    detect_intent,
    detect_sentiment,
    find_best_faq,
    is_bangla_text,
    should_escalate,
    to_bangla_reply,
)


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

    intent = detect_intent(user_message)
    sentiment = detect_sentiment(user_message)
    match = find_best_faq(user_message, business.id)
    confidence = confidence_from_similarity(match.score)

    if match.faq:
        reply = match.faq.answer
    else:
        reply = 'Thanks for your message. I could not find an exact FAQ answer yet. Our team will follow up soon.'

    escalated, escalation_reason = should_escalate(confidence, sentiment, intent)
    if business.handover_enabled and escalated:
        conversation.needs_human = True
        conversation.save(update_fields=['needs_human', 'updated_at'])
        ticket = Ticket.objects.create(
            business=business,
            conversation=conversation,
            subject='Escalated from website chatbot',
            details=f'Reason: {escalation_reason}. Intent: {intent}. Sentiment: {sentiment}.',
        )
        reply = f"I have created a support ticket (#{ticket.id}). A human agent will contact you soon."

    if is_bangla_text(user_message):
        reply = to_bangla_reply(reply)

    Message.objects.create(conversation=conversation, role='assistant', text=reply)

    AIInteractionLog.objects.create(
        business=business,
        conversation=conversation,
        user_message=user_message,
        ai_reply=reply,
        confidence=confidence,
        intent=intent,
        sentiment=sentiment,
        escalated=conversation.needs_human,
        escalation_reason=escalation_reason,
        metadata={'match_method': match.method, 'faq_id': match.faq.id if match.faq else None},
    )

    publish_inbox_event(
        business.id,
        {
            'type': 'conversation_updated',
            'conversation_id': conversation.id,
            'visitor_id': conversation.visitor_id,
            'needs_human': conversation.needs_human,
            'reply': reply,
            'intent': intent,
            'sentiment': sentiment,
            'confidence': confidence,
        },
    )

    return Response(
        {
            'conversation_id': conversation.id,
            'needs_human': conversation.needs_human,
            'reply': reply,
            'confidence': confidence,
            'intent': intent,
            'sentiment': sentiment,
            'escalation_reason': escalation_reason,
            'messages': [
                {'role': m.role, 'text': m.text, 'created_at': m.created_at}
                for m in conversation.messages.order_by('created_at')
            ],
        }
    )


@api_view(['GET'])
def ai_logs(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    logs = AIInteractionLog.objects.filter(business=business).order_by('-created_at')[:200]
    return Response(
        [
            {
                'id': log.id,
                'conversation_id': log.conversation_id,
                'user_message': log.user_message,
                'ai_reply': log.ai_reply,
                'confidence': log.confidence,
                'intent': log.intent,
                'sentiment': log.sentiment,
                'escalated': log.escalated,
                'escalation_reason': log.escalation_reason,
                'metadata': log.metadata,
                'created_at': log.created_at,
            }
            for log in logs
        ]
    )
