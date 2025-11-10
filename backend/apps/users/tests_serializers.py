from django.test import TestCase
from django.contrib.auth import get_user_model
from backend.apps.users.models import Profile
from backend.apps.users.serializers import (
    UserSerializer, RegisterSerializer, ProfileSerializer
)

User = get_user_model()


class TestRegisterSerializer(TestCase):
    """Тесты для RegisterSerializer"""
    
    def test_register_serializer_valid(self):
        """Тест валидной регистрации"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "first_name": "Иван",
            "last_name": "Иванов",
            "password": "securepass123",
            "password_confirm": "securepass123"
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, "newuser")
        self.assertEqual(user.email, "newuser@example.com")
        # Проверяем, что создан профиль
        self.assertIsNotNone(user.profile)
        self.assertEqual(user.profile.role, "buyer")
    
    def test_register_serializer_password_mismatch(self):
        """Тест несовпадения паролей"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "password_confirm": "differentpass"
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Пароли не совпадают", str(serializer.errors))
    
    def test_register_serializer_password_min_length(self):
        """Тест минимальной длины пароля"""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "short",
            "password_confirm": "short"
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())


class TestProfileSerializer(TestCase):
    """Тесты для ProfileSerializer"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass",
            first_name="Иван",
            last_name="Иванов"
        )
        self.profile = Profile.objects.create(
            user=self.user,
            role="buyer",
            phone="+79001234567",
            city="Москва"
        )
    
    def test_profile_serializer(self):
        """Тест сериализации профиля"""
        serializer = ProfileSerializer(self.profile)
        data = serializer.data
        self.assertEqual(data['phone'], "+79001234567")
        self.assertEqual(data['city'], "Москва")
        self.assertIn('full_name', data)
    
    def test_profile_serializer_read_only_fields(self):
        """Тест, что read_only поля не могут быть изменены"""
        data = {
            "phone": "+79009999999",
            "created_at": "2020-01-01T00:00:00Z"  # Попытка изменить read-only поле
        }
        serializer = ProfileSerializer(self.profile, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        updated_profile = serializer.save()
        # created_at не должен измениться
        self.assertNotEqual(str(updated_profile.created_at), "2020-01-01T00:00:00Z")


class TestUserSerializer(TestCase):
    """Тесты для UserSerializer"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass"
        )
        self.profile = Profile.objects.create(user=self.user)
    
    def test_user_serializer(self):
        """Тест сериализации пользователя"""
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['username'], "testuser")
        self.assertEqual(data['email'], "test@example.com")
        self.assertIn('profile', data)
    
    def test_user_serializer_read_only_fields(self):
        """Тест, что read_only поля не могут быть изменены"""
        data = {
            "username": "newusername",
            "id": 999,  # Попытка изменить read-only поле
            "date_joined": "2020-01-01T00:00:00Z"
        }
        serializer = UserSerializer(self.user, data=data, partial=True)
        self.assertTrue(serializer.is_valid())
        # id и date_joined не должны измениться
        updated_user = serializer.save()
        self.assertNotEqual(updated_user.id, 999)

