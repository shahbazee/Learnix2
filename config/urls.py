from django.contrib import admin
from django.urls import include, path
from courses.views import CourseListTemplateView, CourseDetailTemplateView
from accounts.views import LoginTemplateView, SignupTemplateView
from enrollments.views import CertificateVerifyTemplateView, MyCertificatesTemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/courses/", include("courses.urls")),
    path("api/v1/enrollments/", include("enrollments.urls")),

    path("", CourseListTemplateView.as_view(), name="home"),
    path("course/<slug:slug>/", CourseDetailTemplateView.as_view(), name="course-detail"),
    path("login/", LoginTemplateView.as_view(), name="login"),
    path("signup/", SignupTemplateView.as_view(), name="signup"),
    path("certificates/", MyCertificatesTemplateView.as_view(), name="my-certificates"),
    path("certificates/verify/<uuid:verification_id>/", CertificateVerifyTemplateView.as_view(), name="certificate-verify")
]