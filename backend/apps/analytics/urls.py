from django.urls import path

from .views import export_report, health, overview, snapshot

urlpatterns = [
    path('health/', health, name='health'),
    path('overview/', overview, name='analytics-overview'),
    path('snapshot/', snapshot, name='analytics-snapshot'),
    path('export/', export_report, name='analytics-export'),
]
