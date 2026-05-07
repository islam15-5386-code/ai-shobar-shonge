from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health(request):
    return JsonResponse({'service': 'backend', 'status': 'ok'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health, name='health'),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/members/', include('apps.members.urls')),
    path('api/tenants/', include('apps.tenants.urls')),
    path('api/businesses/', include('apps.businesses.urls')),
    path('api/faqs/', include('apps.faqs.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/customers/', include('apps.customers.urls')),
    path('api/conversations/', include('apps.conversations.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/integrations/', include('apps.integrations.urls')),
    path('api/', include('apps.marketplace.urls')),
    path('api/billing/', include('apps.billing.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
    path('api/ai-gateway/', include('apps.ai_gateway.urls')),
    path('api/', include('apps.core.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
