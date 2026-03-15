.PHONY: build run install migrate test lint ci clean docker-build docker-up docker-down docker-logs docker-ps

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
FLASK := $(VENV)/bin/flask

# Build: create venv and install dependencies
build:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

# Lint: run static checks (requires build first)
lint:
	$(VENV)/bin/ruff check app run.py tests conftest.py
	$(VENV)/bin/ruff format --check app run.py tests conftest.py

# Test: run unit tests (requires build first)
test:
	$(VENV)/bin/pytest tests/ -v

# CI: run all stages in order (build → lint → test)
ci: build
	$(MAKE) lint
	$(MAKE) test

# Install deps only (assumes venv exists)
install:
	$(PIP) install -r requirements.txt

# Run migrations
migrate:
	$(FLASK) db upgrade

# Run the REST API locally
run:
	FLASK_APP=run:app $(FLASK) run --debug

# Alternative: run with python (same app)
run-python:
	$(PYTHON) run.py

# Clean venv and cache
clean:
	rm -rf $(VENV)
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name migrations -exec rm -rf {} + 2>/dev/null || true

# Docker: build images
docker-build:
	docker compose build

# Docker: start app + DB in background
docker-up:
	docker compose up -d

# Docker: stop and remove containers
docker-down:
	docker compose down

# Docker: follow app logs
docker-logs:
	docker compose logs -f app

# Docker: list running containers
docker-ps:
	docker compose ps
