from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.businesses.models import Business
from apps.conversations.models import Conversation
from apps.conversations.realtime import publish_inbox_event
from .models import Ticket


@api_view(['GET', 'POST', 'PATCH'])
def tickets(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'GET':
        return Response([
            {
                'id': t.id,
                'subject': t.subject,
                'details': t.details,
                'status': t.status,
                'conversation_id': t.conversation_id,
                'assigned_agent_id': t.assigned_agent_id,
                'created_at': t.created_at,
            }
            for t in Ticket.objects.filter(business=business).order_by('-created_at')
        ])

    if request.method == 'PATCH':
        ticket_id = request.data.get('ticket_id')
        ticket = Ticket.objects.filter(id=ticket_id, business=business).first()
        if not ticket:
            return Response({'detail': 'ticket not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'status' in request.data:
            status_val = str(request.data.get('status'))
            valid = {choice[0] for choice in Ticket.STATUS_CHOICES}
            if status_val not in valid:
                return Response({'detail': 'invalid status'}, status=status.HTTP_400_BAD_REQUEST)
            ticket.status = status_val

        if 'assign_to_me' in request.data and bool(request.data.get('assign_to_me')):
            ticket.assigned_agent = request.user

        ticket.save()
        publish_inbox_event(
            business.id,
            {'type': 'ticket_updated', 'ticket_id': ticket.id, 'status': ticket.status, 'assigned_agent_id': ticket.assigned_agent_id},
        )
        return Response({'id': ticket.id, 'status': ticket.status, 'assigned_agent_id': ticket.assigned_agent_id})

    subject = request.data.get('subject', '').strip() or 'Support Request'
    details = request.data.get('details', '').strip()
    conversation_id = request.data.get('conversation_id')

    conversation = None
    if conversation_id:
        conversation = Conversation.objects.filter(id=conversation_id, business=business).first()

    ticket = Ticket.objects.create(
        business=business,
        conversation=conversation,
        subject=subject,
        details=details,
        assigned_agent=request.user if bool(request.data.get('assign_to_me')) else None,
    )
    publish_inbox_event(
        business.id,
        {'type': 'ticket_created', 'ticket_id': ticket.id, 'status': ticket.status, 'conversation_id': ticket.conversation_id},
    )
    return Response({'id': ticket.id, 'status': ticket.status}, status=201)


@api_view(['GET'])
def ticket_kanban(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    columns = {key: [] for key, _ in Ticket.STATUS_CHOICES}
    for t in Ticket.objects.filter(business=business).order_by('-created_at'):
        columns[t.status].append(
            {
                'id': t.id,
                'subject': t.subject,
                'details': t.details,
                'conversation_id': t.conversation_id,
                'assigned_agent_id': t.assigned_agent_id,
                'created_at': t.created_at,
            }
        )
    return Response(columns)
