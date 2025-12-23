import asyncio
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.domain.google.analytics_service import GoogleAnalyticsService
from app.domain.google.business_profile_service import GoogleBusinessProfileService
from app.domain.auth.oauth_tokens import OAuthTokenService, OAuthProvider
from app.domain.auth.admin_models import AdminUser
from app.domain.auth.settings_models import AdminSettings

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def test_integrations():
    db = SessionLocal()
    admin_id = 1  # Assuming admin ID 1

    print(f"🔍 Testing Google Integrations for Admin ID: {admin_id}")

    # 1. Check Token
    token = OAuthTokenService.get_valid_token(db, admin_id, OAuthProvider.GOOGLE)
    if not token:
        print("❌ No valid Google Token found in oauth_tokens table!")
        return
    print("✅ Valid Google Token found in oauth_tokens table")

    # 2. Test Analytics
    print("\n📊 Testing Google Analytics...")
    try:
        ga_service = GoogleAnalyticsService(access_token=token)
        # Try to list accounts to verify connection
        accounts = await ga_service.list_accounts()
        print(f"✅ Analytics Connection OK! Found {len(accounts)} accounts.")
        if accounts:
            print(f"   First account: {accounts[0].get('displayName')}")

        # Try to get basic report (if property configured)
        # We use the default property from settings or the service default
        print("   Fetching basic report...")
        report = await ga_service.get_overview_metrics(days=7)
        print(f"✅ Analytics Data Fetch OK!")
        print(f"   Active Users (7d): {report.active_users}")
        print(f"   Sessions (7d): {report.sessions}")
    except Exception as e:
        print(f"❌ Analytics Error: {str(e)}")

    # 3. Test Business Profile
    print("\n🏪 Testing Google Business Profile...")
    try:
        gmb_service = GoogleBusinessProfileService(access_token=token)
        accounts = await gmb_service.list_accounts()
        print(f"✅ Business Profile Connection OK! Found {len(accounts)} accounts.")
        if accounts:
            print(f"   First account: {accounts[0].get('accountName')}")

            # Try to list locations
            locations = await gmb_service.list_locations(accounts[0]['name'])
            print(f"✅ Business Profile Locations OK! Found {len(locations)} locations.")
            if locations:
                print(f"   First location: {locations[0].get('title')}")
    except Exception as e:
        print(f"❌ Business Profile Error: {str(e)}")

    # 4. Test Calendar (Scope check)
    print("\n📅 Testing Google Calendar Scope...")
    # We don't have a dedicated service for Calendar yet, but we can check scopes
    from app.domain.google.models import AdminGoogleSettings
    settings_entry = db.query(AdminGoogleSettings).filter(AdminGoogleSettings.admin_id == admin_id).first()

    if settings_entry and settings_entry.scopes:
        if "calendar" in settings_entry.scopes:
             print("✅ Calendar Scope PRESENT in token.")
        else:
             print("⚠️ Calendar Scope MISSING from token.")
    else:
        print("❌ Could not verify scopes.")

if __name__ == "__main__":
    asyncio.run(test_integrations())
