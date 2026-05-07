from django.db import models
from django.contrib.auth.models import User


class Ticket(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_customer', 'Waiting Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='tickets')
    vendor = models.ForeignKey('marketplace.Vendor', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    order = models.ForeignKey('marketplace.Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    assignment_type = models.CharField(max_length=20, default='marketplace')
    conversation = models.ForeignKey('conversations.Conversation', on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    priority = models.CharField(max_length=20, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
