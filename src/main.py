"""
Main application entry point for Knotts Accounting API.

This module initializes the FastAPI application and configures all routes,
middleware, and event handlers for the South African accounting system.
"""

from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from src.core.config import settings
from src.core.database import init_db, close_db
from src.core.logging import get_logger, setup_logging

# Initialize logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle events.
    
    This context manager handles startup and shutdown events for the application.
    """
    # Startup
    logger.info("Starting Knotts Accounting API", version=settings.app_version)
    init_db()
    logger.info("Database initialized successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Knotts Accounting API")
    close_db()
    logger.info("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Accounting Solutions for South African Firms",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure trusted hosts
if not settings.debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions with consistent error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url),
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc: ValueError):
    """Handle value errors with consistent error format."""
    logger.error("Value error", error=str(exc), path=str(request.url))
    return JSONResponse(
        status_code=400,
        content={
            "error": str(exc),
            "status_code": 400,
            "path": str(request.url),
        },
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring.
    
    Returns:
        Dict containing health status and application information.
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production",
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint providing basic API information.
    
    Returns:
        Dict containing welcome message and documentation links.
    """
    return {
        "message": "Welcome to Knotts Accounting API",
        "documentation": "/docs",
        "openapi": "/openapi.json",
        "health": "/health",
    }


# API Routes - These will be imported from route modules
# from src.api import auth, clients, transactions, tax, reports
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(clients.router, prefix="/api/v1/clients", tags=["Clients"])
# app.include_router(transactions.router, prefix="/api/v1/transactions", tags=["Transactions"])
# app.include_router(tax.router, prefix="/api/v1/tax", tags=["Tax"])
# app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])


def main():
    """Main function to run the application."""
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info",
    )


if __name__ == "__main__":
    main()