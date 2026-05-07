from django.urls import path

<<<<<<< HEAD
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
=======
from .views import health, integrations_summary, messenger_setup, messenger_webhook, whatsapp_setup, whatsapp_webhook
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a

urlpatterns = [
    path('health/', health, name='health'),
    path('', integrations_summary, name='integrations-summary'),
    path('messenger/setup/', messenger_setup, name='messenger-setup'),
    path('messenger/webhook/', messenger_webhook, name='messenger-webhook'),
    path('whatsapp/setup/', whatsapp_setup, name='whatsapp-setup'),
<<<<<<< HEAD
    path('whatsapp/status/', whatsapp_connection_status, name='whatsapp-status'),
    path('whatsapp/send/', whatsapp_send, name='whatsapp-send'),
    path('whatsapp/bulk-send/', whatsapp_bulk_send, name='whatsapp-bulk-send'),
=======
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a
    path('whatsapp/webhook/', whatsapp_webhook, name='whatsapp-webhook'),
]
