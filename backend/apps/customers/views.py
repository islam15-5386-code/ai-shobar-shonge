from rest_framework import status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.businesses.models import Business
from .models import CustomerProfile
from .serializers import CustomerProfileSerializer


@api_view(['GET'])
def health(request):
    return Response({'app': 'customers', 'status': 'ok'})


class CustomerProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerProfileSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['external_source']
    search_fields = ['name', 'external_id']
    ordering_fields = ['id', 'name', 'created_at']

    def get_queryset(self):
        business = Business.objects.filter(owner=self.request.user).first()
        if not business:
            return CustomerProfile.objects.none()
        return CustomerProfile.objects.filter(business=business).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        business = Business.objects.filter(owner=request.user).first()
        if not business:
            return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(business=business)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
