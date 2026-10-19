from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AdminAuditLog(TimeStampedModel):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="audit_logs"
    )

    target_type = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100)
    action = models.CharField(max_length=100)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.actor} - {self.action} on {self.target_type}:{self.target_id}"