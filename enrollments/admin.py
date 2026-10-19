from django.contrib import admin

from .models import Certificate, Enrollment, LessonProgress


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ["student", "course", "status", "source"]
    list_filter = ["status", "source"]
    search_fields = ["student__email", "course__title"]


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ["enrollment", "lesson", "is_completed"]
    list_filter = ["is_completed"]


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ["student_name", "course_title", "completion_date"]
    search_fields = ["student_name", "course_title", "verification_id"]
