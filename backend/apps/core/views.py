from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from apps.businesses.access import get_user_business
from apps.ai_gateway.views import website_chat, ai_settings
from apps.billing.views import subscription, usage
from apps.conversations.models import Conversation
from apps.tickets.models import Ticket
from apps.products.models import Product
from apps.customers.models import CustomerProfile


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversations_root(request):
    business = get_user_business(request.user)
    if not business:
        return Response([])
    return Response([
        {'id': c.id, 'visitor_id': c.visitor_id, 'status': c.status, 'updated_at': c.updated_at}
        for c in Conversation.objects.filter(business=business).order_by('-updated_at')[:200]
    ])


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def integrations_root(request):
    return Response({'messenger': '/api/integrations/messenger/setup/', 'whatsapp': '/api/integrations/whatsapp/setup/'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def billing_current(request):
    sub = subscription(request)
    use = usage(request)
    return Response({'subscription': getattr(sub, 'data', None), 'usage': getattr(use, 'data', None)})


@api_view(['GET'])
@permission_classes([AllowAny])
def widget_config(request, widget_key):
    from apps.businesses.models import Business

    b = Business.objects.filter(slug=widget_key).first()
    if not b:
        return Response({'detail': 'widget not found'}, status=404)
    return Response({'widget_key': widget_key, 'business_slug': b.slug, 'welcome_message': b.welcome_message, 'handover_enabled': b.handover_enabled})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_api(request):
    q = str(request.query_params.get('q', '')).strip().lower()
    business = get_user_business(request.user)
    if not business:
        return Response({'results': []})
    results = []
    if q:
        for p in Product.objects.filter(business=business, name__icontains=q)[:10]:
            results.append({'type': 'product', 'id': p.id, 'title': p.name})
        for t in Ticket.objects.filter(business=business, subject__icontains=q)[:10]:
            results.append({'type': 'ticket', 'id': t.id, 'title': t.subject})
        for c in CustomerProfile.objects.filter(business=business, name__icontains=q)[:10]:
            results.append({'type': 'customer', 'id': c.id, 'title': c.name})
    return Response({'results': results})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notifications_unread_count(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'unread_count': 0})
    count = Ticket.objects.filter(business=business, status__in=['open', 'in_progress']).count()
    return Response({'unread_count': count})


def health(request):
    return JsonResponse({'app': 'core', 'status': 'ok'})
