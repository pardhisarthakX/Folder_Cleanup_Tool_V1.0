# ============================================
# Folder Cleanup Tool - Makefile
# Common developer tasks
# ============================================

# --- Setup ---
.PHONY: install install-dev
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# --- Run ---
.PHONY: run ui
run:
	python -m folder_cleanup.main

ui:
	streamlit run src/folder_cleanup/ui.py

# --- Quality ---
.PHONY: lint format
lint:
	ruff check src/

format:
	ruff format src/

# --- Test ---
.PHONY: test test-cov
test:
	pytest -v

test-cov:
	pytest --cov=folder_cleanup --cov-report=term-missing --cov-report=html

# --- Docker ---
.PHONY: docker-build docker-up docker-down
docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

# --- Cleanup ---
.PHONY: clean
clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
