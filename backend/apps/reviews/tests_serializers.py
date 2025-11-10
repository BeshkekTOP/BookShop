from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from backend.apps.reviews.models import Review
from backend.apps.reviews.serializers import ReviewSerializer
from backend.apps.catalog.models import Category, Book
from backend.apps.users.models import Profile

User = get_user_model()


class TestReviewSerializer(TestCase):
    """Тесты для ReviewSerializer"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
        Profile.objects.create(user=self.user)
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.book = Book.objects.create(
            title="Тестовая книга",
            isbn="978-5-17-123456-7",
            category=self.category,
            price=Decimal("100")
        )
    
    def test_review_serializer(self):
        """Тест сериализации отзыва"""
        review = Review.objects.create(
            user=self.user,
            book=self.book,
            rating=5,
            text="Отличная книга!"
        )
        serializer = ReviewSerializer(review)
        data = serializer.data
        self.assertEqual(data['rating'], 5)
        self.assertEqual(data['text'], "Отличная книга!")
        self.assertIn('user_email', data)
        self.assertIn('book_title', data)
    
    def test_review_serializer_validate_rating_min(self):
        """Тест валидации минимального рейтинга"""
        data = {
            "book": self.book.id,
            "rating": 0,
            "text": "Плохая книга"
        }
        serializer = ReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Рейтинг должен быть от 1 до 5", str(serializer.errors))
    
    def test_review_serializer_validate_rating_max(self):
        """Тест валидации максимального рейтинга"""
        data = {
            "book": self.book.id,
            "rating": 6,
            "text": "Отличная книга"
        }
        serializer = ReviewSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Рейтинг должен быть от 1 до 5", str(serializer.errors))
    
    def test_review_serializer_valid_rating(self):
        """Тест валидного рейтинга"""
        data = {
            "book": self.book.id,
            "rating": 5,
            "text": "Отличная книга!"
        }
        serializer = ReviewSerializer(data=data)
        self.assertTrue(serializer.is_valid())

