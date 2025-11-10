from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from backend.apps.users.models import Profile

User = get_user_model()


class TestProfileModel(TestCase):
    """Тесты для модели Profile"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass",
            first_name="Иван",
            last_name="Иванов"
        )
    
    def test_create_profile(self):
        """Тест создания профиля"""
        profile = Profile.objects.create(user=self.user, role="buyer")
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.role, "buyer")
        self.assertFalse(profile.is_blocked)
    
    def test_profile_default_role(self):
        """Тест роли по умолчанию"""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.role, "buyer")
    
    def test_profile_one_to_one(self):
        """Тест уникальности связи OneToOne"""
        Profile.objects.create(user=self.user)
        with self.assertRaises(IntegrityError):
            Profile.objects.create(user=self.user)
    
    def test_profile_full_name(self):
        """Тест свойства full_name"""
        profile = Profile.objects.create(user=self.user)
        self.assertEqual(profile.full_name, "Иван Иванов")
    
    def test_profile_full_name_fallback(self):
        """Тест fallback на username если нет имени"""
        user2 = User.objects.create_user(username="user2", email="user2@example.com", password="pass")
        profile = Profile.objects.create(user=user2)
        self.assertEqual(profile.full_name, "user2")
    
    def test_profile_is_admin(self):
        """Тест метода is_admin"""
        profile = Profile.objects.create(user=self.user, role="admin")
        self.assertTrue(profile.is_admin())
        
        profile.role = "buyer"
        self.assertFalse(profile.is_admin())
    
    def test_profile_is_manager(self):
        """Тест метода is_manager"""
        profile = Profile.objects.create(user=self.user, role="manager")
        self.assertTrue(profile.is_manager())
        
        profile.role = "admin"
        self.assertTrue(profile.is_manager())
        
        profile.role = "buyer"
        self.assertFalse(profile.is_manager())
    
    def test_profile_is_buyer(self):
        """Тест метода is_buyer"""
        profile = Profile.objects.create(user=self.user, role="buyer")
        self.assertTrue(profile.is_buyer())
        
        profile.role = "manager"
        self.assertTrue(profile.is_buyer())
        
        profile.role = "admin"
        self.assertTrue(profile.is_buyer())
        
        profile.role = "guest"
        self.assertFalse(profile.is_buyer())
    
    def test_profile_is_active(self):
        """Тест метода is_active"""
        profile = Profile.objects.create(user=self.user)
        self.assertTrue(profile.is_active())
        
        profile.is_blocked = True
        profile.save()
        self.assertFalse(profile.is_active())
    
    def test_profile_str(self):
        """Тест строкового представления профиля"""
        profile = Profile.objects.create(user=self.user, role="buyer")
        self.assertIn("testuser", str(profile))
        self.assertIn("Покупатель", str(profile))

