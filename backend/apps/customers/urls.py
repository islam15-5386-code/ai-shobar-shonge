from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import CustomerProfileViewSet, health

router = DefaultRouter()
router.register('', CustomerProfileViewSet, basename='customers')

urlpatterns = [
    path('health/', health, name='health'),
] + router.urls
