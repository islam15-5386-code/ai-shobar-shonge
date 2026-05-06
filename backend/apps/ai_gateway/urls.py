from django.urls import path

from .views import website_chat

urlpatterns = [
    path('website-chat/', website_chat, name='website-chat'),
]
