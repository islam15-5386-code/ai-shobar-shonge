from django.urls import path

from .views import faq_detail, faq_list_create

urlpatterns = [
    path('', faq_list_create, name='faq-list-create'),
    path('<int:faq_id>/', faq_detail, name='faq-detail'),
]
