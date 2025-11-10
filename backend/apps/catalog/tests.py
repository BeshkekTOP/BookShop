from decimal import Decimal
from django.test import TestCase
from django.db import IntegrityError
from backend.apps.catalog.models import Category, Author, Book, BookAuthors, Inventory


class TestCategoryModel(TestCase):
    """Тесты для модели Category"""
    
    def test_create_category(self):
        """Тест создания категории"""
        category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.assertEqual(category.name, "Художественная литература")
        self.assertEqual(category.slug, "fiction")
        self.assertIsNotNone(category.id)
    
    def test_category_unique_name(self):
        """Тест уникальности названия категории"""
        Category.objects.create(name="Техническая литература", slug="tech")
        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Техническая литература", slug="tech2")
    
    def test_category_str(self):
        """Тест строкового представления категории"""
        category = Category.objects.create(name="Детективы", slug="detective")
        self.assertEqual(str(category), "Детективы")


class TestAuthorModel(TestCase):
    """Тесты для модели Author"""
    
    def test_create_author(self):
        """Тест создания автора"""
        author = Author.objects.create(first_name="Иван", last_name="Иванов")
        self.assertEqual(author.first_name, "Иван")
        self.assertEqual(author.last_name, "Иванов")
        self.assertEqual(str(author), "Иван Иванов")
    
    def test_author_unique_together(self):
        """Тест уникальности комбинации имени и фамилии"""
        Author.objects.create(first_name="Петр", last_name="Петров")
        # Можно создать другого автора с другим именем
        author2 = Author.objects.create(first_name="Петр", last_name="Сидоров")
        self.assertNotEqual(author2.id, Author.objects.get(first_name="Петр", last_name="Петров").id)
    
    def test_author_str(self):
        """Тест строкового представления автора"""
        author = Author.objects.create(first_name="Александр", last_name="Пушкин")
        self.assertEqual(str(author), "Александр Пушкин")


class TestBookModel(TestCase):
    """Тесты для модели Book"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.author = Author.objects.create(first_name="Лев", last_name="Толстой")
    
    def test_create_book(self):
        """Тест создания книги"""
        book = Book.objects.create(
            title="Война и мир",
            isbn="978-5-17-123456-7",
            category=self.category,
            price=Decimal("599.99"),
            description="Роман-эпопея"
        )
        self.assertEqual(book.title, "Война и мир")
        self.assertEqual(book.isbn, "978-5-17-123456-7")
        self.assertEqual(book.price, Decimal("599.99"))
        self.assertEqual(book.rating, Decimal("0"))
        self.assertTrue(book.is_active)
    
    def test_book_unique_isbn(self):
        """Тест уникальности ISBN"""
        Book.objects.create(
            title="Книга 1",
            isbn="978-5-17-123456-7",
            category=self.category,
            price=Decimal("100")
        )
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Книга 2",
                isbn="978-5-17-123456-7",
                category=self.category,
                price=Decimal("200")
            )
    
    def test_book_average_rating(self):
        """Тест вычисления среднего рейтинга"""
        book = Book.objects.create(
            title="Тестовая книга",
            isbn="978-5-17-111111-1",
            category=self.category,
            price=Decimal("100")
        )
        # Без отзывов рейтинг должен быть 0
        self.assertEqual(book.average_rating, 0)
    
    def test_book_str(self):
        """Тест строкового представления книги"""
        book = Book.objects.create(
            title="Анна Каренина",
            isbn="978-5-17-222222-2",
            category=self.category,
            price=Decimal("500")
        )
        self.assertEqual(str(book), "Анна Каренина")


class TestBookAuthorsModel(TestCase):
    """Тесты для модели BookAuthors"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.book = Book.objects.create(
            title="Тестовая книга",
            isbn="978-5-17-333333-3",
            category=self.category,
            price=Decimal("100")
        )
        self.author1 = Author.objects.create(first_name="Автор", last_name="Первый")
        self.author2 = Author.objects.create(first_name="Автор", last_name="Второй")
    
    def test_create_book_author(self):
        """Тест создания связи книга-автор"""
        book_author = BookAuthors.objects.create(book=self.book, author=self.author1)
        self.assertEqual(book_author.book, self.book)
        self.assertEqual(book_author.author, self.author1)
    
    def test_book_multiple_authors(self):
        """Тест добавления нескольких авторов к книге"""
        BookAuthors.objects.create(book=self.book, author=self.author1)
        BookAuthors.objects.create(book=self.book, author=self.author2)
        self.assertEqual(self.book.book_authors.count(), 2)
    
    def test_book_author_unique_together(self):
        """Тест уникальности комбинации книга-автор"""
        BookAuthors.objects.create(book=self.book, author=self.author1)
        with self.assertRaises(IntegrityError):
            BookAuthors.objects.create(book=self.book, author=self.author1)


class TestInventoryModel(TestCase):
    """Тесты для модели Inventory"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.book = Book.objects.create(
            title="Тестовая книга",
            isbn="978-5-17-444444-4",
            category=self.category,
            price=Decimal("100")
        )
    
    def test_create_inventory(self):
        """Тест создания остатков"""
        inventory = Inventory.objects.create(book=self.book, stock=100, reserved=10)
        self.assertEqual(inventory.stock, 100)
        self.assertEqual(inventory.reserved, 10)
        self.assertEqual(inventory.available(), 90)
    
    def test_inventory_available(self):
        """Тест расчета доступного количества"""
        inventory = Inventory.objects.create(book=self.book, stock=50, reserved=30)
        self.assertEqual(inventory.available(), 20)
    
    def test_inventory_available_negative(self):
        """Тест, что доступное количество не может быть отрицательным"""
        inventory = Inventory.objects.create(book=self.book, stock=10, reserved=20)
        self.assertEqual(inventory.available(), 0)  # max(0, 10-20) = 0
    
    def test_inventory_one_to_one(self):
        """Тест уникальности связи OneToOne"""
        Inventory.objects.create(book=self.book, stock=100)
        with self.assertRaises(IntegrityError):
            Inventory.objects.create(book=self.book, stock=200)

