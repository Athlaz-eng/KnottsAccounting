"""
Transaction model for Knotts Accounting system.

This module defines the Transaction model for financial transactions
with South African tax compliance requirements.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum

from src.core.database import Base


class TransactionType(enum.Enum):
    """Transaction type enumeration."""
    
    INCOME = "income"
    EXPENSE = "expense"
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"


class VATType(enum.Enum):
    """VAT type enumeration for South African VAT."""
    
    STANDARD = "standard"  # 15%
    ZERO_RATED = "zero_rated"  # 0%
    EXEMPT = "exempt"  # No VAT
    OUT_OF_SCOPE = "out_of_scope"  # Not applicable
    INPUT = "input"  # VAT on purchases
    OUTPUT = "output"  # VAT on sales


class Transaction(Base):
    """
    Transaction model representing financial transactions.
    
    This model includes South African specific fields for:
    - VAT calculations and compliance
    - Tax deductibility
    - SARS transaction codes
    """
    
    __tablename__ = "transactions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False, index=True)
    
    # Transaction details
    transaction_date = Column(DateTime, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    reference = Column(String(100), nullable=True, index=True)
    transaction_type = Column(SQLEnum(TransactionType), nullable=False)
    
    # Financial amounts (stored in cents to avoid decimal issues)
    amount_excl_vat = Column(Numeric(15, 2), nullable=False)
    vat_amount = Column(Numeric(15, 2), default=Decimal("0.00"))
    amount_incl_vat = Column(Numeric(15, 2), nullable=False)
    
    # VAT details
    vat_type = Column(SQLEnum(VATType), nullable=False, default=VATType.STANDARD)
    vat_rate = Column(Numeric(5, 2), default=Decimal("15.00"))  # 15% standard rate
    
    # Account classification
    account_code = Column(String(20), nullable=True)  # Chart of accounts code
    account_name = Column(String(200), nullable=True)
    cost_center = Column(String(50), nullable=True)
    
    # Tax compliance
    is_tax_deductible = Column(Boolean, default=True)
    sars_transaction_code = Column(String(20), nullable=True)  # SARS specific codes
    
    # Document references
    invoice_number = Column(String(50), nullable=True)
    receipt_number = Column(String(50), nullable=True)
    document_path = Column(String(500), nullable=True)  # Path to scanned document
    
    # Banking details
    bank_reference = Column(String(100), nullable=True)
    payment_method = Column(String(50), nullable=True)  # EFT, Cash, Card, etc.
    
    # Reconciliation
    is_reconciled = Column(Boolean, default=False)
    reconciliation_date = Column(DateTime, nullable=True)
    bank_statement_ref = Column(String(100), nullable=True)
    
    # Provisional tax
    provisional_tax_period = Column(Integer, nullable=True)  # 1 or 2 for bi-annual
    provisional_tax_year = Column(Integer, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(100), nullable=True)
    modified_by = Column(String(100), nullable=True)
    is_deleted = Column(Boolean, default=False)
    
    # Relationships
    client = relationship("Client", back_populates="transactions")
    
    def __repr__(self) -> str:
        """String representation of the transaction."""
        return f"<Transaction(id={self.id}, date={self.transaction_date}, amount={self.amount_incl_vat})>"
    
    def calculate_vat(self) -> None:
        """
        Calculate VAT amounts based on VAT type and rate.
        
        This method implements South African VAT calculation rules.
        """
        if self.vat_type == VATType.STANDARD:
            # Standard rate (15%)
            self.vat_amount = self.amount_excl_vat * (self.vat_rate / Decimal("100"))
            self.amount_incl_vat = self.amount_excl_vat + self.vat_amount
        elif self.vat_type == VATType.ZERO_RATED:
            # Zero-rated (0%)
            self.vat_amount = Decimal("0.00")
            self.amount_incl_vat = self.amount_excl_vat
        elif self.vat_type in [VATType.EXEMPT, VATType.OUT_OF_SCOPE]:
            # Exempt or out of scope
            self.vat_amount = Decimal("0.00")
            self.amount_incl_vat = self.amount_excl_vat
        else:
            # Input/Output VAT
            self.vat_amount = self.amount_excl_vat * (self.vat_rate / Decimal("100"))
            self.amount_incl_vat = self.amount_excl_vat + self.vat_amount
        
        # Round to 2 decimal places (cents)
        self.vat_amount = self.vat_amount.quantize(Decimal("0.01"))
        self.amount_incl_vat = self.amount_incl_vat.quantize(Decimal("0.01"))
    
    def to_dict(self) -> dict:
        """Convert transaction to dictionary representation."""
        return {
            "id": self.id,
            "client_id": self.client_id,
            "transaction_date": self.transaction_date.isoformat() if self.transaction_date else None,
            "description": self.description,
            "reference": self.reference,
            "transaction_type": self.transaction_type.value if self.transaction_type else None,
            "amount_excl_vat": float(self.amount_excl_vat) if self.amount_excl_vat else 0,
            "vat_amount": float(self.vat_amount) if self.vat_amount else 0,
            "amount_incl_vat": float(self.amount_incl_vat) if self.amount_incl_vat else 0,
            "vat_type": self.vat_type.value if self.vat_type else None,
            "vat_rate": float(self.vat_rate) if self.vat_rate else 0,
            "is_reconciled": self.is_reconciled,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }