from io import BytesIO

from django.core.files.base import ContentFile
from django.utils import timezone
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from courses.models import Lesson
from .models import Certificate, Enrollment, LessonProgress
from .serializers import CertificateSerializer


def generate_certificate_pdf(certificate):
    buffer = BytesIO()
    width, height = landscape(A4)
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(width / 2, height - 120, "Certificate of Completion")
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(width / 2, height - 200, "This certifies that")
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawCentredString(width / 2, height - 250, certificate.student_name)
    pdf.setFont("Helvetica", 16)
    pdf.drawCentredString(
        width / 2, height - 300, f"has completed {certificate.course_title}"
    )
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        width / 2, height - 350, f"Completed on {certificate.completion_date}"
    )
    pdf.drawCentredString(
        width / 2, 80, f"Verification ID: {certificate.verification_id}"
    )
    pdf.showPage()
    pdf.save()
    filename = f"certificate_{certificate.verification_id}.pdf"
    certificate.pdf.save(filename, ContentFile(buffer.getvalue()))


def check_course_completion(enrollment):
    course = enrollment.course
    total_lessons = Lesson.objects.filter(module__course=course).count()
    if total_lessons == 0:
        return None
    completed_lessons = LessonProgress.objects.filter(
        enrollment=enrollment, is_completed=True
    ).count()
    if completed_lessons < total_lessons:
        return None
    certificate, created = Certificate.objects.get_or_create(
        enrollment=enrollment,
        defaults={
            "student_name": enrollment.student.display_name,
            "course_title": course.title,
            "completion_date": timezone.now().date(),
        },
    )
    if created:
        generate_certificate_pdf(certificate)
        enrollment.status = Enrollment.STATUS_COMPLETED
        enrollment.save(update_fields=["status"])
    return certificate


class MyCertificatesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CertificateSerializer

    def get_queryset(self):
        return Certificate.objects.filter(
            enrollment__student=self.request.user
        )