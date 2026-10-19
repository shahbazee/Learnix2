from rest_framework import serializers

from .models import Category, Course, Lesson, Module


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "position", "is_published"]


class ModuleSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Module
        fields = ["id", "title", "position", "lessons"]


class CourseListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    instructor = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "category",
            "instructor",
            "price",
            "is_free",
            "status",
        ]


class CourseDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    instructor = serializers.StringRelatedField(read_only=True)
    modules = ModuleSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = [
            "id",
            "title",
            "slug",
            "summary",
            "category",
            "instructor",
            "price",
            "is_free",
            "status",
            "published_at",
            "modules",
        ]


class CourseCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = [
            "title",
            "slug",
            "summary",
            "category",
            "price",
            "is_free",
            "status",
        ]