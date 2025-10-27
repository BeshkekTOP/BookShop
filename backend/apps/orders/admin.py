from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "created_at")
    inlines = [CartItemInline]


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "total_amount", "shipping_city", "created_at")
    list_filter = ("status", "created_at", "shipping_city")
    search_fields = ("user__username", "user__email", "shipping_address", "shipping_city")
    inlines = [OrderItemInline]
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Основная информация", {
            "fields": ("user", "status", "total_amount")
        }),
        ("Адрес доставки", {
            "fields": ("shipping_address", "shipping_city", "shipping_postal_code")
        }),
        ("Дополнительная информация", {
            "fields": ("notes",)
        }),
        ("Временные метки", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )





