from django.utils import timezone

from .models import Subscription, UsageRecord


def current_month_key() -> str:
    now = timezone.now()
    return f"{now.year:04d}-{now.month:02d}"


def get_ai_reply_limit_state(business) -> dict:
    sub = Subscription.objects.filter(business=business, status__in=['active', 'trial']).select_related('plan').first()
    if not sub:
        return {'allowed': True, 'quantity': 0, 'limit': None}
    month = current_month_key()
    record = UsageRecord.objects.filter(
        business=business, metric='messages', period_type='monthly', period_key=month
    ).first()
    qty = record.quantity if record else 0
    limit = sub.plan.message_limit
    return {'allowed': qty < limit, 'quantity': qty, 'limit': limit}


def increment_ai_usage(business, by: int = 1) -> None:
    month = current_month_key()
    record, _ = UsageRecord.objects.get_or_create(
        business=business, metric='messages', period_type='monthly', period_key=month, defaults={'quantity': 0}
    )
    record.quantity += max(0, by)
    record.save(update_fields=['quantity', 'updated_at'])
