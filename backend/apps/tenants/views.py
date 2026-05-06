from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.billing.models import Subscription
from apps.businesses.models import Business
from .models import TeamMember


def health(request):
    return JsonResponse({'app': 'tenants', 'status': 'ok'})


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
def team_members(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        rows = TeamMember.objects.filter(business=business, is_active=True).select_related('user').order_by('id')
        return Response(
            [
                {'id': m.id, 'user_id': m.user_id, 'username': m.user.username, 'email': m.user.email, 'role': m.role}
                for m in rows
            ]
        )

    if request.method == 'POST':
        username = str(request.data.get('username', '')).strip()
        role = str(request.data.get('role', 'agent')).strip()
        if not username:
            return Response({'detail': 'username is required'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(username=username).first()
        if not user:
            return Response({'detail': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        sub = Subscription.objects.filter(business=business).select_related('plan').first()
        seat_limit = sub.plan.seat_limit if sub else 1
        active_count = TeamMember.objects.filter(business=business, is_active=True).count()
        if active_count >= seat_limit:
            return Response({'detail': 'seat limit exceeded for current plan'}, status=status.HTTP_400_BAD_REQUEST)

        member, _ = TeamMember.objects.update_or_create(
            business=business,
            user=user,
            defaults={'role': role, 'is_active': True},
        )
        return Response({'id': member.id, 'user_id': member.user_id, 'role': member.role}, status=201)

    member_id = request.data.get('member_id')
    member = TeamMember.objects.filter(id=member_id, business=business).first()
    if not member:
        return Response({'detail': 'team member not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PATCH':
        if 'role' in request.data:
            member.role = str(request.data.get('role'))
        if 'is_active' in request.data:
            member.is_active = bool(request.data.get('is_active'))
        member.save()
        return Response({'id': member.id, 'role': member.role, 'is_active': member.is_active})

    member.is_active = False
    member.save(update_fields=['is_active'])
    return Response(status=204)
