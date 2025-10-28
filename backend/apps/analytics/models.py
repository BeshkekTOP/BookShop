from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()


class SalesStats(models.Model):
    """Статистика продаж по дням"""
    date = models.DateField(unique=True, verbose_name='Дата')
    total_orders = models.PositiveIntegerField(default=0, verbose_name='Количество заказов')
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Общая выручка')
    total_books_sold = models.PositiveIntegerField(default=0, verbose_name='Количество проданных книг')
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Средний чек')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Статистика продаж'
        verbose_name_plural = 'Статистика продаж'

    def __str__(self):
        return f"Статистика за {self.date}"

    @classmethod
    def get_or_create_for_date(cls, date):
        """Получить или создать статистику для даты"""
        stats, created = cls.objects.get_or_create(date=date)
        return stats

    @classmethod
    def update_daily_stats(cls, date=None):
        """Обновить статистику за день"""
        if date is None:
            date = timezone.now().date()
        
        from backend.apps.orders.models import Order
        
        # Получаем заказы за день
        orders = Order.objects.filter(
            created_at__date=date,
            status='delivered'
        )
        
        # Вычисляем статистику
        total_orders = orders.count()
        total_revenue = sum(order.total_amount for order in orders)
        total_books_sold = sum(
            sum(item.quantity for item in order.items.all()) 
            for order in orders
        )
        average_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Создаем или обновляем статистику
        stats = cls.get_or_create_for_date(date)
        stats.total_orders = total_orders
        stats.total_revenue = total_revenue
        stats.total_books_sold = total_books_sold
        stats.average_order_value = average_order_value
        stats.save()
        
        return stats

    @classmethod
    def get_weekly_stats(cls, weeks=4):
        """Получить статистику за последние недели"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(weeks=weeks)
        
        return cls.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')

    @classmethod
    def get_monthly_stats(cls, months=12):
        """Получить статистику за последние месяцы"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=months * 30)
        
        return cls.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')


class TopSellingBook(models.Model):
    """Топ продаваемых книг по дням"""
    date = models.DateField(verbose_name='Дата')
    book = models.ForeignKey('catalog.Book', on_delete=models.CASCADE, verbose_name='Книга')
    quantity_sold = models.PositiveIntegerField(verbose_name='Количество проданных')
    revenue = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Выручка')
    rank = models.PositiveIntegerField(verbose_name='Позиция в рейтинге')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'rank']
        unique_together = ['date', 'book']
        verbose_name = 'Топ продаваемых книг'
        verbose_name_plural = 'Топ продаваемых книг'

    def __str__(self):
        return f"{self.book.title} - {self.date} (позиция {self.rank})"

    @classmethod
    def update_daily_top_books(cls, date=None, top_count=10):
        """Обновить топ книг за день"""
        if date is None:
            date = timezone.now().date()
        
        from backend.apps.orders.models import Order
        from django.db.models import Sum, Count
        
        # Получаем статистику по книгам за день
        book_stats = cls.objects.filter(date=date).delete()  # Удаляем старые данные
        
        from backend.apps.catalog.models import Book
        book_stats = Book.objects.annotate(
            daily_quantity=Sum(
                'orderitem__quantity',
                filter=models.Q(orderitem__order__created_at__date=date, orderitem__order__status='delivered')
            ),
            daily_revenue=Sum(
                'orderitem__price',
                filter=models.Q(orderitem__order__created_at__date=date, orderitem__order__status='delivered')
            )
        ).filter(daily_quantity__gt=0).order_by('-daily_quantity')[:top_count]
        
        # Создаем записи для топ книг
        for rank, book in enumerate(book_stats, 1):
            cls.objects.create(
                date=date,
                book=book,
                quantity_sold=book.daily_quantity or 0,
                revenue=book.daily_revenue or 0,
                rank=rank
            )


class CustomerStats(models.Model):
    """Статистика по клиентам"""
    date = models.DateField(verbose_name='Дата')
    total_customers = models.PositiveIntegerField(default=0, verbose_name='Общее количество клиентов')
    new_customers = models.PositiveIntegerField(default=0, verbose_name='Новые клиенты')
    returning_customers = models.PositiveIntegerField(default=0, verbose_name='Постоянные клиенты')
    average_customer_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Средняя стоимость клиента')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['date']
        verbose_name = 'Статистика клиентов'
        verbose_name_plural = 'Статистика клиентов'

    def __str__(self):
        return f"Статистика клиентов за {self.date}"

    @classmethod
    def update_daily_customer_stats(cls, date=None):
        """Обновить статистику клиентов за день"""
        if date is None:
            date = timezone.now().date()
        
        from backend.apps.orders.models import Order
        from django.db.models import Count, Sum
        
        # Общее количество клиентов
        total_customers = User.objects.filter(
            orders__created_at__date__lte=date,
            orders__status='delivered'
        ).distinct().count()
        
        # Новые клиенты (впервые заказали в этот день)
        new_customers = User.objects.filter(
            orders__created_at__date=date,
            orders__status='delivered'
        ).annotate(
            first_order_date=models.Min('orders__created_at__date')
        ).filter(first_order_date=date).count()
        
        # Постоянные клиенты (заказывали и раньше)
        returning_customers = User.objects.filter(
            orders__created_at__date=date,
            orders__status='delivered'
        ).annotate(
            first_order_date=models.Min('orders__created_at__date')
        ).exclude(first_order_date=date).count()
        
        # Средняя стоимость клиента
        customer_revenue = User.objects.filter(
            orders__created_at__date=date,
            orders__status='delivered'
        ).annotate(
            daily_revenue=Sum('orders__total_amount')
        ).aggregate(total=Sum('daily_revenue'))['total'] or 0
        
        active_customers = User.objects.filter(
            orders__created_at__date=date,
            orders__status='delivered'
        ).count()
        
        average_customer_value = customer_revenue / active_customers if active_customers > 0 else 0
        
        # Создаем или обновляем статистику
        stats, created = cls.objects.get_or_create(date=date)
        stats.total_customers = total_customers
        stats.new_customers = new_customers
        stats.returning_customers = returning_customers
        stats.average_customer_value = average_customer_value
        stats.save()
        
        return stats