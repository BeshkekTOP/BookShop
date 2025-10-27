from django.conf import settings
from django.db import models


class PageView(models.Model):
    """Модель для отслеживания просмотров страниц"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    page_url = models.URLField()
    page_title = models.CharField(max_length=255)
    referrer = models.URLField(blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=40, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"PageView: {self.page_title} at {self.created_at}"


class BookView(models.Model):
    """Модель для отслеживания просмотров книг"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'book', 'session_key')

    def __str__(self) -> str:
        return f"BookView: {self.book.title} by {self.user or 'Anonymous'}"


class SearchQuery(models.Model):
    """Модель для отслеживания поисковых запросов"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    query = models.CharField(max_length=255)
    results_count = models.PositiveIntegerField(default=0)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Search: '{self.query}' by {self.user or 'Anonymous'}"


class OrderAnalytics(models.Model):
    """Модель для аналитики заказов"""
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='analytics')
    conversion_source = models.CharField(max_length=100, blank=True)  # organic, paid, direct, etc.
    utm_source = models.CharField(max_length=100, blank=True)
    utm_medium = models.CharField(max_length=100, blank=True)
    utm_campaign = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Analytics for Order #{self.order.pk}"


class UserActivity(models.Model):
    """Модель для отслеживания активности пользователей"""
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('register', 'Register'),
        ('profile_update', 'Profile Update'),
        ('book_view', 'Book View'),
        ('cart_add', 'Add to Cart'),
        ('cart_remove', 'Remove from Cart'),
        ('order_create', 'Order Created'),
        ('review_create', 'Review Created'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.user.username} - {self.action} at {self.created_at}"
