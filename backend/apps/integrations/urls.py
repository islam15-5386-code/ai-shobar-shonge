from django.urls import path

from .views import health, messenger_setup, messenger_webhook, whatsapp_setup, whatsapp_webhook

urlpatterns = [
    path('health/', health, name='health'),
    path('messenger/setup/', messenger_setup, name='messenger-setup'),
    path('messenger/webhook/', messenger_webhook, name='messenger-webhook'),
    path('whatsapp/setup/', whatsapp_setup, name='whatsapp-setup'),
    path('whatsapp/webhook/', whatsapp_webhook, name='whatsapp-webhook'),
]
