"""Admin operations API endpoints."""

from datetime import date, datetime, timedelta
from typing import Any, List, Optional
import uuid

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy import select, func, text, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, get_current_admin
from app.core.exceptions import BadRequestException, NotFoundException
from app.core.responses import success_response, paginated_response
from app.models.user import User, UserStatus
from app.models.ground import Ground
from app.models.slot import Slot, SlotStatus
from app.models.booking import Booking, BookingStatus, BookingSlot, BookingSlotStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.admin import AdminStatsResponse, RevenueChartItem, BlockSlotsRequest, UnblockSlotsRequest, BulkUpdatePriceRequest
from app.schemas.ground import GroundResponse, GroundCreate, GroundUpdate
from app.schemas.slot import SlotResponse
from app.schemas.booking import BookingResponse
from app.schemas.user import UserResponse
from app.services.ground import GroundService
from app.services.slot import SlotService
from app.services.booking import BookingService
from app.repositories.user import UserRepository
from app.repositories.booking import BookingRepository

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(get_current_admin)])


@router.get("/stats", response_model=None, status_code=status.HTTP_200_OK)
async def get_admin_stats(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve system-wide summary metrics for dashboard."""
    # 1. Total revenue (sum of successful payments)
    revenue_stmt = select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == PaymentStatus.SUCCESS)
    revenue_res = await db.execute(revenue_stmt)
    total_revenue = revenue_res.scalar_one() or 0

    # 2. Bookings count
    bookings_stmt = select(func.count(Booking.id))
    bookings_res = await db.execute(bookings_stmt)
    bookings_count = bookings_res.scalar_one() or 0

    # 3. Users count
    users_stmt = select(func.count(User.id)).where(User.deleted_at.is_(None))
    users_res = await db.execute(users_stmt)
    users_count = users_res.scalar_one() or 0

    # 4. Grounds count
    grounds_stmt = select(func.count(Ground.id)).where(Ground.deleted_at.is_(None))
    grounds_res = await db.execute(grounds_stmt)
    grounds_count = grounds_res.scalar_one() or 0

    stats = AdminStatsResponse(
        revenue=total_revenue,
        bookings_count=bookings_count,
        users_count=users_count,
        grounds_count=grounds_count
    ).model_dump(mode="json")
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=stats, request_id=request_id)


@router.get("/revenue-chart", response_model=None, status_code=status.HTTP_200_OK)
async def get_revenue_chart(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve daily revenue over the last 30 days for metrics graphing."""
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    stmt = (
        select(
            func.cast(Payment.created_at, Date).label("payment_date"),
            func.coalesce(func.sum(Payment.amount), 0).label("daily_amount")
        )
        .where(
            Payment.status == PaymentStatus.SUCCESS,
            Payment.created_at >= thirty_days_ago
        )
        .group_by(func.cast(Payment.created_at, Date))
        .order_by(func.cast(Payment.created_at, Date))
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    chart_data = [
        RevenueChartItem(date=row.payment_date, amount=row.daily_amount).model_dump(mode="json")
        for row in rows
    ]
    
    # Cast date to string format for response
    for item in chart_data:
        item["date"] = item["date"].isoformat()
        
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=chart_data, request_id=request_id)


# --- Admin Grounds CRUD ---

@router.post("/grounds", status_code=status.HTTP_201_CREATED)
async def create_ground(
    request: Request,
    payload: GroundCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new sports ground facility."""
    ground_service = GroundService(db)
    # Check uniqueness by name or create directly
    ground = Ground(**payload.model_dump(mode="json"))
    db.add(ground)
    await db.flush()
    
    ground_data = GroundResponse.model_validate(ground).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=ground_data, message="Ground created successfully", request_id=request_id)


@router.put("/grounds/{id}", status_code=status.HTTP_200_OK)
async def update_ground(
    request: Request,
    id: uuid.UUID,
    payload: GroundUpdate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Modify details of an existing ground."""
    ground_service = GroundService(db)
    ground = await ground_service.ground_repo.get(id)
    if not ground or ground.deleted_at is not None:
        raise NotFoundException("Ground not found")

    updated_fields = payload.model_dump(exclude_unset=True)
    for field, val in updated_fields.items():
        setattr(ground, field, val)
    db.add(ground)
    await db.flush()
    
    ground_data = GroundResponse.model_validate(ground).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=ground_data, message="Ground updated successfully", request_id=request_id)


@router.patch("/grounds/{id}/status", status_code=status.HTTP_200_OK)
async def toggle_ground_status(
    request: Request,
    id: uuid.UUID,
    is_active: bool,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Enable or disable a ground for booking catalog lookup."""
    ground_service = GroundService(db)
    ground = await ground_service.ground_repo.get(id)
    if not ground or ground.deleted_at is not None:
        raise NotFoundException("Ground not found")

    ground.is_active = is_active
    db.add(ground)
    await db.flush()
    
    ground_data = GroundResponse.model_validate(ground).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    status_str = "activated" if is_active else "deactivated"
    return success_response(data=ground_data, message=f"Ground successfully {status_str}", request_id=request_id)


@router.delete("/grounds/{id}", status_code=status.HTTP_200_OK)
async def delete_ground(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Soft-delete a ground from the system."""
    ground_service = GroundService(db)
    deleted = await ground_service.ground_repo.soft_delete(id)
    if not deleted:
        raise NotFoundException("Ground not found or already deleted")
        
    request_id = getattr(request.state, "request_id", None)
    return success_response(message="Ground successfully soft-deleted", request_id=request_id)


# --- Admin Slots Management ---

@router.get("/grounds/{id}/slots", status_code=status.HTTP_200_OK)
async def get_admin_slots(
    request: Request,
    id: uuid.UUID,
    target_date: date = Query(..., alias="date"),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Get slots for a ground on a target date (creates slots on-demand if future)."""
    slot_service = SlotService(db)
    slots = await slot_service.get_slots_for_date(id, target_date)
    
    slots_data = [SlotResponse.model_validate(s).model_dump(mode="json") for s in slots]
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=slots_data, request_id=request_id)


@router.post("/slots/block", status_code=status.HTTP_200_OK)
async def block_slots_endpoint(
    request: Request,
    payload: BlockSlotsRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Administrative override to block specific slots from user bookings."""
    slot_service = SlotService(db)
    await slot_service.block_slots(payload.slot_ids)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(message="Slots blocked successfully", request_id=request_id)


@router.post("/slots/unblock", status_code=status.HTTP_200_OK)
async def unblock_slots_endpoint(
    request: Request,
    payload: UnblockSlotsRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Administrative override to release slot blocks back to AVAILABLE status."""
    slot_service = SlotService(db)
    await slot_service.unblock_slots(payload.slot_ids)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(message="Slots unblocked successfully", request_id=request_id)


@router.put("/slots/price", status_code=status.HTTP_200_OK)
async def bulk_update_slot_prices_endpoint(
    request: Request,
    payload: BulkUpdatePriceRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Bulk update prices of selected slots."""
    slot_service = SlotService(db)
    await slot_service.update_slot_prices(payload.slot_ids, payload.price)
    
    request_id = getattr(request.state, "request_id", None)
    return success_response(message="Slot prices updated successfully", request_id=request_id)


# --- Admin Bookings Management ---

@router.get("/bookings", status_code=status.HTTP_200_OK)
async def list_all_bookings(
    request: Request,
    search: Optional[str] = Query(None, description="Search by booking reference"),
    status_filter: Optional[BookingStatus] = Query(None, alias="status", description="Filter by booking status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Search and list all bookings globally."""
    booking_repo = BookingRepository(db)
    skip = (page - 1) * per_page
    bookings, total = await booking_repo.list_all_bookings_admin(
        search=search,
        status_filter=status_filter,
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
        message="All bookings retrieved successfully",
        request_id=request_id
    )


@router.get("/bookings/{id}", status_code=status.HTTP_200_OK)
async def get_booking_details_admin(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve full details of any booking."""
    booking_repo = BookingRepository(db)
    booking = await booking_repo.get_details(id)
    if not booking:
        raise NotFoundException("Booking not found")
        
    booking_data = BookingResponse.model_validate(booking).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=booking_data, request_id=request_id)


@router.post("/bookings/{id}/cancel", status_code=status.HTTP_200_OK)
async def admin_cancel_booking(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Admin cancel booking with immediate refund to wallet (bypasses standard policy check)."""
    # Force cancel booking: we use BookingService cancel flow but override the datetime checks by using a direct model cancellation
    booking_repo = BookingRepository(db)
    booking = await booking_repo.get_details(id)
    if not booking:
        raise NotFoundException("Booking not found")
        
    if booking.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED):
        raise BadRequestException(f"Booking is already in {booking.status.value} state")

    # Cancel booking
    booking.status = BookingStatus.CANCELLED
    booking.cancelled_at = datetime.now(timezone.utc)
    db.add(booking)

    # Cancel slots
    refund_amount = 0
    for bs in booking.booking_slots:
        if bs.status == BookingSlotStatus.ACTIVE:
            bs.status = BookingSlotStatus.CANCELLED
            bs.cancelled_at = datetime.now(timezone.utc)
            db.add(bs)
            
            slot = bs.slot
            slot.status = SlotStatus.AVAILABLE
            db.add(slot)
            
            refund_amount += bs.price

    # Refund wallet
    from app.services.wallet import WalletService
    wallet_service = WalletService(db)
    await wallet_service.top_up_wallet(
        user_id=booking.user_id,
        amount=refund_amount,
        description=f"Admin refund for cancellation of booking {booking.ref}"
    )

    # Mark payments as refunded
    for payment in booking.payments:
        if payment.status == PaymentStatus.SUCCESS:
            payment.status = PaymentStatus.REFUNDED
            db.add(payment)

    # Decrement Promo Code
    if booking.promo_code:
        from app.repositories.promo_code import PromoCodeRepository
        promo_repo = PromoCodeRepository(db)
        promo = await promo_repo.get_by_code(booking.promo_code)
        if promo:
            promo.used_count = max(0, promo.used_count - 1)
            db.add(promo)

    await db.flush()
    
    # Broadcast slot status updates to subscribers
    try:
        from app.core.websocket import broadcast_slot_updates
        await broadcast_slot_updates(db, booking.ground_id, booking.booking_date)
    except Exception as ws_exc:
        # We catch exceptions to prevent server error if WS fails
        pass

    booking_data = BookingResponse.model_validate(booking).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=booking_data, message="Booking cancelled and refunded by admin", request_id=request_id)


# --- Admin Users Management ---

@router.get("/users", status_code=status.HTTP_200_OK)
async def list_all_users(
    request: Request,
    search: Optional[str] = Query(None, description="Search users by name/email/phone"),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Search and list all users globally."""
    skip = (page - 1) * per_page
    stmt = select(User).where(User.deleted_at.is_(None))
    
    if search:
        stmt = stmt.where(
            User.name.ilike(f"%{search}%") | 
            User.email.ilike(f"%{search}%") | 
            User.phone.ilike(f"%{search}%")
        )
        
    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_res = await db.execute(count_stmt)
    total = count_res.scalar_one() or 0
    
    stmt = stmt.order_by(User.created_at.desc()).offset(skip).limit(per_page)
    result = await db.execute(stmt)
    users = result.scalars().all()
    
    users_data = [UserResponse.model_validate(u).model_dump(mode="json") for u in users]
    request_id = getattr(request.state, "request_id", None)
    return paginated_response(
        data=users_data,
        total=total,
        page=page,
        per_page=per_page,
        message="All users retrieved successfully",
        request_id=request_id
    )


@router.get("/users/{id}", status_code=status.HTTP_200_OK)
async def get_user_details_admin(
    request: Request,
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve full details of any user."""
    user_repo = UserRepository(db)
    user = await user_repo.get(id)
    if not user or user.deleted_at is not None:
        raise NotFoundException("User not found")
        
    user_data = UserResponse.model_validate(user).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    return success_response(data=user_data, request_id=request_id)


@router.patch("/users/{id}/status", status_code=status.HTTP_200_OK)
async def toggle_user_block_status(
    request: Request,
    id: uuid.UUID,
    status_val: UserStatus = Query(..., alias="status", description="New status (ACTIVE or BLOCKED)"),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """Block or unblock a user account."""
    if status_val not in (UserStatus.ACTIVE, UserStatus.BLOCKED):
        raise BadRequestException("Invalid status value. Must be ACTIVE or BLOCKED")
        
    user_repo = UserRepository(db)
    user = await user_repo.get(id)
    if not user or user.deleted_at is not None:
        raise NotFoundException("User not found")

    user.status = status_val
    db.add(user)
    await db.flush()
    
    user_data = UserResponse.model_validate(user).model_dump(mode="json")
    request_id = getattr(request.state, "request_id", None)
    action_str = "blocked" if status_val == UserStatus.BLOCKED else "unblocked"
    return success_response(data=user_data, message=f"User successfully {action_str}", request_id=request_id)
