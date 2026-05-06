from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.businesses.models import Business
from apps.conversations.models import Conversation
from .models import Ticket


@api_view(['GET', 'POST'])
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
                'created_at': t.created_at,
            }
            for t in Ticket.objects.filter(business=business).order_by('-created_at')
        ])

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
    )
    return Response({'id': ticket.id, 'status': ticket.status}, status=201)
