from django.urls import path

from .views import (
    RegisterView, 
    LoginView, 
    LogoutView, 
    OTPRequestView, 
    OTPVerifyView, 
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
    GoogleLoginView,
    InstructorTestView,
    )


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("otp/request/", OTPRequestView.as_view(), name="otp-request"),
    path("otp/verify/", OTPVerifyView.as_view(), name="otp-verify"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password-reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path("google/", GoogleLoginView.as_view(), name="google-login"),
    path("test/instructor/", InstructorTestView.as_view(), name="test-instructor"),

]