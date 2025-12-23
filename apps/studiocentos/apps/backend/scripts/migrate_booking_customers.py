"""
Data Migration Script: Populate customer_id in bookings from legacy client data.

This script:
1. Extracts unique customers from existing bookings (client_email as key)
2. Creates Customer records in the customers table
3. Updates bookings.customer_id to link to the new Customer records

IMPORTANT:
- Run this AFTER migration 009_booking_customer_integration
- Backup your database before running
- This script is idempotent (can be run multiple times safely)

Usage:
    python -m scripts.migrate_booking_customers
"""

import sys
import os
from datetime import datetime
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.domain.booking.models import Booking
from app.domain.customers.models import Customer, CustomerStatus, CustomerType, CustomerSource
from app.infrastructure.database.session import get_db


def migrate_booking_customers():
    """
    Migrate booking client data to centralized customers table.
    """
    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        print("=" * 80)
        print("BOOKING TO CUSTOMER MIGRATION")
        print("=" * 80)
        print()

        # Get all bookings without customer_id
        bookings_without_customer = db.query(Booking).filter(
            Booking.customer_id.is_(None)
        ).all()

        print(f"Found {len(bookings_without_customer)} bookings without customer_id")
        print()

        if not bookings_without_customer:
            print("✅ No bookings to migrate. All bookings already have customer_id.")
            return

        # Group bookings by email to find unique customers
        customers_by_email = {}

        for booking in bookings_without_customer:
            email = booking.client_email.lower().strip()

            if email not in customers_by_email:
                customers_by_email[email] = {
                    'name': booking.client_name,
                    'email': booking.client_email,
                    'phone': booking.client_phone,
                    'company_name': booking.client_company,
                    'bookings': []
                }

            customers_by_email[email]['bookings'].append(booking)

        print(f"Identified {len(customers_by_email)} unique customers by email")
        print()

        # Create customers and link bookings
        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Get first admin user for created_by (fallback)
        from app.domain.auth.admin_models import AdminUser
        first_admin = db.query(AdminUser).filter(
            AdminUser.is_active == True
        ).first()

        if not first_admin:
            print("❌ ERROR: No active admin users found. Cannot set created_by.")
            print("Please create an admin user first.")
            return

        default_admin_id = first_admin.id

        for email, customer_data in customers_by_email.items():
            try:
                # Check if customer already exists
                existing_customer = db.query(Customer).filter(
                    Customer.is_deleted == False
                ).all()

                # Decrypt and check emails (slow but necessary for encrypted data)
                customer = None
                for cust in existing_customer:
                    if cust.email and cust.email.lower() == email:
                        customer = cust
                        break

                if customer:
                    print(f"📧 Customer with email {email} already exists (ID: {customer.id})")
                    skipped_count += 1
                else:
                    # Create new customer
                    customer = Customer(
                        name=customer_data['name'],
                        email=customer_data['email'],  # Will be auto-encrypted by hybrid property
                        phone=customer_data['phone'],  # Will be auto-encrypted
                        company_name=customer_data['company_name'],
                        status=CustomerStatus.ACTIVE.value,  # Assume active since they booked
                        customer_type=CustomerType.BUSINESS.value if customer_data['company_name'] else CustomerType.INDIVIDUAL.value,
                        source=CustomerSource.WEBSITE.value,  # Assume website since from booking
                        created_by=default_admin_id,
                        created_at=datetime.utcnow()
                    )

                    db.add(customer)
                    db.flush()  # Get customer.id

                    print(f"✅ Created customer: {customer.name} <{email}> (ID: {customer.id})")
                    created_count += 1

                # Link all bookings to this customer
                for booking in customer_data['bookings']:
                    booking.customer_id = customer.id
                    updated_count += 1

                # Commit after each customer to avoid losing progress on error
                db.commit()

            except Exception as e:
                print(f"❌ Error processing customer {email}: {str(e)}")
                db.rollback()
                continue

        print()
        print("=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)
        print(f"✅ Customers created:  {created_count}")
        print(f"⏭️  Customers skipped:  {skipped_count} (already existed)")
        print(f"🔗 Bookings updated:   {updated_count}")
        print()

        # Verify migration
        remaining = db.query(Booking).filter(
            Booking.customer_id.is_(None)
        ).count()

        if remaining == 0:
            print("✅ SUCCESS: All bookings now have customer_id!")
        else:
            print(f"⚠️  WARNING: {remaining} bookings still without customer_id")

        print()

    except Exception as e:
        print(f"❌ CRITICAL ERROR: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print()
    print("⚠️  IMPORTANT: Make sure you have:")
    print("   1. Backed up your database")
    print("   2. Run migration 009_booking_customer_integration")
    print("   3. Set PII_ENCRYPTION_KEY environment variable")
    print()

    response = input("Continue with migration? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        migrate_booking_customers()
    else:
        print("Migration cancelled.")
