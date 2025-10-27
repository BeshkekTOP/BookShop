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
    list_display = ("title", "isbn", "category", "price", "rating")
    search_fields = ("title", "isbn")
    list_filter = ("category",)
    inlines = [BookAuthorsInline]


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("book", "stock", "reserved")





