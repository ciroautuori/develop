"""
Test Data Flow - Verifica integrazione completa Backend
"""

import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.core.config import settings
from app.domain.portfolio.models import Project, Service
from app.domain.booking.models import Booking, AvailabilitySlot


async def test_portfolio_data():
    """Test portfolio data flow"""
    print("\n🧪 Testing Portfolio Data Flow...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Test projects
        result = await session.execute(select(Project))
        projects = result.scalars().all()
        print(f"✅ Projects found: {len(projects)}")
        for p in projects[:3]:
            print(f"   - {p.title} ({p.year})")
        
        # Test services
        result = await session.execute(select(Service))
        services = result.scalars().all()
        print(f"✅ Services found: {len(services)}")
        for s in services[:3]:
            print(f"   - {s.title}")
    
    await engine.dispose()


async def test_booking_data():
    """Test booking data flow"""
    print("\n🧪 Testing Booking Data Flow...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Test availability slots
        result = await session.execute(select(AvailabilitySlot))
        slots = result.scalars().all()
        print(f"✅ Availability slots found: {len(slots)}")
        
        # Test bookings
        result = await session.execute(select(Booking))
        bookings = result.scalars().all()
        print(f"✅ Bookings found: {len(bookings)}")
        for b in bookings[:3]:
            print(f"   - {b.client_name} - {b.scheduled_at}")
    
    await engine.dispose()


async def test_api_endpoints():
    """Test API endpoints availability"""
    print("\n🧪 Testing API Endpoints...")
    
    import aiohttp
    
    base_url = "http://localhost:8000"
    endpoints = [
        "/api/v1/portfolio/public/projects",
        "/api/v1/portfolio/public/services",
        "/api/v1/booking/calendar/availability",
        "/health",
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            try:
                async with session.get(f"{base_url}{endpoint}") as response:
                    if response.status == 200:
                        print(f"✅ {endpoint} - OK")
                    else:
                        print(f"⚠️  {endpoint} - Status {response.status}")
            except Exception as e:
                print(f"❌ {endpoint} - Error: {e}")


async def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 STUDIOCENTOS DATA FLOW TEST")
    print("=" * 60)
    
    try:
        await test_portfolio_data()
        await test_booking_data()
        
        print("\n" + "=" * 60)
        print("✅ ALL DATA FLOW TESTS PASSED")
        print("=" * 60)
        
        # Optional: test API endpoints if server is running
        print("\n📡 Testing API endpoints (optional)...")
        print("   Make sure backend server is running on localhost:8000")
        try:
            await test_api_endpoints()
        except Exception as e:
            print(f"⚠️  API tests skipped: {e}")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
