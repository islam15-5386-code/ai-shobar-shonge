from django.urls import path

from .views import (
    ai_performance,
    conversations_analytics,
    export_report,
    health,
    overview,
    sentiment_analytics,
    snapshot,
    tickets_analytics,
)

urlpatterns = [
    path('health/', health, name='health'),
    path('overview/', overview, name='analytics-overview'),
    path('conversations/', conversations_analytics, name='analytics-conversations'),
    path('tickets/', tickets_analytics, name='analytics-tickets'),
    path('sentiment/', sentiment_analytics, name='analytics-sentiment'),
    path('ai-performance/', ai_performance, name='analytics-ai-performance'),
    path('snapshot/', snapshot, name='analytics-snapshot'),
    path('export/', export_report, name='analytics-export'),
]
