"""Декораторы для проверки ролей и доступа"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test


def guest_required(view_func):
    """Декоратор для функций, доступных только гостям (неавторизованным)"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Вы уже авторизованы в системе')
            return redirect('catalog')
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def buyer_required(view_func):
    """Декоратор для функций, требующих авторизации (покупатель и выше)"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Для доступа к этой странице необходимо войти в систему')
            return redirect('login')
        
        # Проверяем роль через профиль
        if hasattr(request.user, 'profile'):
            # Проверяем, что роль позволяет доступ (покупатель и выше)
            if request.user.profile.role not in ['buyer', 'manager', 'admin']:
                messages.error(request, 'У вас нет доступа к этой странице')
                return redirect('catalog')
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def admin_required(view_func):
    """Декоратор для функций, доступных только администраторам САЙТА (не Django)"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Необходимо войти в систему')
            return redirect('login')
        
        # Проверяем роль через профиль
        if hasattr(request.user, 'profile'):
            if request.user.profile.role != 'admin':
                messages.error(request, 'У вас нет доступа к этой странице. Требуется роль администратора.')
                return redirect('catalog')
        else:
            # Если нет профиля, проверяем Django staff
            if not request.user.is_staff:
                messages.error(request, 'У вас нет доступа к этой странице')
                return redirect('catalog')
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def manager_required(view_func):
    """Декоратор для функций, доступных менеджерам и админам САЙТА"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Необходимо войти в систему')
            return redirect('login')
        
        # Проверка роли через профиль
        if hasattr(request.user, 'profile'):
            if request.user.profile.role not in ['manager', 'admin']:
                messages.error(request, 'У вас нет доступа к этой странице. Требуется роль менеджера или администратора.')
                return redirect('catalog')
        else:
            # Если нет профиля, проверяем Django staff
            if not request.user.is_staff:
                messages.error(request, 'У вас нет доступа к этой странице')
                return redirect('catalog')
        
        return view_func(request, *args, **kwargs)
    
    return wrapped_view


def role_required(*roles):
    """Универсальный декоратор для проверки роли пользователя
    
    Args:
        *roles: Названия ролей, которым разрешен доступ
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Необходимо войти в систему')
                return redirect('login')
            
            user_role = getattr(request.user, 'role', None) or 'buyer'
            
            if user_role not in roles:
                messages.error(request, 'У вас нет доступа к этой странице')
                return redirect('catalog')
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def permission_required(permission_name):
    """Декоратор для проверки конкретного разрешения"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Необходимо войти в систему')
                return redirect('login')
            
            # Проверка разрешения
            if not getattr(request.user, f'has_{permission_name}_permission', lambda: False)():
                messages.error(request, 'У вас нет прав для выполнения этого действия')
                return redirect('catalog')
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator

