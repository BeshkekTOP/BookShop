#!/bin/bash
# Скрипт для восстановления PostgreSQL базы данных из бэкапа

set -e

# Переменные окружения
DB_NAME="${POSTGRES_DB:-bookstore}"
DB_USER="${POSTGRES_USER:-bookstore}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
BACKUP_DIR="${BACKUP_DIR:-./backups}"

# Проверяем аргументы
if [ $# -eq 0 ]; then
    echo "Usage: $0 <backup_file>"
    echo ""
    echo "Available backups:"
    ls -1 "$BACKUP_DIR"/bookstore_backup_*.sql.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Проверяем существование файла
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Restoring database from: $BACKUP_FILE"
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "User: $DB_USER"
echo ""
echo "WARNING: This will overwrite the existing database!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Распаковываем если сжат
if [[ "$BACKUP_FILE" == *.gz ]]; then
    echo "Decompressing backup..."
    gunzip -c "$BACKUP_FILE" > "$BACKUP_DIR/restore_temp.sql"
    BACKUP_FILE="$BACKUP_DIR/restore_temp.sql"
fi

# Останавливаем приложение (опционально)
echo "Stopping application..."

# Восстанавливаем бэкап
echo "Restoring database..."
PGPASSWORD="${POSTGRES_PASSWORD:-bookstore}" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d postgres \
    -c "SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '$DB_NAME' AND pid <> pg_backend_pid();" 2>/dev/null || true

# Удаляем и пересоздаем базу
echo "Recreating database..."
PGPASSWORD="${POSTGRES_PASSWORD:-bookstore}" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d postgres \
    -c "DROP DATABASE IF EXISTS $DB_NAME;" || true

PGPASSWORD="${POSTGRES_PASSWORD:-bookstore}" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d postgres \
    -c "CREATE DATABASE $DB_NAME;"

# Восстанавливаем данные
echo "Loading data..."
PGPASSWORD="${POSTGRES_PASSWORD:-bookstore}" psql \
    -h "$DB_HOST" \
    -p "$DB_PORT" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    < "$BACKUP_FILE"

# Удаляем временный файл
if [ -f "$BACKUP_DIR/restore_temp.sql" ]; then
    rm "$BACKUP_DIR/restore_temp.sql"
fi

echo "Database restored successfully!"
echo ""
echo "Please restart the application:"
echo "  docker-compose restart web"

