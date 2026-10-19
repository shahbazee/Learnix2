from django.contrib import admin

from .models import AdminAuditLog

admin.site.register(AdminAuditLog)