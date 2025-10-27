from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

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
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['price']),
            models.Index(fields=['rating']),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def average_rating(self):
        """Вычисляет средний рейтинг на основе отзывов"""
        from django.db.models import Avg
        return self.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0


class BookAuthors(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="book_authors")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="author_books")

    class Meta:
        unique_together = ("book", "author")


class Inventory(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name="inventory")
    stock = models.PositiveIntegerField(default=0)
    reserved = models.PositiveIntegerField(default=0)

    def available(self) -> int:
        return max(0, self.stock - self.reserved)





