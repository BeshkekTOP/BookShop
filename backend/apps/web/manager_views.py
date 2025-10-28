"""Views для менеджера магазина"""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.views.decorators.http import require_http_methods
from backend.apps.core.decorators import manager_required
from backend.apps.orders.models import Order, OrderItem
from backend.apps.catalog.models import Book
from backend.apps.core.models import AuditLog
from datetime import datetime, timedelta

User = get_user_model()


@manager_required
def manager_dashboard(request):
    """Главная панель менеджера"""
    # Статистика заказов
    total_orders = Order.objects.count()
    new_orders = Order.objects.filter(status='new').count()
    processing_orders = Order.objects.filter(status='processing').count()
    shipped_orders = Order.objects.filter(status='shipped').count()
    delivered_orders = Order.objects.filter(status='delivered').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()
    
    # Статистика за сегодня
    today = datetime.now().date()
    today_orders = Order.objects.filter(created_at__date=today).count()
    today_revenue = Order.objects.filter(
        created_at__date=today, 
        status__in=['delivered', 'shipped']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Статистика за неделю
    week_ago = today - timedelta(days=7)
    week_orders = Order.objects.filter(created_at__date__gte=week_ago).count()
    week_revenue = Order.objects.filter(
        created_at__date__gte=week_ago,
        status__in=['delivered', 'shipped']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Последние заказы
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    # Топ-5 книг за неделю
    top_books = Book.objects.annotate(
        week_orders=Count('orderitem__order', filter=Q(orderitem__order__created_at__date__gte=week_ago)),
        week_quantity=Sum('orderitem__quantity', filter=Q(orderitem__order__created_at__date__gte=week_ago))
    ).filter(week_orders__gt=0).order_by('-week_orders')[:5]
    
    context = {
        'total_orders': total_orders,
        'new_orders': new_orders,
        'processing_orders': processing_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'cancelled_orders': cancelled_orders,
        'today_orders': today_orders,
        'today_revenue': today_revenue,
        'week_orders': week_orders,
        'week_revenue': week_revenue,
        'recent_orders': recent_orders,
        'top_books': top_books,
    }
    
    return render(request, 'web/manager/dashboard.html', context)


@manager_required
def manager_orders(request):
    """Список всех заказов с фильтрацией"""
    orders = Order.objects.select_related('user').order_by('-created_at')
    
    # Фильтры
    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    search = request.GET.get('search', '')
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            orders = orders.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    if search:
        orders = orders.filter(
            Q(id__icontains=search) |
            Q(user__username__icontains=search) |
            Q(user__email__icontains=search) |
            Q(shipping_address__icontains=search)
        )
    
    # Статусы для фильтра
    STATUS_CHOICES = [
        ('', 'Все статусы'),
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    context = {
        'orders': orders,
        'status_choices': STATUS_CHOICES,
        'current_status': status_filter,
        'date_from': date_from,
        'date_to': date_to,
        'search': search,
    }
    
    return render(request, 'web/manager/orders.html', context)


@manager_required
def manager_order_detail(request, order_id):
    """Детальный просмотр заказа"""
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.select_related('book').all()
    
    # Статусы для изменения
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    context = {
        'order': order,
        'order_items': order_items,
        'status_choices': STATUS_CHOICES,
    }
    
    return render(request, 'web/manager/order_detail.html', context)


@manager_required
@require_http_methods(["POST"])
def manager_update_order_status(request, order_id):
    """Изменение статуса заказа"""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    cancel_reason = request.POST.get('cancel_reason', '')
    
    if not new_status:
        messages.error(request, 'Необходимо выбрать статус')
        return redirect('manager-order-detail', order_id=order_id)
    
    # Валидация статуса
    valid_statuses = ['new', 'processing', 'shipped', 'delivered', 'cancelled']
    if new_status not in valid_statuses:
        messages.error(request, 'Неверный статус')
        return redirect('manager-order-detail', order_id=order_id)
    
    # Проверка на отмену
    if new_status == 'cancelled' and not cancel_reason:
        messages.error(request, 'При отмене заказа необходимо указать причину')
        return redirect('manager-order-detail', order_id=order_id)
    
    try:
        old_status = order.status
        order.status = new_status
        
        # Добавляем причину отмены если нужно
        if new_status == 'cancelled':
            order.cancel_reason = cancel_reason
        
        order.save()
        
        # Логируем изменение
        AuditLog.objects.create(
            action='updated',
            actor=request.user,
            object_id=order.id,
            old_data={'status': old_status},
            new_data={'status': new_status, 'cancel_reason': cancel_reason if new_status == 'cancelled' else ''},
            method='POST',
            ip_address=request.META.get('REMOTE_ADDR'),
            path=request.path
        )
        
        status_display = dict(Order.STATUS_CHOICES)[new_status]
        messages.success(request, f'Статус заказа #{order.id} изменен на "{status_display}"')
        
    except Exception as e:
        messages.error(request, f'Ошибка при изменении статуса: {str(e)}')
    
    return redirect('manager-order-detail', order_id=order_id)


@manager_required
def manager_statistics(request):
    """Статистика продаж для менеджера"""
    # Период для статистики
    period = request.GET.get('period', 'week')
    
    if period == 'week':
        start_date = datetime.now().date() - timedelta(days=7)
    elif period == 'month':
        start_date = datetime.now().date() - timedelta(days=30)
    elif period == 'quarter':
        start_date = datetime.now().date() - timedelta(days=90)
    else:
        start_date = datetime.now().date() - timedelta(days=7)
    
    # Общая статистика за период
    orders_stats = Order.objects.filter(created_at__date__gte=start_date)
    total_orders = orders_stats.count()
    total_revenue = orders_stats.filter(
        status__in=['delivered', 'shipped']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Средний чек
    if total_orders > 0:
        avg_order_value = total_revenue / total_orders
    else:
        avg_order_value = 0
    
    # Статистика по статусам
    status_stats = orders_stats.values('status').annotate(
        count=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('status')
    
    # Топ-10 книг за период
    top_books = Book.objects.annotate(
        orders_count=Count('orderitem__order', filter=Q(orderitem__order__created_at__date__gte=start_date)),
        quantity_sold=Sum('orderitem__quantity', filter=Q(orderitem__order__created_at__date__gte=start_date)),
        revenue=Sum('orderitem__price', filter=Q(orderitem__order__created_at__date__gte=start_date))
    ).filter(orders_count__gt=0).order_by('-orders_count')[:10]
    
    # Статистика по дням (для графика)
    daily_stats = orders_stats.extra(
        select={'day': 'date(created_at)'}
    ).values('day').annotate(
        orders=Count('id'),
        revenue=Sum('total_amount')
    ).order_by('day')
    
    context = {
        'period': period,
        'start_date': start_date,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
        'status_stats': status_stats,
        'top_books': top_books,
        'daily_stats': daily_stats,
    }
    
    return render(request, 'web/manager/statistics.html', context)


