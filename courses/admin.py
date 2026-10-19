from django.contrib import admin

from .models import Category, Course, Lesson, Module


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active"]
    search_fields = ["name"]
    list_filter = ["is_active"]


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["title", "instructor", "category", "status", "price"]
    search_fields = ["title"]
    list_filter = ["status", "category"]
    inlines = [ModuleInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ["title", "course", "position"]
    list_filter = ["course"]
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["title", "module", "position", "is_published"]
    list_filter = ["is_published"]
