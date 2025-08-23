"""
Core functionality for Knotts Accounting system.

This module contains the fundamental components and configurations
for the accounting automation system.
"""

from .config import Settings, settings
from .database import Base, engine, SessionLocal, get_db
from .logging import setup_logging, get_logger
from .security import (
    SecurityManager, SecurityError, security_manager,
    encrypt_credential, decrypt_credential, validate_api_keys,
    generate_secure_key, audit_security_event, validate_environment_variables
)

__all__ = [
    # Configuration
    "Settings", 
    "settings",
    
    # Database
    "Base", 
    "engine", 
    "SessionLocal", 
    "get_db",
    
    # Logging
    "setup_logging",
    "get_logger",
    
    # Security
    "SecurityManager",
    "SecurityError", 
    "security_manager",
    "encrypt_credential",
    "decrypt_credential",
    "validate_api_keys",
    "generate_secure_key",
    "audit_security_event",
    "validate_environment_variables"
]
