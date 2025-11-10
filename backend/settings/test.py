from .base import *  # noqa

# Использование SQLite для тестов (быстрее чем PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Упрощенный хэшер паролей для ускорения тестов
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Отключение логирования в тестах (опционально)
# LOGGING_CONFIG = None



