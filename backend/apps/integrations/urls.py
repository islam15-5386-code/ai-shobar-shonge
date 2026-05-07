from django.urls import path

from .views import (
    health,
    integrations_summary,
    messenger_setup,
    messenger_webhook,
    whatsapp_bulk_send,
    whatsapp_connection_status,
    whatsapp_send,
    whatsapp_setup,
    whatsapp_webhook,
)

urlpatterns = [
    path('health/', health, name='health'),
    path('', integrations_summary, name='integrations-summary'),
    path('messenger/setup/', messenger_setup, name='messenger-setup'),
    path('messenger/webhook/', messenger_webhook, name='messenger-webhook'),
    path('whatsapp/setup/', whatsapp_setup, name='whatsapp-setup'),
    path('whatsapp/status/', whatsapp_connection_status, name='whatsapp-status'),
    path('whatsapp/send/', whatsapp_send, name='whatsapp-send'),
    path('whatsapp/bulk-send/', whatsapp_bulk_send, name='whatsapp-bulk-send'),
    path('whatsapp/webhook/', whatsapp_webhook, name='whatsapp-webhook'),
]
