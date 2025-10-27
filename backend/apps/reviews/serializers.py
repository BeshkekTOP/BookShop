from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)

    class Meta:
        model = Review
        fields = ("id", "user", "user_email", "book", "book_title", "rating", "text", "is_moderated", "created_at")
        read_only_fields = ("user", "is_moderated")




