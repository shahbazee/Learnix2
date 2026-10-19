from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, TemplateView
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (
                                AllowAny, 
                                IsAuthenticated,
                                IsAuthenticatedOrReadOnly)

from .forms import CourseForm
from accounts.models import User

from .models import Category, Course, Lesson, Module
from enrollments.models import Enrollment, LessonProgress
from enrollments.services import check_course_completion
from .serializers import CourseDetailSerializer, CourseListSerializer, CourseCreateUpdateSerializer, ModuleSerializer, LessonSerializer
from .permissions import IsCourseOwnerOrAdmin, IsInstructorOrAdmin


class CourseListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseListSerializer
    queryset = Course.objects.filter(status=Course.STATUS_PUBLISHED)


class CourseDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = CourseDetailSerializer
    queryset = Course.objects.filter(status=Course.STATUS_PUBLISHED)
    lookup_field = "slug"


class CourseCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class CourseUpdateView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsCourseOwnerOrAdmin]
    serializer_class = CourseCreateUpdateSerializer
    queryset = Course.objects.all()
    lookup_field = "slug"


class ModuleListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ModuleSerializer

    def get_queryset(self):
        return Module.objects.filter(course__slug=self.kwargs["slug"])

    def perform_create(self, serializer):
        course = get_object_or_404(Course, slug=self.kwargs["slug"])
        user = self.request.user
        if user.role != "admin" and course.instructor != user:
            raise PermissionDenied(
                "You can only add modules to your own courses."
            )
        serializer.save(course=course)


class LessonListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = LessonSerializer

    def get_queryset(self):
        return Lesson.objects.filter(module_id=self.kwargs["module_id"])

    def perform_create(self, serializer):
        module = get_object_or_404(Module, id=self.kwargs["module_id"])
        user = self.request.user
        if user.role != "admin" and module.course.instructor != user:
            raise PermissionDenied(
                "You can only add lessons to your own courses."
            )
        serializer.save(module=module)

    
class CourseListTemplateView(ListView):
    model = Course
    template_name = "courses/course_list.html"
    context_object_name = "courses"

    def get_queryset(self):
        return Course.objects.filter(status=Course.STATUS_PUBLISHED)


class CourseDetailTemplateView(DetailView):
    model = Course
    template_name = "courses/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        return Course.objects.filter(status=Course.STATUS_PUBLISHED)


class LessonDetailTemplateView(LoginRequiredMixin, DetailView):
    model = Lesson
    template_name = "courses/lesson_detail.html"
    context_object_name = "lesson"

    def get_queryset(self):
        return Lesson.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        try:
            enrollment = Enrollment.objects.get(
                student=self.request.user,
                course=lesson.module.course,
            )
        except Enrollment.DoesNotExist:
            context["not_enrolled"] = True
            context["is_completed"] = False
            return context
        progress = LessonProgress.objects.filter(
            enrollment=enrollment, lesson=lesson
        ).first()
        context["not_enrolled"] = False
        context["is_completed"] = progress.is_completed if progress else False
        return context

    def post(self, request, *args, **kwargs):
        lesson = self.get_object()
        try:
            enrollment = Enrollment.objects.get(
                student=request.user, course=lesson.module.course
            )
        except Enrollment.DoesNotExist:
            return redirect("course-detail", slug=lesson.module.course.slug)
        progress, _ = LessonProgress.objects.get_or_create(
            enrollment=enrollment, lesson=lesson
        )
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        check_course_completion(enrollment)
        return redirect("lesson-detail", pk=lesson.pk)


class CourseCreateTemplateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def test_func(self):
        return self.request.user.role in ("instructor", "admin")

    def form_valid(self, form):
        form.instance.instructor = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("home")


class CourseUpdateTemplateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "courses/course_form.html"

    def test_func(self):
        course = self.get_object()
        user = self.request.user
        if user.role == "admin":
            return True
        return user.role == "instructor" and course.instructor == user

    def get_success_url(self):
        return reverse("home")

class LandingTemplateView(TemplateView):
    template_name = "landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured_courses"] = Course.objects.filter(status=Course.STATUS_PUBLISHED).annotate(
            lessons_count=Count("modules__lessons")
        )[:6]
        context["categories"] = Category.objects.filter(is_active=True).annotate(
            published_courses_count=Count("courses", filter=Q(courses__status=Course.STATUS_PUBLISHED))
        )
        context["instructors"] = User.objects.filter(
            role=User.ROLE_INSTRUCTOR, courses__status=Course.STATUS_PUBLISHED
        ).distinct()
        return context


class AboutTemplateView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.filter(is_active=True)
        return context
