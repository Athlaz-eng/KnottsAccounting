"""
Pytest configuration and fixtures for Knotts Accounting tests.

This module provides common fixtures and configuration for all tests.
"""

import os
import sys
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import Base, get_db
from src.main import app


# Test database URL
TEST_DATABASE_URL = "sqlite:///./test_knotts_accounting.db"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    # Clean up test database file
    if os.path.exists("./test_knotts_accounting.db"):
        os.remove("./test_knotts_accounting.db")


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create a new database session for each test."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session) -> TestClient:
    """Create a test client with overridden database dependency."""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_client_data():
    """Provide sample client data for testing."""
    return {
        "name": "Test Company (Pty) Ltd",
        "client_type": "company",
        "email": "test@testcompany.co.za",
        "phone": "+27 11 123 4567",
        "vat_number": "4123456789",
        "company_registration": "2024/123456/07",
        "tax_reference": "9123456789",
        "is_vat_registered": True,
        "financial_year_end": 2,  # March year-end
        "physical_address": "123 Test Street",
        "physical_suburb": "Sandton",
        "physical_city": "Johannesburg",
        "physical_province": "Gauteng",
        "physical_postal_code": "2196",
    }


@pytest.fixture
def sample_transaction_data():
    """Provide sample transaction data for testing."""
    return {
        "client_id": 1,
        "transaction_date": "2024-01-15T10:00:00",
        "description": "Professional services rendered",
        "reference": "INV-2024-001",
        "transaction_type": "income",
        "amount_excl_vat": 10000.00,
        "vat_type": "standard",
        "vat_rate": 15.00,
        "account_code": "4100",
        "account_name": "Professional Fees",
        "is_tax_deductible": True,
        "invoice_number": "INV-2024-001",
        "payment_method": "EFT",
    }


@pytest.fixture
def sample_paye_data():
    """Provide sample PAYE calculation data."""
    return {
        "annual_income": 600000.00,
        "age": 35,
        "tax_year": "2024/2025",
    }


@pytest.fixture
def sample_vat_data():
    """Provide sample VAT calculation data."""
    return {
        "amount": 1000.00,
        "vat_inclusive": False,
        "rate": 0.15,
    }