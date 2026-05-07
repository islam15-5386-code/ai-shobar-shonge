from django.urls import path

from .views import ai_logs, ai_settings, website_chat

urlpatterns = [
    path('website-chat/', website_chat, name='website-chat'),
    path('logs/', ai_logs, name='ai-logs'),
    path('settings/', ai_settings, name='ai-settings'),
]
