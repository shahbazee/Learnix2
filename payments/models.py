from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from courses.models import Course


class Payment(TimeStampedModel):
    STATUS_PENDING = "pending"
    STATUS_COMPLETED = "successed"
    STATUS_FAILED = "failed"
    STATUS_CANCELED = "canceled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_FAILED, "Failed"),
        (STATUS_CANCELED, "Canceled"),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments"
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name="payments"
        )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING
        )
    stripe_session_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )
    stripe_event_id = models.CharField(
        max_length=255, unique=True, null=True, blank=True
    )

    def __str__(self):
        return f"{self.student.email} - {self.course.title} - {self.amount} {self.currency}"