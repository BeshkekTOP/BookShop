"""
Система ролей и прав доступа для книжного магазина

Роли:
- Гость (Guest): Неавторизованные пользователи
- Покупатель (Customer): Обычные зарегистрированные пользователи
- Менеджер (Manager): Работники магазина, обрабатывают заказы
- Администратор (Admin): Полный доступ к системе
"""

from enum import Enum
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from backend.apps.orders.models import Order
from backend.apps.catalog.models import Book, Category, Author


class UserRole(Enum):
    GUEST = "guest"
    CUSTOMER = "customer"
    MANAGER = "manager"
    ADMIN = "admin"


class RolePermissions:
    """Определение прав доступа для каждой роли"""
    
    @staticmethod
    def can_view_catalog(role):
        """Могут ли просматривать каталог"""
        return role in [UserRole.GUEST, UserRole.CUSTOMER, UserRole.MANAGER, UserRole.ADMIN]
    
    @staticmethod
    def can_add_to_cart(role):
        """Могут ли добавлять в корзину"""
        return role in [UserRole.CUSTOMER, UserRole.MANAGER, UserRole.ADMIN]
    
    @staticmethod
    def can_create_order(role):
        """Могут ли оформлять заказы"""
        return role in [UserRole.CUSTOMER, UserRole.MANAGER, UserRole.ADMIN]
    
    @staticmethod
    def can_view_own_orders(role):
        """Могут ли видеть свои заказы"""
        return role in [UserRole.CUSTOMER, UserRole.MANAGER, UserRole.ADMIN]
    
    @staticmethod
    def can_view_all_orders(role):
        """Могут ли видеть все заказы"""
        return role in [UserRole.MANAGER, UserRole.ADMIN]
    
    @staticmethod
    def can_update_order_status(role):
        """Могут ли менять статус заказов"""
        return role in [UserRole.MANAGER, UserRole.ADMIN]
    
    @staticmethod
    def can_write_reviews(role):
        """Могут ли писать отзывы"""
        return role in [UserRole.CUSTOMER, UserRole.MANAGER, UserRole.ADMIN]
    
    @staticmethod
    def can_manage_catalog(role):
        """Могут ли управлять каталогом (книги, авторы, категории)"""
        return role == UserRole.ADMIN
    
    @staticmethod
    def can_manage_users(role):
        """Могут ли управлять пользователями"""
        return role == UserRole.ADMIN
    
    @staticmethod
    def can_view_reports(role):
        """Могут ли просматривать отчеты и аналитику"""
        return role in [UserRole.MANAGER, UserRole.ADMIN]
    
    @staticmethod
    def get_role_for_user(user):
        """Определяет роль пользователя"""
        if not user or not user.is_authenticated:
            return UserRole.GUEST
        
        if user.is_superuser:
            return UserRole.ADMIN
        
        # Проверяем флаги
        if hasattr(user, 'is_staff') and user.is_staff:
            # Если есть специальный флаг менеджера
            if hasattr(user, 'is_manager') and user.is_manager:
                return UserRole.MANAGER
            return UserRole.ADMIN
        
        # Обычный пользователь
        return UserRole.CUSTOMER


def setup_role_permissions():
    """Настройка групп и прав доступа для системы"""
    from django.contrib.auth.models import Group
    
    # Создаем группы
    groups = {
        'customers': 'Покупатели',
        'managers': 'Менеджеры',
        'admins': 'Администраторы'
    }
    
    for group_name, group_display in groups.items():
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            # Назначаем базовые разрешения
            if group_name == 'customers':
                # Покупатели могут добавлять в корзину
                pass
            elif group_name == 'managers':
                # Менеджеры могут просматривать и изменять заказы
                view_order = Permission.objects.get(
                    content_type__app_label='orders',
                    codename='view_order'
                )
                change_order = Permission.objects.get(
                    content_type__app_label='orders',
                    codename='change_order'
                )
                group.permissions.add(view_order, change_order)
            elif group_name == 'admins':
                # Администраторы имеют все права
                group.permissions.set(Permission.objects.all())


















