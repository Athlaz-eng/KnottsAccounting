# Knotts Accounting Makefile
# Common commands for development and deployment

.PHONY: help install test lint format clean docker-build docker-run docker-stop

# Default target
help:
	@echo "Knotts Accounting - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install     - Install dependencies"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  clean       - Clean cache and temporary files"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run with Docker Compose"
	@echo "  docker-stop  - Stop Docker services"
	@echo ""
	@echo "Database:"
	@echo "  db-init     - Initialize database"
	@echo "  db-migrate  - Run database migrations"
	@echo "  db-reset    - Reset database"
	@echo ""
	@echo "Setup:"
	@echo "  setup       - Complete project setup"
	@echo "  setup-dev   - Development environment setup"

# Development commands
install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -e .[dev]

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src --cov-report=html

lint:
	@echo "Running linting..."
	flake8 src/ tests/
	mypy src/

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/

clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/ dist/ .coverage htmlcov/

# Docker commands
docker-build:
	@echo "Building Docker image..."
	docker build -t knotts-accounting .

docker-run:
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

docker-stop:
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "Showing Docker logs..."
	docker-compose logs -f

# Database commands
db-init:
	@echo "Initializing database..."
	python -c "from src.core.database import init_db; init_db()"

db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head

db-reset:
	@echo "Resetting database..."
	rm -f knotts_accounting.db
	python -c "from src.core.database import init_db; init_db()"

# Setup commands
setup: install db-init
	@echo "Project setup complete!"

setup-dev: install
	@echo "Setting up development environment..."
	pre-commit install
	cp env.example .env
	@echo "Development setup complete!"
	@echo "Please update .env with your configuration values."

# South African specific commands
setup-sa-tax:
	@echo "Setting up South African tax calculations..."
	python -c "from src.services.tax_service import TaxService; TaxService().setup_sa_tax_rates()"

generate-vat-report:
	@echo "Generating VAT report..."
	python -c "from src.services.report_service import ReportService; ReportService().generate_vat_report()"

# Utility commands
check-security:
	@echo "Running security checks..."
	bandit -r src/
	safety check

update-deps:
	@echo "Updating dependencies..."
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

create-migration:
	@echo "Creating new migration..."
	alembic revision --autogenerate -m "$(message)"

# Documentation
docs-serve:
	@echo "Serving documentation..."
	mkdocs serve

docs-build:
	@echo "Building documentation..."
	mkdocs build

# Production commands
deploy-staging:
	@echo "Deploying to staging..."
	# Add your staging deployment commands here

deploy-production:
	@echo "Deploying to production..."
	# Add your production deployment commands here

# Monitoring
health-check:
	@echo "Running health check..."
	curl -f http://localhost:8000/health || echo "Health check failed"

# Backup and restore
backup-db:
	@echo "Creating database backup..."
	docker-compose exec db pg_dump -U knotts_user knotts_accounting > backup_$(date +%Y%m%d_%H%M%S).sql

restore-db:
	@echo "Restoring database from backup..."
	# Usage: make restore-db BACKUP_FILE=backup_20231201_120000.sql
	docker-compose exec -T db psql -U knotts_user knotts_accounting < $(BACKUP_FILE)
