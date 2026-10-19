import uuid
from django.conf import settings
from django.db import models

from core.models import TimeStampedModel
from courses.models import Course, Lesson


class Enrollment(TimeStampedModel):
    STATUS_ACTIVE = "active"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_COMPLETED, "Completed"),
    ]

    SOURCE_FREE = "free"
    SOURCE_PAID = "paid"
    SOURCE_CHOICES = [
        (SOURCE_FREE, "Free"),
        (SOURCE_PAID, "Paid"),
    ]
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="enrollments"
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course"], name="unique_enrollment_per_student_course"
            )
        ]

    def __str__(self):
        return f"{self.student.email} - {self.course.title}"


class LessonProgress(TimeStampedModel):
    enrollment = models.ForeignKey(
        Enrollment, on_delete=models.CASCADE, related_name="progress"
    )
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["enrollment", "lesson"], name="unique_progress_per_enrollment_lesson"
            )
        ]
    
    def __str__(self):
        status = "completed" if self.is_completed else "pending"
        return f"{self.lesson.title} - {status}"


class Certificate(TimeStampedModel):
    enrollment = models.OneToOneField(
        Enrollment, on_delete=models.CASCADE, related_name="certificate"
    )
    verification_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    student_name = models.CharField(max_length=150)
    course_title = models.CharField(max_length=200)
    completion_date = models.DateField()
    pdf = models.FileField(upload_to="certificates/", null=True, blank=True)

    def __str__(self):
        return f"Certificate {self.verification_id} - {self.student_name}"