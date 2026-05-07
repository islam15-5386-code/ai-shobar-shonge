from django.urls import path

from apps.conversations.consumers import InboxConsumer

websocket_urlpatterns = [
    path('ws/business/<int:business_id>/inbox/', InboxConsumer.as_asgi()),
]
