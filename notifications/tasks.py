from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_otp_email(email, code):
    send_mail(
        subject="Your Learnix OTP",
        message=f"Your OTP code is: {code}",
        from_email=None,
        recipient_list=[email],
        fail_silently=False,
    )