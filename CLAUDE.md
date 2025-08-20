# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Knotts Accounting is an AI-powered accounting solution specifically designed for South African accounting firms. The system focuses on tax compliance, workflow automation, and adherence to South African accounting standards (IFRS/SA GAAP).

## Build and Development Commands

### Essential Commands
```bash
# Setup and Installation
make setup          # Complete project setup (install deps + init DB)
make setup-dev      # Development environment setup with pre-commit hooks
make install        # Install Python dependencies

# Development
make test           # Run pytest with coverage (tests/ -v --cov=src)
make lint           # Run flake8 and mypy on src/
make format         # Format with black and isort
make clean          # Clean cache and temp files

# Database
make db-init        # Initialize database
make db-migrate     # Run Alembic migrations
make db-reset       # Reset database completely

# Docker
make docker-build   # Build Docker image
make docker-run     # Start services with docker-compose
make docker-stop    # Stop Docker services

# South African Tax Features
make setup-sa-tax         # Setup SA tax rates
make generate-vat-report  # Generate VAT201 report
```

### Running Single Tests
```bash
pytest tests/test_module.py::TestClass::test_method -v
pytest tests/ -k "test_name" -v
pytest tests/ -m unit  # Run only unit tests
```

## Architecture Overview

### Core Structure
The application follows a modular architecture with clear separation of concerns:

```
src/
├── core/           # Configuration, database, logging infrastructure
├── models/         # SQLAlchemy models for database entities
├── services/       # Business logic and external integrations
└── utils/          # Shared utilities and helpers
```

### Key Design Patterns

#### 1. Configuration Management
- **Central Configuration**: All settings in `src/core/config.py` using Pydantic BaseSettings
- **Environment-based**: Reads from `.env` file and environment variables
- **South African Defaults**: Pre-configured with SA tax rates (VAT 15%, UIF 1%, SDL 1%)

#### 2. Database Architecture
- **Repository Pattern**: Database operations abstracted through SQLAlchemy ORM
- **Session Management**: Dependency injection pattern with `get_db()` generator
- **Multi-database Support**: SQLite for development, PostgreSQL for production

#### 3. Service Layer Pattern
Services encapsulate business logic and should be used for:
- Tax calculations (PAYE, VAT, provisional tax)
- SARS submissions and compliance
- Report generation
- External API integrations

#### 4. Logging Strategy
- **Structured Logging**: Using structlog for JSON-formatted logs
- **Audit Trail**: All financial transactions and calculations logged for compliance
- **Log Levels**: Configurable through environment variables

## South African Accounting Specifics

### Tax Compliance
- **VAT**: 15% standard rate, automatic VAT201 generation
- **PAYE**: Employee tax calculations with UIF and SDL
- **Provisional Tax**: Bi-annual payment calculations
- **Financial Year**: Default March year-end

### Regulatory Compliance
- **POPIA**: Data protection with consent management and retention policies
- **Companies Act**: Maintains 7-year record retention for tax documents
- **FICA**: Customer due diligence and transaction monitoring
- **FAIS**: Financial advisory compliance where applicable

### Key Compliance Files
- `LAW.md`: Comprehensive legal and compliance framework
- Tax calculation methods must follow SARS requirements
- All financial calculations use Decimal type with proper rounding

## Development Standards

### Python Code Style
- **Type Hints**: Required for all functions (enforced by mypy)
- **Docstrings**: Required for all functions and classes
- **Error Handling**: Use structured logging instead of print statements
- **Testing**: Minimum 80% code coverage requirement

### Database Operations
- **Transactions**: Use SQLAlchemy sessions with proper commit/rollback
- **Migrations**: Use Alembic for all schema changes
- **Queries**: Use parameterized queries to prevent SQL injection

### API Development
- **Framework**: FastAPI with automatic OpenAPI documentation
- **Authentication**: JWT tokens with passlib bcrypt hashing
- **Validation**: Pydantic models for request/response validation

## Testing Strategy

### Test Categories
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test database operations and API endpoints
- **Marks**: Use `@pytest.mark.unit` and `@pytest.mark.integration`

### Running Tests
```python
# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

## Docker Environment

The application uses Docker Compose with multiple services:
- **app**: Main FastAPI application on port 8000
- **db**: PostgreSQL database on port 5432
- **redis**: Cache and task queue on port 6379
- **worker**: Celery worker for background tasks
- **beat**: Celery beat for scheduled tasks
- **nginx**: Optional reverse proxy on ports 80/443

## Security Considerations

### Authentication & Authorization
- Role-based access control implementation required
- Secure password hashing with bcrypt
- Session management with Redis

### Data Protection
- POPIA compliance mandatory
- Encryption at rest and in transit
- Audit logging for all financial operations
- Secure API key management in environment variables

## External Integrations

### Claude AI Integration
- API key configuration: `CLAUDE_API_KEY` environment variable
- Model selection: `CLAUDE_MODEL` (default: claude-3-sonnet)
- Used for intelligent document processing and workflow automation

### SARS Integration Points
- VAT201 submissions
- EMP201 monthly returns
- IRP5/IT3(a) certificate generation
- Provisional tax calculations

## Background Tasks

### Celery Configuration
- **Broker**: Redis for task queue
- **Worker**: Processes async tasks
- **Beat**: Handles scheduled tasks (monthly reports, tax submissions)

### Common Background Tasks
- Report generation
- Email notifications
- Data synchronization
- Scheduled tax submissions

## Error Handling

### Standard Error Response Format
```python
{
    "error": "error_code",
    "message": "User-friendly message",
    "details": {},  # Optional additional context
    "timestamp": "ISO 8601 timestamp"
}
```

### Logging Errors
Always use structured logging with context:
```python
logger.error("Transaction failed", 
            transaction_id=trans_id, 
            error=str(e),
            user_id=user.id)
```

## Database Schema Patterns

### Audit Fields
All financial models should include:
- `created_at`: Timestamp of creation
- `updated_at`: Last modification timestamp
- `created_by`: User who created the record
- `modified_by`: User who last modified
- `is_deleted`: Soft delete flag

### Financial Precision
- Use `Decimal` type for all monetary values
- Store amounts in cents to avoid floating point issues
- Round using `ROUND_HALF_UP` for South African standards

## Performance Optimization

### Caching Strategy
- Redis for session management
- Cache frequently accessed reference data (tax rates, exchange rates)
- Implement cache invalidation for updated data

### Database Optimization
- Proper indexing on frequently queried columns
- Use database connection pooling
- Implement query pagination for large datasets

## Monitoring and Observability

### Key Metrics to Track
- API response times
- Database query performance
- Background task completion rates
- Error rates and types
- User activity patterns

### Health Checks
- Endpoint: `GET /health`
- Checks: Database connectivity, Redis availability, disk space
- Used by Docker and monitoring systems