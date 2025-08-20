"""
Knotts Accounting - AI-Powered Accounting Solutions for South African Firms

This package provides comprehensive automation and AI-powered solutions
for South African accounting professionals.
"""

__version__ = "0.1.0"
__author__ = "Knotts Accounting Team"
__email__ = "dev@knottsaccounting.co.za"

# Core modules
from . import core
from . import models
from . import services
from . import utils

__all__ = ["core", "models", "services", "utils"]
