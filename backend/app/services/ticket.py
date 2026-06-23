"""Ticket service to generate PDF booking tickets."""

from io import BytesIO
from typing import Optional
import uuid

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas

from app.models.booking import Booking


class TicketService:
    """Service to handle generation of PDF booking tickets."""

    @staticmethod
    def generate_pdf_ticket(booking: Booking) -> BytesIO:
        """Generate a PDF ticket for a booking in memory."""
        buffer = BytesIO()
        
        # Create PDF canvas
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setTitle(f"BookMyBox Ticket - {booking.ref}")

        # Page setup
        width, height = letter

        # Colors
        navy = colors.HexColor("#1A2B4C")
        yellow = colors.HexColor("#FFBE0B")
        ink = colors.HexColor("#121212")
        light_gray = colors.HexColor("#F8F9FA")
        border_gray = colors.HexColor("#E5E5E5")

        # --- Draw Modern Neo-Brutalist Frame / Header ---
        # Main background
        p.setFillColor(light_gray)
        p.rect(20, 20, width - 40, height - 40, fill=True, stroke=True)

        # Header block
        p.setFillColor(navy)
        p.rect(30, height - 120, width - 60, 90, fill=True, stroke=False)

        # Title
        p.setFillColor(colors.white)
        p.setFont("Helvetica-Bold", 26)
        p.drawString(50, height - 80, "BOOKMYBOX TICKET")

        p.setFont("Helvetica", 12)
        p.drawString(50, height - 105, "Show this QR/Reference code at the venue entry")

        # --- Booking Info ---
        p.setFillColor(ink)
        p.setFont("Helvetica-Bold", 14)
        p.drawString(40, height - 160, "BOOKING DETAILS")

        # Left Column
        p.setFont("Helvetica", 11)
        p.drawString(40, height - 190, "Ground:")
        p.drawString(40, height - 215, "Location:")
        p.drawString(40, height - 240, "Date:")
        p.drawString(40, height - 265, "Status:")

        p.setFont("Helvetica-Bold", 11)
        p.drawString(140, height - 190, booking.ground.name)
        p.drawString(140, height - 215, booking.ground.location)
        p.drawString(140, height - 240, booking.booking_date.strftime("%A, %B %d, %Y"))
        p.drawString(140, height - 265, booking.status.value)

        # Right Column (Reference Card)
        p.setFillColor(yellow)
        p.rect(width - 240, height - 260, 200, 100, fill=True, stroke=True)
        p.setStrokeColor(ink)
        p.setLineWidth(2)

        p.setFillColor(ink)
        p.setFont("Helvetica-Bold", 10)
        p.drawCentredString(width - 140, height - 185, "BOOKING REFERENCE")
        p.setFont("Courier-Bold", 14)
        p.drawCentredString(width - 140, height - 220, booking.ref)

        # --- Divider ---
        p.setStrokeColor(border_gray)
        p.setLineWidth(1)
        p.line(40, height - 290, width - 40, height - 290)

        # --- Booked Slots ---
        p.setFont("Helvetica-Bold", 14)
        p.drawString(40, height - 320, "RESERVED SLOTS")

        p.setFont("Helvetica-Bold", 10)
        p.setFillColor(colors.HexColor("#555555"))
        p.drawString(50, height - 350, "SLOT TIME")
        p.drawRightString(width - 50, height - 350, "PRICE")
        p.line(40, height - 355, width - 40, height - 355)

        y = height - 380
        p.setFillColor(ink)
        p.setFont("Helvetica", 11)
        
        for bs in booking.booking_slots:
            slot_status_str = f" ({bs.status.value})" if bs.status != "ACTIVE" else ""
            p.drawString(50, y, f"{bs.slot.start_time.strftime('%H:%M')} - {bs.slot.end_time.strftime('%H:%M')}{slot_status_str}")
            p.drawRightString(width - 50, y, f"INR {bs.price}")
            y -= 25

        p.line(40, y + 10, width - 40, y + 10)

        # --- Price Calculation ---
        y -= 20
        p.setFont("Helvetica", 11)
        p.drawString(width - 250, y, "Total Amount:")
        p.drawRightString(width - 50, y, f"INR {booking.total_amount}")
        
        y -= 20
        p.drawString(width - 250, y, "Discounts/Promo:")
        p.drawRightString(width - 50, y, f"- INR {booking.discount}")
        
        y -= 25
        p.setFont("Helvetica-Bold", 13)
        p.drawString(width - 250, y, "Final Amount Paid:")
        p.drawRightString(width - 50, y, f"INR {booking.final_amount}")

        # --- Bottom Terms/Brutalist Box ---
        p.setFillColor(colors.HexColor("#F0F0F0"))
        p.rect(40, 50, width - 80, 100, fill=True, stroke=False)
        p.setFillColor(ink)
        p.setFont("Helvetica-Bold", 10)
        p.drawString(55, 130, "TERMS AND CONDITIONS:")
        p.setFont("Helvetica", 9)
        p.drawString(55, 110, "1. Please arrive 15 minutes prior to your slot time.")
        p.drawString(55, 95, "2. Studs or spiked shoes are strictly prohibited inside the box.")
        p.drawString(55, 80, "3. Cancellation policy: Free cancellation is allowed up to 6 hours before slot start time.")
        p.drawString(55, 65, "4. The management is not responsible for any personal injury or loss of belongings.")

        # Save page
        p.showPage()
        p.save()

        buffer.seek(0)
        return buffer
