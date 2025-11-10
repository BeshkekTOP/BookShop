from decimal import Decimal
from django.test import TestCase
from backend.apps.catalog.models import Category, Author, Book, BookAuthors, Inventory
from backend.apps.catalog.serializers import (
    CategorySerializer, AuthorSerializer, BookSerializer, BookWriteSerializer
)


class TestCategorySerializer(TestCase):
    """Тесты для CategorySerializer"""
    
    def test_category_serializer(self):
        """Тест сериализации категории"""
        category = Category.objects.create(name="Художественная литература", slug="fiction")
        serializer = CategorySerializer(category)
        data = serializer.data
        self.assertEqual(data['name'], "Художественная литература")
        self.assertEqual(data['slug'], "fiction")
    
    def test_category_deserializer(self):
        """Тест десериализации категории"""
        data = {"name": "Детективы", "slug": "detective"}
        serializer = CategorySerializer(data=data)
        self.assertTrue(serializer.is_valid())
        category = serializer.save()
        self.assertEqual(category.name, "Детективы")


class TestAuthorSerializer(TestCase):
    """Тесты для AuthorSerializer"""
    
    def test_author_serializer(self):
        """Тест сериализации автора"""
        author = Author.objects.create(first_name="Иван", last_name="Иванов")
        serializer = AuthorSerializer(author)
        data = serializer.data
        self.assertEqual(data['first_name'], "Иван")
        self.assertEqual(data['last_name'], "Иванов")
    
    def test_author_deserializer(self):
        """Тест десериализации автора"""
        data = {"first_name": "Петр", "last_name": "Петров"}
        serializer = AuthorSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        author = serializer.save()
        self.assertEqual(author.first_name, "Петр")


class TestBookSerializer(TestCase):
    """Тесты для BookSerializer"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.author = Author.objects.create(first_name="Лев", last_name="Толстой")
        self.book = Book.objects.create(
            title="Война и мир",
            isbn="978-5-17-123456-7",
            category=self.category,
            price=Decimal("599.99")
        )
        BookAuthors.objects.create(book=self.book, author=self.author)
        Inventory.objects.create(book=self.book, stock=100, reserved=10)
    
    def test_book_serializer(self):
        """Тест сериализации книги"""
        serializer = BookSerializer(self.book)
        data = serializer.data
        self.assertEqual(data['title'], "Война и мир")
        self.assertEqual(data['isbn'], "978-5-17-123456-7")
        self.assertEqual(data['category']['name'], "Художественная литература")
        self.assertIn('authors', data)
        self.assertIn('inventory', data)
    
    def test_book_serializer_authors(self):
        """Тест сериализации авторов книги"""
        serializer = BookSerializer(self.book)
        data = serializer.data
        self.assertEqual(len(data['authors']), 1)
        self.assertEqual(data['authors'][0]['first_name'], "Лев")


class TestBookWriteSerializer(TestCase):
    """Тесты для BookWriteSerializer"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.author1 = Author.objects.create(first_name="Автор", last_name="Первый")
        self.author2 = Author.objects.create(first_name="Автор", last_name="Второй")
    
    def test_book_write_serializer_create(self):
        """Тест создания книги через сериализатор"""
        data = {
            "title": "Новая книга",
            "isbn": "978-5-17-999999-9",
            "category": self.category.id,
            "price": "299.99",
            "author_ids": [self.author1.id, self.author2.id]
        }
        serializer = BookWriteSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        book = serializer.save()
        self.assertEqual(book.title, "Новая книга")
        self.assertEqual(book.book_authors.count(), 2)
        # Проверяем, что создан Inventory
        self.assertIsNotNone(book.inventory)
    
    def test_book_write_serializer_update(self):
        """Тест обновления книги через сериализатор"""
        book = Book.objects.create(
            title="Старая книга",
            isbn="978-5-17-888888-8",
            category=self.category,
            price=Decimal("100")
        )
        BookAuthors.objects.create(book=book, author=self.author1)
        
        data = {
            "title": "Обновленная книга",
            "isbn": "978-5-17-888888-8",
            "category": self.category.id,
            "price": "150.00",
            "author_ids": [self.author2.id]
        }
        serializer = BookWriteSerializer(book, data=data)
        self.assertTrue(serializer.is_valid())
        updated_book = serializer.save()
        self.assertEqual(updated_book.title, "Обновленная книга")
        self.assertEqual(updated_book.book_authors.count(), 1)
        self.assertEqual(updated_book.book_authors.first().author, self.author2)

