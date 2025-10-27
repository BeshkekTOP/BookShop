# Скрипт для резервного копирования PostgreSQL базы данных (Windows PowerShell)

$ErrorActionPreference = "Stop"

# Переменные окружения
$DB_NAME = $env:POSTGRES_DB
if (-not $DB_NAME) { $DB_NAME = "bookstore" }
$DB_USER = $env:POSTGRES_USER
if (-not $DB_USER) { $DB_USER = "bookstore" }
$DB_HOST = $env:POSTGRES_HOST
if (-not $DB_HOST) { $DB_HOST = "localhost" }
$DB_PORT = $env:POSTGRES_PORT
if (-not $DB_PORT) { $DB_PORT = "5432" }
$DB_PASSWORD = $env:POSTGRES_PASSWORD
if (-not $DB_PASSWORD) { $DB_PASSWORD = "bookstore" }

$BACKUP_DIR = "./backups"
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "$BACKUP_DIR/bookstore_backup_$TIMESTAMP.sql"

# Создаем директорию для бэкапов
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR
}

Write-Host "Starting database backup..."
Write-Host "Database: $DB_NAME"
Write-Host "Output: $BACKUP_FILE"
Write-Host ""

# Создаем бэкап через docker exec (если используем Docker)
if (Test-Path "docker-compose.yml") {
    Write-Host "Using Docker for backup..."
    docker exec bookstore_db pg_dump -U $DB_USER -d $DB_NAME > $BACKUP_FILE
} else {
    # Прямое подключение к PostgreSQL
    $env:PGPASSWORD = $DB_PASSWORD
    & pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -F p -v > $BACKUP_FILE
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backup completed successfully!"
    Write-Host "File: $BACKUP_FILE"
    $size = (Get-Item $BACKUP_FILE).Length / 1MB
    Write-Host "Size: $([math]::Round($size, 2)) MB"
} else {
    Write-Host "Backup failed!" -ForegroundColor Red
    exit 1
}

# Показываем список бэкапов
Write-Host ""
Write-Host "Available backups:"
Get-ChildItem "$BACKUP_DIR/bookstore_backup_*.sql" | Sort-Object LastWriteTime -Descending

