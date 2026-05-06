from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('waiting_human', 'Waiting Human'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='conversations')
    visitor_id = models.CharField(max_length=128)
    needs_human = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    assigned_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Message(models.Model):
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('ai', 'AI'),
        ('agent', 'Agent'),
        ('system', 'System'),
        ('user', 'User'),
        ('assistant', 'Assistant'),
    )

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    text = models.TextField()
    intent = models.CharField(max_length=80, blank=True)
    sentiment = models.CharField(max_length=40, blank=True)
    confidence = models.FloatField(default=0.0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InternalNote(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='internal_notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
