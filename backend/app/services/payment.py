"""Payment service managing mock gateways, transaction initiation, and webhook confirmations."""

from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.core.logging import get_logger
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.booking import BookingStatus, BookingSlotStatus
from app.models.slot import SlotStatus
from app.repositories.payment import PaymentRepository
from app.repositories.booking import BookingRepository
from app.repositories.slot import SlotRepository

logger = get_logger(__name__)


class PaymentService:
    """Service handling payment gateways and confirmation lifecycle."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.payment_repo = PaymentRepository(db)
        self.booking_repo = BookingRepository(db)
        self.slot_repo = SlotRepository(db)

    async def initiate_payment(
        self, user_id: uuid.UUID, booking_id: uuid.UUID, method: PaymentMethod
    ) -> Payment:
        """Initiate payment transaction for an existing booking."""
        booking = await self.booking_repo.get_details(booking_id)
        if not booking:
            raise NotFoundException("Booking not found")

        if booking.user_id != user_id:
            raise BadRequestException("Access denied to this booking")

        # Check if there is already a successful payment
        existing_payments = await self.payment_repo.get_by_booking_id(booking_id)
        for p in existing_payments:
            if p.status == PaymentStatus.SUCCESS:
                raise BadRequestException("Booking has already been successfully paid")

        # Generate a unique transaction reference
        tx_ref = f"TXN-MOCK-{uuid.uuid4().hex[:12].upper()}"

        payment = Payment(
            booking_id=booking_id,
            user_id=user_id,
            amount=booking.final_amount,
            method=method,
            status=PaymentStatus.PENDING,
            transaction_ref=tx_ref,
        )
        self.db.add(payment)
        await self.db.flush()

        logger.info("payment_initiated", booking_ref=booking.ref, tx_ref=tx_ref, amount=booking.final_amount)
        return payment

    async def confirm_payment(
        self, transaction_ref: str, status: PaymentStatus, gateway_response: Optional[dict] = None
    ) -> Payment:
        """Confirm a pending payment transaction (simulates webhook or payment verification)."""
        payment = await self.payment_repo.get_by_transaction_ref(transaction_ref)
        if not payment:
            raise NotFoundException(f"Payment with transaction reference {transaction_ref} not found")

        if payment.status in (PaymentStatus.SUCCESS, PaymentStatus.FAILED, PaymentStatus.REFUNDED):
            logger.info("payment_already_processed", tx_ref=transaction_ref, current_status=payment.status)
            return payment

        payment.status = status
        payment.gateway_response = gateway_response or {}
        self.db.add(payment)

        # Retrieve booking to update state based on payment outcome
        booking = await self.booking_repo.get_details(payment.booking_id)
        if not booking:
            raise NotFoundException("Booking associated with this payment not found")

        if status == PaymentStatus.SUCCESS:
            booking.status = BookingStatus.CONFIRMED
            self.db.add(booking)
            
            # Ensure slots are marked booked
            for bs in booking.booking_slots:
                slot = bs.slot
                if slot.status != SlotStatus.BOOKED:
                    slot.status = SlotStatus.BOOKED
                    self.db.add(slot)
            logger.info("payment_success_booking_confirmed", booking_ref=booking.ref, tx_ref=transaction_ref)

        elif status == PaymentStatus.FAILED:
            # If payment failed, cancel the booking and release slots
            booking.status = BookingStatus.CANCELLED
            self.db.add(booking)

            for bs in booking.booking_slots:
                bs.status = BookingSlotStatus.CANCELLED
                self.db.add(bs)
                
                slot = bs.slot
                slot.status = SlotStatus.AVAILABLE
                self.db.add(slot)
            logger.info("payment_failed_booking_cancelled", booking_ref=booking.ref, tx_ref=transaction_ref)

        await self.db.flush()
        return payment
