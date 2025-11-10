"""Команда для назначения роли пользователю"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from backend.apps.users.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Назначить роль пользователю на сайте'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Имя пользователя')
        parser.add_argument('role', type=str, choices=['guest', 'buyer', 'manager', 'admin'],
                          help='Роль для назначения')
        parser.add_argument(
            '--create-profile',
            action='store_true',
            help='Создать профиль, если его нет'
        )

    def handle(self, *args, **options):
        username = options['username']
        role = options['role']
        create_profile = options['create_profile']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'Пользователь "{username}" не найден')
        
        # Получаем или создаем профиль
        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={'role': role}
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Профиль создан для пользователя "{username}" с ролью "{role}"'
                )
            )
        else:
            old_role = profile.role
            profile.role = role
            profile.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Роль пользователя "{username}" изменена с "{old_role}" на "{role}"'
                )
            )
        
        # Выводим информацию о пользователе
        self.stdout.write(f'\nИнформация о пользователе:')
        self.stdout.write(f'  Username: {user.username}')
        self.stdout.write(f'  Email: {user.email}')
        self.stdout.write(f'  Django is_staff: {user.is_staff}')
        self.stdout.write(f'  Django is_superuser: {user.is_superuser}')
        self.stdout.write(f'  Site role: {profile.role}')
        
        # Показываем разрешения
        if profile.role == 'admin':
            self.stdout.write(f'\n✅ Доступны все возможности сайта')
        elif profile.role == 'manager':
            self.stdout.write(f'\n✅ Доступны: просмотр заказов, изменение статусов')
        elif profile.role == 'buyer':
            self.stdout.write(f'\n✅ Доступны: покупки, корзина, отзывы')
        elif profile.role == 'guest':
            self.stdout.write(f'\n⚠️  Только просмотр каталога')
























