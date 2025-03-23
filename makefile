# Определяем переменные
DOCKER_COMPOSE = docker-compose
SERVICE_WEB = web
SERVICE_DB = db

# Команды
.PHONY: build up down migrate

# Сборка контейнеров
build:
	$(DOCKER_COMPOSE) build

# Запуск контейнеров в фоновом режиме
up:
	$(DOCKER_COMPOSE) up 

# Остановка контейнеров
down:
	$(DOCKER_COMPOSE) down

# Выполнение миграций Alembic
migrate:
	docker-compose exec web poetry run alembic upgrade head


start: build up migrate