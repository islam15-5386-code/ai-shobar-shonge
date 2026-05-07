from django.urls import path

from .views import faq_bulk_import, faq_detail, faq_list_create, faq_reindex

urlpatterns = [
    path('', faq_list_create, name='faq-list-create'),
    path('bulk-import/', faq_bulk_import, name='faq-bulk-import'),
    path('reindex/', faq_reindex, name='faq-reindex'),
    path('<int:faq_id>/', faq_detail, name='faq-detail'),
]
