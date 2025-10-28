#!/bin/bash
set -e

# Ждем готовности базы данных
echo "Waiting for database..."
while ! python -c "import socket; socket.create_connection(('db', 5432))" 2>/dev/null; do
  sleep 1
done
echo "Database is ready!"

# Ждем готовности Redis
echo "Waiting for Redis..."
while ! python -c "import socket; socket.create_connection(('redis', 6379))" 2>/dev/null; do
  sleep 1
done
echo "Redis is ready!"

# Применяем миграции
echo "Running migrations..."
python manage.py migrate --noinput

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Создаем суперпользователя если не существует
echo "Creating superuser if not exists..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"

# Загружаем тестовые данные если база пустая (пропускаем если уже есть книги)
echo "Loading test data..."
python manage.py init_data

# Запускаем сервер
echo "Starting server..."
exec python manage.py runserver 0.0.0.0:8000
