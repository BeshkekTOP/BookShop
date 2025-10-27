#!/bin/bash
# Скрипт для резервного копирования PostgreSQL базы данных

set -e

# Переменные окружения
DB_NAME="${POSTGRES_DB:-bookstore}"
DB_USER="${POSTGRES_USER:-bookstore}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/bookstore_backup_$TIMESTAMP.sql"
BACKUP_FILE_COMPRESSED="$BACKUP_FILE.gz"

# Создаем директорию для бэкапов
mkdir -p "$BACKUP_DIR"

echo "Starting database backup..."
echo "Database: $DB_NAME"
echo "Output: $BACKUP_FILE"

# Создаем бэкап
PGPASSWORD="${POSTGRES_PASSWORD:-bookstore}" pg_dump \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    -F p \
    --verbose \
    --no-password \
    > "$BACKUP_FILE"

# Сжимаем бэкап
echo "Compressing backup..."
gzip "$BACKUP_FILE"

# Удаляем старые бэкапы (храним последние 7 дней)
echo "Cleaning old backups (older than 7 days)..."
find "$BACKUP_DIR" -name "bookstore_backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed successfully!"
echo "File: $BACKUP_FILE_COMPRESSED"
echo "Size: $(du -h "$BACKUP_FILE_COMPRESSED" | cut -f1)"

# Показываем список бэкапов
echo ""
echo "Available backups:"
ls -lh "$BACKUP_DIR"/bookstore_backup_*.sql.gz 2>/dev/null || echo "No backups found"

