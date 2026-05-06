from django.db import models


class AIInteractionLog(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='ai_logs')
    conversation = models.ForeignKey('conversations.Conversation', on_delete=models.SET_NULL, null=True, blank=True)
    user_message = models.TextField()
    ai_reply = models.TextField(blank=True)
    confidence = models.FloatField(default=0.0)
    intent = models.CharField(max_length=80, default='general')
    sentiment = models.CharField(max_length=40, default='neutral')
    escalated = models.BooleanField(default=False)
    escalation_reason = models.CharField(max_length=120, default='none')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
