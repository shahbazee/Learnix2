from django.urls import path

from .views import EnrollmentCreateView, LessonProgressView, CertificateVerifyView, MyCertificatesView


urlpatterns = [
    path("", EnrollmentCreateView.as_view(), name="enrollment-create"),
    path(
    "lessons/<int:lesson_id>/progress/",
    LessonProgressView.as_view(),
    name="lesson-progress",
    ),
    path(
        "certificates/verify/<uuid:verification_id>/",
        CertificateVerifyView.as_view(),
        name="certificate-verify",
    ),
    path(
    "certificates/",
    MyCertificatesView.as_view(),
    name="my-certificates",
    ),
]