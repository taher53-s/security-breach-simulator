"""
Error Handling and Custom Exceptions for Security Breach Simulator
Provides consistent error handling across the application.
"""
from __future__ import annotations

from typing import Any


class BreachSimulatorError(Exception):
    """Base exception for all simulator errors"""
    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details
        }


class ScenarioNotFoundError(BreachSimulatorError):
    """Raised when a scenario is not found"""
    pass


class InvalidScenarioError(BreachSimulatorError):
    """Raised when scenario data is invalid"""
    pass


class PolicyNotFoundError(BreachSimulatorError):
    """Raised when a policy is not found"""
    pass


class ScoringError(BreachSimulatorError):
    """Raised when there's an error in scoring"""
    pass


class ReplayError(BreachSimulatorError):
    """Raised when replay operations fail"""
    pass


class ConfigurationError(BreachSimulatorError):
    """Raised when configuration is invalid"""
    pass


class APIError(BreachSimulatorError):
    """Raised when API operations fail"""
    def __init__(self, message: str, status_code: int = 500, details: dict | None = None):
        super().__init__(message, details)
        self.status_code = status_code


class ValidationError(BreachSimulatorError):
    """Raised when input validation fails"""
    pass


class TimerError(BreachSimulatorError):
    """Raised when timer operations fail"""
    pass


class AuditError(BreachSimulatorError):
    """Raised when audit logging fails"""
    pass


def handle_exception(exc: Exception) -> dict[str, Any]:
    """Convert any exception to a standardized error response"""
    if isinstance(exc, BreachSimulatorError):
        return exc.to_dict()
    
    # Handle standard library exceptions
    error_mapping = {
        FileNotFoundError: ("File not found", 404),
        ValueError: ("Invalid value", 400),
        TypeError: ("Type error", 400),
        KeyError: ("Key not found", 404),
        PermissionError: ("Permission denied", 403),
        TimeoutError: ("Operation timed out", 504),
    }
    
    error_class = type(exc).__name__
    message = str(exc)
    status_code = 500
    
    for exc_type, (msg, code) in error_mapping.items():
        if isinstance(exc, exc_type):
            message = f"{msg}: {message}"
            status_code = code
            break
    
    return {
        "error": error_class,
        "message": message,
        "details": {}
    }


# Error handler for FastAPI
def setup_error_handlers(app):
    """Setup error handlers for FastAPI app"""
    from fastapi import Request, status
    from fastapi.responses import JSONResponse
    
    @app.exception_handler(BreachSimulatorError)
    async def simulator_exception_handler(request: Request, exc: BreachSimulatorError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=exc.to_dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        error = handle_exception(exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error
        )
    
    return app
