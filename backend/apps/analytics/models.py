from django.db import models


class AnalyticsSnapshot(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='analytics_snapshots')
    date = models.DateField()
    total_messages = models.IntegerField(default=0)
    ai_messages = models.IntegerField(default=0)
    human_handover_count = models.IntegerField(default=0)
    ticket_count = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('business', 'date')
