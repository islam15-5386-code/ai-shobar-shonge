from django.db import models


class FAQ(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    category = models.CharField(max_length=120, blank=True)
    tags = models.JSONField(default=list, blank=True)
    language = models.CharField(max_length=10, default='bn')
    embedding_status = models.CharField(max_length=20, default='pending')
    embedding_vector = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question
