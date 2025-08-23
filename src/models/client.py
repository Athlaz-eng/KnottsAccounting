"""
Client model for Knotts Accounting system.

This module defines the Client model representing accounting clients
with South African specific requirements.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum

from src.core.database import Base


class ClientType(enum.Enum):
    """Client type enumeration."""
    
    INDIVIDUAL = "individual"
    COMPANY = "company"
    TRUST = "trust"
    PARTNERSHIP = "partnership"
    SOLE_PROPRIETOR = "sole_proprietor"
    NON_PROFIT = "non_profit"
    CLOSE_CORPORATION = "close_corporation"


class ClientStatus(enum.Enum):
    """Client status enumeration."""
    
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"


class Client(Base):
    """
    Client model representing accounting clients.
    
    This model includes South African specific fields such as:
    - VAT registration number
    - Company registration number (CIPC)
    - Tax reference number
    - BEE status
    """
    
    __tablename__ = "clients"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    client_type = Column(SQLEnum(ClientType), nullable=False, default=ClientType.INDIVIDUAL)
    status = Column(SQLEnum(ClientStatus), nullable=False, default=ClientStatus.ACTIVE)
    
    # South African specific identifiers
    id_number = Column(String(13), unique=True, nullable=True)  # For individuals
    passport_number = Column(String(50), unique=True, nullable=True)  # For foreign individuals
    company_registration = Column(String(50), unique=True, nullable=True)  # CIPC registration
    vat_number = Column(String(10), unique=True, nullable=True)  # VAT registration
    tax_reference = Column(String(10), unique=True, nullable=True)  # SARS tax reference
    
    # Contact information
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    mobile = Column(String(20), nullable=True)
    
    # Address information
    physical_address = Column(Text, nullable=True)
    physical_suburb = Column(String(100), nullable=True)
    physical_city = Column(String(100), nullable=True)
    physical_province = Column(String(50), nullable=True)
    physical_postal_code = Column(String(10), nullable=True)
    
    postal_address = Column(Text, nullable=True)
    postal_suburb = Column(String(100), nullable=True)
    postal_city = Column(String(100), nullable=True)
    postal_province = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    
    # Financial information
    financial_year_end = Column(Integer, default=2)  # Month (0-11), default February (March year-end)
    annual_turnover = Column(Numeric(15, 2), nullable=True)
    bee_level = Column(Integer, nullable=True)  # BEE level (1-8)
    
    # Tax settings
    is_vat_registered = Column(Boolean, default=False)
    is_provisional_taxpayer = Column(Boolean, default=False)
    is_paye_registered = Column(Boolean, default=False)
    
    # Banking information (encrypted in production)
    bank_name = Column(String(100), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    bank_branch_code = Column(String(10), nullable=True)
    bank_account_type = Column(String(50), nullable=True)
    
    # FICA compliance
    fica_status = Column(String(50), nullable=True)
    fica_date = Column(DateTime, nullable=True)
    
    # Notes and metadata
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="client", lazy="dynamic")
    ocr_documents = relationship("OCRDocument", back_populates="client", lazy="dynamic")
    invoices = relationship("Invoice", back_populates="client", lazy="dynamic")
    user = relationship("User", back_populates="client")
    # tax_calculations = relationship("TaxCalculation", back_populates="client", lazy="dynamic")  # TODO: Add when TaxCalculation model is created
    
    def __repr__(self) -> str:
        """String representation of the client."""
        return f"<Client(id={self.id}, name='{self.name}', type={self.client_type.value})>"
    
    def to_dict(self) -> dict:
        """Convert client to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "client_type": self.client_type.value if self.client_type else None,
            "status": self.status.value if self.status else None,
            "email": self.email,
            "vat_number": self.vat_number,
            "tax_reference": self.tax_reference,
            "is_vat_registered": self.is_vat_registered,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }