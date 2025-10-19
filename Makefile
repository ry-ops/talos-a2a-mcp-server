.PHONY: help install dev test lint format type-check clean run docker-build docker-run

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	uv sync

dev: ## Install development dependencies
	uv sync --all-extras

test: ## Run tests
	uv run pytest

test-cov: ## Run tests with coverage
	uv run pytest --cov=src --cov-report=html --cov-report=term

lint: ## Run linter
	uv run ruff check .

lint-fix: ## Run linter and fix issues
	uv run ruff check --fix .

format: ## Format code
	uv run ruff format .

format-check: ## Check code formatting
	uv run ruff format --check .

type-check: ## Run type checker
	uv run mypy src

check: lint format-check type-check test ## Run all checks

clean: ## Clean up build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run: ## Run the MCP server
	uv run talos-mcp-server

build: ## Build distribution packages
	uv build

docker-build: ## Build Docker image
	docker build -t talos-mcp-server:latest .

docker-run: ## Run Docker container
	docker-compose up -d

docker-stop: ## Stop Docker container
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

setup: ## Run setup script
	./setup.sh

# Development workflow
.PHONY: watch
watch: ## Watch for changes and run tests
	uv run pytest-watch
