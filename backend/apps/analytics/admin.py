from django.contrib import admin
from .models import PageView, BookView, SearchQuery, PurchaseEvent


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ("path", "user", "ip_address", "timestamp")
    list_filter = ("timestamp", "path")
    search_fields = ("path", "user__username", "ip_address")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)


@admin.register(BookView)
class BookViewAdmin(admin.ModelAdmin):
    list_display = ("book", "user", "ip_address", "timestamp")
    list_filter = ("timestamp", "book__category")
    search_fields = ("book__title", "user__username", "ip_address")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ("query", "user", "results_count", "timestamp")
    list_filter = ("timestamp", "results_count")
    search_fields = ("query", "user__username")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)


@admin.register(PurchaseEvent)
class PurchaseEventAdmin(admin.ModelAdmin):
    list_display = ("user", "order", "total_amount", "items_count", "timestamp")
    list_filter = ("timestamp", "total_amount")
    search_fields = ("user__username", "order__id")
    readonly_fields = ("timestamp",)
    ordering = ("-timestamp",)

