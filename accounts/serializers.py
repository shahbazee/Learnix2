from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import UserProfile


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "display_name"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "An account with this email is already exists."
            )
        return value

    def validate_password(self, value):
        validate_password(value)
        return value
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(
            password=password,
            role="student",
            **validated_data,
        )
        UserProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid Credentials.")
        if not user.check_password(password):
            raise serializers.ValidationError("Invalid Credentials.")
        data["user"] = user
        return data


class OTPRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validated_new_password(self, value):
        validate_password(value)
        return value


class GoogleLoginSerializer(serializers.Serializer):
    id_token = serializers.CharField()