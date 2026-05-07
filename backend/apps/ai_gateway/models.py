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


class AIRequestLog(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='ai_request_logs')
    conversation = models.ForeignKey('conversations.Conversation', on_delete=models.SET_NULL, null=True, blank=True)
    input_text = models.TextField()
    output_text = models.TextField(blank=True)
    intent = models.CharField(max_length=80, default='general')
    sentiment = models.CharField(max_length=40, default='neutral')
    confidence = models.FloatField(default=0.0)
    sources = models.JSONField(default=list, blank=True)
    model_name = models.CharField(max_length=120, default='mock')
    latency_ms = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default='ok')
    error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AIAssistantSetting(models.Model):
    business = models.OneToOneField('businesses.Business', on_delete=models.CASCADE, related_name='ai_settings')
    auto_reply_enabled = models.BooleanField(default=True)
    confidence_threshold = models.FloatField(default=0.75)
    business_tone = models.CharField(max_length=40, default='professional')
    language = models.CharField(max_length=20, default='mixed')
    rule_refund = models.BooleanField(default=True)
    rule_negative_sentiment = models.BooleanField(default=True)
    rule_below_confidence = models.BooleanField(default=True)
    rule_customer_requests_human = models.BooleanField(default=True)
    system_prompt = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
