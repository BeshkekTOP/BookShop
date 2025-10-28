# Makefile для управления Docker контейнерами

.PHONY: help build up down restart logs shell migrate createsuperuser test clean

# Показать справку
help:
	@echo "Доступные команды:"
	@echo "  build          - Собрать Docker образы"
	@echo "  up             - Запустить все сервисы (продакшен)"
	@echo "  up-dev         - Запустить все сервисы (разработка)"
	@echo "  down           - Остановить все сервисы"
	@echo "  restart        - Перезапустить все сервисы"
	@echo "  logs           - Показать логи всех сервисов"
	@echo "  logs-web       - Показать логи веб-сервиса"
	@echo "  shell          - Подключиться к веб-контейнеру"
	@echo "  migrate        - Применить миграции"
	@echo "  createsuperuser - Создать суперпользователя"
	@echo "  test           - Запустить тесты"
	@echo "  clean          - Очистить все контейнеры и образы"

# Собрать образы
build:
	docker-compose build

# Запустить продакшен
up:
	docker-compose up -d

# Запустить разработку
up-dev:
	docker-compose -f docker-compose.dev.yml up -d

# Остановить сервисы
down:
	docker-compose down
	docker-compose -f docker-compose.dev.yml down

# Перезапустить сервисы
restart: down up

# Показать логи
logs:
	docker-compose logs -f

# Показать логи веб-сервиса
logs-web:
	docker-compose logs -f web

# Подключиться к веб-контейнеру
shell:
	docker-compose exec web bash

# Применить миграции
migrate:
	docker-compose exec web python manage.py migrate

# Создать суперпользователя
createsuperuser:
	docker-compose exec web python manage.py createsuperuser

# Запустить тесты
test:
	docker-compose exec web python manage.py test

# Очистить все
clean:
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f
	docker volume prune -f













