from django.core.management.base import BaseCommand
from backend.apps.catalog.models import Book, Category, Author, BookAuthors
from pathlib import Path
import csv


class Command(BaseCommand):
    help = 'Импорт книг из CSV файла'

    def add_arguments(self, parser):
        parser.add_argument(
            'input_file',
            type=str,
            help='Путь к CSV файлу для импорта'
        )
        parser.add_argument(
            '--skip-header',
            action='store_true',
            help='Пропустить первую строку (заголовок)'
        )

    def handle(self, *args, **options):
        input_file = options['input_file']
        skip_header = options['skip_header']
        
        if not Path(input_file).exists():
            self.stdout.write(self.style.ERROR(f'File not found: {input_file}'))
            return
        
        created_count = 0
        updated_count = 0
        errors = []
        
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            
            if skip_header:
                next(reader, None)  # Пропускаем заголовок
            
            for row_num, row in enumerate(reader, start=1):
                try:
                    if len(row) < 11:
                        errors.append(f'Row {row_num}: Not enough columns')
                        continue
                    
                    isbn = row[2].strip()
                    if not isbn:
                        errors.append(f'Row {row_num}: ISBN is required')
                        continue
                    
                    # Получаем или создаем категорию
                    category_name = row[3].strip()
                    if category_name:
                        category, _ = Category.objects.get_or_create(
                            name=category_name,
                            defaults={'slug': category_name.lower().replace(' ', '-')}
                        )
                    else:
                        category = None
                    
                    # Создаем или обновляем книгу
                    book, created = Book.objects.update_or_create(
                        isbn=isbn,
                        defaults={
                            'title': row[1].strip(),
                            'category': category,
                            'price': float(row[5]) if row[5] else 0,
                            'rating': float(row[6]) if row[6] else 0,
                            'pages': int(row[7]) if row[7] else None,
                            'is_active': row[9].strip().lower() in ['true', '1', 'yes'],
                            'description': '',
                        }
                    )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                    
                    # Обрабатываем авторов
                    authors_str = row[4].strip()
                    if authors_str:
                        BookAuthors.objects.filter(book=book).delete()
                        for author_name in authors_str.split(','):
                            author_name = author_name.strip()
                            if author_name:
                                names = author_name.split(' ', 1)
                                if len(names) == 2:
                                    first_name, last_name = names[0], names[1]
                                else:
                                    first_name, last_name = author_name, ''
                                
                                author, _ = Author.objects.get_or_create(
                                    first_name=first_name,
                                    last_name=last_name
                                )
                                BookAuthors.objects.create(book=book, author=author)
                    
                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(
            f'Import completed: {created_count} created, {updated_count} updated'
        ))
        
        if errors:
            self.stdout.write(self.style.ERROR(f'Errors ({len(errors)}):'))
            for error in errors[:10]:  # Показываем первые 10 ошибок
                self.stdout.write(self.style.ERROR(f'  {error}'))


