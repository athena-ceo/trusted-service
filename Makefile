# Makefile for Trusted Services
# Provides convenient shortcuts for common development tasks

.PHONY: help install test lint clean docker

# Default target
help:
	@echo "Trusted Services - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install all dependencies"
	@echo "  make install-backend  Install Python dependencies"
	@echo "  make install-frontend Install Node.js dependencies"
	@echo "  make install-tests    Install test dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-unit        Run unit tests"
	@echo "  make test-smoke       Run smoke tests"
	@echo "  make test-integration Run integration tests"
	@echo "  make test-backend     Run backend smoke tests only"
	@echo "  make test-frontend    Run frontend smoke tests only"
	@echo "  make test-watch       Run tests in watch mode"
	@echo "  make coverage         Generate coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run all linters"
	@echo "  make lint-backend     Lint Python code"
	@echo "  make lint-frontend    Lint TypeScript code"
	@echo "  make format           Format all code"
	@echo "  make format-backend   Format Python code"
	@echo "  make security         Run security checks"
	@echo ""
	@echo "Development:"
	@echo "  make dev              Start all services in dev mode"
	@echo "  make dev-backend      Start backend only"
	@echo "  make dev-frontend     Start frontend only"
	@echo "  make build            Build all components"
	@echo "  make build-frontend   Build frontend"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker images"
	@echo "  make docker-up        Start services with Docker Compose"
	@echo "  make docker-down      Stop Docker services"
	@echo "  make docker-logs      Show Docker logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Clean build artifacts"
	@echo "  make clean-cache      Clean Python cache files"
	@echo "  make clean-test       Clean test artifacts"

# ============================================================================
# Installation
# ============================================================================

install: install-backend install-frontend install-tests
	@echo "✓ All dependencies installed"

install-backend:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt

install-frontend:
	@echo "Installing frontend dependencies..."
	cd apps/delphes/frontend && npm install

install-tests:
	@echo "Installing test dependencies..."
	pip install -r tests/requirements.txt
	playwright install chromium

# ============================================================================
# Testing
# ============================================================================

test:
	@echo "Running all tests..."
	python run_tests.py all

test-unit:
	@echo "Running unit tests..."
	python run_tests.py unit

test-smoke:
	@echo "Running smoke tests..."
	python run_tests.py smoke

test-integration:
	@echo "Running integration tests..."
	python run_tests.py integration

test-backend:
	@echo "Running backend smoke tests..."
	python run_tests.py smoke --backend

test-frontend:
	@echo "Running frontend smoke tests..."
	python run_tests.py smoke --frontend

test-watch:
	@echo "Running tests in watch mode..."
	pytest-watch tests/unit/

coverage:
	@echo "Generating coverage report..."
	pytest tests/unit/ --cov=src --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

# ============================================================================
# Code Quality
# ============================================================================

lint: lint-backend lint-frontend
	@echo "✓ Linting complete"

lint-backend:
	@echo "Linting Python code..."
	ruff check src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/
	mypy src/

lint-frontend:
	@echo "Linting TypeScript code..."
	cd apps/delphes/frontend && npm run lint

format: format-backend
	@echo "✓ Code formatted"

format-backend:
	@echo "Formatting Python code..."
	black src/ tests/
	isort src/ tests/

security:
	@echo "Running security checks..."
	bandit -r src/ -f json -o bandit-report.json || true
	safety check
	@echo "Security reports generated"

# ============================================================================
# Development
# ============================================================================

dev:
	@echo "Starting all services..."
	@echo "Backend: http://localhost:8002"
	@echo "Frontend: http://localhost:3000"
	@echo "Press Ctrl+C to stop"
	@make -j2 dev-backend dev-frontend

dev-backend:
	@echo "Starting backend server..."
	python launcher_api.py ./runtime

dev-frontend:
	@echo "Starting frontend development server..."
	cd apps/delphes/frontend && npm run dev

build: build-frontend
	@echo "✓ Build complete"

build-frontend:
	@echo "Building frontend..."
	cd apps/delphes/frontend && npm run build

# ============================================================================
# Docker
# ============================================================================

docker-build:
	@echo "Building Docker images..."
	docker compose -f docker-compose.dev.yml build

docker-up:
	@echo "Starting services with Docker Compose..."
	docker compose -f docker-compose.dev.yml up -d
	@echo "Services started:"
	@echo "  Backend: http://localhost:8002"
	@echo "  Frontend: http://localhost:3000"

docker-down:
	@echo "Stopping Docker services..."
	docker compose -f docker-compose.dev.yml down

docker-logs:
	docker compose -f docker-compose.dev.yml logs -f

docker-clean:
	@echo "Cleaning Docker resources..."
	docker compose -f docker-compose.dev.yml down -v
	docker system prune -f

# ============================================================================
# Cleanup
# ============================================================================

clean: clean-cache clean-test
	@echo "Cleaning build artifacts..."
	rm -rf apps/delphes/frontend/.next
	rm -rf apps/delphes/frontend/out
	rm -rf dist/
	rm -rf build/
	@echo "✓ Cleaned"

clean-cache:
	@echo "Cleaning Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

clean-test:
	@echo "Cleaning test artifacts..."
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf test-results/
	rm -rf playwright-report/
	rm -f backend.log frontend.log
	rm -f .backend.pid .frontend.pid

# ============================================================================
# CI/CD Simulation
# ============================================================================

ci-backend:
	@echo "Simulating backend CI pipeline..."
	make lint-backend
	make test-unit
	make test-backend

ci-frontend:
	@echo "Simulating frontend CI pipeline..."
	make lint-frontend
	make build-frontend

ci-all:
	@echo "Simulating full CI pipeline..."
	make lint
	make test
	make build

# ============================================================================
# Database (if needed)
# ============================================================================

db-reset:
	@echo "Resetting database..."
	# Add your database reset commands here

# ============================================================================
# Utilities
# ============================================================================

check-ports:
	@echo "Checking if required ports are available..."
	@lsof -i :8002 && echo "Port 8002 is in use" || echo "Port 8002 is free"
	@lsof -i :3000 && echo "Port 3000 is in use" || echo "Port 3000 is free"

kill-servers:
	@echo "Killing servers on ports 8002 and 3000..."
	@lsof -ti :8002 | xargs kill -9 2>/dev/null || echo "No process on 8002"
	@lsof -ti :3000 | xargs kill -9 2>/dev/null || echo "No process on 3000"

version:
	@echo "Trusted Services Version Information"
	@python --version
	@node --version
	@npm --version
	@echo "pytest: $$(pytest --version | head -1)"

