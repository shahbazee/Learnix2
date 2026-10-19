from rest_framework import serializers


from .models import Certificate


class EnrollmentCreateSerializer(serializers.Serializer):
    course_slug = serializers.SlugField()


class LessonProgressSerializer(serializers.Serializer):
    is_completed = serializers.BooleanField()


class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = [
            "student_name",
            "course_title",
            "completion_date",
            "verification_id",
            "pdf",
        ]