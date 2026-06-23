"""
Custom exception classes and centralized error handling.
All business-logic errors inherit from AppException for consistent API responses.
"""

from typing import Any, Dict, List, Optional


class AppException(Exception):
    """Base application exception — all custom errors inherit from this."""

    def __init__(
        self,
        message: str = "An error occurred",
        status_code: int = 500,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.errors = errors or []
        super().__init__(self.message)


class BadRequestException(AppException):
    """400 — Invalid request data or business rule violation."""

    def __init__(self, message: str = "Bad request", errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message=message, status_code=400, errors=errors)


class UnauthorizedException(AppException):
    """401 — Missing or invalid authentication."""

    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(AppException):
    """403 — Authenticated but insufficient permissions."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)


class NotFoundException(AppException):
    """404 — Resource not found."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class ConflictException(AppException):
    """409 — Resource already exists or state conflict."""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message=message, status_code=409)


class RateLimitException(AppException):
    """429 — Too many requests."""

    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(message=message, status_code=429)


class ValidationException(AppException):
    """422 — Validation failed."""

    def __init__(self, message: str = "Validation error", errors: Optional[List[Dict[str, Any]]] = None):
        super().__init__(message=message, status_code=422, errors=errors)


class PaymentException(AppException):
    """402 — Payment failed."""

    def __init__(self, message: str = "Payment failed"):
        super().__init__(message=message, status_code=402)


class SlotUnavailableException(AppException):
    """409 — Slot no longer available (race condition)."""

    def __init__(self, message: str = "One or more selected slots are no longer available"):
        super().__init__(message=message, status_code=409)
