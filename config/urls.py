from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path
from courses.views import AboutTemplateView, CourseCreateTemplateView, CourseDetailTemplateView, CourseListTemplateView, CourseUpdateTemplateView, LandingTemplateView, LessonDetailTemplateView
from accounts.views import GoogleTemplateLoginView, LoginTemplateView, SignupTemplateView
from enrollments.views import CertificateVerifyTemplateView, EnrollFreeTemplateView, MyCertificatesTemplateView, MyLearningTemplateView
from payments.views import CheckoutTemplateView


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
    path("google/complete/", GoogleTemplateLoginView.as_view(), name="google-complete"),
    path("certificates/", MyCertificatesTemplateView.as_view(), name="my-certificates"),
    path("certificates/verify/<uuid:verification_id>/", CertificateVerifyTemplateView.as_view(), name="certificate-verify"),
    path("my-learning/", MyLearningTemplateView.as_view(), name="my-learning"),
    path("lesson/<int:pk>/", LessonDetailTemplateView.as_view(), name="lesson-detail"),
    path("instructor/courses/create/", CourseCreateTemplateView.as_view(), name="course-create"),
    path("instructor/courses/<slug:slug>/edit/", CourseUpdateTemplateView.as_view(), name="course-edit"),
    path("about/", AboutTemplateView.as_view(), name="about"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("checkout/<slug:slug>/", CheckoutTemplateView.as_view(), name="checkout"),
    path("enroll/<slug:slug>/", EnrollFreeTemplateView.as_view(), name="enroll-free"),
]