"""
Standard API response wrapper.
Every API endpoint returns this format for consistency.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationMeta(BaseModel):
    """Pagination metadata included in list responses."""

    page: int = Field(ge=1, description="Current page number")
    per_page: int = Field(ge=1, le=100, description="Items per page")
    total: int = Field(ge=0, description="Total number of items")
    total_pages: int = Field(ge=0, description="Total number of pages")


class ApiResponse(BaseModel, Generic[T]):
    """Standard wrapper for all API responses."""

    success: bool = True
    data: Optional[T] = None
    message: str = "Success"
    meta: Optional[PaginationMeta] = None
    errors: Optional[List[Dict[str, Any]]] = None
    request_id: Optional[str] = None


def success_response(
    data: Any = None,
    message: str = "Success",
    meta: Optional[PaginationMeta] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a successful API response dict."""
    response: Dict[str, Any] = {
        "success": True,
        "data": data,
        "message": message,
        "errors": None,
    }
    if meta:
        response["meta"] = meta.model_dump()
    if request_id:
        response["request_id"] = request_id
    return response


def error_response(
    message: str = "An error occurred",
    errors: Optional[List[Dict[str, Any]]] = None,
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build an error API response dict."""
    return {
        "success": False,
        "data": None,
        "message": message,
        "errors": errors or [],
        "request_id": request_id,
    }


def paginated_response(
    data: Any,
    total: int,
    page: int,
    per_page: int,
    message: str = "Success",
    request_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a paginated list response with metadata."""
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
    meta = PaginationMeta(
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages,
    )
    return success_response(data=data, message=message, meta=meta, request_id=request_id)
