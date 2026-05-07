from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import admin_overview, google_callback, google_dev_login, google_start, google_status, login, logout, me, register

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', logout, name='logout'),
    path('me/', me, name='me'),
    path('admin-overview/', admin_overview, name='admin-overview'),
    path('google/start/', google_start, name='google-start'),
    path('google/status/', google_status, name='google-status'),
    path('google/dev-login/', google_dev_login, name='google-dev-login'),
    path('google/callback/', google_callback, name='google-callback'),
]
