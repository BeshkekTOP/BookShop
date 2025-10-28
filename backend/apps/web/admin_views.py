"""Views для администраторской панели сайта"""
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from backend.apps.users.models import Profile
from backend.apps.orders.models import Order, OrderItem
from backend.apps.catalog.models import Book, Inventory
from backend.apps.core.decorators import admin_required
from backend.apps.core.models import AuditLog
import datetime

User = get_user_model()


@admin_required
def admin_dashboard(request):
    """Главная панель администратора"""
    # Статистика пользователей
    total_users = User.objects.count()
    active_users = Profile.objects.filter(is_blocked=False).count()
    blocked_users = Profile.objects.filter(is_blocked=True).count()
    
    users_by_role = Profile.objects.values('role').annotate(count=Count('id'))
    
    # Статистика заказов
    total_orders = Order.objects.count()
    orders_today = Order.objects.filter(created_at__date=datetime.date.today()).count()
    orders_this_month = Order.objects.filter(
        created_at__year=datetime.date.today().year,
        created_at__month=datetime.date.today().month
    ).count()
    
    # Общая выручка
    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0
    
    # Топ-5 продаваемых книг
    top_books = OrderItem.objects.values(
        'book__title', 'book__id'
    ).annotate(
        total_sold=Sum('quantity'),
        revenue=Sum('price') * Sum('quantity')
    ).order_by('-total_sold')[:5]
    
    # Последние заказы
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'blocked_users': blocked_users,
        'users_by_role': users_by_role,
        'total_orders': total_orders,
        'orders_today': orders_today,
        'orders_this_month': orders_this_month,
        'total_revenue': total_revenue,
        'top_books': top_books,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'web/admin/dashboard.html', context)


@admin_required
def admin_users_list(request):
    """Список пользователей для управления"""
    search = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    status_filter = request.GET.get('status', '')
    
    users = User.objects.select_related('profile').all()
    
    if search:
        users = users.filter(
            username__icontains=search
        ) | users.filter(
            email__icontains=search
        ) | users.filter(
            profile__phone__icontains=search
        )
    
    if role_filter:
        users = users.filter(profile__role=role_filter)
    
    if status_filter == 'blocked':
        users = users.filter(profile__is_blocked=True)
    elif status_filter == 'active':
        users = users.filter(profile__is_blocked=False)
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'search': search,
        'role_filter': role_filter,
        'status_filter': status_filter,
    }
    
    return render(request, 'web/admin/users_list.html', context)


@admin_required
def admin_user_detail(request, user_id):
    """Детальная информация о пользователе"""
    user = get_object_or_404(User, id=user_id)
    
    try:
        profile = user.profile
    except Profile.DoesNotExist:
        profile = None
    
    # Заказы пользователя
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    # Общая статистика
    total_orders = orders.count()
    total_spent = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    avg_order_value = orders.aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    context = {
        'user': user,
        'profile': profile,
        'orders': orders[:20],
        'total_orders': total_orders,
        'total_spent': total_spent,
        'avg_order_value': avg_order_value,
    }
    
    return render(request, 'web/admin/user_detail.html', context)


