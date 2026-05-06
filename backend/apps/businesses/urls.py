from django.urls import path

from .views import business_setup, upload_logo

urlpatterns = [
    path('setup/', business_setup, name='business-setup'),
    path('upload-logo/', upload_logo, name='business-upload-logo'),
]
