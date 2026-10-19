from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import LoginForm, SignupForm
from .models import EmailOTP, UserProfile, User
from notifications.tasks import send_otp_email
from .otp_utils import generate_otp, hash_otp, otp_expiry
from .permissions import IsInstructor
from .serializers import (
    RegisterSerializer, 
    LoginSerializer, 
    OTPRequestSerializer, 
    OTPVerifySerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
    GoogleLoginSerializer,
)

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": serializer.data,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": {
                    "email": user.email,
                    "display_name": user.display_name,
                },
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response (
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            token = RefreshToken.for_user(user)
            token.blacklist()
        except Exception:
            return Response(
                {"detail": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {"detail": "Successfully logged out. "},
            status=status.HTTP_200_OK,
        )


class OTPRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        EmailOTP.objects.filter(
            user=user, purpose="registration", used=False
        ).update(used=True)
        code = generate_otp()
        EmailOTP.objects.create(
            user=user,
            purpose="registration",
            code_hash=hash_otp(code),
            expires_at=otp_expiry(),
        )
        send_otp_email.delay(email, code)
        return Response(
            {"detail": "OTP sent to email."},
            status=status.HTTP_200_OK,
        )


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found. "},
                status=status.HTTP_404_NOT_FOUND,
            )
        otp = (
            EmailOTP.objects.filter(
                user=user, purpose="registration", used=False
            )
            .order_by("-created_at")
            .first()
        )
        if not otp:
            return Response(
                {"detail": "Invalid OTP. "},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp.expires_at < timezone.now():
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp.attempts >= 5:
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp.code_hash != hash_otp(otp_code):
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            return Response(
                {"detail": "Invalid OTP. "},
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp.used = True
        otp.save(update_fields=["used"])
        user.email_verified = True
        user.save(update_fields=["email_verified"])
        return Response(
            {"detial": "Email verified Successfully. "},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        user = User.objects.filter(email__iexact=email).first()
        if user:
            EmailOTP.objects.filter(
                user=user, purpose="password_reset", used=False
            ).update(used=True)
            code = generate_otp()
            EmailOTP.objects.create(
                user=user,
                purpose="password_reset",
                code_hash=hash_otp(code),
                expires_at=otp_expiry(),
            )
            send_otp_email.delay(email, code)
        return Response(
            {"detail": "If the email exists, an OTP has been sent."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp_code = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp = (
            EmailOTP.objects.filter(
                user=user, purpose="password_reset", used=False
            )
            .order_by("-created_at")
            .first()
        )
        if not otp:
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp.expires_at < timezone.now():
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp.attempts >= 5:
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if otp.code_hash != hash_otp(otp_code):
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            return Response(
                {"detail": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp.used = True
        otp.save(update_fields=["used"])
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response(
            {"detail": "Password reset successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]
        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.set_password(new_password)
        user.save(update_fields=["password"])
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["id_token"]
        try:
            idinfo = google_id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response(
                {"detail": "Invalid Google token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        email = idinfo.get("email")
        if not email or not idinfo.get("email_verified"):
            return Response(
                {"detail": "Invalid Google token."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.create_user(
                email=email.lower(),
                role="student",
                display_name=idinfo.get("name", ""),
            )
            user.set_unusable_password()
            user.email_verified = True
            user.save()
            UserProfile.objects.create(user=user)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "display_name": user.display_name,
                    "role": user.role,
                },
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            },
            status=status.HTTP_200_OK,
)


class InstructorTestView(APIView):
    permission_classes = [IsInstructor]

    def get(self, request):
        return Response({"detail": "You are an instructor."})


class LoginTemplateView(FormView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["google_client_id"] = settings.GOOGLE_CLIENT_ID
        return context

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            user = None
        if user is None or not user.check_password(password):
            form.add_error(None, "Invalid credentials.")
            return self.form_invalid(form)
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return super().form_valid(form)


class SignupTemplateView(FormView):
    template_name = "accounts/signup.html"
    form_class = SignupForm
    success_url = "/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["google_client_id"] = settings.GOOGLE_CLIENT_ID
        return context

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            form.add_error("email", "Email already registered.")
            return self.form_invalid(form)
        user = User(
            email=email,
            display_name=form.cleaned_data["display_name"],
            role="student",
        )
        user.set_password(form.cleaned_data["password"])
        user.save()
        UserProfile.objects.create(user=user)
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        return super().form_valid(form)

@method_decorator(csrf_exempt, name="dispatch")
class GoogleTemplateLoginView(View):
    def post(self, request):
        if request.COOKIES.get("g_csrf_token") != request.POST.get("g_csrf_token"):
            return redirect("login")
        token = request.POST.get("credential")
        if not token:
            return redirect("login")
        try:
            idinfo = google_id_token.verify_oauth2_token(
                token, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return redirect("login")
        email = idinfo.get("email")
        if not email or not idinfo.get("email_verified"):
            return redirect("login")
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            user = User.objects.create_user(
                email=email.lower(),
                role="student",
                display_name=idinfo.get("name", ""),
            )
            user.set_unusable_password()
            user.email_verified = True
            user.save()
            UserProfile.objects.create(user=user)
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("/")
