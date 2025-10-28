"""Views для статистики продаж"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from backend.apps.core.decorators import admin_required, manager_required
from backend.apps.analytics.models import SalesStats, TopSellingBook, CustomerStats
from backend.apps.orders.models import Order
from backend.apps.catalog.models import Book


@admin_required
def sales_dashboard(request):
    """Главная панель статистики продаж"""
    # Период для статистики
    period = request.GET.get('period', 'week')
    
    if period == 'week':
        start_date = timezone.now().date() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now().date() - timedelta(days=30)
    elif period == 'quarter':
        start_date = timezone.now().date() - timedelta(days=90)
    else:
        start_date = timezone.now().date() - timedelta(days=7)
    
    # Общая статистика за период
    stats = SalesStats.objects.filter(date__gte=start_date)
    total_orders = stats.aggregate(total=Sum('total_orders'))['total'] or 0
    total_revenue = stats.aggregate(total=Sum('total_revenue'))['total'] or 0
    total_books_sold = stats.aggregate(total=Sum('total_books_sold'))['total'] or 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Статистика за сегодня
    today = timezone.now().date()
    today_stats = SalesStats.objects.filter(date=today).first()
    
    # Статистика за вчера
    yesterday = today - timedelta(days=1)
    yesterday_stats = SalesStats.objects.filter(date=yesterday).first()
    
    # Топ-10 книг за период
    top_books = TopSellingBook.objects.filter(
        date__gte=start_date
    ).select_related('book').values(
        'book__title', 'book__author__name', 'book__isbn'
    ).annotate(
        total_quantity=Sum('quantity_sold'),
        total_revenue=Sum('revenue')
    ).order_by('-total_quantity')[:10]
    
    # Статистика по дням для графика
    daily_stats = stats.order_by('date')
    
    # Статистика клиентов
    customer_stats = CustomerStats.objects.filter(date__gte=start_date)
    total_customers = customer_stats.aggregate(total=Sum('total_customers'))['total'] or 0
    new_customers = customer_stats.aggregate(total=Sum('new_customers'))['total'] or 0
    returning_customers = customer_stats.aggregate(total=Sum('returning_customers'))['total'] or 0
    
    context = {
        'period': period,
        'start_date': start_date,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'total_books_sold': total_books_sold,
        'avg_order_value': avg_order_value,
        'today_stats': today_stats,
        'yesterday_stats': yesterday_stats,
        'top_books': top_books,
        'daily_stats': daily_stats,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'returning_customers': returning_customers,
    }
    
    return render(request, 'web/sales/dashboard.html', context)


@admin_required
def sales_reports(request):
    """Отчеты по продажам"""
    # Период для отчета
    period = request.GET.get('period', 'month')
    report_type = request.GET.get('type', 'overview')
    
    if period == 'week':
        start_date = timezone.now().date() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now().date() - timedelta(days=30)
    elif period == 'quarter':
        start_date = timezone.now().date() - timedelta(days=90)
    else:
        start_date = timezone.now().date() - timedelta(days=30)
    
    context = {
        'period': period,
        'report_type': report_type,
        'start_date': start_date,
    }
    
    if report_type == 'overview':
        # Общий обзор
        stats = SalesStats.objects.filter(date__gte=start_date).order_by('date')
        context.update({
            'stats': stats,
            'total_revenue': stats.aggregate(total=Sum('total_revenue'))['total'] or 0,
            'total_orders': stats.aggregate(total=Sum('total_orders'))['total'] or 0,
        })
        return render(request, 'web/sales/reports_overview.html', context)
    
    elif report_type == 'books':
        # Отчет по книгам
        top_books = TopSellingBook.objects.filter(
            date__gte=start_date
        ).select_related('book').values(
            'book__title', 'book__author__name', 'book__isbn', 'book__price'
        ).annotate(
            total_quantity=Sum('quantity_sold'),
            total_revenue=Sum('revenue'),
            avg_rank=Avg('rank')
        ).order_by('-total_quantity')
        
        context.update({
            'top_books': top_books,
        })
        return render(request, 'web/sales/reports_books.html', context)
    
    elif report_type == 'customers':
        # Отчет по клиентам
        customer_stats = CustomerStats.objects.filter(date__gte=start_date).order_by('date')
        context.update({
            'customer_stats': customer_stats,
        })
        return render(request, 'web/sales/reports_customers.html', context)
    
    else:
        return render(request, 'web/sales/reports_overview.html', context)


@manager_required
def manager_sales_stats(request):
    """Статистика продаж для менеджера (упрощенная версия)"""
    # Период для статистики
    period = request.GET.get('period', 'week')
    
    if period == 'week':
        start_date = timezone.now().date() - timedelta(days=7)
    elif period == 'month':
        start_date = timezone.now().date() - timedelta(days=30)
    else:
        start_date = timezone.now().date() - timedelta(days=7)
    
    # Статистика заказов
    orders = Order.objects.filter(
        created_at__date__gte=start_date,
        status='delivered'
    )
    
    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
    
    # Статистика по статусам
    status_stats = Order.objects.filter(
        created_at__date__gte=start_date
    ).values('status').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('status')
    
    # Топ-5 книг
    top_books = Book.objects.annotate(
        orders_count=Count('orderitem__order', filter=models.Q(
            orderitem__order__created_at__date__gte=start_date,
            orderitem__order__status='delivered'
        )),
        quantity_sold=Sum('orderitem__quantity', filter=models.Q(
            orderitem__order__created_at__date__gte=start_date,
            orderitem__order__status='delivered'
        )),
        revenue=Sum('orderitem__price', filter=models.Q(
            orderitem__order__created_at__date__gte=start_date,
            orderitem__order__status='delivered'
        ))
    ).filter(orders_count__gt=0).order_by('-orders_count')[:5]
    
    context = {
        'period': period,
        'start_date': start_date,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'status_stats': status_stats,
        'top_books': top_books,
    }
    
    return render(request, 'web/sales/manager_stats.html', context)






