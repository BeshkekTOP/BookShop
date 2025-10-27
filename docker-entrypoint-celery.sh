#!/bin/bash
set -e

# Wait for database
echo "Waiting for database..."
while ! python -c "import socket; socket.create_connection(('db', 5432))" 2>/dev/null; do
  sleep 1
done
echo "Database is ready!"

# Wait for Redis
echo "Waiting for Redis..."
while ! python -c "import socket; socket.create_connection(('redis', 6379))" 2>/dev/null; do
  sleep 1
done
echo "Redis is ready!"

# Start Celery worker
echo "Starting Celery worker..."
exec celery -A backend worker -l info
