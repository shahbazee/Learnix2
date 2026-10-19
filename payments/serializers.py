from rest_framework import serializers


class CheckoutSerializer(serializers.Serializer):
    course_slug = serializers.SlugField()