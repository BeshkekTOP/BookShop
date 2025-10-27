from django.conf import settings
from django.db import models


class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 star'),
        (2, '2 stars'),
        (3, '3 stars'),
        (4, '4 stars'),
        (5, '5 stars'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200, blank=True)
    text = models.TextField(blank=True)
    is_moderated = models.BooleanField(default=False)
    is_helpful = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "book")
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.book} - {self.rating}/5 by {self.user}"

