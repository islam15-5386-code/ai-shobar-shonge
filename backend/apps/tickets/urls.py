from django.urls import path

from .views import ticket_kanban, tickets

urlpatterns = [
    path('', tickets, name='tickets'),
    path('kanban/', ticket_kanban, name='ticket-kanban'),
]
