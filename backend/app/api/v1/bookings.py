"""Bookings API endpoints."""

from datetime import date
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import StreamingResponse

from app.api.deps import get_db, get_current_user
from app.core.responses import success_response, paginated_response
from app.models.user import User
from app.schemas.booking import BookingResponse, BookingCreateRequest, ValidatePromoRequest, ValidatePromoResponse, CancelSlotsRequest
from app.services.booking import BookingService
from app.services.promo_code import PromoCodeService
from app.services.ticket import TicketService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_booking_endpoint(
    request: Request,
    payload: BookingCreateRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Create a new booking and process payment (Wallet or simulated card/UPI/NB)."""
    booking_service = BookingService(db)
    booking = await booking_service.create_booking(
        user_id=current_user.id,
        ground_id=payload.ground_id,
        booking_date=payload.booking_date,
        slot_ids=payload.slot_ids,
        promo_code_str=payload.promo_code,
        payment_method=payload.payment_method,
    )
    
    # Reload details to include slot and ground relations
    booking_details = await booking_service.get_booking_details(current_user.id, booking.id)
    booking_data = BookingResponse.model_validate(booking_details).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(
        data=booking_data,
        message="Booking created successfully",
        request_id=request_id
    )


@router.get("", status_code=status.HTTP_200_OK)
async def get_my_bookings(
    request: Request,
    tab: Optional[str] = Query(None, description="Group filters: UPCOMING, PAST, CANCELLED"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Retrieve paginated active user bookings with group status tabs."""
    booking_service = BookingService(db)
    skip = (page - 1) * per_page
    bookings, total = await booking_service.booking_repo.list_user_bookings(
        user_id=current_user.id,
        tab=tab,
        skip=skip,
        limit=per_page
    )
    
    bookings_data = [BookingResponse.model_validate(b).model_dump(mode="json") for b in bookings]
    request_id = getattr(request.state, "request_id", None)
    
    return paginated_response(
        data=bookings_data,
        total=total,
        page=page,
        per_page=per_page,
        message="Bookings retrieved successfully",
        request_id=request_id
    )


@router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_booking_by_id(
    request: Request,
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Retrieve full details of a specific booking."""
    booking_service = BookingService(db)
    booking = await booking_service.get_booking_details(current_user.id, id)
    
    booking_data = BookingResponse.model_validate(booking).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(data=booking_data, request_id=request_id)


@router.post("/{id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_booking_endpoint(
    request: Request,
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Cancel entire booking and credit the amount back to user wallet."""
    booking_service = BookingService(db)
    booking = await booking_service.cancel_booking(current_user.id, id)
    
    booking_data = BookingResponse.model_validate(booking).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(
        data=booking_data,
        message="Booking cancelled successfully and amount refunded to wallet",
        request_id=request_id
    )


@router.post("/{id}/cancel-slots", status_code=status.HTTP_200_OK)
async def cancel_booking_slots_endpoint(
    request: Request,
    id: uuid.UUID,
    payload: CancelSlotsRequest,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Partially cancel specific slots in a booking and refund proportionally to wallet."""
    booking_service = BookingService(db)
    booking = await booking_service.cancel_specific_slots(current_user.id, id, payload.slot_ids)
    
    booking_data = BookingResponse.model_validate(booking).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(
        data=booking_data,
        message="Selected slots cancelled and refunded successfully",
        request_id=request_id
    )


@router.post("/validate-promo", status_code=status.HTTP_200_OK)
async def validate_promo_endpoint(
    request: Request,
    payload: ValidatePromoRequest,
    db=Depends(get_db)
) -> Any:
    """Dry-run validate a promo code discount eligibility."""
    promo_service = PromoCodeService(db)
    valid, discount, final_amount, msg = await promo_service.validate_promo(
        code=payload.code,
        total_amount=payload.total_amount
    )
    
    response_data = ValidatePromoResponse(
        valid=valid,
        discount=discount,
        final_amount=final_amount,
        message=msg
    ).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    
    return success_response(data=response_data, request_id=request_id)


@router.get("/{id}/ticket", status_code=status.HTTP_200_OK)
async def download_booking_ticket(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db)
) -> Any:
    """Download the booking confirmation ticket as a PDF file."""
    booking_service = BookingService(db)
    booking = await booking_service.get_booking_details(current_user.id, id)
    
    pdf_buffer = TicketService.generate_pdf_ticket(booking)
    filename = f"BMB_Ticket_{booking.ref}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
