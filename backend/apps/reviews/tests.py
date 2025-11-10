from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from backend.apps.reviews.models import Review
from backend.apps.catalog.models import Category, Book
from backend.apps.users.models import Profile

User = get_user_model()


class TestReviewModel(TestCase):
    """Тесты для модели Review"""
    
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
    
    def test_create_review(self):
        """Тест создания отзыва"""
        review = Review.objects.create(
            user=self.user,
            book=self.book,
            rating=5,
            text="Отличная книга!"
        )
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.book, self.book)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.text, "Отличная книга!")
        self.assertFalse(review.is_moderated)
    
    def test_review_unique_together(self):
        """Тест уникальности комбинации пользователь-книга"""
        Review.objects.create(user=self.user, book=self.book, rating=5)
        with self.assertRaises(IntegrityError):
            Review.objects.create(user=self.user, book=self.book, rating=4)
    
    def test_review_str(self):
        """Тест строкового представления отзыва"""
        review = Review.objects.create(user=self.user, book=self.book, rating=5)
        self.assertIn("Тестовая книга", str(review))
        self.assertIn("testuser", str(review))
        self.assertIn("5/5", str(review))
    
    def test_review_default_is_moderated(self):
        """Тест значения по умолчанию для is_moderated"""
        review = Review.objects.create(user=self.user, book=self.book, rating=5)
        self.assertFalse(review.is_moderated)

