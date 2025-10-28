"""Система аудита и middleware для логирования"""
import logging
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class AuditMiddleware(MiddlewareMixin):
    """Middleware для логирования запросов пользователей"""
    
    def process_request(self, request):
        """Логирует информацию о запросе"""
        if request.user.is_authenticated:
            logger.info(
                f"User: {request.user.username}, "
                f"Path: {request.path}, "
                f"Method: {request.method}, "
                f"IP: {self.get_client_ip(request)}"
            )
        return None
    
    @staticmethod
    def get_client_ip(request):
        """Получает IP адрес клиента"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# RoleBasedAccessMiddleware убран, так как он конфликтует с текущей архитектурой
# Используем декораторы в views вместо middleware для проверки ролей
