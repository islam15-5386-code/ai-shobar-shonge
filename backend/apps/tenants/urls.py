from django.urls import path

from .views import health, team_members

urlpatterns = [
    path('health/', health, name='health'),
    path('team-members/', team_members, name='team-members'),
]
