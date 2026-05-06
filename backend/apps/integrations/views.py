import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.ai_gateway.models import AIInteractionLog
from apps.ai_gateway.services import (
    confidence_from_similarity,
    detect_intent,
    detect_sentiment,
    find_best_faq,
    should_escalate,
)
from apps.businesses.models import Business
from apps.conversations.models import Conversation, Message
from apps.customers.models import CustomerProfile
from apps.tickets.models import Ticket
from .models import MessengerIntegration, WhatsAppIntegration
from .services import (
    fetch_whatsapp_media_bytes,
    send_facebook_reply,
    send_whatsapp_text,
    transcribe_audio_with_ai_service,
)


def health(request):
    return JsonResponse({'app': 'integrations', 'status': 'ok'})


@api_view(['POST', 'GET'])
def messenger_setup(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        integration = MessengerIntegration.objects.filter(business=business).first()
        if not integration:
            return Response({'detail': 'messenger not configured'}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                'business_id': business.id,
                'page_id': integration.page_id,
                'app_id': integration.app_id,
                'verify_token': integration.verify_token,
                'is_active': integration.is_active,
            }
        )

    page_id = str(request.data.get('page_id', '')).strip()
    page_access_token = str(request.data.get('page_access_token', '')).strip()
    verify_token = str(request.data.get('verify_token', '')).strip()
    app_id = str(request.data.get('app_id', '')).strip()
    app_secret = str(request.data.get('app_secret', '')).strip()
    if not page_id or not page_access_token or not verify_token:
        return Response({'detail': 'page_id, page_access_token, verify_token are required'}, status=status.HTTP_400_BAD_REQUEST)

    integration, _ = MessengerIntegration.objects.update_or_create(
        business=business,
        defaults={
            'page_id': page_id,
            'page_access_token': page_access_token,
            'verify_token': verify_token,
            'app_id': app_id,
            'app_secret': app_secret,
            'is_active': True,
        },
    )
    return Response({'id': integration.id, 'page_id': integration.page_id, 'is_active': integration.is_active}, status=201)


