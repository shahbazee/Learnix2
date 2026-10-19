from django.contrib import admin
from django.urls import include, path
from courses.views import CourseCreateTemplateView, CourseDetailTemplateView, CourseListTemplateView, CourseUpdateTemplateView, LandingTemplateView, LessonDetailTemplateView
from accounts.views import LoginTemplateView, SignupTemplateView
from enrollments.views import CertificateVerifyTemplateView, MyCertificatesTemplateView, MyLearningTemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/courses/", include("courses.urls")),
    path("api/v1/enrollments/", include("enrollments.urls")),

    path("", LandingTemplateView.as_view(), name="home"),
    path("courses/", CourseListTemplateView.as_view(), name="course-list"),
    path("course/<slug:slug>/", CourseDetailTemplateView.as_view(), name="course-detail"),
    path("login/", LoginTemplateView.as_view(), name="login"),
    path("signup/", SignupTemplateView.as_view(), name="signup"),
    path("certificates/", MyCertificatesTemplateView.as_view(), name="my-certificates"),
    path("certificates/verify/<uuid:verification_id>/", CertificateVerifyTemplateView.as_view(), name="certificate-verify"),
    path("my-learning/", MyLearningTemplateView.as_view(), name="my-learning"),
    path("lesson/<int:pk>/", LessonDetailTemplateView.as_view(), name="lesson-detail"),
    path("instructor/courses/create/", CourseCreateTemplateView.as_view(), name="course-create"),
    path("instructor/courses/<slug:slug>/edit/", CourseUpdateTemplateView.as_view(), name="course-edit"),

]