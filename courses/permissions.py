from rest_framework import permissions


class IsInstructorOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ("instructor", "admin")
        )


class IsCourseOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role == "admin":
            return True
        return obj.instructor == request.user