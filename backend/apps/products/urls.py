from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet, health

router = DefaultRouter()
router.register('', ProductViewSet, basename='products')

urlpatterns = [
    path('health/', health, name='health'),
] + router.urls
