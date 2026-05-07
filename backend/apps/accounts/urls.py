from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import admin_overview, login, logout, me, register

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', logout, name='logout'),
    path('me/', me, name='me'),
    path('admin-overview/', admin_overview, name='admin-overview'),
]
