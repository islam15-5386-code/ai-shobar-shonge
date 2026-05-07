import os
import secrets
from urllib.parse import urlencode

import requests
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseRedirect
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


def _google_oauth_config() -> dict[str, str]:
    return {
        'client_id': os.getenv('GOOGLE_CLIENT_ID', '').strip(),
        'client_secret': os.getenv('GOOGLE_CLIENT_SECRET', '').strip(),
        'redirect_uri': os.getenv('GOOGLE_REDIRECT_URI', '').strip(),
        'frontend_url': os.getenv('FRONTEND_URL', 'http://127.0.0.1:5173').strip(),
    }

def _google_missing_fields(cfg: dict[str, str]) -> list[str]:
    missing = []
    if not cfg.get('client_id'):
        missing.append('GOOGLE_CLIENT_ID')
    if not cfg.get('client_secret'):
        missing.append('GOOGLE_CLIENT_SECRET')
    if not cfg.get('redirect_uri'):
        missing.append('GOOGLE_REDIRECT_URI')
    return missing


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


@api_view(['GET'])
@permission_classes([AllowAny])
def google_start(request):
    cfg = _google_oauth_config()
    missing = _google_missing_fields(cfg)
    if missing:
        if settings.DEBUG:
            dev_url = request.build_absolute_uri('/api/accounts/google/dev-login/')
            return Response({'auth_url': dev_url, 'mode': 'dev-fallback', 'missing': missing})
        return Response({'detail': 'google oauth not configured', 'missing': missing}, status=status.HTTP_501_NOT_IMPLEMENTED)

    state = request.GET.get('state', '').strip() or 'login'
    params = {
        'client_id': cfg['client_id'],
        'redirect_uri': cfg['redirect_uri'],
        'response_type': 'code',
        'scope': 'openid email profile',
        'access_type': 'offline',
        'include_granted_scopes': 'true',
        'prompt': 'select_account',
        'state': state,
    }
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return Response({'auth_url': auth_url})


@api_view(['GET'])
@permission_classes([AllowAny])
def google_status(request):
    cfg = _google_oauth_config()
    missing = _google_missing_fields(cfg)
    return Response({'configured': len(missing) == 0, 'missing': missing, 'dev_fallback_available': bool(settings.DEBUG)})


@api_view(['GET'])
@permission_classes([AllowAny])
def google_callback(request):
    cfg = _google_oauth_config()
    frontend_callback = f"{cfg['frontend_url'].rstrip('/')}/auth/google/callback"

    code = (request.GET.get('code') or '').strip()
    error = (request.GET.get('error') or '').strip()
    if error:
        return HttpResponseRedirect(f"{frontend_callback}?error={error}")
    if not code:
        return HttpResponseRedirect(f"{frontend_callback}?error=missing_oauth_code")
    if not cfg['client_id'] or not cfg['client_secret'] or not cfg['redirect_uri']:
        return HttpResponseRedirect(f"{frontend_callback}?error=google_oauth_not_configured")

    token_res = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'code': code,
            'client_id': cfg['client_id'],
            'client_secret': cfg['client_secret'],
            'redirect_uri': cfg['redirect_uri'],
            'grant_type': 'authorization_code',
        },
        timeout=15,
    )
    if token_res.status_code >= 400:
        return HttpResponseRedirect(f"{frontend_callback}?error=token_exchange_failed")
    token_json = token_res.json()
    google_access_token = token_json.get('access_token')
    if not google_access_token:
        return HttpResponseRedirect(f"{frontend_callback}?error=google_access_token_missing")

    userinfo_res = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {google_access_token}'},
        timeout=15,
    )
    if userinfo_res.status_code >= 400:
        return HttpResponseRedirect(f"{frontend_callback}?error=google_profile_failed")
    profile = userinfo_res.json()
    email = str(profile.get('email') or '').strip().lower()
    full_name = str(profile.get('name') or '').strip()
    if not email:
        return HttpResponseRedirect(f"{frontend_callback}?error=google_email_missing")

    user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(username=email, email=email, password=secrets.token_urlsafe(24))
    else:
        if not user.email:
            user.email = email
            user.save(update_fields=['email'])
    UserProfile.objects.update_or_create(
        user=user,
        defaults={'full_name': full_name, 'role': 'owner', 'is_active': True},
    )

    tokens = _jwt_for_user(user)
    redirect_url = f"{frontend_callback}?access={tokens['access']}&refresh={tokens['refresh']}"
    return HttpResponseRedirect(redirect_url)


@api_view(['GET'])
@permission_classes([AllowAny])
def google_dev_login(request):
    if not settings.DEBUG:
        return Response({'detail': 'not found'}, status=status.HTTP_404_NOT_FOUND)

    cfg = _google_oauth_config()
    frontend_callback = f"{cfg['frontend_url'].rstrip('/')}/auth/google/callback"
    email = "google_demo@supportbond.ai"
    full_name = "Google Demo User"

    user = User.objects.filter(username=email).first() or User.objects.filter(email=email).first()
    if not user:
        user = User.objects.create_user(username=email, email=email, password=secrets.token_urlsafe(24))
    UserProfile.objects.update_or_create(
        user=user,
        defaults={'full_name': full_name, 'role': 'owner', 'is_active': True},
    )
    tokens = _jwt_for_user(user)
    return HttpResponseRedirect(f"{frontend_callback}?access={tokens['access']}&refresh={tokens['refresh']}")
