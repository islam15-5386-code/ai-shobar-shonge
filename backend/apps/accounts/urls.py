from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

<<<<<<< HEAD
from .views import admin_overview, google_callback, google_dev_login, google_start, google_status, login, logout, me, register
=======
from .views import admin_overview, login, logout, me, register
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', logout, name='logout'),
    path('me/', me, name='me'),
    path('admin-overview/', admin_overview, name='admin-overview'),
<<<<<<< HEAD
    path('google/start/', google_start, name='google-start'),
    path('google/status/', google_status, name='google-status'),
    path('google/dev-login/', google_dev_login, name='google-dev-login'),
    path('google/callback/', google_callback, name='google-callback'),
=======
>>>>>>> 1a3cceb383ca42cb29c58b955a27e37a6bea8e6a
]
