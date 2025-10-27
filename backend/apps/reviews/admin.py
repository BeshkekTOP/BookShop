from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "is_moderated", "created_at")
    list_filter = ("is_moderated", "rating")
    search_fields = ("book__title", "user__username", "user__email")





