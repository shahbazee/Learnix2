from django.urls import path

from .views import (
    CourseCreateView,
    CourseDetailView,
    CourseListView,
    CourseUpdateView,
    ModuleListCreateView,
    LessonListCreateView
)

urlpatterns = [
    path("", CourseListView.as_view(), name="course-list"),
    path("create/", CourseCreateView.as_view(), name="course-create"),
    path("<slug:slug>/", CourseDetailView.as_view(), name="course-detail"),
    path("<slug:slug>/edit/", CourseUpdateView.as_view(), name="course-update"),
    path("<slug:slug>/modules/", ModuleListCreateView.as_view(), name="module-list-create"),
    path("modules/<int:module_id>/lessons/", LessonListCreateView.as_view(), name="lesson-list-create")
]