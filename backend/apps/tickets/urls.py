from django.urls import path

from .views import (
    human_handover,
    ticket_assign,
    ticket_comment,
    ticket_kanban,
    ticket_priority,
    ticket_resolve,
    ticket_status,
    tickets,
)

urlpatterns = [
    path('', tickets, name='tickets'),
    path('kanban/', ticket_kanban, name='ticket-kanban'),
    path('<int:ticket_id>/comments/', ticket_comment, name='ticket-comment'),
    path('<int:ticket_id>/assign/', ticket_assign, name='ticket-assign'),
    path('<int:ticket_id>/status/', ticket_status, name='ticket-status'),
    path('<int:ticket_id>/priority/', ticket_priority, name='ticket-priority'),
    path('<int:ticket_id>/resolve/', ticket_resolve, name='ticket-resolve'),
    path('<int:ticket_id>/handover/', human_handover, name='ticket-handover'),
]
