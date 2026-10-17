import hashlib
import hmac
import random
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


def generate_otp():
    return str(random.randint(100000, 999999))

def hash_otp(code):
    return hmac.new(
        settings.SECRET_KEY.encode(), code.encode(), hashlib.sha256
    ).hexdigest()

def otp_expiry():
    return timezone.now() + timedelta(minutes=10)
