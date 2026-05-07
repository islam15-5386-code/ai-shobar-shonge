from django.urls import path

<<<<<<< HEAD
from .views import admin_businesses, admin_suspend_business, business_setup, upload_logo
=======
from .views import business_setup, upload_logo
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a

urlpatterns = [
    path('setup/', business_setup, name='business-setup'),
    path('upload-logo/', upload_logo, name='business-upload-logo'),
<<<<<<< HEAD
    path('admin/businesses/', admin_businesses, name='admin-businesses'),
    path('admin/businesses/<int:business_id>/suspend/', admin_suspend_business, name='admin-business-suspend'),
=======
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a
]
