import asyncio
import os
import sys
from datetime import date, time, datetime, timezone, timedelta
import uuid

# Add current directory to path for app imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.session import get_db_context
from app.models.user import User, UserRole, UserStatus
from app.models.wallet import Wallet
from app.models.ground import Ground
from app.models.slot import Slot, SlotStatus
from app.models.booking import Booking, BookingSlot, BookingStatus, BookingSlotStatus
from app.models.review import Review
from app.models.promo_code import PromoCode, PromoCodeType
from app.core.security import hash_password

async def seed_data():
    print("Starting database seeding...")
    async with get_db_context() as db:
        # 1. Clear existing data in reverse order of relationships
        print("Clearing existing tables...")
        await db.execute(text("TRUNCATE TABLE reviews CASCADE"))
        await db.execute(text("TRUNCATE TABLE booking_slots CASCADE"))
        await db.execute(text("TRUNCATE TABLE payments CASCADE"))
        await db.execute(text("TRUNCATE TABLE bookings CASCADE"))
        await db.execute(text("TRUNCATE TABLE slots CASCADE"))
        await db.execute(text("TRUNCATE TABLE grounds CASCADE"))
        await db.execute(text("TRUNCATE TABLE wallet_transactions CASCADE"))
        await db.execute(text("TRUNCATE TABLE wallets CASCADE"))
        await db.execute(text("TRUNCATE TABLE refresh_tokens CASCADE"))
        await db.execute(text("TRUNCATE TABLE users CASCADE"))
        await db.execute(text("TRUNCATE TABLE promo_codes CASCADE"))
        await db.commit()

        # 2. Seed Users & Wallets
        print("Seeding users & wallets...")
        users_data = [
            {
                "name": "Pavan Kumar",
                "email": "user@bookmybox.com",
                "phone": "+91 98765 43210",
                "password": "password123",
                "city": "Hyderabad",
                "role": UserRole.USER,
                "wallet_balance": 1250,
            },
            {
                "name": "Anil Verma",
                "email": "anil@bookmybox.com",
                "phone": "+91 99887 12345",
                "password": "password123",
                "city": "Bengaluru",
                "role": UserRole.USER,
                "wallet_balance": 500,
            },
            {
                "name": "Admin Singh",
                "email": "admin@bookmybox.com",
                "phone": "+91 99000 11111",
                "password": "admin123",
                "city": "Hyderabad",
                "role": UserRole.ADMIN,
                "wallet_balance": 0,
            }
        ]

        users_map = {}
        for u in users_data:
            user_obj = User(
                name=u["name"],
                email=u["email"],
                phone=u["phone"],
                password_hash=hash_password(u["password"]),
                city=u["city"],
                role=u["role"],
                status=UserStatus.ACTIVE
            )
            db.add(user_obj)
            await db.flush()
            
            # Create wallet
            wallet_obj = Wallet(user_id=user_obj.id, balance=u["wallet_balance"])
            db.add(wallet_obj)
            await db.flush()
            
            users_map[u["email"]] = user_obj
            print(f"Created user: {u['name']} ({u['role'].value})")

        # 3. Seed Promo Codes
        print("Seeding promo codes...")
        promo_codes = [
            PromoCode(
                code="WELCOME10",
                type=PromoCodeType.PERCENTAGE,
                value=10,
                min_amount=500,
                max_discount=200,
                usage_limit=1000,
                valid_from=date.today() - timedelta(days=10),
                valid_to=date.today() + timedelta(days=90),
                is_active=True
            ),
            PromoCode(
                code="FLAT150",
                type=PromoCodeType.FLAT,
                value=150,
                min_amount=1000,
                max_discount=150,
                usage_limit=500,
                valid_from=date.today() - timedelta(days=5),
                valid_to=date.today() + timedelta(days=30),
                is_active=True
            )
        ]
        for pc in promo_codes:
            db.add(pc)
        await db.flush()

        # 4. Seed Grounds
        print("Seeding grounds...")
        grounds_data = [
            {
                "name": "Sixer Arena",
                "location": "Hitech City",
                "city": "Hyderabad",
                "price": 800,
                "rating": 4.7,
                "review_count": 184,
                "amenities": ["Floodlights", "Parking", "Cafeteria", "Live Scoring"],
                "tag": "POPULAR",
                "description": "Premium box cricket turf with LED floodlights, professional astro turf and netting on all sides. Perfect for corporate matches and friendly games.",
                "openTime": "06:00",
                "closeTime": "23:00",
                "gradient": "linear-gradient(135deg,#FFE500,#FF6B6B)",
                "icon": "🏏"
            },
            {
                "name": "PowerPlay Box",
                "location": "Gachibowli",
                "city": "Hyderabad",
                "price": 1000,
                "rating": 4.9,
                "review_count": 232,
                "amenities": ["Floodlights", "Parking", "Changing Room", "Cafeteria", "Live Scoring"],
                "tag": "PREMIUM",
                "description": "Top-rated venue with international-standard turf, live streaming and a full cafeteria.",
                "openTime": "06:00",
                "closeTime": "23:00",
                "gradient": "linear-gradient(135deg,#4ECDC4,#B388FF)",
                "icon": "🎯"
            },
            {
                "name": "Boundary Hitters",
                "location": "Kondapur",
                "city": "Hyderabad",
                "price": 600,
                "rating": 4.4,
                "review_count": 96,
                "amenities": ["Floodlights", "Parking"],
                "tag": "NEW",
                "description": "Budget-friendly box cricket ground with great turf quality.",
                "openTime": "07:00",
                "closeTime": "22:00",
                "gradient": "linear-gradient(135deg,#69F0AE,#FFE500)",
                "icon": "⚡"
            },
            {
                "name": "Yorker Zone",
                "location": "Madhapur",
                "city": "Hyderabad",
                "price": 900,
                "rating": 4.6,
                "review_count": 145,
                "amenities": ["Floodlights", "Cafeteria", "Live Scoring"],
                "tag": "POPULAR",
                "description": "Bowler-friendly turf with practice nets and a coaching area.",
                "openTime": "06:00",
                "closeTime": "23:00",
                "gradient": "linear-gradient(135deg,#B388FF,#FF6B6B)",
                "icon": "🔥"
            },
            {
                "name": "Cover Drive Cricket",
                "location": "Banjara Hills",
                "city": "Hyderabad",
                "price": 1200,
                "rating": 4.8,
                "review_count": 201,
                "amenities": ["Floodlights", "Parking", "Changing Room", "Cafeteria", "Live Scoring"],
                "tag": "PREMIUM",
                "description": "Elite venue with rooftop seating, live commentary and HD recording.",
                "openTime": "06:00",
                "closeTime": "24:00",
                "gradient": "linear-gradient(135deg,#FF6B6B,#FFE500)",
                "icon": "👑"
            },
            {
                "name": "Stumps & Wickets",
                "location": "Kukatpally",
                "city": "Hyderabad",
                "price": 500,
                "rating": 4.2,
                "review_count": 64,
                "amenities": ["Parking", "Changing Room"],
                "tag": "NEW",
                "description": "Affordable neighbourhood box cricket ground.",
                "openTime": "07:00",
                "closeTime": "22:00",
                "gradient": "linear-gradient(135deg,#4ECDC4,#FFE500)",
                "icon": " Stadium "
            },
            {
                "name": "Helmet Heroes Arena",
                "location": "Miyapur",
                "city": "Hyderabad",
                "price": 700,
                "rating": 4.5,
                "review_count": 118,
                "amenities": ["Floodlights", "Parking", "Cafeteria"],
                "tag": "POPULAR",
                "description": "Friendly turf with snack counter and ample parking.",
                "openTime": "06:00",
                "closeTime": "23:00",
                "gradient": "linear-gradient(135deg,#69F0AE,#4ECDC4)",
                "icon": " Helmet "
            },
            {
                "name": "Cricket Cage 360",
                "location": "Jubilee Hills",
                "city": "Hyderabad",
                "price": 1100,
                "rating": 4.7,
                "review_count": 173,
                "amenities": ["Floodlights", "Parking", "Changing Room", "Cafeteria", "Live Scoring"],
                "tag": "PREMIUM",
                "description": "Fully caged premium ground with smart booking kiosks.",
                "openTime": "06:00",
                "closeTime": "24:00",
                "gradient": "linear-gradient(135deg,#FFE500,#B388FF)",
                "icon": " Circus "
            },
            {
                "name": "Gully Cricket Club",
                "location": "Begumpet",
                "city": "Hyderabad",
                "price": 400,
                "rating": 4.3,
                "review_count": 52,
                "amenities": ["Parking", "Cafeteria"],
                "tag": "NEW",
                "description": "A cozy neighborhood box cricket setup that brings back the nostalgia of street cricket with modern turfs.",
                "openTime": "07:00",
                "closeTime": "22:00",
                "gradient": "linear-gradient(135deg,#FFE500,#69F0AE)",
                "icon": "🏏"
            },
            {
                "name": "The Turf Koramangala",
                "location": "Koramangala",
                "city": "Bengaluru",
                "price": 950,
                "rating": 4.8,
                "review_count": 120,
                "amenities": ["Floodlights", "Parking", "Changing Room", "Live Scoring"],
                "tag": "PREMIUM",
                "description": "High-end box turf in the heart of Koramangala, optimized for corporate matches and weekend tournaments.",
                "openTime": "06:00",
                "closeTime": "23:00",
                "gradient": "linear-gradient(135deg,#4ECDC4,#FFE500)",
                "icon": "🎯"
            },
            {
                "name": "Indiranagar Cricket Arena",
                "location": "Indiranagar",
                "city": "Bengaluru",
                "price": 850,
                "rating": 4.6,
                "review_count": 94,
                "amenities": ["Floodlights", "Parking", "Cafeteria"],
                "tag": "POPULAR",
                "description": "Popular youth hangout turf featuring international quality astro-turf and netting on all sides.",
                "openTime": "06:00",
                "closeTime": "23:00",
                "gradient": "linear-gradient(135deg,#B388FF,#FF6B6B)",
                "icon": "🔥"
            },
            {
                "name": "Whitefield Ground",
                "location": "Whitefield",
                "city": "Bengaluru",
                "price": 750,
                "rating": 4.5,
                "review_count": 81,
                "amenities": ["Floodlights", "Parking", "Live Scoring"],
                "tag": "POPULAR",
                "description": "Spacious box cricket arena located in IT hub Whitefield, perfect for stress-busting corporate sessions.",
                "openTime": "07:00",
                "closeTime": "22:00",
                "gradient": "linear-gradient(135deg,#69F0AE,#4ECDC4)",
                "icon": "⚡"
            }
        ]

        grounds_map = {}
        for g in grounds_data:
            ground_obj = Ground(
                name=g["name"],
                location=g["location"],
                city=g["city"],
                description=g["description"],
                price_per_hour=g["price"],
                rating=g["rating"],
                review_count=g["review_count"],
                amenities=g["amenities"],
                open_time=g["openTime"],
                close_time=g["closeTime"],
                slot_duration_minutes=60,
                tag=g["tag"],
                gradient=g["gradient"],
                icon=g["icon"],
                is_active=True
            )
            db.add(ground_obj)
            await db.flush()
            grounds_map[g["name"]] = ground_obj
            print(f"Created ground: {g['name']}")

        # 5. Seed Historical Bookings and Reviews
        # In mockData, reviews are written by: Rohit S., Priya M., Karthik R., Sneha T., Vikram J., Meera P.
        # We'll create dummy users or just link them all to the seeded normal user.
        print("Seeding reviews and bookings...")
        reviews_data = [
            {"user_name": "Rohit S.", "rating": 5, "text": "Top notch turf and floodlights. Booked 3 slots, got 10% off. Smooth experience!", "ground": "Sixer Arena"},
            {"user_name": "Priya M.", "rating": 5, "text": "Booking 4 slots for our office tournament was so easy. Loved the cart flow.", "ground": "PowerPlay Box"},
            {"user_name": "Karthik R.", "rating": 4, "text": "Great ground, parking was a bit tight on a Saturday night but turf was perfect.", "ground": "Boundary Hitters"},
            {"user_name": "Sneha T.", "rating": 5, "text": "Used the partial cancellation to refund one slot. Worked flawlessly.", "ground": "Yorker Zone"},
            {"user_name": "Vikram J.", "rating": 4, "text": "Fast booking, no hidden charges. Will return.", "ground": "Cover Drive Cricket"},
            {"user_name": "Meera P.", "rating": 5, "text": "Best box cricket platform in the city. Period.", "ground": "Cricket Cage 360"}
        ]

        for i, r in enumerate(reviews_data):
            # Create a slot in the past
            past_date = date.today() - timedelta(days=(i + 1))
            ground_obj = grounds_map[r["ground"]]
            user_obj = users_map["user@bookmybox.com"]  # link reviews to Pavan Kumar for simplicity
            
            slot_obj = Slot(
                ground_id=ground_obj.id,
                date=past_date,
                start_time=time(18, 0),
                end_time=time(19, 0),
                price=ground_obj.price_per_hour,
                status=SlotStatus.BOOKED,
                duration_minutes=60
            )
            db.add(slot_obj)
            await db.flush()

            # Create Completed Booking
            booking_ref = f"BMB-2026-COMPLETED-{10000 + i}"
            booking_obj = Booking(
                ref=booking_ref,
                user_id=user_obj.id,
                ground_id=ground_obj.id,
                booking_date=past_date,
                total_amount=ground_obj.price_per_hour,
                discount=0,
                final_amount=ground_obj.price_per_hour,
                status=BookingStatus.COMPLETED
            )
            db.add(booking_obj)
            await db.flush()

            # Create Booking Slot
            bs_obj = BookingSlot(
                booking_id=booking_obj.id,
                slot_id=slot_obj.id,
                price=ground_obj.price_per_hour,
                status=BookingSlotStatus.ACTIVE
            )
            db.add(bs_obj)
            await db.flush()

            # Create Review
            review_obj = Review(
                user_id=user_obj.id,
                ground_id=ground_obj.id,
                booking_id=booking_obj.id,
                rating=r["rating"],
                text=f"{r['user_name']}: {r['text']}"
            )
            db.add(review_obj)
            await db.flush()
            print(f"Created completed booking and review for {r['ground']}")

        await db.commit()
        print("Database seeded successfully!")

from sqlalchemy import text

if __name__ == "__main__":
    asyncio.run(seed_data())