@admin_required
@require_http_methods(["POST"])
def admin_user_block(request, user_id):
    """Блокировка/разблокировка пользователя"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'Нельзя заблокировать самого себя')
        return redirect('admin-user-detail', user_id=user_id)
    
    profile, _ = Profile.objects.get_or_create(user=user)
    
    if request.POST.get('action') == 'block':
        reason = request.POST.get('reason', '')
        profile.is_blocked = True
        profile.blocked_reason = reason
        profile.save()
        
        # Логируем действие
        AuditLog.objects.create(
            action='updated',
            actor=request.user,
            object_id=user.id,
            old_data={'is_blocked': False},
            new_data={'is_blocked': True, 'reason': reason},
            method='POST',
            ip_address=request.META.get('REMOTE_ADDR'),
            path=request.path
        )
        
        messages.success(request, f'Пользователь {user.username} заблокирован')
    
    elif request.POST.get('action') == 'unblock':
        profile.is_blocked = False
        profile.blocked_reason = ''
        profile.save()
        
        # Логируем действие
        AuditLog.objects.create(
            action='updated',
            actor=request.user,
            object_id=user.id,
            old_data={'is_blocked': True},
            new_data={'is_blocked': False},
            method='POST',
            ip_address=request.META.get('REMOTE_ADDR'),
            path=request.path
        )
        
        messages.success(request, f'Пользователь {user.username} разблокирован')
    
    return redirect('admin-user-detail', user_id=user_id)


@admin_required
@require_http_methods(["POST"])
def admin_user_set_role(request, user_id):
    """Назначение роли пользователю"""
    user = get_object_or_404(User, id=user_id)
    role = request.POST.get('role')
    
    if role not in ['guest', 'buyer', 'manager', 'admin']:
        messages.error(request, 'Некорректная роль')
        return redirect('admin-user-detail', user_id=user_id)
    
    profile, _ = Profile.objects.get_or_create(user=user)
    old_role = profile.role
    profile.role = role
    profile.save()
    
    # Логируем действие
    AuditLog.objects.create(
        action='updated',
        actor=request.user,
        object_id=user.id,
        old_data={'role': old_role},
        new_data={'role': role},
        method='POST',
        ip_address=request.META.get('REMOTE_ADDR'),
        path=request.path
    )
    
    messages.success(request, f'Роль пользователя {user.username} изменена на {role}')
    return redirect('admin-user-detail', user_id=user_id)


@admin_required
@require_http_methods(["POST"])
def admin_user_delete(request, user_id):
    """Удаление пользователя"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'Нельзя удалить самого себя')
        return redirect('admin-user-detail', user_id=user_id)
    
    username = user.username
    
    try:
        # Логируем действие
        AuditLog.objects.create(
            action='deleted',
            actor=request.user,
            object_id=user.id,
            new_data={'username': username},
            method='POST',
            ip_address=request.META.get('REMOTE_ADDR'),
            path=request.path
        )
        
        user.delete()
        messages.success(request, f'Пользователь {username} удален')
        
    except Exception as e:
        messages.error(request, f'Ошибка при удалении пользователя: {str(e)}')
    
    return redirect('admin-users')


