from django.urls import path

from . import views
from apps.ai_gateway.views import website_chat, ai_settings

urlpatterns = [
    path('health/', views.health),
    path('conversations/', views.conversations_root),
    path('integrations/', views.integrations_root),
    path('billing/current/', views.billing_current),
    path('widget/config/<str:widget_key>/', views.widget_config),
    path('widget/message/', website_chat),
    path('ai-settings/', ai_settings),
    path('search/', views.search_api),
    path('notifications/unread-count/', views.notifications_unread_count),
]
