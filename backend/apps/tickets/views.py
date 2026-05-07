from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from apps.businesses.access import get_user_business, is_agent, is_owner_or_manager
from apps.conversations.models import Conversation
from apps.conversations.realtime import publish_inbox_event
from apps.marketplace.permissions import can_manage_marketplace, get_vendor_for_user
from .models import Ticket, TicketComment


@api_view(['GET', 'POST', 'PATCH'])
def tickets(request):
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    vendor = get_vendor_for_user(request.user, business)
    manage_all = is_owner_or_manager(request.user, business) or can_manage_marketplace(request.user, business)

    if request.method == 'GET':
        qs = Ticket.objects.filter(business=business)
        if not manage_all:
            if is_agent(request.user, business):
                qs = qs.filter(assigned_agent=request.user)
            elif vendor:
                qs = qs.filter(vendor=vendor)
            else:
                qs = qs.none()
        if request.query_params.get('vendor'):
            qs = qs.filter(vendor_id=request.query_params.get('vendor'))
        if request.query_params.get('order'):
            qs = qs.filter(order_id=request.query_params.get('order'))
        if request.query_params.get('product'):
            qs = qs.filter(product_id=request.query_params.get('product'))
        if request.query_params.get('assignment_type'):
            qs = qs.filter(assignment_type=request.query_params.get('assignment_type'))
        return Response([
            {
                'id': t.id,
                'subject': t.subject,
                'details': t.details,
                'status': t.status,
                'vendor_id': t.vendor_id,
                'order_id': t.order_id,
                'product_id': t.product_id,
                'assignment_type': t.assignment_type,
                'conversation_id': t.conversation_id,
                'assigned_agent_id': t.assigned_agent_id,
                'created_at': t.created_at,
            }
            for t in qs.order_by('-created_at')
        ])

    if request.method == 'PATCH':
        ticket_id = request.data.get('ticket_id')
        ticket = Ticket.objects.filter(id=ticket_id, business=business).first()
        if not ticket:
            return Response({'detail': 'ticket not found'}, status=status.HTTP_404_NOT_FOUND)
        if not manage_all and not (is_agent(request.user, business) and ticket.assigned_agent_id == request.user.id) and not (vendor and ticket.vendor_id == vendor.id):
            return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)

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
        vendor_id=request.data.get('vendor_id') or (conversation.vendor_id if conversation else None),
        order_id=request.data.get('order_id') or (conversation.order_id if conversation else None),
        product_id=request.data.get('product_id') or (conversation.product_id if conversation else None),
        assignment_type=str(request.data.get('assignment_type', 'marketplace')),
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
    business = get_user_business(request.user)
    if not business:
        return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
    vendor = get_vendor_for_user(request.user, business)
    manage_all = is_owner_or_manager(request.user, business) or can_manage_marketplace(request.user, business)

    columns = {key: [] for key, _ in Ticket.STATUS_CHOICES}
    qs = Ticket.objects.filter(business=business)
    if not manage_all:
        if is_agent(request.user, business):
            qs = qs.filter(assigned_agent=request.user)
        elif vendor:
            qs = qs.filter(vendor=vendor)
        else:
            qs = qs.none()
    for t in qs.order_by('-created_at'):
        columns[t.status].append(
            {
                'id': t.id,
                'subject': t.subject,
                'details': t.details,
                'vendor_id': t.vendor_id,
                'order_id': t.order_id,
                'product_id': t.product_id,
                'assignment_type': t.assignment_type,
                'conversation_id': t.conversation_id,
                'assigned_agent_id': t.assigned_agent_id,
                'created_at': t.created_at,
            }
        )
    return Response(columns)


