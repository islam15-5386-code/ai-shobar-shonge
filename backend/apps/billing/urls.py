from django.urls import path

from .views import health, invoices, pricing_plans, subscription, usage

urlpatterns = [
    path('health/', health, name='health'),
    path('plans/', pricing_plans, name='pricing-plans'),
    path('subscription/', subscription, name='subscription'),
    path('usage/', usage, name='usage'),
    path('invoices/', invoices, name='invoices'),
]
