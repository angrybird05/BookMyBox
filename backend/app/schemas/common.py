"""Common Pydantic schemas used across the application."""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field, conint

T = TypeVar("T")


class PaginationQueryParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    per_page: int = Field(default=10, ge=1, le=100, description="Items per page (max 100)")


class StandardResponse(BaseModel, Generic[T]):
    """Pydantic model representing standard API response payload."""

    success: bool
    data: Optional[T] = None
    message: str
    errors: Optional[List[dict]] = None
    request_id: Optional[str] = None
