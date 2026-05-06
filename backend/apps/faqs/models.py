from django.db import models


class FAQ(models.Model):
    business = models.ForeignKey('businesses.Business', on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=500)
    answer = models.TextField()
    embedding_vector = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question
