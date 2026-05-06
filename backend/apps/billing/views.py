from datetime import datetime
from decimal import Decimal

from django.http import JsonResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.businesses.models import Business
from .models import Invoice, PricingPlan, Subscription, UsageRecord


def health(request):
    return JsonResponse({'app': 'billing', 'status': 'ok'})


def _month_key() -> str:
    now = timezone.now()
    return f"{now.year:04d}-{now.month:02d}"


@api_view(['GET', 'POST'])
def pricing_plans(request):
    if request.method == 'GET':
        plans = PricingPlan.objects.filter(is_active=True).order_by('monthly_price')
        return Response(
            [
                {
                    'id': p.id,
                    'code': p.code,
                    'name': p.name,
                    'monthly_price': str(p.monthly_price),
                    'message_limit': p.message_limit,
                    'seat_limit': p.seat_limit,
                    'features': p.features,
                }
                for p in plans
            ]
        )

    code = str(request.data.get('code', '')).strip()
    name = str(request.data.get('name', '')).strip()
    if not code or not name:
        return Response({'detail': 'code and name are required'}, status=status.HTTP_400_BAD_REQUEST)
    plan = PricingPlan.objects.create(
        code=code,
        name=name,
        monthly_price=Decimal(str(request.data.get('monthly_price', '0'))),
        message_limit=int(request.data.get('message_limit', 500)),
        seat_limit=int(request.data.get('seat_limit', 1)),
        features=request.data.get('features', {}) or {},
    )
    return Response({'id': plan.id, 'code': plan.code}, status=201)


@api_view(['GET', 'POST', 'PATCH'])
def subscription(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    sub = Subscription.objects.filter(business=business).select_related('plan').first()
    if request.method == 'GET':
        if not sub:
            return Response({'detail': 'no subscription'}, status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                'id': sub.id,
                'status': sub.status,
                'plan': {'id': sub.plan_id, 'code': sub.plan.code, 'name': sub.plan.name},
                'start_date': sub.start_date,
                'current_period_end': sub.current_period_end,
                'cancel_at_period_end': sub.cancel_at_period_end,
            }
        )

    if request.method == 'POST':
        plan_id = request.data.get('plan_id')
        plan = PricingPlan.objects.filter(id=plan_id, is_active=True).first()
        if not plan:
            return Response({'detail': 'valid plan_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        sub, _ = Subscription.objects.update_or_create(
            business=business,
            defaults={
                'plan': plan,
                'status': str(request.data.get('status', 'active')),
                'current_period_end': request.data.get('current_period_end'),
                'cancel_at_period_end': bool(request.data.get('cancel_at_period_end', False)),
            },
        )
        return Response({'id': sub.id, 'status': sub.status, 'plan_id': sub.plan_id}, status=201)

    if not sub:
        return Response({'detail': 'no subscription'}, status=status.HTTP_404_NOT_FOUND)
    if 'status' in request.data:
        sub.status = str(request.data.get('status'))
    if 'cancel_at_period_end' in request.data:
        sub.cancel_at_period_end = bool(request.data.get('cancel_at_period_end'))
    sub.save()
    return Response({'id': sub.id, 'status': sub.status, 'cancel_at_period_end': sub.cancel_at_period_end})


@api_view(['GET', 'POST'])
def usage(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    month = str(request.query_params.get('month', _month_key()))
    metric = str(request.query_params.get('metric', 'messages'))
    if request.method == 'POST':
        metric = str(request.data.get('metric', 'messages'))
        month = str(request.data.get('month', _month_key()))
        increment = int(request.data.get('increment', 1))
        record, _ = UsageRecord.objects.get_or_create(
            business=business, metric=metric, period_type='monthly', period_key=month, defaults={'quantity': 0}
        )
        record.quantity += max(0, increment)
        record.save(update_fields=['quantity', 'updated_at'])
        return Response({'metric': record.metric, 'month': record.period_key, 'quantity': record.quantity})

    record = UsageRecord.objects.filter(business=business, metric=metric, period_type='monthly', period_key=month).first()
    quantity = record.quantity if record else 0
    sub = Subscription.objects.filter(business=business).select_related('plan').first()
    limit = sub.plan.message_limit if sub and metric == 'messages' else None
    return Response(
        {
            'metric': metric,
            'month': month,
            'quantity': quantity,
            'limit': limit,
            'remaining': (limit - quantity) if isinstance(limit, int) else None,
            'is_exceeded': bool(isinstance(limit, int) and quantity > limit),
        }
    )


@api_view(['GET', 'POST', 'PATCH'])
def invoices(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        data = []
        for inv in Invoice.objects.filter(business=business).order_by('-created_at'):
            data.append(
                {
                    'id': inv.id,
                    'invoice_number': inv.invoice_number,
                    'amount': str(inv.amount),
                    'currency': inv.currency,
                    'status': inv.status,
                    'due_date': inv.due_date,
                    'issued_at': inv.issued_at,
                    'paid_at': inv.paid_at,
                }
            )
        return Response(data)

    if request.method == 'POST':
        sub = Subscription.objects.filter(business=business).first()
        number = str(request.data.get('invoice_number', '')).strip() or f"INV-{business.id}-{int(timezone.now().timestamp())}"
        inv = Invoice.objects.create(
            business=business,
            subscription=sub,
            amount=Decimal(str(request.data.get('amount', '0'))),
            currency=str(request.data.get('currency', 'USD')),
            status=str(request.data.get('status', 'draft')),
            invoice_number=number,
            due_date=request.data.get('due_date') or None,
            issued_at=timezone.now() if str(request.data.get('status', 'draft')) in ['issued', 'paid'] else None,
            metadata=request.data.get('metadata', {}) or {},
        )
        return Response({'id': inv.id, 'invoice_number': inv.invoice_number, 'status': inv.status}, status=201)

    invoice_id = request.data.get('invoice_id')
    inv = Invoice.objects.filter(id=invoice_id, business=business).first()
    if not inv:
        return Response({'detail': 'invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    if 'status' in request.data:
        inv.status = str(request.data.get('status'))
        if inv.status == 'issued' and not inv.issued_at:
            inv.issued_at = timezone.now()
        if inv.status == 'paid':
            inv.paid_at = timezone.now()
    if 'due_date' in request.data:
        val = request.data.get('due_date')
        inv.due_date = datetime.strptime(val, '%Y-%m-%d').date() if val else None
    inv.save()
    return Response({'id': inv.id, 'status': inv.status, 'paid_at': inv.paid_at})
