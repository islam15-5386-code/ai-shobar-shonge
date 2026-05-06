from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Business


@api_view(['GET', 'POST', 'PATCH'])
def business_setup(request):
    business = Business.objects.filter(owner=request.user).first()

    if request.method == 'GET':
        if not business:
            return Response({'detail': 'business not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(_serialize(business))

    payload = {
        'name': request.data.get('name', ''),
        'slug': request.data.get('slug', ''),
        'website': request.data.get('website', ''),
        'welcome_message': request.data.get('welcome_message', 'Hello! How can I help you today?'),
        'handover_enabled': request.data.get('handover_enabled', True),
    }

    if not business:
        if not payload['name'] or not payload['slug']:
            return Response({'detail': 'name and slug are required'}, status=status.HTTP_400_BAD_REQUEST)
        business = Business.objects.create(owner=request.user, **payload)
        return Response(_serialize(business), status=201)

    for key, value in payload.items():
        if key in request.data:
            setattr(business, key, value)
    business.save()
    return Response(_serialize(business))


def _serialize(business: Business):
    return {
        'id': business.id,
        'name': business.name,
        'slug': business.slug,
        'website': business.website,
        'welcome_message': business.welcome_message,
        'handover_enabled': business.handover_enabled,
    }
