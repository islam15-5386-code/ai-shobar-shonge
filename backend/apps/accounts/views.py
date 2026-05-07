from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.businesses.models import Business
from .models import UserProfile


def _jwt_for_user(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {'refresh': str(refresh), 'access': str(refresh.access_token)}


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    if not username and email:
        username = email
    password = request.data.get('password', '')
    full_name = request.data.get('full_name', '').strip()
    phone = request.data.get('phone', '').strip()
    role = request.data.get('role', 'owner').strip() or 'owner'

    if not username or not password:
        return Response({'detail': 'username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({'detail': 'username already exists'}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    UserProfile.objects.update_or_create(
        user=user,
        defaults={'full_name': full_name, 'phone': phone, 'role': role if role in ['owner', 'manager', 'agent'] else 'owner', 'is_active': True},
    )
    business_name = request.data.get('business_name', '').strip()
    business_slug = request.data.get('business_slug', '').strip()
    if business_name and business_slug:
        Business.objects.get_or_create(
            owner=user,
            defaults={'name': business_name, 'slug': business_slug, 'website': request.data.get('business_website', '').strip()},
        )
    tokens = _jwt_for_user(user)
    return Response(
        {
            'tokens': tokens,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': full_name,
                'phone': phone,
                'role': role,
            },
        },
        status=201,
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    username = request.data.get('username', '').strip()
    if not username:
        username = request.data.get('email', '').strip()
    password = request.data.get('password', '')

    user = User.objects.filter(username=username).first()
    if not user or not user.check_password(password):
        return Response({'detail': 'invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    tokens = _jwt_for_user(user)
    profile = getattr(user, 'profile', None)
    return Response(
        {
            'tokens': tokens,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': profile.full_name if profile else '',
                'phone': profile.phone if profile else '',
                'role': profile.role if profile else 'owner',
            },
        }
    )


@api_view(['POST'])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass
    return Response({'detail': 'logged out'})


@api_view(['GET', 'PUT', 'PATCH'])
def me(request):
    profile = getattr(request.user, 'profile', None)
    if request.method in ['PUT', 'PATCH']:
        full_name = str(request.data.get('full_name', profile.full_name if profile else '')).strip()
        phone = str(request.data.get('phone', profile.phone if profile else '')).strip()
        if profile:
            profile.full_name = full_name
            profile.phone = phone
            profile.save(update_fields=['full_name', 'phone'])
        else:
            UserProfile.objects.create(user=request.user, full_name=full_name, phone=phone, role='owner', is_active=True)
        profile = getattr(request.user, 'profile', None)

    return Response(
        {
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'full_name': profile.full_name if profile else '',
            'phone': profile.phone if profile else '',
            'role': profile.role if profile else 'owner',
            'is_active': profile.is_active if profile else request.user.is_active,
        }
    )


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_overview(request):
    return Response(
        {
            'users': User.objects.count(),
            'businesses': Business.objects.count(),
        }
    )
