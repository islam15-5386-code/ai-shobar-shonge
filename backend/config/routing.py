from django.urls import path

from apps.conversations.consumers import InboxConsumer

websocket_urlpatterns = [
    path('ws/inbox/<int:business_id>/', InboxConsumer.as_asgi()),
]
