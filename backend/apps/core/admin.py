from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "action", "actor", "method", "path")
    search_fields = ("action", "actor__email", "path")
    list_filter = ("method",)



