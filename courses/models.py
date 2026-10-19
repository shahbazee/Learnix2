from django.conf import settings
from django.db import models

from core.models import TimeStampedModel


class Category(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Course(TimeStampedModel):
    STATUS_DRAFT = "draft"
    STATUS_PENDING = "pending"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PENDING, "Pending Approval"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses"
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="courses"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_free = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title


class Module(TimeStampedModel):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="modules"
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "position"],
                name="unique_module_position_per_course",
            )
        ]

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(TimeStampedModel):
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name="lessons"
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    position = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(
                fields=["module", "position"],
                name="unique_lesson_position_per_module",
            )
        ]

    def __str__(self):
        return f"{self.module.title} - {self.title}"
