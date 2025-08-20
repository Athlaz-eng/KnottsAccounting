"""
Core functionality for Knotts Accounting system.

This module contains the fundamental components and configurations
for the accounting automation system.
"""

from .config import Settings
from .database import Database
from .logging import setup_logging

__all__ = ["Settings", "Database", "setup_logging"]
