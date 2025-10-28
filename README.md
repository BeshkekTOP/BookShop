# Книжный магазин - BookShop

Полнофункциональная система управления книжным магазином с ролевой моделью доступа, аналитикой, импорт/экспортом данных и расширенной документацией.

## 🚀 Быстрый старт

### Docker (рекомендуется)

```bash
# 1. Клонируйте репозиторий
git clone <repository-url>
cd BookShop

# 2. Запустите контейнеры
docker-compose up -d --build

# 3. Примените миграции и создайте суперпользователя
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

# 4. Примените SQL скрипты (VIEW, процедуры, триггеры)
docker-compose exec db bash scripts/deploy_sql.sh

# 5. Соберите статические файлы
docker-compose exec web python manage.py collectstatic --noinput

# 6. Откройте в браузере
# http://localhost - Веб-интерфейс
# http://localhost:8000 - Django напрямую
# http://localhost:8000/api/docs/ - API документация
# http://localhost:8000/admin/ - Админ-панель
```

### Локальная установка (без Docker)

```bash
# 1. Установите зависимости
pip install -r requirements.txt

# 2. Настройте PostgreSQL и создайте базу данных
createdb bookstore

# 3. Настройте переменные окружения
cp .env.example .env
# Отредактируйте .env

# 4. Примените миграции
python manage.py migrate

# 5. Создайте суперпользователя
python manage.py createsuperuser

# 6. Примените SQL скрипты
psql -d bookstore -f backend/sql/views.sql
psql -d bookstore -f backend/sql/procedures.sql
psql -d bookstore -f backend/sql/triggers.sql

# 7. Запустите сервер
python manage.py runserver
```

## 📋 Возможности системы

### 1. Роли и права доступа

Система поддерживает 4 роли:

- **Гость** - Просмотр каталога, поиск книг, регистрация
- **Покупатель** - Добавление в корзину, оформление заказов, отзывы
- **Менеджер** - Управление заказами, изменение статусов, отчеты
- **Администратор** - Полный доступ ко всем функциям

### 2. База данных

- **17+ таблиц** с полной нормализацией до 3НФ
- **5 представлений (VIEW)** для аналитики:
  - `v_book_sales_stats` - статистика продаж по книгам
  - `v_category_revenue` - доход по категориям
  - `v_user_purchase_history` - история покупок
  - `v_top_selling_books` - топ продаваемых книг
  - `v_user_statistics` - статистика пользователей
- **5 хранимых процедур** для бизнес-логики
- **5 триггеров** для автоматизации и аудита

### 3. Безопасность

- Хеширование паролей (bcrypt)
- JWT аутентификация
- Ролевая модель доступа (RBAC)
- Расширенная система аудита (до/после изменений)
- Защита от SQL-инъекций и XSS

### 4. Импорт/экспорт данных

```bash
# Экспорт книг в CSV
python manage.py export_books --output my_books.csv

# Импорт книг из CSV
python manage.py import_books my_books.csv --skip-header
```

### 5. Резервное копирование

```bash
# Windows PowerShell
./scripts/backup_db.ps1

# Linux/Mac
./scripts/backup_db.sh

# Восстановление
./scripts/restore_db.ps1 backups/bookstore_backup_20250101_120000.sql
```

### 6. Горячие клавиши

- `Alt+H` - Главная страница
- `Alt+C` - Каталог
- `Alt+B` - Корзина
- `Alt+S` - Поиск
- `Alt+P` - Профиль
- `Alt+L` - Вход/Выход
- `Ctrl+K` - Показать справку
- `Escape` - Закрыть окно

### 7. Адаптивный дизайн

- **Мобильные** (до 640px) - одноколоночная верстка
- **Планшеты** (641px-1024px) - 2-3 колонки
- **Десктопы** (1025px+) - полная версия

## 🛠 Технологический стек

- **Backend**: Python 3.11, Django 4.2, Django REST Framework
- **База данных**: PostgreSQL 15
- **Кэш/Очереди**: Redis, Celery
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Веб-сервер**: Nginx, uWSGI
- **Контейнеризация**: Docker, Docker Compose

## 📁 Структура проекта

```
BookShop/
├── backend/
│   ├── apps/           # Django приложения
│   │   ├── catalog/    # Каталог книг
│   │   ├── orders/     # Заказы и корзина
│   │   ├── users/      # Пользователи
│   │   ├── reviews/    # Отзывы
│   │   ├── analytics/  # Аналитика
│   │   └── core/       # Ядро системы (аудит, роли)
│   ├── sql/           # SQL скрипты
│   │   ├── views.sql
│   │   ├── procedures.sql
│   │   └── triggers.sql
│   └── api/           # API endpoints
├── static/            # Статические файлы
│   ├── styles.css
│   └── keyboard.js
├── templates/         # HTML шаблоны
├── scripts/           # Утилиты
│   ├── backup_db.ps1
│   └── restore_db.ps1
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## 📊 API Endpoints

Основные эндпоинты API:

- `GET /api/books/` - Список книг
- `GET /api/books/{id}/` - Детали книги
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход
- `GET /api/cart/` - Корзина
- `POST /api/orders/` - Создать заказ
- `GET /api/analytics/sales/` - Статистика продаж

Полная документация: http://localhost:8000/api/docs/

## 🔧 Управление системой

### Создание резервной копии

```bash
docker-compose exec web python manage.py dumpdata > backup.json
```

### Применение SQL скриптов

```bash
docker-compose exec db psql -U bookstore -d bookstore -f /path/to/views.sql
```

### Доступ к Python shell

```bash
docker-compose exec web python manage.py shell
```

### Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Только web
docker-compose logs -f web

# Только БД
docker-compose logs -f db
```

## 👥 Авторизация

По умолчанию создан суперпользователь:
- Username: `admin`
- Password: `admin123`

**Важно**: Измените пароль после первого входа!

## 📚 Документация

- [Архитектура системы](docs/architecture.md)
- [API спецификация](docs/api.md)
- [Руководство пользователя](docs/user_guide.md)
- [Разработка и тестирование](docs/development.md)

## ✅ Соответствие ТЗ

Проект полностью соответствует требованиям:

✅ **База данных**: 17+ таблиц, нормализация 3НФ, VIEW, процедуры, триггеры  
✅ **Безопасность**: RBAC, аудит, хеширование паролей  
✅ **CRUD**: Полный CRUD через API и веб-интерфейс  
✅ **Импорт/экспорт**: CSV формат  
✅ **Аналитика**: Представления, статистика, отчеты  
✅ **Резервирование**: Скрипты бэкапа и восстановления  
✅ **Документация**: README, API docs, комментарии  
✅ **Тестирование**: Тестовые данные и сценарии  

## 🤝 Разработка

### Запуск тестов

```bash
docker-compose exec web python manage.py test
```

### Линтинг

```bash
docker-compose exec web flake8 backend/
docker-compose exec web black backend/
```

## 📝 Лицензия

Educational project - используйте для обучения


