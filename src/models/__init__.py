"""
Database models for Knotts Accounting system.

This module contains all database models and schemas for the
accounting system including clients, transactions, invoices, and reports.
"""

from .client import Client, ClientType, ClientStatus
from .transaction import Transaction, TransactionType, VATType
from .ocr_document import OCRDocument, OCRBatchJob, DocumentMetadata, OCRProvider, OCRStatus, DocumentCategory, ProcessingStatus, DocumentType
from .invoice import Invoice, InvoiceLineItem, Payment, InvoiceStatus, PaymentTerms, VATType as InvoiceVATType
from .general_ledger import ChartOfAccounts, JournalEntry, JournalEntryLine, AccountType, AccountSubType, JournalType
from .bank import BankAccount, BankStatement, BankTransaction, BankName, ReconciliationStatus

__all__ = [
    # Client models
    "Client", 
    "ClientType", 
    "ClientStatus",
    
    # Transaction models
    "Transaction", 
    "TransactionType", 
    "VATType",
    
    # OCR models
    "OCRDocument",
    "OCRBatchJob", 
    "DocumentMetadata",
    "OCRProvider",
    "OCRStatus",
    "DocumentCategory",
    "ProcessingStatus",
    "DocumentType",
    
    # Invoice models
    "Invoice",
    "InvoiceLineItem", 
    "Payment",
    "InvoiceStatus",
    "PaymentTerms",
    "InvoiceVATType",
    
    # General Ledger models
    "ChartOfAccounts",
    "JournalEntry",
    "JournalEntryLine",
    "AccountType",
    "AccountSubType",
    "JournalType",
    
    # Bank models
    "BankAccount",
    "BankStatement",
    "BankTransaction",
    "BankName",
    "ReconciliationStatus"
]
