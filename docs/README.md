# Knotts Accounting Documentation

## Overview

Knotts Accounting is an AI-powered accounting automation system designed specifically for South African accounting firms. This system provides comprehensive solutions for workflow automation, tax calculations, compliance management, and client communication.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Architecture](#architecture)
3. [API Reference](#api-reference)
4. [South African Compliance](#south-african-compliance)
5. [Development Guide](#development-guide)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL 13+ (or SQLite for development)
- Redis 6+
- Docker and Docker Compose (optional)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd knotts-accounting
   ```

2. **Setup development environment**
   ```bash
   make setup-dev
   ```

3. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Start the application**
   ```bash
   make docker-run
   # or for local development
   uvicorn src.main:app --reload
   ```

5. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

## Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Layer     │    │   Database      │
│   (React/Vue)   │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Services      │
                       │   (Business     │
                       │    Logic)       │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI/Claude     │
                       │   Integration   │
                       └─────────────────┘
```

### Key Modules

- **Core**: Configuration, database, logging
- **Models**: Database models and schemas
- **Services**: Business logic and automation
- **Utils**: Helper functions and utilities
- **API**: REST API endpoints
- **Automations**: Workflow automation scripts

## API Reference

### Authentication

All API endpoints require authentication using JWT tokens.

```bash
# Login
POST /auth/login
{
  "username": "user@example.com",
  "password": "password"
}

# Use token in headers
Authorization: Bearer <token>
```

### Core Endpoints

#### Clients
- `GET /clients` - List all clients
- `POST /clients` - Create new client
- `GET /clients/{id}` - Get client details
- `PUT /clients/{id}` - Update client
- `DELETE /clients/{id}` - Delete client

#### Transactions
- `GET /transactions` - List transactions
- `POST /transactions` - Create transaction
- `GET /transactions/{id}` - Get transaction details
- `PUT /transactions/{id}` - Update transaction

#### Tax Calculations
- `POST /tax/calculate-vat` - Calculate VAT
- `POST /tax/calculate-paye` - Calculate PAYE
- `POST /tax/calculate-provisional` - Calculate provisional tax

#### Reports
- `GET /reports/vat/{period}` - Generate VAT report
- `GET /reports/financial/{year}` - Generate financial statements
- `GET /reports/tax/{year}` - Generate tax summary

### Webhook Endpoints

- `POST /webhooks/sars` - SARS integration webhook
- `POST /webhooks/banking` - Banking integration webhook

## South African Compliance

### Tax Calculations

#### VAT (Value Added Tax)
- Standard rate: 15%
- Zero-rated supplies: 0%
- Exempt supplies: No VAT
- Input VAT: Reclaimable
- Output VAT: Payable

#### PAYE (Pay As You Earn)
- Progressive tax rates
- UIF: 1% employee, 1% employer
- SDL: 1% employer
- Monthly submissions

#### Provisional Tax
- Bi-annual payments
- Based on estimated income
- Penalties for underpayment

### Compliance Requirements

#### POPIA (Protection of Personal Information Act)
- Data encryption at rest and in transit
- Consent management
- Data retention policies
- Right to deletion

#### SARS Requirements
- VAT201 submissions
- EMP201 submissions
- ITR12 submissions
- Audit trail maintenance

#### CIPC Requirements
- Annual returns
- Director updates
- Shareholder changes

## Development Guide

### Code Standards

- Follow PEP 8 for Python code
- Use type hints for all functions
- Write comprehensive docstrings
- Maintain 80%+ test coverage
- Use conventional commit messages

### Project Structure

```
src/
├── core/           # Core functionality
├── models/         # Database models
├── services/       # Business logic
├── utils/          # Utility functions
├── api/            # API endpoints
└── automations/    # Workflow automation
```

### Testing

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_tax_service.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Security checks
make check-security
```

## Deployment

### Docker Deployment

```bash
# Build and run
make docker-build
make docker-run

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Configuration

#### Development
```bash
DEBUG=true
DATABASE_URL=sqlite:///./knotts_accounting.db
```

#### Production
```bash
DEBUG=false
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379
```

### Monitoring

- Health checks: `/health`
- Metrics: `/metrics`
- Logs: Structured JSON logging
- Alerts: Sentry integration

## Troubleshooting

### Common Issues

#### Database Connection
```bash
# Check database status
docker-compose exec db psql -U knotts_user -d knotts_accounting

# Reset database
make db-reset
```

#### Redis Connection
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Clear cache
docker-compose exec redis redis-cli FLUSHALL
```

#### API Issues
```bash
# Check API health
curl http://localhost:8000/health

# View logs
docker-compose logs app
```

### Performance Optimization

- Database indexing
- Query optimization
- Caching strategies
- Background task processing

### Security Best Practices

- Regular dependency updates
- Security scanning
- Access control
- Data encryption
- Audit logging

## Support

For support and questions:
- Documentation: [docs.knottsaccounting.co.za](https://docs.knottsaccounting.co.za)
- Email: support@knottsaccounting.co.za
- GitHub Issues: [github.com/knotts-accounting/issues](https://github.com/knotts-accounting/issues)

---

*Last updated: December 2024*
