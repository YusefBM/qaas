setup-env: refresh-env-files stop build migrate create-super-user stop  ## Complete Django app setup (environment, build, migrate, superuser)
refresh-env: stop soft-clean-env setup-env  ## Refresh environment and rebuild everything

soft-clean-env:  ## Remove containers and volumes (keeps images)
	@echo 'Removing containers and volumes (images will not be erased)...'
	@docker compose down --volumes

refresh-env-files:  ## Refresh .env file from .env.example template
	@echo 'Refreshing .env from .env.example ...'
	@cp .env.example .env
	@grep SECRET_KEY secrets.env >> .env
	@echo 'Done!'


generate-migrations:  ## Generate Django database migrations (use app=<name> for specific app)
	@echo 'Generating database migrations ...'
	@docker compose run --rm api python manage.py makemigrations $(app)

migrate:  ## Run Django database migrations (use app=<name> migration=<number> for specific migration)
	@if [ -n "$(migration)" ] && [ -z "$(app)" ]; then \
		echo "Error: 'app' must be specified when 'migration' is provided."; \
		exit 1; \
	fi
	@echo 'Migrating database ...'
	@docker compose run --rm api python manage.py migrate $(app) $(migration)

create-super-user:  ## Create Django superuser for admin access
	@echo 'Creating superuser ...'
	@docker compose run --rm api python manage.py createsuperuser

build:  ## Build all Docker images
	@echo 'Building images ...'
	@docker compose build

run:  ## Start all application containers in background
	@echo 'Running containers ...'
	@docker compose up -d

stop:  ## Stop all running containers
	@echo 'Stopping containers ...'
	@docker compose down

restart: stop run  ## Restart all containers (stop + run)

shell:  ## Access Django shell with shell_plus extensions
	@echo 'Starting shell ...'
	@docker compose run --rm api python src/manage.py shell_plus

test:  ## Run all Django tests
	@echo 'Running all tests ...'
	@docker compose exec api python manage.py test

# Code Quality Commands
lint-flake8:  ## Run flake8 linter to check code style and quality
	@echo 'Running flake8 linter ...'
	@docker compose run --rm api flake8 . --max-line-length=120 --exclude=migrations,venv,env,.git,__pycache__,.pytest_cache

lint-black:  ## Run black formatter in check mode (shows what would be reformatted)
	@echo 'Running black formatter (check mode) ...'
	@docker compose run --rm api black --check --diff . --exclude="/(migrations|venv|env|\.git|__pycache__|\.pytest_cache)/"

format-black:  ## Run black formatter to automatically format code
	@echo 'Running black formatter (apply changes) ...'
	@docker compose run --rm api black . --exclude="/(migrations|venv|env|\.git|__pycache__|\.pytest_cache)/"

lint:  ## Run all linting checks (flake8 + black check)
lint: lint-flake8 lint-black
	@echo 'All linting checks completed!'

format:  ## Format code automatically using black
format: format-black
	@echo 'Code formatting completed!'

# Celery Commands
celery-worker:  ## Start Celery worker for background tasks
	@echo 'Starting Celery worker ...'
	@docker compose run --rm api celery -A config worker --loglevel=info

celery-beat:  ## Start Celery beat scheduler
	@echo 'Starting Celery beat scheduler ...'
	@docker compose run --rm api celery -A config beat --loglevel=info

celery-flower:  ## Start Celery Flower monitoring tool
	@echo 'Starting Celery Flower monitoring ...'
	@docker compose run --rm -p 5555:5555 api celery -A config flower

help:  ## Show this help message
	@echo 'Available commands:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'