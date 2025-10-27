#!/bin/bash
# Скрипт для применения SQL скриптов (VIEW, процедуры, триггеры) к PostgreSQL

set -e

# Переменные окружения
DB_NAME="${POSTGRES_DB:-bookstore}"
DB_USER="${POSTGRES_USER:-bookstore}"
DB_HOST="${POSTGRES_HOST:-localhost}"
DB_PORT="${POSTGRES_PORT:-5432}"
SQL_DIR="${SQL_DIR:-./backend/sql}"

echo "Deploying SQL scripts to database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo ""

# Проверяем существование директории
if [ ! -d "$SQL_DIR" ]; then
    echo "Error: SQL directory not found: $SQL_DIR"
    exit 1
fi

# Список скриптов в порядке выполнения
SCRIPTS=(
    "views.sql"
    "procedures.sql"
    "triggers.sql"
)

for script in "${SCRIPTS[@]}"; do
    script_path="$SQL_DIR/$script"
    
    if [ ! -f "$script_path" ]; then
        echo "Warning: Script not found: $script_path"
        continue
    fi
    
    echo "Applying: $script"
    PGPASSWORD="${POSTGRES_PASSWORD:-bookstore}" psql \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        -f "$script_path"
    
    if [ $? -eq 0 ]; then
        echo "  ✓ Successfully applied"
    else
        echo "  ✗ Failed to apply"
        exit 1
    fi
done

echo ""
echo "All SQL scripts applied successfully!"

