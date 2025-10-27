FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gettext \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем Python зависимости
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . /app

# Создаем директории для статических файлов, медиа и логов
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Скрипты запуска
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY docker-entrypoint-celery.sh /app/docker-entrypoint-celery.sh
RUN chmod +x /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint-celery.sh

# Создаем пользователя для запуска приложения
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["/app/docker-entrypoint.sh"]


