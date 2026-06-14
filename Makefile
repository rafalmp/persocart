.PHONY: dev dev-build down logs migrate makemigrations superuser \
        test test-backend test-frontend lint lint-backend lint-frontend \
        typecheck format shell clean help

COMPOSE := docker compose

# ===========================================
# Development
# ===========================================
dev: ## Start the development stack
	$(COMPOSE) up

dev-build: ## Rebuild and start the development stack
	$(COMPOSE) up --build

down: ## Stop the stack
	$(COMPOSE) down

logs: ## Tail logs
	$(COMPOSE) logs -f

# ===========================================
# Database / Django
# ===========================================
migrate: ## Apply migrations
	$(COMPOSE) run --rm backend python manage.py migrate

makemigrations: ## Create migrations
	$(COMPOSE) run --rm backend python manage.py makemigrations

superuser: ## Create an operator superuser
	$(COMPOSE) run --rm backend python manage.py createsuperuser

shell: ## Open a Django shell
	$(COMPOSE) run --rm backend python manage.py shell

# ===========================================
# Testing
# ===========================================
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	$(COMPOSE) run --rm backend pytest

test-frontend: ## Run frontend tests
	$(COMPOSE) run --rm frontend bun run test

# ===========================================
# Code quality
# ===========================================
lint: lint-backend lint-frontend ## Lint everything

lint-backend: ## Ruff + mypy (backend)
	$(COMPOSE) run --rm backend sh -c "ruff check . && mypy ."

lint-frontend: ## Biome + tsc (frontend)
	$(COMPOSE) run --rm frontend sh -c "bun run lint && bun run typecheck"

typecheck: ## Type-check backend and frontend
	$(COMPOSE) run --rm backend mypy .
	$(COMPOSE) run --rm frontend bun run typecheck

format: ## Format code
	$(COMPOSE) run --rm backend ruff format .
	$(COMPOSE) run --rm frontend bun run format

# ===========================================
# Cleanup
# ===========================================
clean: ## Stop stack and remove volumes/artifacts
	$(COMPOSE) down -v
	rm -rf frontend/node_modules frontend/dist backend/staticfiles

# ===========================================
# Help
# ===========================================
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
