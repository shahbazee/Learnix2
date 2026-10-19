from django.db import models

from core.models import TimeStampedModel


class EmailLog(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_SENT = "sent"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_SENT, "Sent"),
        (STATUS_FAILED, "Failed"),
    ]

    event_type = models.CharField(max_length=50)
    recipient = models.EmailField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    attempts = models.PositiveIntegerField(default=0)
    error_detail = models.TextField(blank=True)

    def __str__(self):
        return f"{self.event_type} to {self.recipient} - {self.status}"