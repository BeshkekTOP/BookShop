# Bookstore (Django + DRF + PostgreSQL)

Production-ready course project: online bookstore with auth/roles, catalog, cart/orders, reviews, analytics, admin, docs, tests, Docker.

## Quick start (Docker)

1. Copy env and adjust values:
```bash
cp .env.example .env
```
2. Start services:
```bash
docker compose up -d --build
```
3. Apply migrations and create superuser:
```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```
4. Open API docs: http://localhost:8000/api/docs/

## Stack
- Python 3.11
- Django 4.2
- DRF, JWT
- PostgreSQL 15
- Redis (cache), Celery (tasks), Channels (WebSocket)

## Project layout
```
bookstore/
  docker-compose.yml
  Dockerfile
  requirements.txt
  manage.py
  .env.example
  backend/
    settings/
    apps/
    api/
```


