from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.businesses.access import get_user_business
from apps.businesses.models import Business
from .models import Product
from .serializers import ProductSerializer


@api_view(['GET'])
def health(request):
    return Response({'app': 'products', 'status': 'ok'})


def _ensure_business_for_user(user):
    business = get_user_business(user)
    if business:
        return business
    base_slug = f"business-{user.id}"
    slug = base_slug
    i = 2
    while Business.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{i}"
        i += 1
    return Business.objects.create(
        owner=user,
        name=f"Business {user.id}",
        slug=slug,
        website="",
        welcome_message="Hello! How can I help you today?",
        handover_enabled=True,
        category="shop",
        support_email="",
        support_phone="",
        business_hours="",
        address="",
    )


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['is_active', 'currency']
    search_fields = ['name', 'description']
    ordering_fields = ['id', 'name', 'price', 'created_at']

    def get_queryset(self):
        business = get_user_business(self.request.user)
        if not business:
            return Product.objects.none()
        return Product.objects.filter(business=business).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        business = _ensure_business_for_user(request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(business=business)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='reindex')
    def reindex(self, request):
        qs = self.get_queryset()
        qs.update(embedding_status='pending')
        return Response({'status': 'queued', 'count': qs.count()})