@api_view(['POST'])
def ticket_comment(request, ticket_id):
    business = get_user_business(request.user)
    ticket = Ticket.objects.filter(id=ticket_id, business=business).first()
    if not ticket:
        return Response({'detail': 'ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    vendor = get_vendor_for_user(request.user, business)
    if not (is_owner_or_manager(request.user, business) or (is_agent(request.user, business) and ticket.assigned_agent_id == request.user.id) or (vendor and ticket.vendor_id == vendor.id)):
        return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    text = str(request.data.get('text', '')).strip()
    if not text:
        return Response({'detail': 'text is required'}, status=status.HTTP_400_BAD_REQUEST)
    comment = TicketComment.objects.create(ticket=ticket, author=request.user, text=text)
    return Response({'id': comment.id, 'text': comment.text, 'created_at': comment.created_at}, status=201)


@api_view(['POST'])
def ticket_assign(request, ticket_id):
    business = get_user_business(request.user)
    ticket = Ticket.objects.filter(id=ticket_id, business=business).first()
    if not ticket:
        return Response({'detail': 'ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    if not (is_owner_or_manager(request.user, business) or is_agent(request.user, business)):
        return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    ticket.assigned_agent = request.user
    ticket.save(update_fields=['assigned_agent'])
    return Response({'id': ticket.id, 'assigned_agent_id': ticket.assigned_agent_id})


@api_view(['POST'])
def ticket_status(request, ticket_id):
    business = get_user_business(request.user)
    ticket = Ticket.objects.filter(id=ticket_id, business=business).first()
    if not ticket:
        return Response({'detail': 'ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    vendor = get_vendor_for_user(request.user, business)
    if not (is_owner_or_manager(request.user, business) or (is_agent(request.user, business) and ticket.assigned_agent_id == request.user.id) or (vendor and ticket.vendor_id == vendor.id)):
        return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    val = str(request.data.get('status', '')).strip()
    valid = {x[0] for x in Ticket.STATUS_CHOICES}
    if val not in valid:
        return Response({'detail': 'invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    ticket.status = val
    ticket.save(update_fields=['status'])
    return Response({'id': ticket.id, 'status': ticket.status})


@api_view(['POST'])
def ticket_priority(request, ticket_id):
    business = get_user_business(request.user)
    ticket = Ticket.objects.filter(id=ticket_id, business=business).first()
    if not ticket:
        return Response({'detail': 'ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    if not is_owner_or_manager(request.user, business):
        return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    val = str(request.data.get('priority', '')).strip() or 'medium'
    ticket.priority = val
    ticket.save(update_fields=['priority'])
    return Response({'id': ticket.id, 'priority': ticket.priority})


@api_view(['POST'])
def ticket_resolve(request, ticket_id):
    business = get_user_business(request.user)
    ticket = Ticket.objects.filter(id=ticket_id, business=business).first()
    if not ticket:
        return Response({'detail': 'ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    vendor = get_vendor_for_user(request.user, business)
    if not (is_owner_or_manager(request.user, business) or (is_agent(request.user, business) and ticket.assigned_agent_id == request.user.id) or (vendor and ticket.vendor_id == vendor.id)):
        return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    ticket.status = 'resolved'
    ticket.save(update_fields=['status'])
    return Response({'id': ticket.id, 'status': ticket.status})


@api_view(['POST'])
def human_handover(request, ticket_id):
    business = get_user_business(request.user)
    ticket = Ticket.objects.filter(id=ticket_id, business=business).select_related('conversation').first()
    if not ticket:
        return Response({'detail': 'ticket not found'}, status=status.HTTP_404_NOT_FOUND)
    if not (is_owner_or_manager(request.user, business) or is_agent(request.user, business)):
        return Response({'detail': 'permission denied'}, status=status.HTTP_403_FORBIDDEN)
    if ticket.conversation:
        ticket.conversation.needs_human = True
        ticket.conversation.status = 'waiting_human'
        ticket.conversation.save(update_fields=['needs_human', 'status', 'updated_at'])
    ticket.status = 'in_progress'
    ticket.save(update_fields=['status'])
    return Response({'id': ticket.id, 'status': ticket.status, 'handover': True})
