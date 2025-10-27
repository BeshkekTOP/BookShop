from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профиль'


# Отменяем регистрацию стандартного UserAdmin и регистрируем наш
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

admin.site.register(User, UserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "city", "created_at")
    search_fields = ("user__username", "user__email", "phone", "city")
    list_filter = ("city", "created_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Основная информация", {
            "fields": ("user", "phone")
        }),
        ("Адрес", {
            "fields": ("address", "city", "postal_code")
        }),
        ("Дополнительная информация", {
            "fields": ("date_of_birth", "avatar")
        }),
        ("Временные метки", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )





