from django.conf import settings
from django.db import models


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Cart #{self.pk} for {self.user}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "book")


class Order(models.Model):
    STATUS_CHOICES = (
        ("processing", "Обрабатывается"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменен"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="processing")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping_address = models.TextField(default="")
    shipping_city = models.CharField(max_length=100, default="")
    shipping_postal_code = models.CharField(max_length=20, default="")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]

    def __str__(self) -> str:
        return f"Order #{self.pk} ({self.status})"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    book = models.ForeignKey('catalog.Book', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

