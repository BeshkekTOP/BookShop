from django.conf import settings
from django.db import models


class Profile(models.Model):
    """
    Профиль пользователя с ролью
    
    Роли для сайта (НЕ Django admin):
    - guest: Гость (неавторизованный)
    - buyer: Покупатель (обычный пользователь)
    - manager: Менеджер (обработка заказов)
    - admin: Администратор сайта
    """
    
    ROLE_CHOICES = [
        ('guest', 'Гость'),
        ('buyer', 'Покупатель'),
        ('manager', 'Менеджер'),
        ('admin', 'Администратор'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer', verbose_name='Роль на сайте')
    is_blocked = models.BooleanField(default=False, verbose_name='Заблокирован')
    blocked_reason = models.TextField(blank=True, verbose_name='Причина блокировки')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"Profile of {self.user} ({self.get_role_display()})"

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    def is_admin(self):
        """Проверка, является ли пользователь администратором сайта"""
        return self.role == 'admin'
    
    def is_manager(self):
        """Проверка, является ли пользователь менеджером"""
        return self.role in ['manager', 'admin']
    
    def is_buyer(self):
        """Проверка, является ли пользователь покупателем или выше"""
        return self.role in ['buyer', 'manager', 'admin']
    
    def is_active(self):
        """Проверка, активен ли пользователь (не заблокирован)"""
        return not self.is_blocked





