from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from apps.billing.limits import get_ai_reply_limit_state, increment_ai_usage
from apps.businesses.models import Business
from apps.businesses.access import get_user_business
from apps.conversations.models import Conversation, Message
from apps.conversations.realtime import publish_inbox_event
from apps.customers.models import CustomerProfile
from apps.tickets.models import Ticket
from .ai_client import ai_respond
from .models import AIInteractionLog, AIRequestLog, AIAssistantSetting
from .services import (
    confidence_from_similarity,
    detect_intent,
    detect_sentiment,
    build_knowledge_context,
    is_bangla_text,
    should_escalate,
    should_escalate_with_settings,
    to_bangla_reply,
)

SAFE_BN_FALLBACK = "দুঃখিত, এই মুহূর্তে AI assistant response দিতে পারছে না। একজন support agent শীঘ্রই আপনাকে সাহায্য করবে।"


@api_view(['POST'])
@permission_classes([AllowAny])
def website_chat(request):
    business_slug = request.data.get('business_slug', '').strip()
    widget_key = request.data.get('widget_key', '').strip()
    customer = request.data.get('customer', {}) or {}
    visitor_id = request.data.get('visitor_id', '').strip() or str(customer.get('external_id', '')).strip()
    user_message = request.data.get('message', '').strip()

    if not business_slug and widget_key:
        business_slug = widget_key

    if not business_slug or not visitor_id or not user_message:
        return Response(
            {'detail': 'business_slug/widget_key, visitor_id/customer.external_id, and message are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    business = Business.objects.filter(slug=business_slug).first()
    if not business:
        return Response({'detail': 'business not found'}, status=status.HTTP_404_NOT_FOUND)

    ai_settings, _ = AIAssistantSetting.objects.get_or_create(business=business)
    customer_external_id = str(customer.get('external_id', '')).strip() or visitor_id
    customer_name = str(customer.get('name', '')).strip()
    customer_obj, _ = CustomerProfile.objects.update_or_create(
        business=business,
        external_source='website',
        external_id=customer_external_id,
        defaults={'name': customer_name, 'metadata': customer if isinstance(customer, dict) else {}},
    )

    conversation, _ = Conversation.objects.get_or_create(business=business, visitor_id=visitor_id)
    Message.objects.create(conversation=conversation, role='user', text=user_message)

    intent = detect_intent(user_message)
    sentiment = detect_sentiment(user_message)
    knowledge = build_knowledge_context(user_message, business.id)
    match = knowledge.faq_match
    confidence = confidence_from_similarity(match.score)

    forced_escalation = False
    escalation_reason = 'none'

    limit_state = get_ai_reply_limit_state(business)
    ai_call = {'ok': False, 'status': 'limit', 'latency_ms': 0, 'error': '', 'data': None}

    if ai_settings.auto_reply_enabled and limit_state['allowed']:
        ai_call = ai_respond(
            user_message,
            business_id=business.id,
            locale='bn' if is_bangla_text(user_message) else 'en',
            vendor_id=knowledge.vendor_id,
            order_id=knowledge.order_id,
            customer_id=customer_obj.id,
            context_snippets=knowledge.snippets,
        )

    if ai_call.get('ok') and (ai_call.get('data') or {}).get('answer'):
        ai_response = ai_call['data']
        reply = str(ai_response.get('answer'))
        confidence = float(ai_response.get('confidence', confidence))
        intent = str(ai_response.get('intent', intent))
        sentiment = str(ai_response.get('sentiment', sentiment))
        increment_ai_usage(business, by=1)
    elif not limit_state['allowed']:
        reply = 'আপনার বর্তমান প্ল্যানের AI reply limit শেষ হয়ে গেছে। একজন support agent শীঘ্রই আপনাকে সাহায্য করবে।'
        forced_escalation = True
        escalation_reason = 'plan_limit_exceeded'
    elif match.faq:
        reply = match.faq.answer
    else:
        reply = SAFE_BN_FALLBACK

    escalated, rule_reason = should_escalate_with_settings(
        confidence=confidence,
        sentiment=sentiment,
        intent=intent,
        user_text=user_message,
        settings_obj=ai_settings,
    )
    if forced_escalation:
        escalated = True
    if escalation_reason == 'none':
        escalation_reason = rule_reason

    if business.handover_enabled and escalated:
        conversation.needs_human = True
        conversation.save(update_fields=['needs_human', 'updated_at'])
        ticket = Ticket.objects.create(
            business=business,
            conversation=conversation,
            subject='Escalated from website chatbot',
            details=f'Reason: {escalation_reason}. Intent: {intent}. Sentiment: {sentiment}.',
        )
        if forced_escalation:
            reply = f"{reply} (Ticket #{ticket.id})"
        else:
            reply = f"I have created a support ticket (#{ticket.id}). A human agent will contact you soon."
    elif confidence < float(ai_settings.confidence_threshold):
        conversation.needs_human = True
        conversation.save(update_fields=['needs_human', 'updated_at'])
        ticket = Ticket.objects.create(
            business=business,
            conversation=conversation,
            subject='Low-confidence website chatbot response',
            details=f'Confidence: {confidence}. Intent: {intent}. Sentiment: {sentiment}.',
        )
        reply = f"I have created a support ticket (#{ticket.id}). A human agent will contact you soon."
        escalation_reason = 'below_confidence_threshold'

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

    AIRequestLog.objects.create(
        business=business,
        conversation=conversation,
        input_text=user_message,
        output_text=reply,
        intent=intent,
        sentiment=sentiment,
        confidence=confidence,
        sources=(ai_call.get('data') or {}).get('sources', []),
        model_name=(ai_call.get('data') or {}).get('model_name', 'mock'),
        latency_ms=ai_call.get('latency_ms', 0),
        status=ai_call.get('status', 'ok'),
        error=ai_call.get('error', ''),
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
            'sender': 'assistant',
            'should_handover': conversation.needs_human,
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


@api_view(['GET', 'PUT'])
def ai_settings(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    settings_obj, _ = AIAssistantSetting.objects.get_or_create(business=business)

    if request.method == 'GET':
        return Response(
            {
                'auto_reply_enabled': settings_obj.auto_reply_enabled,
                'confidence_threshold': settings_obj.confidence_threshold,
                'business_tone': settings_obj.business_tone,
                'language': settings_obj.language,
                'rule_refund': settings_obj.rule_refund,
                'rule_negative_sentiment': settings_obj.rule_negative_sentiment,
                'rule_below_confidence': settings_obj.rule_below_confidence,
                'rule_customer_requests_human': settings_obj.rule_customer_requests_human,
                'system_prompt': settings_obj.system_prompt,
            }
        )

    data = request.data
    if 'auto_reply_enabled' in data:
        settings_obj.auto_reply_enabled = bool(data.get('auto_reply_enabled'))
    if 'confidence_threshold' in data:
        settings_obj.confidence_threshold = float(data.get('confidence_threshold'))
    if 'business_tone' in data:
        settings_obj.business_tone = str(data.get('business_tone'))
    if 'language' in data:
        settings_obj.language = str(data.get('language'))
    if 'rule_refund' in data:
        settings_obj.rule_refund = bool(data.get('rule_refund'))
    if 'rule_negative_sentiment' in data:
        settings_obj.rule_negative_sentiment = bool(data.get('rule_negative_sentiment'))
    if 'rule_below_confidence' in data:
        settings_obj.rule_below_confidence = bool(data.get('rule_below_confidence'))
    if 'rule_customer_requests_human' in data:
        settings_obj.rule_customer_requests_human = bool(data.get('rule_customer_requests_human'))
    if 'system_prompt' in data:
        settings_obj.system_prompt = str(data.get('system_prompt') or '')
    settings_obj.save()
    return Response({'detail': 'saved'})


@api_view(['GET'])
def ai_logs(request):
    business = get_user_business(request.user)
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
