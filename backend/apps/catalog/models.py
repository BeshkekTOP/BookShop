from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to="author_photos/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("first_name", "last_name")
        ordering = ["last_name", "first_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Book(models.Model):
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="books")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    pages = models.PositiveIntegerField(null=True, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=50, default="ru")
    cover_image = models.ImageField(upload_to="book_covers/", null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class BookAuthors(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_authors")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="author_books")

    class Meta:
        unique_together = ("book", "author")


class Inventory(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name="inventory")
    stock = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)
    min_stock = models.PositiveIntegerField(default=0)
    max_stock = models.PositiveIntegerField(null=True, blank=True)
    last_restocked = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def available(self) -> int:
        return max(0, self.stock - self.reserved)

    def is_low_stock(self) -> bool:
        return self.stock <= self.min_stock

    def __str__(self) -> str:
        return f"Inventory for {self.book.title}: {self.stock} in stock"





