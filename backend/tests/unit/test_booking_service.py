"""Unit tests for BookingService business logic."""

from datetime import date, time, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import uuid
import pytest

from app.core.exceptions import BadRequestException, SlotUnavailableException
from app.models.booking import Booking, BookingStatus, BookingSlotStatus, BookingSlot
from app.models.slot import Slot, SlotStatus
from app.models.ground import Ground
from app.models.payment import PaymentMethod, PaymentStatus
from app.models.wallet import Wallet, WalletTransactionType
from app.models.promo_code import PromoCode, PromoCodeType
from app.services.booking import BookingService


@pytest.mark.asyncio
async def test_create_booking_success_wallet(mock_db, mock_redis):
    """Test successful booking creation using Wallet payment."""
    user_id = uuid.uuid4()
    ground_id = uuid.uuid4()
    booking_date = date.today() + timedelta(days=1)
    
    # Mock ground
    ground = Ground(id=ground_id, name="Test Ground", price_per_hour=800, is_active=True)
    
    # Mock slots
    slot1 = Slot(id=uuid.uuid4(), ground_id=ground_id, date=booking_date, start_time=time(10, 0), price=800, status=SlotStatus.AVAILABLE)
    slot2 = Slot(id=uuid.uuid4(), ground_id=ground_id, date=booking_date, start_time=time(11, 0), price=800, status=SlotStatus.AVAILABLE)
    slot_ids = [slot1.id, slot2.id]
    
    # Mock wallet
    wallet = Wallet(id=uuid.uuid4(), user_id=user_id, balance=2000)

    # Instantiate service
    service = BookingService(mock_db)
    
    # Mock repositories
    service.ground_repo.get = AsyncMock(return_value=ground)
    service.slot_repo.get_with_lock = AsyncMock(side_effect=[slot1, slot2])
    service.wallet_repo.get_or_create_by_user_id = AsyncMock(return_value=wallet)

    # Call service method
    booking = await service.create_booking(
        user_id=user_id,
        ground_id=ground_id,
        booking_date=booking_date,
        slot_ids=slot_ids,
        promo_code_str=None,
        payment_method=PaymentMethod.WALLET,
    )

    # Assertions
    assert booking.user_id == user_id
    assert booking.ground_id == ground_id
    assert booking.total_amount == 1600
    assert booking.discount == 0
    assert booking.final_amount == 1600
    assert booking.status == BookingStatus.CONFIRMED
    assert wallet.balance == 400  # 2000 - 1600
    
    # Verify DB flushes and adds
    assert mock_db.add.call_count >= 5  # Booking, 2 BookingSlots, 1 Wallet, 1 WalletTx, 1 Payment


@pytest.mark.asyncio
async def test_create_booking_bulk_discount(mock_db, mock_redis):
    """Test 10% discount gets automatically applied for 3+ slots."""
    user_id = uuid.uuid4()
    ground_id = uuid.uuid4()
    booking_date = date.today() + timedelta(days=1)
    
    ground = Ground(id=ground_id, name="Test Ground", price_per_hour=1000, is_active=True)
    slot1 = Slot(id=uuid.uuid4(), ground_id=ground_id, date=booking_date, start_time=time(10, 0), price=1000, status=SlotStatus.AVAILABLE)
    slot2 = Slot(id=uuid.uuid4(), ground_id=ground_id, date=booking_date, start_time=time(11, 0), price=1000, status=SlotStatus.AVAILABLE)
    slot3 = Slot(id=uuid.uuid4(), ground_id=ground_id, date=booking_date, start_time=time(12, 0), price=1000, status=SlotStatus.AVAILABLE)
    slot_ids = [slot1.id, slot2.id, slot3.id]
    
    wallet = Wallet(id=uuid.uuid4(), user_id=user_id, balance=5000)

    service = BookingService(mock_db)
    service.ground_repo.get = AsyncMock(return_value=ground)
    service.slot_repo.get_with_lock = AsyncMock(side_effect=[slot1, slot2, slot3])
    service.wallet_repo.get_or_create_by_user_id = AsyncMock(return_value=wallet)

    booking = await service.create_booking(
        user_id=user_id,
        ground_id=ground_id,
        booking_date=booking_date,
        slot_ids=slot_ids,
        promo_code_str=None,
        payment_method=PaymentMethod.WALLET,
    )

    # 3 slots at 1000 each = 3000 total. 10% off = 300 discount. Final = 2700.
    assert booking.total_amount == 3000
    assert booking.discount == 300
    assert booking.final_amount == 2700
    assert wallet.balance == 2300


