from django.conf import settings
from django.db import models


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField()
    text = models.TextField(blank=True)
    is_moderated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "book")
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.book} - {self.rating}/5 by {self.user}"

