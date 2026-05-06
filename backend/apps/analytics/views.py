import csv
from datetime import date, timedelta
from io import StringIO

from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.ai_gateway.models import AIInteractionLog
from apps.billing.limits import get_ai_reply_limit_state
from apps.billing.models import Subscription
from apps.businesses.models import Business
from apps.conversations.models import Message
from apps.tickets.models import Ticket
from .models import AnalyticsSnapshot


def health(request):
    return JsonResponse({'app': 'analytics', 'status': 'ok'})


@api_view(['GET'])
def overview(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    conversations = business.conversations.count()
    total_messages = Message.objects.filter(conversation__business=business).count()
    ai_messages = Message.objects.filter(conversation__business=business, role='assistant').count()
    open_tickets = Ticket.objects.filter(business=business, status__in=['open', 'in_progress', 'waiting_customer']).count()
    ai_logs = AIInteractionLog.objects.filter(business=business).count()
    escalated = AIInteractionLog.objects.filter(business=business, escalated=True).count()

    usage_state = get_ai_reply_limit_state(business)
    sub = Subscription.objects.filter(business=business).select_related('plan').first()
    return Response(
        {
            'business_id': business.id,
            'conversations': conversations,
            'total_messages': total_messages,
            'ai_messages': ai_messages,
            'open_tickets': open_tickets,
            'ai_logs': ai_logs,
            'escalated_count': escalated,
            'usage': usage_state,
            'plan': {'code': sub.plan.code, 'name': sub.plan.name} if sub else None,
        }
    )


@api_view(['GET'])
def conversations_analytics(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(
        {
            'total_conversations': business.conversations.count(),
            'daily_message_count': Message.objects.filter(conversation__business=business).count(),
            'ai_resolved_conversations': business.conversations.filter(needs_human=False).count(),
            'human_handover_count': business.conversations.filter(needs_human=True).count(),
        }
    )


@api_view(['GET'])
def tickets_analytics(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    return Response(
        {
            'open_tickets': Ticket.objects.filter(business=business, status='open').count(),
            'in_progress_tickets': Ticket.objects.filter(business=business, status='in_progress').count(),
            'resolved_tickets': Ticket.objects.filter(business=business, status='resolved').count(),
            'closed_tickets': Ticket.objects.filter(business=business, status='closed').count(),
        }
    )


@api_view(['GET'])
def sentiment_analytics(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    qs = AIInteractionLog.objects.filter(business=business)
    return Response(
        {
            'positive': qs.filter(sentiment='positive').count(),
            'neutral': qs.filter(sentiment='neutral').count(),
            'negative': qs.filter(sentiment='negative').count(),
        }
    )


@api_view(['GET'])
def ai_performance(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    qs = AIInteractionLog.objects.filter(business=business)
    total = qs.count() or 1
    avg_conf = round(sum(row.confidence for row in qs) / total, 3) if total else 0
    intents = {}
    for row in qs:
        intents[row.intent] = intents.get(row.intent, 0) + 1
    top_intents = sorted(intents.items(), key=lambda x: x[1], reverse=True)[:5]
    return Response(
        {
            'average_ai_confidence': avg_conf,
            'top_intents': [{'intent': k, 'count': v} for k, v in top_intents],
            'human_handover_count': qs.filter(escalated=True).count(),
        }
    )


@api_view(['POST'])
def snapshot(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    target_date = timezone.localdate()
    snap, _ = AnalyticsSnapshot.objects.update_or_create(
        business=business,
        date=target_date,
        defaults={
            'total_messages': Message.objects.filter(conversation__business=business).count(),
            'ai_messages': Message.objects.filter(conversation__business=business, role='assistant').count(),
            'human_handover_count': AIInteractionLog.objects.filter(business=business, escalated=True).count(),
            'ticket_count': Ticket.objects.filter(business=business).count(),
            'metadata': {'generated_at': timezone.now().isoformat()},
        },
    )
    return Response({'id': snap.id, 'date': snap.date}, status=201)


@api_view(['GET'])
def export_report(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    days = int(request.query_params.get('days', 30))
    if days < 1:
        days = 30
    from_date = date.today() - timedelta(days=days - 1)
    rows = AnalyticsSnapshot.objects.filter(business=business, date__gte=from_date).order_by('date')

    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['date', 'total_messages', 'ai_messages', 'human_handover_count', 'ticket_count'])
    for row in rows:
        writer.writerow([row.date.isoformat(), row.total_messages, row.ai_messages, row.human_handover_count, row.ticket_count])

    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="analytics-report-{business.slug}.csv"'
    return response
