"""Команда для добавления placeholder изображений к книгам"""
from django.core.management.base import BaseCommand
from backend.apps.catalog.models import Book
from django.core.files.base import ContentFile
import requests
from io import BytesIO


class Command(BaseCommand):
    help = 'Добавляет placeholder изображения к книгам без фото'

    def handle(self, *args, **options):
        books = Book.objects.filter(cover_image='')
        
        if not books.exists():
            self.stdout.write(self.style.SUCCESS('Все книги уже имеют изображения!'))
            return
        
        self.stdout.write(f'Найдено {books.count()} книг без изображений')
        
        for book in books:
            try:
                # Используем Lorem Picsum для placeholder изображений
                # Размер 400x600 (стандартное соотношение обложки книги)
                image_url = f"https://picsum.photos/400/600?random={book.id}"
                
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = BytesIO(response.content)
                    filename = f"book_{book.id}.jpg"
                    book.cover_image.save(
                        filename,
                        ContentFile(image_data.read()),
                        save=True
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ Изображение добавлено к "{book.title}"')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Не удалось загрузить изображение для "{book.title}"')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Ошибка для "{book.title}": {str(e)}')
                )
        
        self.stdout.write(self.style.SUCCESS('\nГотово! Изображения добавлены.'))
        self.stdout.write(
            self.style.WARNING(
                '\n⚠️  Это тестовые изображения! Замените их на реальные обложки через админ-панель.'
            )
        )

