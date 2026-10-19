from django.contrib import admin

from .models import User, UserProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "display_name", "role", "email_verified"]
    search_fields = ["email", "display_name"]
    list_filter = ["role", "email_verified"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "bio"]