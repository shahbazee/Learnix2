from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course,Lesson
from .models import Certificate, Enrollment, LessonProgress
from .services import check_course_completion
from .serializers import EnrollmentCreateSerializer, CertificateSerializer, LessonProgressSerializer


class EnrollmentCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EnrollmentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(
            Course,
            slug=serializer.validated_data["course_slug"],
            status=Course.STATUS_PUBLISHED,
        )
        if not course.is_free and course.price > 0:
            return Response(
                {"detail": "This is the paid course. Please complete payment."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
            defaults={"source": Enrollment.SOURCE_FREE},
        )
        if not created:
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"detail": "Enrolled successfully."},
            status=status.HTTP_201_CREATED,
        )


class LessonProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        serializer = LessonProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        lesson = get_object_or_404(Lesson, id=lesson_id)
        enrollment = Enrollment.objects.filter(
            student=request.user, course=lesson.module.course
        ).first()
        if not enrollment:
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )
        progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )
        is_completed = serializer.validated_data["is_completed"]
        progress.is_completed = is_completed
        progress.completed_at = timezone.now() if is_completed else None
        progress.save(update_fields=["is_completed", "completed_at"])
        check_course_completion(enrollment)
        return Response(
            {"detail": "Progress updated."},
            status=status.HTTP_200_OK,
        )


class CertificateVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, verification_id):
        certificate = get_object_or_404(
            Certificate, verification_id=verification_id
        )
        serializer = CertificateSerializer(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyCertificatesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CertificateSerializer

    def get_queryset(self):
        return Certificate.objects.filter(
            enrollment__student=self.request.user
        )


class MyCertificatesTemplateView(LoginRequiredMixin, ListView):
    model = Certificate
    template_name = "enrollments/certificate_list.html"
    context_object_name = "certificates"

    def get_queryset(self):
        return Certificate.objects.filter(enrollment__student=self.request.user)


class CertificateVerifyTemplateView(DetailView):
    model = Certificate
    template_name = "enrollments/certificate_verify.html"
    context_object_name = "certificate"
    slug_field = "verification_id"
    slug_url_kwarg = "verification_id"