@pytest.mark.asyncio
async def test_create_booking_promo_code(mock_db, mock_redis):
    """Test valid percentage promo code calculation and capping."""
    user_id = uuid.uuid4()
    ground_id = uuid.uuid4()
    booking_date = date.today() + timedelta(days=1)
    
    ground = Ground(id=ground_id, name="Test Ground", price_per_hour=1000, is_active=True)
    slot1 = Slot(id=uuid.uuid4(), ground_id=ground_id, date=booking_date, start_time=time(10, 0), price=1000, status=SlotStatus.AVAILABLE)
    slot_ids = [slot1.id]
    
    wallet = Wallet(id=uuid.uuid4(), user_id=user_id, balance=5000)
    
    # 50% discount capped at ₹200
    promo = PromoCode(
        code="HALFPRICE",
        type=PromoCodeType.PERCENTAGE,
        value=50,
        min_amount=500,
        max_discount=200,
        valid_from=date.today() - timedelta(days=1),
        valid_to=date.today() + timedelta(days=1),
        is_active=True,
        usage_limit=10,
        used_count=0
    )

    service = BookingService(mock_db)
    service.ground_repo.get = AsyncMock(return_value=ground)
    service.slot_repo.get_with_lock = AsyncMock(return_value=slot1)
    service.promo_repo.get_by_code = AsyncMock(return_value=promo)
    service.wallet_repo.get_or_create_by_user_id = AsyncMock(return_value=wallet)

    booking = await service.create_booking(
        user_id=user_id,
        ground_id=ground_id,
        booking_date=booking_date,
        slot_ids=slot_ids,
        promo_code_str="HALFPRICE",
        payment_method=PaymentMethod.WALLET,
    )

    # 1000 total. 50% of 1000 is 500, but capped at 200. Final amount = 800.
    assert booking.total_amount == 1000
    assert booking.discount == 200
    assert booking.final_amount == 800
    assert promo.used_count == 1


@pytest.mark.asyncio
async def test_create_booking_unavailable_slot(mock_db, mock_redis):
    """Test exception raised when a slot is already booked."""
    user_id = uuid.uuid4()
    ground_id = uuid.uuid4()
    booking_date = date.today() + timedelta(days=1)
    
    ground = Ground(id=ground_id, name="Test Ground", price_per_hour=800, is_active=True)
    slot1 = Slot(id=uuid.uuid4(), ground_id=ground_id, date=booking_date, start_time=time(10, 0), price=800, status=SlotStatus.BOOKED)

    service = BookingService(mock_db)
    service.ground_repo.get = AsyncMock(return_value=ground)
    service.slot_repo.get_with_lock = AsyncMock(return_value=slot1)

    with pytest.raises(SlotUnavailableException):
        await service.create_booking(
            user_id=user_id,
            ground_id=ground_id,
            booking_date=booking_date,
            slot_ids=[slot1.id],
            promo_code_str=None,
            payment_method=PaymentMethod.WALLET,
        )


@pytest.mark.asyncio
async def test_cancel_booking_policy_violation(mock_db):
    """Test cancellation blocked if less than 6 hours before slot start."""
    user_id = uuid.uuid4()
    booking_id = uuid.uuid4()
    
    # Slot starts 3 hours from now
    slot_time = (datetime.now() + timedelta(hours=3)).time()
    
    booking = Booking(
        id=booking_id,
        user_id=user_id,
        booking_date=date.today(),
        status=BookingStatus.CONFIRMED,
        final_amount=800,
    )
    slot = Slot(id=uuid.uuid4(), start_time=slot_time, status=SlotStatus.BOOKED)
    booking_slot = BookingSlot(booking_id=booking_id, slot=slot, status=BookingSlotStatus.ACTIVE, price=800)
    booking.booking_slots = [booking_slot]

    service = BookingService(mock_db)
    service.booking_repo.get_details = AsyncMock(return_value=booking)

    with pytest.raises(BadRequestException) as exc:
        await service.cancel_booking(user_id, booking_id)
        
    assert "Cancellation policy violation" in str(exc.value)
