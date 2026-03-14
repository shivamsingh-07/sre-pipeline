.PHONY: build run install migrate test clean

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
FLASK := $(VENV)/bin/flask

# Build: create venv and install dependencies
build:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	$(FLASK) db upgrade 2>/dev/null || true

# Install deps only (assumes venv exists)
install:
	$(PIP) install -r requirements.txt

# Run migrations
migrate:
	$(FLASK) db upgrade

# Run unit tests
test:
	$(VENV)/bin/pytest tests/ -v

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
