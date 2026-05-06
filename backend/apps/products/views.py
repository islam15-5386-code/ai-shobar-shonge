from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.businesses.models import Business
from .models import Product
from .serializers import ProductSerializer


@api_view(['GET'])
def health(request):
    return Response({'app': 'products', 'status': 'ok'})


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'currency']
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name', 'price', 'created_at']

    def get_queryset(self):
        business = Business.objects.filter(owner=self.request.user).first()
        if not business:
            return Product.objects.none()
        return Product.objects.filter(business=business).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        business = Business.objects.filter(owner=request.user).first()
        if not business:
            return Response({'detail': 'business setup required'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(business=business)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='reindex')
    def reindex(self, request):
        qs = self.get_queryset()
        qs.update(embedding_status='pending')
        return Response({'status': 'queued', 'count': qs.count()})
