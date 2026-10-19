from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import (
                                AllowAny, 
                                IsAuthenticated,
                                IsAuthenticatedOrReadOnly)

from .models import Course, Module
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