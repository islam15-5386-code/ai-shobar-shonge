from django.urls import path

from .views import ai_suggested_reply, assign_agent, conversation_history, inbox, internal_notes

urlpatterns = [
    path('history/', conversation_history, name='conversation-history'),
    path('inbox/', inbox, name='conversation-inbox'),
    path('<int:conversation_id>/assign/', assign_agent, name='conversation-assign-agent'),
    path('<int:conversation_id>/notes/', internal_notes, name='conversation-internal-notes'),
    path('<int:conversation_id>/suggested-reply/', ai_suggested_reply, name='conversation-ai-suggested-reply'),
]
