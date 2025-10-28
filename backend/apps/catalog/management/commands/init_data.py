"""Команда для инициализации базы данных с тестовыми данными"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
import random

from backend.apps.catalog.models import Book, Category, Author, BookAuthors, Inventory

User = get_user_model()


class Command(BaseCommand):
    help = 'Создание тестовых данных: админ и книги'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить все существующие данные и создать заново'
        )

    def handle(self, *args, **options):
        with transaction.atomic():
            from backend.apps.users.models import Profile
            
            # Создание или получение администратора Django (для доступа к /admin/)
            admin_user, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@bookshop.ru',
                    'first_name': 'Администратор',
                    'is_staff': True,
                    'is_superuser': True,
                }
            )
            if created:
                admin_user.set_password('admin123')
                admin_user.save()
                self.stdout.write(self.style.SUCCESS('Создан администратор Django: admin / admin123'))
            else:
                # Обновляем права если админ уже существует
                if not admin_user.is_staff or not admin_user.is_superuser:
                    admin_user.is_staff = True
                    admin_user.is_superuser = True
                    admin_user.save()
                    self.stdout.write(self.style.SUCCESS('Права администратора Django обновлены'))
            
            # Создаем профиль с ролью администратора САЙТА (не Django)
            profile, profile_created = Profile.objects.get_or_create(
                user=admin_user,
                defaults={'role': 'admin'}
            )
            if not profile_created and profile.role != 'admin':
                profile.role = 'admin'
                profile.save()
                self.stdout.write(self.style.SUCCESS('Профиль администратора сайта обновлен'))
            elif profile_created:
                self.stdout.write(self.style.SUCCESS('Профиль администратора сайта создан'))
            
            self.stdout.write(self.style.SUCCESS('\n✅ Администратор готов к использованию!'))
            self.stdout.write(self.style.WARNING('Данные для входа:'))
            self.stdout.write(self.style.WARNING('  Логин: admin'))
            self.stdout.write(self.style.WARNING('  Пароль: admin123'))

            if options['reset']:
                # Удаление старых данных
                BookAuthors.objects.all().delete()
                Inventory.objects.all().delete()
                Book.objects.all().delete()
                Category.objects.all().delete()
                Author.objects.all().delete()
                self.stdout.write(self.style.WARNING('Удалены старые данные'))

            # Создание категорий
            categories_data = [
                ('Роман', 'roman'),
                ('Фантастика', 'fantasy'),
                ('Детектив', 'detective'),
                ('Научная литература', 'science'),
                ('Историческая проза', 'history'),
                ('Биография', 'biography'),
                ('Поэзия', 'poetry'),
                ('Компьютерная литература', 'computers'),
            ]
            
            categories = {}
            for name, slug in categories_data:
                cat, _ = Category.objects.get_or_create(
                    slug=slug,
                    defaults={'name': name}
                )
                categories[name] = cat
            
            # Создание авторов
            authors_data = [
                ('Лев', 'Толстой'),
                ('Фёдор', 'Достоевский'),
                ('Антон', 'Чехов'),
                ('Александр', 'Пушкин'),
                ('Михаил', 'Булгаков'),
                ('Иван', 'Тургенев'),
                ('Николай', 'Гоголь'),
                ('Александр', 'Солженицын'),
                ('Джордж', 'Оруэлл'),
                ('Эрнест', 'Хемингуэй'),
                ('Джейн', 'Остин'),
                ('Чарльз', 'Диккенс'),
                ('Стивен', 'Кинг'),
                ('Джон', 'Р.Р. Толкин'),
                ('Рэй', 'Брэдбери'),
            ]
            
            authors = {}
            for first_name, last_name in authors_data:
                author, _ = Author.objects.get_or_create(
                    first_name=first_name,
                    last_name=last_name
                )
                authors[f"{first_name} {last_name}"] = author
            
            # Создание книг
            books_data = [
                {
                    'title': 'Война и мир',
                    'isbn': '978-5-17-100056-9',
                    'category': 'Роман',
                    'authors': ['Лев Толстой'],
                    'price': Decimal('899.00'),
                    'pages': 1274,
                    'description': 'Великое произведение мировой литературы о судьбах людей в период Отечественной войны 1812 года.',
                },
                {
                    'title': 'Преступление и наказание',
                    'isbn': '978-5-17-100141-2',
                    'category': 'Роман',
                    'authors': ['Фёдор Достоевский'],
                    'price': Decimal('349.00'),
                    'pages': 671,
                    'description': 'Философский роман о молодом студенте, совершившем преступление.',
                },
                {
                    'title': 'Мастер и Маргарита',
                    'isbn': '978-5-17-100789-5',
                    'category': 'Роман',
                    'authors': ['Михаил Булгаков'],
                    'price': Decimal('299.00'),
                    'pages': 512,
                    'description': 'Мистический роман о дьяволе и его визите в Москву.',
                },
                {
                    'title': 'Евгений Онегин',
                    'isbn': '978-5-17-100234-1',
                    'category': 'Поэзия',
                    'authors': ['Александр Пушкин'],
                    'price': Decimal('199.00'),
                    'pages': 256,
                    'description': 'Роман в стихах, вершина творчества Пушкина.',
                },
                {
                    'title': '1984',
                    'isbn': '978-5-17-101456-7',
                    'category': 'Фантастика',
                    'authors': ['Джордж Оруэлл'],
                    'price': Decimal('249.00'),
                    'pages': 318,
                    'description': 'Антиутопия о тоталитарном обществе будущего.',
                },
                {
                    'title': 'Старик и море',
                    'isbn': '978-5-17-100567-8',
                    'category': 'Роман',
                    'authors': ['Эрнест Хемингуэй'],
                    'price': Decimal('179.00'),
                    'pages': 128,
                    'description': 'Повесть о старом рыбаке и его борьбе с большой рыбой.',
                },
                {
                    'title': 'Гарри Поттер и философский камень',
                    'isbn': '978-5-17-101678-9',
                    'category': 'Фантастика',
                    'authors': ['Дж.К. Роулинг'],
                    'price': Decimal('599.00'),
                    'pages': 368,
                    'description': 'Первая книга о юном волшебнике Гарри Поттере.',
                },
                {
                    'title': 'Властелин колец: Братство кольца',
                    'isbn': '978-5-17-100789-6',
                    'category': 'Фантастика',
                    'authors': ['Джон Р.Р. Толкин'],
                    'price': Decimal('699.00'),
                    'pages': 544,
                    'description': 'Первая часть легендарной саги о Средиземье.',
                },
                {
                    'title': '451 градус по Фаренгейту',
                    'isbn': '978-5-17-101234-5',
                    'category': 'Фантастика',
                    'authors': ['Рэй Брэдбери'],
                    'price': Decimal('279.00'),
                    'pages': 256,
                    'description': 'Антиутопия о будущем, где книги запрещены и сжигаются.',
                },
                {
                    'title': 'Сияние',
                    'isbn': '978-5-17-101567-8',
                    'category': 'Детектив',
                    'authors': ['Стивен Кинг'],
                    'price': Decimal('399.00'),
                    'pages': 670,
                    'description': 'Ужасы в горном отеле, закрытом на зиму.',
                },
                {
                    'title': 'Пикник на обочине',
                    'isbn': '978-5-17-100123-4',
                    'category': 'Фантастика',
                    'authors': ['Аркадий Стругацкий', 'Борис Стругацкий'],
                    'price': Decimal('249.00'),
                    'pages': 256,
                    'description': 'Научно-фантастический роман о сталкерах в Зоне.',
                },
                {
                    'title': 'Алиса в Стране чудес',
                    'isbn': '978-5-17-101890-1',
                    'category': 'Роман',
                    'authors': ['Льюис Кэрролл'],
                    'price': Decimal('179.00'),
                    'pages': 128,
                    'description': 'Сказка о девочке Алисе и её удивительных приключениях.',
                },
            ]
            
            created_books = 0
            updated_books = 0
            
            for book_data in books_data:
                # Подготавливаем данные
                category_obj = categories.get(book_data['category'])
                if not category_obj:
                    continue
                
                # Создаем или обновляем книгу
                book, created = Book.objects.update_or_create(
                    isbn=book_data['isbn'],
                    defaults={
                        'title': book_data['title'],
                        'category': category_obj,
                        'price': book_data['price'],
                        'pages': book_data.get('pages'),
                        'description': book_data.get('description', ''),
                        'is_active': True,
                        'rating': Decimal(str(random.uniform(3.5, 5.0))).quantize(Decimal('0.01')),
                    }
                )
                
                # Добавляем авторов
                for author_name in book_data.get('authors', []):
                    if author_name in authors:
                        BookAuthors.objects.get_or_create(
                            book=book,
                            author=authors[author_name]
                        )
                    else:
                        # Если автора нет в списке, создаем его
                        name_parts = author_name.split(' ', 1)
                        if len(name_parts) == 2:
                            first_name, last_name = name_parts
                        else:
                            first_name, last_name = author_name, 'Unknown'
                        
                        author, _ = Author.objects.get_or_create(
                            first_name=first_name,
                            last_name=last_name
                        )
                        BookAuthors.objects.get_or_create(
                            book=book,
                            author=author
                        )
                
                # Создаем запись на складе
                Inventory.objects.get_or_create(
                    book=book,
                    defaults={
                        'stock': random.randint(10, 100),
                        'reserved': 0
                    }
                )
                
                if created:
                    created_books += 1
                else:
                    updated_books += 1
            
            self.stdout.write(self.style.SUCCESS(
                f'\nСоздано книг: {created_books}, обновлено: {updated_books}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'\nСоздано категорий: {len(categories_data)}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Создано авторов: {len(authors_data)}\n'
            ))
            
            self.stdout.write(self.style.SUCCESS('\n✅ База данных инициализирована!'))
            self.stdout.write(self.style.WARNING('\n📝 Данные для входа:'))
            self.stdout.write(self.style.WARNING('  Логин: admin'))
            self.stdout.write(self.style.WARNING('  Пароль: admin123'))

