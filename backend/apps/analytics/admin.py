from django.contrib import admin
from .models import SalesStats, TopSellingBook, CustomerStats


@admin.register(SalesStats)
class SalesStatsAdmin(admin.ModelAdmin):
    list_display = ("date", "total_orders", "total_revenue", "total_books_sold", "average_order_value")
    list_filter = ("date",)
    search_fields = ("date",)
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-date",)


@admin.register(TopSellingBook)
class TopSellingBookAdmin(admin.ModelAdmin):
    list_display = ("book", "date", "quantity_sold", "revenue", "rank")
    list_filter = ("date", "rank")
    search_fields = ("book__title", "book__author__name")
    readonly_fields = ("created_at",)
    ordering = ("-date", "rank")


@admin.register(CustomerStats)
class CustomerStatsAdmin(admin.ModelAdmin):
    list_display = ("date", "total_customers", "new_customers", "returning_customers", "average_customer_value")
    list_filter = ("date",)
    search_fields = ("date",)
    readonly_fields = ("created_at",)
    ordering = ("-date",)