@admin_required
def admin_user_block(request, user_id):
    """Блокировка/разблокировка пользователя"""
    user = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    
    if user == request.user:
        messages.error(request, 'Нельзя заблокировать самого себя')
        return redirect('admin-user-detail', user_id=user_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        reason = request.POST.get('reason', '')
        
        try:
            if action == 'block':
                profile.is_blocked = True
                profile.blocked_reason = reason
                profile.save()
                
                # Логируем действие
                AuditLog.objects.create(
                    action='updated',
                    actor=request.user,
                    object_id=user.id,
                    new_data={'is_blocked': True, 'blocked_reason': reason},
                    method='POST',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    path=request.path
                )
                
                messages.success(request, f'Пользователь {user.username} заблокирован')
            elif action == 'unblock':
                profile.is_blocked = False
                profile.blocked_reason = ''
                profile.save()
                
                # Логируем действие
                AuditLog.objects.create(
                    action='updated',
                    actor=request.user,
                    object_id=user.id,
                    new_data={'is_blocked': False, 'blocked_reason': ''},
                    method='POST',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    path=request.path
                )
                
                messages.success(request, f'Пользователь {user.username} разблокирован')
                
        except Exception as e:
            messages.error(request, f'Ошибка при изменении статуса пользователя: {str(e)}')
    
    return redirect('admin-user-detail', user_id=user_id)


@admin_required
def admin_user_change_role(request, user_id):
    """Изменение роли пользователя"""
    user = get_object_or_404(User, id=user_id)
    profile, _ = Profile.objects.get_or_create(user=user)
    
    if user == request.user:
        messages.error(request, 'Нельзя изменить роль самому себе')
        return redirect('admin-user-detail', user_id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        
        if new_role not in [choice[0] for choice in Profile.ROLE_CHOICES]:
            messages.error(request, 'Неверная роль')
            return redirect('admin-user-detail', user_id=user_id)
        
        try:
            old_role = profile.role
            profile.role = new_role
            profile.save()
            
            # Логируем действие
            AuditLog.objects.create(
                action='updated',
                actor=request.user,
                object_id=user.id,
                old_data={'role': old_role},
                new_data={'role': new_role},
                method='POST',
                ip_address=request.META.get('REMOTE_ADDR'),
                path=request.path
            )
            
            messages.success(request, f'Роль пользователя {user.username} изменена с {old_role} на {new_role}')
            
        except Exception as e:
            messages.error(request, f'Ошибка при изменении роли: {str(e)}')
    
    return redirect('admin-user-detail', user_id=user_id)


@admin_required
def admin_user_activity_logs(request, user_id):
    """Логи активности пользователя"""
    user = get_object_or_404(User, id=user_id)
    
    # Получаем логи активности пользователя
    logs = AuditLog.objects.filter(
        Q(actor=user) | Q(object_id=user.id)
    ).order_by('-created_at')[:50]
    
    context = {
        'user': user,
        'logs': logs,
    }
    return render(request, 'web/admin/user_activity_logs.html', context)


@admin_required
def admin_reports(request):
    """Главная страница отчетов"""
    return render(request, 'web/admin/reports.html')


@admin_required
def admin_reports_export(request):
    """Экспорт отчетов в CSV"""
    report_type = request.GET.get('type', 'all')
    
    if report_type == 'top_books':
        return export_top_books_csv(request)
    elif report_type == 'user_activity':
        return export_user_activity_csv(request)
    elif report_type == 'combined':
        return export_combined_csv(request)
    else:
        messages.error(request, 'Неверный тип отчета')
        return redirect('admin-reports')


def export_top_books_csv(request):
    """Экспорт топ-10 книг в CSV"""
    from django.http import HttpResponse
    import csv
    from io import StringIO
    
    # Получаем топ-10 книг
    top_books = Book.objects.annotate(
        total_orders=Count('orderitem__order'),
        total_quantity=Sum('orderitem__quantity'),
        total_revenue=Sum('orderitem__price')
    ).filter(total_orders__gt=0).order_by('-total_orders')[:10]
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="top_books_report.csv"'
    
    # Добавляем BOM для корректного отображения в Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow(['Позиция', 'Название книги', 'ISBN', 'Категория', 'Цена', 'Количество заказов', 'Общее количество проданных', 'Общая выручка'])
    
    for i, book in enumerate(top_books, 1):
        writer.writerow([
            i,
            book.title,
            book.isbn,
            book.category.name,
            book.price,
            book.total_orders,
            book.total_quantity or 0,
            book.total_revenue or 0
        ])
    
    return response


def export_user_activity_csv(request):
    """Экспорт активности пользователей в CSV"""
    from django.http import HttpResponse
    import csv
    from io import StringIO
    
    # Получаем активных пользователей
    active_users = User.objects.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).filter(total_orders__gt=0).order_by('-total_orders')[:20]
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="user_activity_report.csv"'
    
    # Добавляем BOM для корректного отображения в Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    writer.writerow(['Позиция', 'Имя пользователя', 'Email', 'Имя', 'Фамилия', 'Количество заказов', 'Общая сумма покупок', 'Средний чек', 'Дата регистрации'])
    
    for i, user in enumerate(active_users, 1):
        avg_order = user.total_spent / user.total_orders if user.total_orders > 0 else 0
        writer.writerow([
            i,
            user.username,
            user.email or '',
            user.first_name or '',
            user.last_name or '',
            user.total_orders,
            user.total_spent or 0,
            round(avg_order, 2),
            user.date_joined.strftime('%d.%m.%Y %H:%M')
        ])
    
    return response


def export_combined_csv(request):
    """Экспорт комбинированного отчета в CSV"""
    from django.http import HttpResponse
    import csv
    from io import StringIO
    from datetime import datetime
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="combined_report_{datetime.now().strftime("%Y%m%d_%H%M")}.csv"'
    
    # Добавляем BOM для корректного отображения в Excel
    response.write('\ufeff')
    
    writer = csv.writer(response)
    
    # Заголовок отчета
    writer.writerow(['КОМБИНИРОВАННЫЙ ОТЧЕТ'])
    writer.writerow([f'Дата создания: {datetime.now().strftime("%d.%m.%Y %H:%M")}'])
    writer.writerow([])
    
    # Топ-10 книг
    writer.writerow(['ТОП-10 КНИГ ПО ПРОДАЖАМ'])
    writer.writerow(['Позиция', 'Название книги', 'ISBN', 'Категория', 'Цена', 'Количество заказов', 'Общее количество проданных', 'Общая выручка'])
    
    top_books = Book.objects.annotate(
        total_orders=Count('orderitem__order'),
        total_quantity=Sum('orderitem__quantity'),
        total_revenue=Sum('orderitem__price')
    ).filter(total_orders__gt=0).order_by('-total_orders')[:10]
    
    for i, book in enumerate(top_books, 1):
        writer.writerow([
            i,
            book.title,
            book.isbn,
            book.category.name,
            book.price,
            book.total_orders,
            book.total_quantity or 0,
            book.total_revenue or 0
        ])
    
    writer.writerow([])
    
    # Активность пользователей
    writer.writerow(['АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЕЙ'])
    writer.writerow(['Позиция', 'Имя пользователя', 'Email', 'Имя', 'Фамилия', 'Количество заказов', 'Общая сумма покупок', 'Средний чек', 'Дата регистрации'])
    
    active_users = User.objects.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).filter(total_orders__gt=0).order_by('-total_orders')[:20]
    
    for i, user in enumerate(active_users, 1):
        avg_order = user.total_spent / user.total_orders if user.total_orders > 0 else 0
        writer.writerow([
            i,
            user.username,
            user.email or '',
            user.first_name or '',
            user.last_name or '',
            user.total_orders,
            user.total_spent or 0,
            round(avg_order, 2),
            user.date_joined.strftime('%d.%m.%Y %H:%M')
        ])
    
    return response


