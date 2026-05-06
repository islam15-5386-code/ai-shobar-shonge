from django.urls import path

from .views import conversation_history

urlpatterns = [
    path('history/', conversation_history, name='conversation-history'),
]
