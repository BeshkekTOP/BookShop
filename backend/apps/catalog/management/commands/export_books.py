from django.core.management.base import BaseCommand
from backend.apps.catalog.models import Book, Category, Author
import csv
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Экспорт книг в CSV файл'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='books_export.csv',
            help='Имя выходного CSV файла'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        
        # Создаем директорию exports если её нет
        output_dir = Path('exports')
        output_dir.mkdir(exist_ok=True)
        
        file_path = output_dir / output_file
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Заголовки
            writer.writerow([
                'ID', 'Title', 'ISBN', 'Category', 'Authors', 'Price', 
                'Rating', 'Pages', 'Publication Date', 'Active', 
                'Stock', 'Reserved'
            ])
            
            # Данные
            books = Book.objects.select_related('category').prefetch_related('book_authors__author').all()
            for book in books:
                authors = ', '.join([str(a.author) for a in book.book_authors.all()])
                
                # Получаем данные об инвентаре
                try:
                    inventory = book.inventory
                    stock = inventory.stock
                    reserved = inventory.reserved
                except:
                    stock = 0
                    reserved = 0
                
                writer.writerow([
                    book.id,
                    book.title,
                    book.isbn,
                    book.category.name if book.category else '',
                    authors,
                    book.price,
                    book.rating,
                    book.pages or '',
                    book.publication_date or '',
                    book.is_active,
                    stock,
                    reserved
                ])
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully exported {books.count()} books to {file_path}')
        )


