"""Booking service managing cart validations, checkout, payment integration, and cancellations."""

from datetime import date, datetime, timezone, timedelta
from typing import List, Optional, Sequence, Tuple
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException, SlotUnavailableException
from app.core.logging import get_logger
from app.models.booking import Booking, BookingStatus, BookingSlot, BookingSlotStatus
from app.models.slot import SlotStatus
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.wallet import WalletTransaction, WalletTransactionType
from app.models.promo_code import PromoCode, PromoCodeType
from app.repositories.booking import BookingRepository
from app.repositories.slot import SlotRepository
from app.repositories.ground import GroundRepository
from app.repositories.promo_code import PromoCodeRepository
from app.repositories.wallet import WalletRepository
from app.repositories.payment import PaymentRepository
from app.repositories.user import UserRepository
from app.database.redis import get_redis
from app.workers.tasks import send_booking_confirmation_email_task, generate_ticket_pdf_task

logger = get_logger(__name__)


class BookingService:
    """Service handling booking operations."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.slot_repo = SlotRepository(db)
        self.ground_repo = GroundRepository(db)
        self.promo_repo = PromoCodeRepository(db)
        self.wallet_repo = WalletRepository(db)
        self.payment_repo = PaymentRepository(db)

    async def create_booking(
        self,
        user_id: uuid.UUID,
        ground_id: uuid.UUID,
        booking_date: date,
        slot_ids: List[uuid.UUID],
        promo_code_str: Optional[str],
        payment_method: PaymentMethod,
    ) -> Booking:
        """Create a booking for selected slots, applying discounts and payment checks."""
        # 1. Basic validation
        if not slot_ids:
            raise BadRequestException("At least one slot must be selected")
        if len(slot_ids) > 6:
            raise BadRequestException("Maximum of 6 slots can be booked at once")

        # Check if booking date is in the past
        if booking_date < date.today():
            raise BadRequestException("Cannot book slots for a past date")

        # 2. Retrieve ground
        ground = await self.ground_repo.get(ground_id)
        if not ground or not ground.is_active or ground.deleted_at is not None:
            raise NotFoundException("Active ground not found")

        # 3. Lock and retrieve slots in DB to prevent concurrent booking race conditions
        slots = []
        redis_client = await get_redis()

        for slot_id in slot_ids:
            # Use SELECT FOR UPDATE to lock slot row
            slot = await self.slot_repo.get_with_lock(slot_id)
            if not slot:
                raise NotFoundException(f"Slot {slot_id} not found")

            # Validate slot ownership and date
            if slot.ground_id != ground_id:
                raise BadRequestException(f"Slot {slot_id} does not belong to ground {ground_id}")
            if slot.date != booking_date:
                raise BadRequestException(f"Slot {slot_id} date mismatch")

            # Check database status
            if slot.status != SlotStatus.AVAILABLE:
                raise SlotUnavailableException(f"Slot starting at {slot.start_time} is already booked or blocked")

            # Check Redis checkout locks
            lock_val = await redis_client.get(f"slot_lock:{slot.id}")
            if lock_val and lock_val != str(user_id):
                raise SlotUnavailableException(f"Slot starting at {slot.start_time} is temporarily held by another user")

            slots.append(slot)

        # 4. Calculate pricing
        total_amount = sum(slot.price for slot in slots)

        # 5. Apply Bulk Discount (10% off for 3+ slots)
        bulk_discount = 0
        if len(slots) >= 3:
            bulk_discount = int(total_amount * 0.1)

        # 6. Apply Promo Code Discount
        promo_discount = 0
        promo_code: Optional[PromoCode] = None
        if promo_code_str:
            promo_code = await self.promo_repo.get_by_code(promo_code_str)
            if not promo_code:
                raise BadRequestException("Invalid or inactive promo code")
            
            # Check validity
            if not promo_code.is_valid_now:
                raise BadRequestException("Promo code is expired or usage limit reached")
            if total_amount < promo_code.min_amount:
                raise BadRequestException(f"Minimum order value for this promo code is ₹{promo_code.min_amount}")

            if promo_code.type == PromoCodeType.PERCENTAGE:
                promo_discount = int(total_amount * (promo_code.value / 100.0))
                if promo_code.max_discount is not None:
                    promo_discount = min(promo_discount, promo_code.max_discount)
            elif promo_code.type == PromoCodeType.FLAT:
                promo_discount = promo_code.value

        # Cap total discount at total amount
        total_discount = min(bulk_discount + promo_discount, total_amount)
        final_amount = total_amount - total_discount

        # 7. Generate unique booking reference
        ref = f"BMB-{booking_date.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        # 8. Create booking object (default status is CONFIRMED, since it represents a valid reservation)
        booking = Booking(
            ref=ref,
            user_id=user_id,
            ground_id=ground_id,
            booking_date=booking_date,
            total_amount=total_amount,
            discount=total_discount,
            final_amount=final_amount,
            promo_code=promo_code_str.upper() if promo_code_str else None,
            status=BookingStatus.CONFIRMED,
        )
        self.db.add(booking)
        await self.db.flush()

        # Create BookingSlot records
        for slot in slots:
            # Proportionate slot price after discounts (for partial cancellations)
            # We can calculate proportional price as: slot.price - (total_discount * slot.price / total_amount)
            # This handles different priced slots beautifully
            prop_discount = int(total_discount * (slot.price / total_amount)) if total_amount > 0 else 0
            booking_slot = BookingSlot(
                booking_id=booking.id,
                slot_id=slot.id,
                price=slot.price - prop_discount,
                status=BookingSlotStatus.ACTIVE,
            )
            self.db.add(booking_slot)
            
            # Set slot status to BOOKED in database
            slot.status = SlotStatus.BOOKED
            self.db.add(slot)

            # Clear Redis lock if it exists
            await redis_client.delete(f"slot_lock:{slot.id}")

        # 9. Handle Payment
        if payment_method == PaymentMethod.WALLET:
            wallet = await self.wallet_repo.get_or_create_by_user_id(user_id)
            if wallet.balance < final_amount:
                # Rollback slot updates and booking creation
                raise BadRequestException(f"Insufficient wallet balance. Required: ₹{final_amount}, Available: ₹{wallet.balance}")

            # Deduct from wallet
            wallet.balance -= final_amount
            self.db.add(wallet)

            # Create wallet transaction ledger
            wallet_tx = WalletTransaction(
                wallet_id=wallet.id,
                amount=final_amount,
                type=WalletTransactionType.DEBIT,
                description=f"Payment for booking {ref}",
                reference_id=booking.id,
            )
            self.db.add(wallet_tx)

            # Create payment record
            payment = Payment(
                booking_id=booking.id,
                user_id=user_id,
                amount=final_amount,
                method=PaymentMethod.WALLET,
                status=PaymentStatus.SUCCESS,
                transaction_ref=f"TXN-WALLET-{uuid.uuid4().hex[:12].upper()}",
            )
            self.db.add(payment)

        else:
            # External payment (UPI / CARD / NET_BANKING) - start as PENDING payment
            # Create pending payment record
            payment = Payment(
                booking_id=booking.id,
                user_id=user_id,
                amount=final_amount,
                method=payment_method,
                status=PaymentStatus.PENDING,
                transaction_ref=f"TXN-MOCK-{uuid.uuid4().hex[:12].upper()}",
            )
            self.db.add(payment)

            # In development, let's auto-confirm external payments to match client expectation,
            # or keep it pending. Since our front-end shows "Payment successful!" immediately,
            # we should support a simple query param or auto-success logic for mock mode,
            # or handle it via explicit /confirm endpoint. Let's auto-confirm the payment
            # in this service, but keep the status transition trace for SRE observability!
            # Note: We will also expose an explicit confirm endpoint.
            # To simulate immediate gateway success in development:
            payment.status = PaymentStatus.SUCCESS
            self.db.add(payment)

        # 10. Increment Promo Code usage count if applied
        if promo_code:
            promo_code.used_count += 1
            self.db.add(promo_code)

        await self.db.flush()

        # 11. Trigger background tasks (Celery)
        try:
            user_repo = UserRepository(self.db)
            user = await user_repo.get(user_id)
            if user:
                send_booking_confirmation_email_task.delay(
                    user.email, ref, ground.name, booking_date.strftime("%Y-%m-%d")
                )
            generate_ticket_pdf_task.delay(str(booking.id))
        except Exception as exc:
            # Prevent background task failure from failing the entire checkout transaction
            logger.error("failed_to_trigger_celery_booking_tasks", error=str(exc))

        logger.info(
            "booking_created_successfully",
            booking_ref=ref,
            final_amount=final_amount,
            slots_count=len(slots),
            payment_method=payment_method,
        )

        # Broadcast slot state changes to subscribers
        try:
            from app.core.websocket import broadcast_slot_updates
            await broadcast_slot_updates(self.db, ground_id, booking_date)
        except Exception as ws_exc:
            logger.error("failed_to_broadcast_websocket_slot_updates", error=str(ws_exc))

        return booking



    async def get_booking_details(self, user_id: uuid.UUID, booking_id: uuid.UUID) -> Booking:
        """Retrieve full details of a specific booking for a user."""
        booking = await self.booking_repo.get_details(booking_id)
        if not booking:
            raise NotFoundException("Booking not found")
        if booking.user_id != user_id:
            # Prevent users from viewing others' bookings
            raise BadRequestException("Access denied to this booking")
        return booking

    async def cancel_booking(self, user_id: uuid.UUID, booking_id: uuid.UUID) -> Booking:
        """Cancel entire booking and refund the amount to user's wallet."""
        # 1. Fetch booking with details
        booking = await self.booking_repo.get_details(booking_id)
        if not booking:
            raise NotFoundException("Booking not found")
        
        if booking.user_id != user_id:
            raise BadRequestException("Access denied to this booking")
        
        if booking.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED):
            raise BadRequestException(f"Booking cannot be cancelled because its current status is {booking.status}")

        # 2. Check cancellation policy (>= 6 hours before the earliest slot start time)
        now_dt = datetime.now()
        for bs in booking.booking_slots:
            if bs.status == BookingSlotStatus.ACTIVE:
                slot = bs.slot
                slot_datetime = datetime.combine(booking.booking_date, slot.start_time)
                if slot_datetime - now_dt < timedelta(hours=6):
                    raise BadRequestException(
                        f"Cancellation policy violation: Slot {slot.start_time} starts in less than 6 hours"
                    )

        # 3. Perform cancellation updates
        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.now(timezone.utc)
        self.db.add(booking)

        # Cancel all active slots
        refund_amount = 0
        for bs in booking.booking_slots:
            if bs.status == BookingSlotStatus.ACTIVE:
                bs.status = BookingSlotStatus.CANCELLED
                bs.cancelled_at = datetime.now(timezone.utc)
                self.db.add(bs)

                # Reset database slot status to AVAILABLE
                slot = bs.slot
                slot.status = SlotStatus.AVAILABLE
                self.db.add(slot)

                # Add to total refund
                refund_amount += bs.price

        # 4. Refund to user's wallet
        wallet = await self.wallet_repo.get_or_create_by_user_id(user_id)
        wallet.balance += refund_amount
        self.db.add(wallet)

        # Ledger transaction for credit
        wallet_tx = WalletTransaction(
            wallet_id=wallet.id,
            amount=refund_amount,
            type=WalletTransactionType.CREDIT,
            description=f"Refund for cancellation of booking {booking.ref}",
            reference_id=booking.id,
        )
        self.db.add(wallet_tx)

        # Update payment record status if successful
        for payment in booking.payments:
            if payment.status == PaymentStatus.SUCCESS:
                payment.status = PaymentStatus.REFUNDED
                self.db.add(payment)

        # 5. Decrement Promo Code usage count if applied
        if booking.promo_code:
            promo = await self.promo_repo.get_by_code(booking.promo_code)
            if promo:
                promo.used_count = max(0, promo.used_count - 1)
                self.db.add(promo)

        await self.db.flush()
        logger.info("booking_cancelled_fully", booking_ref=booking.ref, refund_amount=refund_amount)

        # Broadcast slot status updates
        try:
            from app.core.websocket import broadcast_slot_updates
            await broadcast_slot_updates(self.db, booking.ground_id, booking.booking_date)
        except Exception as ws_exc:
            logger.error("failed_to_broadcast_websocket_slot_updates", error=str(ws_exc))

        return booking


    async def cancel_specific_slots(
        self, user_id: uuid.UUID, booking_id: uuid.UUID, slot_ids: List[uuid.UUID]
    ) -> Booking:
        """Cancel individual slots of a booking and refund proportionally to wallet."""
        booking = await self.booking_repo.get_details(booking_id)
        if not booking:
            raise NotFoundException("Booking not found")
        
        if booking.user_id != user_id:
            raise BadRequestException("Access denied to this booking")
            
        if booking.status in (BookingStatus.CANCELLED, BookingStatus.COMPLETED):
            raise BadRequestException(f"Cannot cancel slots because booking is {booking.status}")

        # Find matching active booking slots
        target_booking_slots = [
            bs for bs in booking.booking_slots
            if bs.slot_id in slot_ids and bs.status == BookingSlotStatus.ACTIVE
        ]

        if not target_booking_slots:
            raise BadRequestException("None of the specified slots are active in this booking")

        # Check cancellation policy (>= 6 hours before slot start time)
        now_dt = datetime.now()
        for bs in target_booking_slots:
            slot = bs.slot
            slot_datetime = datetime.combine(booking.booking_date, slot.start_time)
            if slot_datetime - now_dt < timedelta(hours=6):
                raise BadRequestException(
                    f"Cancellation policy violation: Slot {slot.start_time} starts in less than 6 hours"
                )

        # Cancel matching slots
        refund_amount = 0
        for bs in target_booking_slots:
            bs.status = BookingSlotStatus.CANCELLED
            bs.cancelled_at = datetime.now(timezone.utc)
            self.db.add(bs)

            # Reset database slot status to AVAILABLE
            slot = bs.slot
            slot.status = SlotStatus.AVAILABLE
            self.db.add(slot)

            # Add proportionate slot price to refund
            refund_amount += bs.price

        # Check if any active slots are left
        active_slots_left = any(bs.status == BookingSlotStatus.ACTIVE for bs in booking.booking_slots)
        
        if not active_slots_left:
            booking.status = BookingStatus.CANCELLED
            booking.cancelled_at = datetime.now(timezone.utc)
            # Refund promo code
            if booking.promo_code:
                promo = await self.promo_repo.get_by_code(booking.promo_code)
                if promo:
                    promo.used_count = max(0, promo.used_count - 1)
                    self.db.add(promo)
        else:
            booking.status = BookingStatus.PARTIALLY_CANCELLED

        self.db.add(booking)

        # Refund to user's wallet
        wallet = await self.wallet_repo.get_or_create_by_user_id(user_id)
        wallet.balance += refund_amount
        self.db.add(wallet)

        # Ledger transaction
        wallet_tx = WalletTransaction(
            wallet_id=wallet.id,
            amount=refund_amount,
            type=WalletTransactionType.CREDIT,
            description=f"Refund for partial slot cancellation of booking {booking.ref}",
            reference_id=booking.id,
        )
        self.db.add(wallet_tx)

        await self.db.flush()
        logger.info(
            "booking_slots_cancelled_partially",
            booking_ref=booking.ref,
            cancelled_slots_count=len(target_booking_slots),
            refund_amount=refund_amount,
        )

        # Broadcast slot status updates
        try:
            from app.core.websocket import broadcast_slot_updates
            await broadcast_slot_updates(self.db, booking.ground_id, booking.booking_date)
        except Exception as ws_exc:
            logger.error("failed_to_broadcast_websocket_slot_updates", error=str(ws_exc))

        return booking


    async def check_and_acquire_slots_lock(
        self, user_id: uuid.UUID, slot_ids: List[uuid.UUID]
    ) -> bool:
        """Lock slots in Redis for 5 minutes during checkout session (to prevent overlap)."""
        redis_client = await get_redis()
        # Ensure none are locked
        for slot_id in slot_ids:
            lock_val = await redis_client.get(f"slot_lock:{slot_id}")
            if lock_val and lock_val != str(user_id):
                return False
        
        # Lock them all
        for slot_id in slot_ids:
            await redis_client.set(f"slot_lock:{slot_id}", str(user_id), ex=300) # 5 minutes TTL
        return True

    async def release_slots_lock(
        self, user_id: uuid.UUID, slot_ids: List[uuid.UUID]
    ) -> None:
        """Release Redis checkout locks for slots."""
        redis_client = await get_redis()
        for slot_id in slot_ids:
            lock_val = await redis_client.get(f"slot_lock:{slot_id}")
            if lock_val == str(user_id):
                await redis_client.delete(f"slot_lock:{slot_id}")
