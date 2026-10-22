"""
Seed script to populate an expanded, rich demo catalog for AgenticBuy.
Multiple merchants across diverse categories (Electronics, Gaming, Footwear, Smart Home).
"""

import asyncio
import uuid
from decimal import Decimal

from sqlalchemy import select, delete

from app.auth.utils import hash_password
from app.database import async_session, init_db
from app.models.crawl import CrawlJob
from app.models.merchant import Merchant
from app.models.negotiation import NegotiationMessage, NegotiationSession
from app.models.order import Order
from app.models.product import Product
from app.models.user import User


async def seed():
    print("Initializing database...")
    await init_db()

    async with async_session() as db:
        # Clear existing demo data to rebuild clean multi-merchant catalog
        print("Clearing old demo data...")
        await db.execute(delete(CrawlJob))
        await db.execute(delete(Order))
        await db.execute(delete(NegotiationMessage))
        await db.execute(delete(NegotiationSession))
        await db.execute(delete(Product))
        await db.execute(delete(Merchant))
        await db.execute(delete(User))
        await db.commit()

        print("Creating demo users and merchants...")
        # 1. TechGear Store (Electronics & Audio)
        user_m1 = User(
            id=uuid.uuid4(),
            email="merchant@techgear.com",
            hashed_password=hash_password("merchant123"),
            full_name="Alex Rivera",
            role="merchant",
            is_active=True,
        )
        db.add(user_m1)
        await db.flush()

        m1 = Merchant(
            id=uuid.uuid4(),
            user_id=user_m1.id,
            business_name="TechGear Store",
            website_url="https://techgear.com",
            description="Premium audio, accessories, and computer peripherals.",
            is_active=True,
            crawl_status="completed",
            graphify_data_path="./graphify_data/techgear",
        )
        db.add(m1)

        # 2. Apex Gaming Vault (Laptops, Monitors, Gaming)
        user_m2 = User(
            id=uuid.uuid4(),
            email="sales@apexgaming.com",
            hashed_password=hash_password("apex123"),
            full_name="Marcus Vance",
            role="merchant",
            is_active=True,
        )
        db.add(user_m2)
        await db.flush()

        m2 = Merchant(
            id=uuid.uuid4(),
            user_id=user_m2.id,
            business_name="Apex Gaming Vault",
            website_url="https://apexgaming.com",
            description="High performance gaming laptops, curved monitors, and esports gear.",
            is_active=True,
            crawl_status="completed",
            graphify_data_path="./graphify_data/apex",
        )
        db.add(m2)

        # 3. Urban Athletics (Footwear & Apparel)
        user_m3 = User(
            id=uuid.uuid4(),
            email="info@urbanathletics.com",
            hashed_password=hash_password("urban123"),
            full_name="Elena Rostova",
            role="merchant",
            is_active=True,
        )
        db.add(user_m3)
        await db.flush()

        m3 = Merchant(
            id=uuid.uuid4(),
            user_id=user_m3.id,
            business_name="Urban Athletics",
            website_url="https://urbanathletics.com",
            description="Running shoes, performance trainers, and street sportswear.",
            is_active=True,
            crawl_status="completed",
            graphify_data_path="./graphify_data/urban",
        )
        db.add(m3)

        # Consumer User
        consumer = User(
            id=uuid.uuid4(),
            email="shopper@agenticbuy.com",
            hashed_password=hash_password("shopper123"),
            full_name="Alice Chen",
            role="consumer",
            is_active=True,
        )
        db.add(consumer)
        await db.flush()

        print("Populating diverse multi-merchant products...")
        products = [
            # Merchant 1 (TechGear)
            Product(
                id=uuid.uuid4(),
                merchant_id=m1.id,
                name="Pro Wireless Noise-Cancelling Headphones",
                category="Audio",
                price=149.99,
                min_acceptable_price=110.0,
                auto_accept_threshold=135.0,
                stock_quantity=24,
                bargaining_enabled=True,
                max_negotiation_rounds=5,
                description="Over-ear active noise cancellation with 40h battery and LDAC codec support.",
                image_url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
                is_active=True,
            ),
            Product(
                id=uuid.uuid4(),
                merchant_id=m1.id,
                name="Mechanical Ergonomic Keyboard (RGB)",
                category="Computer Peripherals",
                price=119.00,
                min_acceptable_price=90.0,
                auto_accept_threshold=105.0,
                stock_quantity=15,
                bargaining_enabled=True,
                max_negotiation_rounds=4,
                description="Hot-swappable tactile brown switches, wireless bluetooth/2.4G.",
                image_url="https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500",
                is_active=True,
            ),
            Product(
                id=uuid.uuid4(),
                merchant_id=m1.id,
                name="Ultra-Fast GaN 100W Travel Charger",
                category="Accessories",
                price=49.99,
                min_acceptable_price=42.0,
                auto_accept_threshold=46.0,
                stock_quantity=50,
                bargaining_enabled=False,
                max_negotiation_rounds=3,
                description="3x USB-C ports, 1x USB-A port, GaN III technology.",
                image_url="https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=500",
                is_active=True,
            ),
            Product(
                id=uuid.uuid4(),
                merchant_id=m1.id,
                name="Studio USB Condenser Microphone",
                category="Audio",
                price=79.99,
                min_acceptable_price=60.0,
                auto_accept_threshold=70.0,
                stock_quantity=18,
                bargaining_enabled=True,
                max_negotiation_rounds=4,
                description="Cardioid condenser mic with pop filter and zero-latency monitoring.",
                image_url="https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=500",
                is_active=True,
            ),

            # Merchant 2 (Apex Gaming Vault)
            Product(
                id=uuid.uuid4(),
                merchant_id=m2.id,
                name="Titan 16 Pro Gaming Laptop (RTX 4070)",
                category="Computers & Laptops",
                price=1499.00,
                min_acceptable_price=1350.0,
                auto_accept_threshold=1420.0,
                stock_quantity=8,
                bargaining_enabled=True,
                max_negotiation_rounds=5,
                description="Intel Core i9 14th Gen, 32GB DDR5 RAM, 1TB NVMe, RTX 4070 8GB, 240Hz QHD display.",
                image_url="https://images.unsplash.com/photo-1603302576837-37561b2e2302?w=500",
                is_active=True,
            ),
            Product(
                id=uuid.uuid4(),
                merchant_id=m2.id,
                name="34-inch Curved UltraWide 165Hz Monitor",
                category="Displays",
                price=429.00,
                min_acceptable_price=370.0,
                auto_accept_threshold=400.0,
                stock_quantity=12,
                bargaining_enabled=True,
                max_negotiation_rounds=4,
                description="1500R curvature, 3440x1440 WQHD, 1ms response time, HDR400.",
                image_url="https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500",
                is_active=True,
            ),
            Product(
                id=uuid.uuid4(),
                merchant_id=m2.id,
                name="Wireless Esports Ultralight Mouse (58g)",
                category="Computer Peripherals",
                price=69.99,
                min_acceptable_price=55.0,
                auto_accept_threshold=62.0,
                stock_quantity=30,
                bargaining_enabled=True,
                max_negotiation_rounds=3,
                description="PAW3395 26,000 DPI sensor, 80-hour battery, lag-free 1000Hz polling rate.",
                image_url="https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=500",
                is_active=True,
            ),

            # Merchant 3 (Urban Athletics)
            Product(
                id=uuid.uuid4(),
                merchant_id=m3.id,
                name="AeroStride Carbon Running Shoes",
                category="Footwear",
                price=160.00,
                min_acceptable_price=130.0,
                auto_accept_threshold=145.0,
                stock_quantity=22,
                bargaining_enabled=True,
                max_negotiation_rounds=5,
                description="Full-length carbon fiber propulsion plate, superfoam cushioning for marathon running.",
                image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
                is_active=True,
            ),
            Product(
                id=uuid.uuid4(),
                merchant_id=m3.id,
                name="CloudPace Daily Trainer Sneakers",
                category="Footwear",
                price=110.00,
                min_acceptable_price=85.0,
                auto_accept_threshold=95.0,
                stock_quantity=35,
                bargaining_enabled=True,
                max_negotiation_rounds=4,
                description="Plush EVA midsole, breathable engineered mesh upper, daily walking and training.",
                image_url="https://images.unsplash.com/photo-1551107696-a4b0c5a0d9a2?w=500",
                is_active=True,
            ),
            Product(
                id=uuid.uuid4(),
                merchant_id=m3.id,
                name="HydroShield Breathable Windbreaker",
                category="Apparel",
                price=85.00,
                min_acceptable_price=70.0,
                auto_accept_threshold=78.0,
                stock_quantity=20,
                bargaining_enabled=True,
                max_negotiation_rounds=3,
                description="Water-repellent ultralight running jacket with reflective strips.",
                image_url="https://images.unsplash.com/photo-1544441893-675973e31985?w=500",
                is_active=True,
            ),
        ]

        db.add_all(products)
        await db.commit()
        print(f"Successfully seeded {len(products)} products across 3 merchants!")
        print("Merchants:")
        print("  1. TechGear Store (Audio, Accessories, Keyboards)")
        print("  2. Apex Gaming Vault (Gaming Laptops, Monitors, Mice)")
        print("  3. Urban Athletics (Running Shoes, Sneakers, Windbreakers)")


if __name__ == "__main__":
    asyncio.run(seed())
