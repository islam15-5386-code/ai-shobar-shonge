from django.urls import path

from .views import ai_logs, website_chat

urlpatterns = [
    path('website-chat/', website_chat, name='website-chat'),
    path('logs/', ai_logs, name='ai-logs'),
]
