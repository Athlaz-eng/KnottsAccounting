#!/usr/bin/env python
"""
Setup script for Knotts Accounting package.

This script is used for package installation and distribution.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
def read_requirements(filename):
    """Read requirements from a file."""
    with open(filename) as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Setup configuration
setup(
    name="knotts-accounting",
    version="0.1.0",
    author="Knotts Accounting Team",
    author_email="dev@knottsaccounting.co.za",
    description="AI-Powered Accounting Solutions for South African Firms",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/knotts-accounting/knotts-accounting",
    project_urls={
        "Bug Tracker": "https://github.com/knotts-accounting/knotts-accounting/issues",
        "Documentation": "https://knotts-accounting.readthedocs.io",
        "Source Code": "https://github.com/knotts-accounting/knotts-accounting",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "isort>=5.12.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
            "jupyter>=1.0.0",
            "ipython>=8.18.1",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.4.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "knotts-accounting=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)