from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.businesses.models import Business
from apps.tenants.models import TeamMember
from .serializers import TeamMemberSerializer


class TeamMemberViewSet(viewsets.ModelViewSet):
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'is_active']
    search_fields = ['user__username', 'user__email']
    ordering_fields = ['id', 'created_at']

    def get_queryset(self):
        business = Business.objects.filter(owner=self.request.user).first()
        if not business:
            return TeamMember.objects.none()
        return TeamMember.objects.filter(business=business).select_related('user').order_by('-id')

    def perform_create(self, serializer):
        business = Business.objects.filter(owner=self.request.user).first()
        serializer.save(business=business)
