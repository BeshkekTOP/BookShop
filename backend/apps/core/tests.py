from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from backend.apps.core.decorators import buyer_required, admin_required, manager_required
from backend.apps.core.middleware import AuditMiddleware
from backend.apps.users.models import Profile

User = get_user_model()


class TestDecorators(TestCase):
    """Тесты для декораторов доступа"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
        self.profile = Profile.objects.create(user=self.user, role="buyer")
    
    def _get_request_with_middleware(self, path='/test/'):
        """Создает запрос с настроенными middleware"""
        request = self.factory.get(path)
        # Добавляем middleware для работы messages
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)
        return request
    
    def test_buyer_required_authenticated(self):
        """Тест декоратора buyer_required для авторизованного пользователя"""
        @buyer_required
        def test_view(request):
            return HttpResponse("OK")
        
        request = self._get_request_with_middleware()
        request.user = self.user
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
    
    def test_buyer_required_unauthenticated(self):
        """Тест декоратора buyer_required для неавторизованного пользователя"""
        from django.contrib.auth.models import AnonymousUser
        
        @buyer_required
        def test_view(request):
            return HttpResponse("OK")
        
        request = self._get_request_with_middleware()
        request.user = AnonymousUser()
        response = test_view(request)
        self.assertEqual(response.status_code, 302)  # Редирект на login
    
    def test_admin_required(self):
        """Тест декоратора admin_required"""
        @admin_required
        def test_view(request):
            return HttpResponse("OK")
        
        # Тест для администратора
        self.profile.role = "admin"
        self.profile.save()
        request = self._get_request_with_middleware()
        request.user = self.user
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        
        # Тест для неадминистратора
        self.profile.role = "buyer"
        self.profile.save()
        request = self._get_request_with_middleware()
        request.user = self.user
        response = test_view(request)
        self.assertEqual(response.status_code, 302)  # Редирект
    
    def test_manager_required(self):
        """Тест декоратора manager_required"""
        @manager_required
        def test_view(request):
            return HttpResponse("OK")
        
        # Тест для менеджера
        self.profile.role = "manager"
        self.profile.save()
        request = self._get_request_with_middleware()
        request.user = self.user
        response = test_view(request)
        self.assertEqual(response.status_code, 200)
        
        # Тест для покупателя
        self.profile.role = "buyer"
        self.profile.save()
        request = self._get_request_with_middleware()
        request.user = self.user
        response = test_view(request)
        self.assertEqual(response.status_code, 302)  # Редирект


class TestAuditMiddleware(TestCase):
    """Тесты для AuditMiddleware"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="testpass")
        self.middleware = AuditMiddleware(get_response=lambda request: HttpResponse("OK"))
    
    def test_middleware_process_request(self):
        """Тест обработки запроса middleware"""
        request = self.factory.get('/test/')
        request.user = self.user
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        response = self.middleware.process_request(request)
        self.assertIsNone(response)  # Middleware должен вернуть None
    
    def test_middleware_get_client_ip(self):
        """Тест получения IP адреса клиента"""
        request = self.factory.get('/test/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        ip = AuditMiddleware.get_client_ip(request)
        self.assertEqual(ip, '192.168.1.1')
    
    def test_middleware_get_client_ip_x_forwarded_for(self):
        """Тест получения IP из X-Forwarded-For"""
        request = self.factory.get('/test/')
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        
        ip = AuditMiddleware.get_client_ip(request)
        self.assertEqual(ip, '10.0.0.1')  # Берется первый IP из списка