@admin_required
def admin_inventory(request):
    """Управление остатками на складе"""
    books = Book.objects.select_related('category', 'inventory').all()
    
    search = request.GET.get('search', '')
    if search:
        books = books.filter(title__icontains=search)
    
    context = {'books': books, 'search': search}
    
    return render(request, 'web/admin/inventory.html', context)


@admin_required
@require_http_methods(["POST"])
def admin_inventory_update(request, book_id):
    """Обновление остатков на складе"""
    book = get_object_or_404(Book, id=book_id)
    
    try:
        new_stock = int(request.POST.get('stock', 0))
    except (ValueError, TypeError):
        messages.error(request, 'Некорректное значение количества')
        return redirect('admin-inventory')
    
    inventory, _ = Inventory.objects.get_or_create(book=book)
    old_stock = inventory.stock
    inventory.stock = new_stock
    inventory.save()
    
    # Логируем действие
    AuditLog.objects.create(
        action='updated',
        actor=request.user,
        object_id=book.id,
        old_data={'stock': old_stock},
        new_data={'stock': new_stock},
        method='POST',
        ip_address=request.META.get('REMOTE_ADDR'),
        path=request.path
    )
    
    messages.success(request, f'Остатки по книге "{book.title}" обновлены')
    return redirect('admin-inventory')


@admin_required
def admin_reports_top_books(request):
    """Отчет: Топ-10 продаваемых книг"""
    top_books = OrderItem.objects.values(
        'book__id',
        'book__title',
        'book__category__name',
        'book__price'
    ).annotate(
        total_sold=Sum('quantity'),
        total_revenue=Sum('price') * Sum('quantity'),
        order_count=Count('order', distinct=True)
    ).order_by('-total_sold')[:10]
    
    context = {'top_books': top_books}
    return render(request, 'web/admin/reports/top_books.html', context)


@admin_required
def admin_reports_user_activity(request):
    """Отчет: Активность пользователей"""
    # Пользователи с наибольшим количеством заказов
    active_users = User.objects.annotate(
        total_orders=Count('orders'),
        total_spent=Sum('orders__total_amount')
    ).filter(total_orders__gt=0).order_by('-total_orders')[:20]
    
    context = {'active_users': active_users}
    return render(request, 'web/admin/reports/user_activity.html', context)


@admin_required
def admin_audit_logs(request):
    """Просмотр логов действий"""
    logs = AuditLog.objects.select_related('actor').order_by('-created_at')[:100]
    
    context = {'logs': logs}
    return render(request, 'web/admin/audit_logs.html', context)



