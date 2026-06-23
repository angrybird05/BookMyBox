"""Grounds API endpoints."""

from datetime import date
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import get_db
from app.core.responses import success_response, paginated_response
from app.schemas.ground import GroundResponse
from app.schemas.slot import SlotResponse
from app.services.ground import GroundService
from app.services.slot import SlotService

router = APIRouter(prefix="/grounds", tags=["Grounds"])


@router.get("", status_code=status.HTTP_200_OK)
async def list_grounds(
    request: Request,
    city: Optional[str] = Query(None, description="Filter grounds by city"),
    search: Optional[str] = Query(None, description="Search grounds by name/location"),
    price_min: Optional[int] = Query(None, ge=0, description="Minimum price per hour"),
    price_max: Optional[int] = Query(None, ge=0, description="Maximum price per hour"),
    amenities: Optional[List[str]] = Query(None, description="Filter by amenities list"),
    tag: Optional[str] = Query(None, description="Filter by tag (POPULAR, PREMIUM, NEW)"),
    sort_by: Optional[str] = Query(None, description="Sort options (price_asc, price_desc, rating_desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db=Depends(get_db)
) -> Any:
    """Retrieve grounds list matching filters, sorted and paginated."""
    ground_service = GroundService(db)
    grounds, total = await ground_service.list_grounds(
        city=city,
        search_query=search,
        price_min=price_min,
        price_max=price_max,
        amenities=amenities,
        tag=tag,
        sort_by=sort_by,
        page=page,
        per_page=per_page
    )
    
    grounds_data = [GroundResponse.model_validate(g).model_dump(mode="json") for g in grounds]
    request_id = getattr(request.state, "request_id", None)
    
    return paginated_response(
        data=grounds_data,
        total=total,
        page=page,
        per_page=per_page,
        message="Grounds retrieved successfully",
        request_id=request_id
    )


@router.get("/top", status_code=status.HTTP_200_OK)
async def get_top_rated(
    request: Request,
    limit: int = Query(6, ge=1, le=20, description="Max grounds to return"),
    db=Depends(get_db)
) -> Any:
    """Retrieve top-rated grounds list for homepage carousel."""
    ground_service = GroundService(db)
    grounds = await ground_service.get_top_grounds(limit=limit)
    
    grounds_data = [GroundResponse.model_validate(g).model_dump(mode="json") for g in grounds]
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(data=grounds_data, request_id=request_id)


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_ground_by_id(
    request: Request,
    id: uuid.UUID,
    db=Depends(get_db)
) -> Any:
    """Retrieve details of a specific ground."""
    ground_service = GroundService(db)
    ground = await ground_service.get_ground(id)
    
    ground_data = GroundResponse.model_validate(ground).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(data=ground_data, request_id=request_id)


@router.get("/{id}/slots", status_code=status.HTTP_200_OK)
async def get_ground_slots(
    request: Request,
    id: uuid.UUID,
    date_query: Optional[date] = Query(None, alias="date", description="Query date for slots (defaults to today)"),
    db=Depends(get_db)
) -> Any:
    """Retrieve slot catalog for a ground on a specific date (auto-generates future slots)."""
    target_date = date_query or date.today()
    slot_service = SlotService(db)
    slots = await slot_service.get_slots_for_date(id, target_date)
    
    slots_data = [SlotResponse.model_validate(s).model_dump(mode="json") for s in slots]
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(
        data=slots_data,
        message=f"Slots for {target_date} retrieved successfully",
        request_id=request_id
    )


@router.get("/{id}/reviews", status_code=status.HTTP_200_OK)
async def get_ground_reviews(
    request: Request,
    id: uuid.UUID,
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    db=Depends(get_db)
) -> Any:
    """Retrieve paginated reviews for a specific ground."""
    from app.services.review import ReviewService
    from app.schemas.review import ReviewResponse
    
    review_service = ReviewService(db)
    reviews, total = await review_service.get_reviews_for_ground(
        ground_id=id,
        skip=(page - 1) * per_page,
        limit=per_page
    )
    
    reviews_data = [ReviewResponse.model_validate(r).model_dump(mode="json") for r in reviews]
    request_id = getattr(request.state, "request_id", None)
    
    return paginated_response(
        data=reviews_data,
        total=total,
        page=page,
        per_page=per_page,
        message="Reviews retrieved successfully",
        request_id=request_id
    )

