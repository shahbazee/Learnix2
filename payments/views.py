import stripe
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from courses.models import Course
from enrollments.models import Enrollment
from .models import Payment
from .serializers import CheckoutSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = get_object_or_404(
            Course,
            slug=serializer.validated_data["course_slug"],
            status=Course.STATUS_PUBLISHED,
        )
        if course.is_free or course.price <= 0:
            return Response(
                {"detail": "This course is free."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Enrollment.objects.filter(
            student=request.user, course=course
        ).exists():
            return Response(
                {"detail": "You are already enrolled in this course."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        payment = Payment.objects.create(
            student=request.user,
            course=course,
            amount=course.price,
            currency="USD",
            status=Payment.STATUS_PENDING,
        )
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "unit_amount": int(course.price * 100),
                        "product_data": {"name": course.title},
                    },
                    "quantity": 1,
                }
            ],
            success_url="http://localhost:3000/success",
            cancel_url="http://localhost:3000/cancel",
            metadata={"payment_id": payment.id},
        )
        payment.stripe_session_id = session.id
        payment.save(update_fields=["stripe_session_id"])
        return Response(
            {"checkout_url": session.url},
            status=status.HTTP_200_OK,
        )


class StripeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if event["type"] != "checkout.session.completed":
            return Response(status=status.HTTP_200_OK)
        if Payment.objects.filter(stripe_event_id=event["id"]).exists():
            return Response(status=status.HTTP_200_OK)
        session = event["data"]["object"]
        payment = Payment.objects.filter(
            stripe_session_id=session["id"]
        ).first()
        if payment and payment.status == Payment.STATUS_PENDING:
            payment.status = Payment.STATUS_COMPLETED
            payment.stripe_event_id = event["id"]
            payment.save(update_fields=["status", "stripe_event_id"])
            Enrollment.objects.get_or_create(
                student=payment.student,
                course=payment.course,
                defaults={"source": Enrollment.SOURCE_PAID},
            )
        return Response(status=status.HTTP_200_OK)