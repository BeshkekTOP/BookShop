from django.conf import settings
from django.db import models


class PageView(models.Model):
    """Модель для отслеживания просмотров страниц"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, blank=True)
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referer = models.URLField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['path', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.path} - {self.timestamp}"


class BookView(models.Model):
    """Модель для отслеживания просмотров книг"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='book_views')
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        unique_together = ['book', 'session_key', 'timestamp']
        indexes = [
            models.Index(fields=['book', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.book.title} - {self.timestamp}"


class SearchQuery(models.Model):
    """Модель для отслеживания поисковых запросов"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    query = models.CharField(max_length=255)
    results_count = models.PositiveIntegerField(default=0)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['query', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.query} - {self.results_count} results"


class PurchaseEvent(models.Model):
    """Модель для отслеживания покупок"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='purchase_events')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    items_count = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Purchase {self.order.id} - {self.total_amount}"

