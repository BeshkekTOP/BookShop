from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from backend.apps.orders.models import Cart, CartItem, Order, OrderItem
from backend.apps.catalog.models import Category, Book, Inventory

User = get_user_model()


class TestCartModel(TestCase):
    """Тесты для модели Cart"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.book = Book.objects.create(
            title="Тестовая книга",
            isbn="978-5-17-555555-5",
            category=self.category,
            price=Decimal("100")
        )
    
    def test_create_cart(self):
        """Тест создания корзины"""
        cart = Cart.objects.create(user=self.user)
        self.assertEqual(cart.user, self.user)
        self.assertIsNotNone(cart.created_at)
    
    def test_cart_str(self):
        """Тест строкового представления корзины"""
        cart = Cart.objects.create(user=self.user)
        self.assertIn("Cart #", str(cart))
        self.assertIn("testuser", str(cart))


class TestCartItemModel(TestCase):
    """Тесты для модели CartItem"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
        self.cart = Cart.objects.create(user=self.user)
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.book = Book.objects.create(
            title="Тестовая книга",
            isbn="978-5-17-666666-6",
            category=self.category,
            price=Decimal("100")
        )
    
    def test_create_cart_item(self):
        """Тест создания позиции корзины"""
        cart_item = CartItem.objects.create(cart=self.cart, book=self.book, quantity=2)
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.book, self.book)
        self.assertEqual(cart_item.quantity, 2)
    
    def test_cart_item_unique_together(self):
        """Тест уникальности комбинации корзина-книга"""
        CartItem.objects.create(cart=self.cart, book=self.book, quantity=1)
        with self.assertRaises(IntegrityError):
            CartItem.objects.create(cart=self.cart, book=self.book, quantity=2)
    
    def test_cart_item_default_quantity(self):
        """Тест значения по умолчанию для количества"""
        cart_item = CartItem.objects.create(cart=self.cart, book=self.book)
        self.assertEqual(cart_item.quantity, 1)


class TestOrderModel(TestCase):
    """Тесты для модели Order"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
    
    def test_create_order(self):
        """Тест создания заказа"""
        order = Order.objects.create(
            user=self.user,
            status="processing",
            total_amount=Decimal("500.00"),
            shipping_address="ул. Тестовая, д. 1",
            shipping_city="Москва"
        )
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, "processing")
        self.assertEqual(order.total_amount, Decimal("500.00"))
        self.assertEqual(order.shipping_city, "Москва")
    
    def test_order_default_status(self):
        """Тест статуса по умолчанию"""
        order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("100"),
            shipping_address="Адрес",
            shipping_city="Город"
        )
        self.assertEqual(order.status, "processing")
    
    def test_order_str(self):
        """Тест строкового представления заказа"""
        order = Order.objects.create(
            user=self.user,
            status="delivered",
            total_amount=Decimal("100"),
            shipping_address="Адрес",
            shipping_city="Город"
        )
        self.assertIn("Order #", str(order))
        self.assertIn("delivered", str(order))
    
    def test_order_status_choices(self):
        """Тест выбора статусов"""
        statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        self.assertIn("processing", statuses)
        self.assertIn("shipped", statuses)
        self.assertIn("delivered", statuses)
        self.assertIn("cancelled", statuses)


class TestOrderItemModel(TestCase):
    """Тесты для модели OrderItem"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
        self.order = Order.objects.create(
            user=self.user,
            total_amount=Decimal("200"),
            shipping_address="Адрес",
            shipping_city="Город"
        )
        self.category = Category.objects.create(name="Художественная литература", slug="fiction")
        self.book = Book.objects.create(
            title="Тестовая книга",
            isbn="978-5-17-777777-7",
            category=self.category,
            price=Decimal("100")
        )
    
    def test_create_order_item(self):
        """Тест создания позиции заказа"""
        order_item = OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("100"),
            quantity=2
        )
        self.assertEqual(order_item.order, self.order)
        self.assertEqual(order_item.book, self.book)
        self.assertEqual(order_item.price, Decimal("100"))
        self.assertEqual(order_item.quantity, 2)
    
    def test_order_item_protect_on_delete(self):
        """Тест, что книга защищена от удаления при наличии заказа"""
        OrderItem.objects.create(
            order=self.order,
            book=self.book,
            price=Decimal("100"),
            quantity=1
        )
        # Попытка удалить книгу должна вызвать ProtectedError
        from django.db.models.deletion import ProtectedError
        with self.assertRaises(ProtectedError):
            self.book.delete()