@csrf_exempt
def messenger_webhook(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge', '')
        if mode != 'subscribe' or not token:
            return HttpResponse('forbidden', status=403)
        integration = MessengerIntegration.objects.filter(verify_token=token, is_active=True).first()
        if not integration:
            return HttpResponse('forbidden', status=403)
        return HttpResponse(challenge, status=200)

    if request.method != 'POST':
        return HttpResponse('method not allowed', status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponse('bad request', status=400)

    entries = body.get('entry', [])
    for entry in entries:
        page_id = str(entry.get('id', '')).strip()
        integration = MessengerIntegration.objects.filter(page_id=page_id, is_active=True).select_related('business').first()
        if not integration:
            continue

        for messaging_event in entry.get('messaging', []):
            sender = messaging_event.get('sender') or {}
            message = messaging_event.get('message') or {}
            psid = str(sender.get('id', '')).strip()
            text = str(message.get('text', '')).strip()
            if not psid or not text:
                continue

            _handle_incoming_text(integration, psid, text)

    return HttpResponse('EVENT_RECEIVED', status=200)


def _handle_incoming_text(integration: MessengerIntegration, psid: str, text: str) -> None:
    business = integration.business
    CustomerProfile.objects.get_or_create(
        business=business,
        external_source='facebook',
        external_id=psid,
        defaults={'metadata': {'psid': psid}},
    )

    visitor_id = f"fb:{psid}"
    conversation, _ = Conversation.objects.get_or_create(business=business, visitor_id=visitor_id)
    Message.objects.create(conversation=conversation, role='user', text=text)

    intent = detect_intent(text)
    sentiment = detect_sentiment(text)
    match = find_best_faq(text, business.id)
    confidence = confidence_from_similarity(match.score)
    reply = match.faq.answer if match.faq else business.welcome_message

    escalated, escalation_reason = should_escalate(confidence, sentiment, intent)
    if business.handover_enabled and escalated:
        conversation.needs_human = True
        conversation.save(update_fields=['needs_human', 'updated_at'])
        Ticket.objects.create(
            business=business,
            conversation=conversation,
            subject='Escalated from Messenger',
            details=f'Reason: {escalation_reason}. Intent: {intent}. Sentiment: {sentiment}.',
        )
        reply = 'Your message has been forwarded to a human agent. They will contact you soon.'

    Message.objects.create(conversation=conversation, role='assistant', text=reply)
    send_facebook_reply(integration.page_access_token, psid, reply)

    AIInteractionLog.objects.create(
        business=business,
        conversation=conversation,
        user_message=text,
        ai_reply=reply,
        confidence=confidence,
        intent=intent,
        sentiment=sentiment,
        escalated=conversation.needs_human,
        escalation_reason=escalation_reason,
        metadata={'channel': 'messenger', 'psid': psid, 'match_method': match.method, 'faq_id': match.faq.id if match.faq else None},
    )


@api_view(['POST', 'GET'])
def whatsapp_setup(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        integration = WhatsAppIntegration.objects.filter(business=business).first()
        if not integration:
            return Response({'detail': 'whatsapp not configured'}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                'business_id': business.id,
                'phone_number_id': integration.phone_number_id,
                'verify_token': integration.verify_token,
                'waba_id': integration.waba_id,
                'is_active': integration.is_active,
            }
        )

    phone_number_id = str(request.data.get('phone_number_id', '')).strip()
    access_token = str(request.data.get('access_token', '')).strip()
    verify_token = str(request.data.get('verify_token', '')).strip()
    waba_id = str(request.data.get('waba_id', '')).strip()
    if not phone_number_id or not access_token or not verify_token:
        return Response({'detail': 'phone_number_id, access_token, verify_token are required'}, status=status.HTTP_400_BAD_REQUEST)

    integration, _ = WhatsAppIntegration.objects.update_or_create(
        business=business,
        defaults={
            'phone_number_id': phone_number_id,
            'access_token': access_token,
            'verify_token': verify_token,
            'waba_id': waba_id,
            'is_active': True,
        },
    )
    return Response({'id': integration.id, 'phone_number_id': integration.phone_number_id, 'is_active': integration.is_active}, status=201)


@csrf_exempt
def whatsapp_webhook(request):
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge', '')
        if mode != 'subscribe' or not token:
            return HttpResponse('forbidden', status=403)
        integration = WhatsAppIntegration.objects.filter(verify_token=token, is_active=True).first()
        if not integration:
            return HttpResponse('forbidden', status=403)
        return HttpResponse(challenge, status=200)

    if request.method != 'POST':
        return HttpResponse('method not allowed', status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponse('bad request', status=400)

    for entry in body.get('entry', []):
        for change in entry.get('changes', []):
            value = change.get('value') or {}
            metadata = value.get('metadata') or {}
            phone_number_id = str(metadata.get('phone_number_id', '')).strip()
            integration = WhatsAppIntegration.objects.filter(phone_number_id=phone_number_id, is_active=True).select_related('business').first()
            if not integration:
                continue
            messages = value.get('messages') or []
            for message in messages:
                _handle_whatsapp_message(integration, message)

    return HttpResponse('EVENT_RECEIVED', status=200)


def _handle_whatsapp_message(integration: WhatsAppIntegration, message: dict) -> None:
    business = integration.business
    wa_from = str(message.get('from', '')).strip()
    if not wa_from:
        return

    customer, _ = CustomerProfile.objects.get_or_create(
        business=business,
        external_source='whatsapp',
        external_id=wa_from,
        defaults={'metadata': {'whatsapp_number': wa_from}},
    )
    _ = customer

    message_type = str(message.get('type', '')).strip()
    text = ""
    metadata: dict = {'channel': 'whatsapp', 'from': wa_from, 'message_type': message_type}

    if message_type == 'text':
        text = str((message.get('text') or {}).get('body', '')).strip()
    elif message_type == 'image':
        image_payload = message.get('image') or {}
        caption = str(image_payload.get('caption', '')).strip()
        media_id = str(image_payload.get('id', '')).strip()
        text = caption or 'User sent an image.'
        metadata['media_id'] = media_id
    elif message_type == 'audio':
        audio_payload = message.get('audio') or {}
        media_id = str(audio_payload.get('id', '')).strip()
        metadata['media_id'] = media_id
        transcript = ''
        if media_id:
            audio_bytes, media_err = fetch_whatsapp_media_bytes(integration.access_token, media_id)
            if audio_bytes:
                ok, transcript_or_err = transcribe_audio_with_ai_service(audio_bytes, filename=f"{media_id}.ogg")
                if ok:
                    transcript = transcript_or_err
                else:
                    metadata['transcription_error'] = transcript_or_err
            else:
                metadata['media_error'] = media_err
        text = transcript or 'User sent a voice message.'
    else:
        text = f"Unsupported WhatsApp message type: {message_type}"

    visitor_id = f"wa:{wa_from}"
    conversation, _ = Conversation.objects.get_or_create(business=business, visitor_id=visitor_id)
    Message.objects.create(conversation=conversation, role='user', text=text)

    intent = detect_intent(text)
    sentiment = detect_sentiment(text)
    match = find_best_faq(text, business.id)
    confidence = confidence_from_similarity(match.score)
    reply = match.faq.answer if match.faq else business.welcome_message

    escalated, escalation_reason = should_escalate(confidence, sentiment, intent)
    if business.handover_enabled and escalated:
        conversation.needs_human = True
        conversation.save(update_fields=['needs_human', 'updated_at'])
        Ticket.objects.create(
            business=business,
            conversation=conversation,
            subject='Escalated from WhatsApp',
            details=f'Reason: {escalation_reason}. Intent: {intent}. Sentiment: {sentiment}.',
        )
        reply = 'Your WhatsApp message has been forwarded to a human agent.'

    Message.objects.create(conversation=conversation, role='assistant', text=reply)
    send_whatsapp_text(integration.access_token, integration.phone_number_id, wa_from, reply)

    AIInteractionLog.objects.create(
        business=business,
        conversation=conversation,
        user_message=text,
        ai_reply=reply,
        confidence=confidence,
        intent=intent,
        sentiment=sentiment,
        escalated=conversation.needs_human,
        escalation_reason=escalation_reason,
        metadata={**metadata, 'match_method': match.method, 'faq_id': match.faq.id if match.faq else None},
    )
