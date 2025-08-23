"""
Configuration settings for Knotts Accounting system.

This module contains all configuration settings including South African
accounting specific constants and environment variables.
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with South African accounting defaults."""
    
    # Application settings
    app_name: str = "Knotts Accounting"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database settings
    database_url: str = Field(default="sqlite:///./knotts_accounting.db", env="DATABASE_URL")
    
    # Security settings
    secret_key: str = Field(env="SECRET_KEY", default="your-secret-key-here")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # South African Tax Constants
    vat_rate: float = 0.15  # 15% VAT
    uif_rate_employee: float = 0.01  # 1% UIF employee contribution
    uif_rate_employer: float = 0.01  # 1% UIF employer contribution
    sdl_rate: float = 0.01  # 1% Skills Development Levy
    
    # Financial year settings (March year-end for most SA entities)
    financial_year_end_month: int = 3  # March
    financial_year_end_day: int = 31
    
    # Currency settings
    default_currency: str = "ZAR"
    supported_currencies: list[str] = ["ZAR", "USD", "EUR", "GBP"]
    
    # File upload settings
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: list[str] = [".pdf", ".xlsx", ".xls", ".csv", ".doc", ".docx"]
    upload_dir: str = Field(default="uploads", env="UPLOAD_DIR")  # Document upload directory
    
    # Email settings
    smtp_server: Optional[str] = Field(default=None, env="SMTP_SERVER")
    smtp_port: int = Field(default=587, env="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    
    # AI/Claude settings
    claude_api_key: Optional[str] = Field(default=None, env="CLAUDE_API_KEY")
    claude_model: str = Field(default="claude-3-sonnet-20240229", env="CLAUDE_MODEL")
    
    # Redis settings
    redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    
    # Logging settings
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: Optional[str] = Field(default=None, env="LOG_FILE")
    
    # CORS settings
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]
    
    # Access token settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Compliance settings
    popia_compliant: bool = True
    audit_trail_enabled: bool = True
    data_retention_days: int = 2555  # 7 years for tax records
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"  # Ignore extra fields from .env file
    }


# Global settings instance
settings = Settings()
