from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "rating", "is_moderated", "created_at")
    list_filter = ("is_moderated", "rating", "created_at")
    search_fields = ("book__title", "user__username", "user__email", "text")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Основная информация", {
            "fields": ("book", "user", "rating", "text")
        }),
        ("Модерация", {
            "fields": ("is_moderated",)
        }),
        ("Временные метки", {
            "fields": ("created_at",),
            "classes": ("collapse",)
        }),
    )
    actions = ['approve_reviews', 'reject_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_moderated=True)
        self.message_user(request, f"Одобрено {queryset.count()} отзывов")
    approve_reviews.short_description = "Одобрить выбранные отзывы"

    def reject_reviews(self, request, queryset):
        queryset.update(is_moderated=False)
        self.message_user(request, f"Отклонено {queryset.count()} отзывов")
    reject_reviews.short_description = "Отклонить выбранные отзывы"





