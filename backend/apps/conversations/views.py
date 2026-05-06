from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.businesses.models import Business
from .models import Conversation


@api_view(['GET'])
def conversation_history(request):
    business = Business.objects.filter(owner=request.user).first()
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)

    payload = []
    for conv in Conversation.objects.filter(business=business).order_by('-updated_at')[:100]:
        payload.append(
            {
                'id': conv.id,
                'visitor_id': conv.visitor_id,
                'needs_human': conv.needs_human,
                'updated_at': conv.updated_at,
                'messages': [
                    {
                        'id': msg.id,
                        'role': msg.role,
                        'text': msg.text,
                        'created_at': msg.created_at,
                    }
                    for msg in conv.messages.order_by('created_at')
                ],
            }
        )
    return Response(payload)
