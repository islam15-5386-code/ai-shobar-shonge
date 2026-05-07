from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.accounts.models import UserProfile
from apps.billing.models import Subscription
from apps.businesses.access import can_manage_business_data, get_user_business
from .models import TeamMember


def health(request):
    return JsonResponse({'app': 'tenants', 'status': 'ok'})


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
def team_members(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    if not can_manage_business_data(request.user, business):
        # Fallback for users who are manager/owner via profile but may not
        # have synced TeamMember role yet.
        profile = getattr(request.user, 'profile', None)
        profile_role = getattr(profile, 'role', '')
        if profile_role not in ['owner', 'manager']:
            return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)

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
        email = str(request.data.get('email', '')).strip()
        role = str(request.data.get('role', 'agent')).strip()
        identifier = username or email
        if not identifier:
            return Response({'detail': 'username or email is required'}, status=status.HTTP_400_BAD_REQUEST)
        if role not in ['owner', 'manager', 'agent']:
            return Response({'detail': 'invalid role'}, status=status.HTTP_400_BAD_REQUEST)
        if role == 'owner' and business.owner_id != request.user.id:
            return Response({'detail': 'only business owner can assign owner role'}, status=status.HTTP_403_FORBIDDEN)

        user = User.objects.filter(username=identifier).first()
        if not user and '@' in identifier:
            user = User.objects.filter(email=identifier).first()

        auto_created = False
        if not user:
            uname = identifier if '@' not in identifier else identifier
            user = User.objects.create(username=uname, email=identifier if '@' in identifier else '')
            user.set_unusable_password()
            user.save(update_fields=['password'])
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'full_name': uname.split('@')[0].replace('.', ' ').replace('_', ' ').title(),
                    'phone': '',
                    'role': role if role in ['owner', 'manager', 'agent'] else 'agent',
                    'is_active': True,
                },
            )
            auto_created = True

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
        return Response(
            {
                'id': member.id,
                'user_id': member.user_id,
                'username': user.username,
                'email': user.email,
                'role': member.role,
                'auto_created_user': auto_created,
            },
            status=201,
        )

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
