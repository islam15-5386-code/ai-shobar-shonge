from django.urls import path

from .views import admin_businesses, admin_suspend_business, business_setup, upload_logo

urlpatterns = [
    path('setup/', business_setup, name='business-setup'),
    path('upload-logo/', upload_logo, name='business-upload-logo'),
    path('admin/businesses/', admin_businesses, name='admin-businesses'),
    path('admin/businesses/<int:business_id>/suspend/', admin_suspend_business, name='admin-business-suspend'),
]
