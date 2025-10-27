from django.contrib import admin
from .models import Category, Author, Book, BookAuthors, Inventory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")
    search_fields = ("first_name", "last_name")


class BookAuthorsInline(admin.TabularInline):
    model = BookAuthors
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "isbn", "category", "price", "rating", "is_active", "created_at")
    search_fields = ("title", "isbn", "description")
    list_filter = ("category", "is_active", "created_at", "publication_date")
    inlines = [BookAuthorsInline]
    readonly_fields = ("created_at", "updated_at", "average_rating")
    fieldsets = (
        ("Основная информация", {
            "fields": ("title", "isbn", "description", "category")
        }),
        ("Цена и рейтинг", {
            "fields": ("price", "rating", "average_rating")
        }),
        ("Дополнительная информация", {
            "fields": ("pages", "publication_date", "cover_image")
        }),
        ("Статус", {
            "fields": ("is_active",)
        }),
        ("Временные метки", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("book", "stock", "reserved")





