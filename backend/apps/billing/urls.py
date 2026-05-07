from django.urls import path

from .views import current, health, invoices, pricing_plans, sandbox_checkout, subscription, usage

urlpatterns = [
    path('health/', health, name='health'),
    path('plans/', pricing_plans, name='pricing-plans'),
    path('subscription/', subscription, name='subscription'),
    path('current/', current, name='current'),
    path('usage/', usage, name='usage'),
    path('invoices/', invoices, name='invoices'),
    path('sandbox/checkout/', sandbox_checkout, name='sandbox-checkout'),
]
