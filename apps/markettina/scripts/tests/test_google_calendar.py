#!/usr/bin/env python3
"""
Test Google Calendar Integration
Crea un appuntamento di test e verifica che appaia in Google Calendar
"""
import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "apps" / "backend"
sys.path.insert(0, str(backend_path))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.domain.booking.services import create_google_meet_link
from app.domain.google.calendar_service import GoogleCalendarService

# Database connection
DATABASE_URL = "postgresql://markettina:39a61d2579f38ae46b2c9514e1e5e7ca063772bd3799fb0a48c1ce5bfa8fa17a@localhost:5433/markettina"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


async def test_google_calendar_connection():
    """Test 1: Verifica connessione Google Calendar"""
    print("\n" + "="*80)
    print("TEST 1: Verifica connessione Google Calendar")
    print("="*80)

    db = SessionLocal()
    try:
        service = GoogleCalendarService.from_admin_token(db, admin_id=1)

        if not service:
            print("❌ ERRORE: Impossibile creare GoogleCalendarService")
            print("   Token Google mancante o scaduto")
            print("\n📋 AZIONE RICHIESTA:")
            print("   1. Vai su https://markettina.it/admin/settings")
            print("   2. Clicca 'Connetti Google Calendar'")
            print("   3. Autorizza l'applicazione")
            return False

        print("✅ GoogleCalendarService creato con successo")

        # Test: Lista calendari
        print("\n📅 Listing calendars...")
        calendars = await service.list_calendars()

        if calendars:
            print(f"✅ Trovati {len(calendars)} calendari:")
            for cal in calendars[:3]:
                print(f"   - {cal.get('summary', 'N/A')} ({cal.get('id', 'N/A')})")
        else:
            print("⚠️  Nessun calendario trovato (potrebbe essere un problema di permessi)")

        return True

    except Exception as e:
        print(f"❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def test_create_google_meet_event():
    """Test 2: Crea evento Google Calendar con Meet"""
    print("\n" + "="*80)
    print("TEST 2: Creazione evento Google Calendar con Meet")
    print("="*80)

    db = SessionLocal()
    try:
        # Dati evento di test
        start_time = datetime.now(timezone.utc) + timedelta(hours=2)

        print(f"\n📅 Creazione evento:")
        print(f"   Titolo: Test Google Calendar Integration")
        print(f"   Data/Ora: {start_time.strftime('%Y-%m-%d %H:%M')} UTC")
        print(f"   Durata: 30 minuti")
        print(f"   Partecipante: test@example.com")

        result = await create_google_meet_link(
            db=db,
            admin_id=1,
            title="Test Google Calendar Integration",
            start_time=start_time,
            duration_minutes=30,
            attendee_email="test@example.com",
            attendee_name="Test User"
        )

        if result:
            print("\n✅ SUCCESSO! Evento creato:")
            print(f"   Event ID: {result.get('event_id')}")
            print(f"   Google Meet Link: {result.get('meet_link')}")
            print(f"   Calendar Link: {result.get('html_link')}")
            print(f"\n🎉 Verifica il tuo Google Calendar!")
            print(f"   Link diretto: https://calendar.google.com")
            return True
        else:
            print("\n❌ ERRORE: Creazione evento fallita")
            print("   Controlla i logs per dettagli:")
            print("   docker logs markettina-backend | grep -i google")
            return False

    except Exception as e:
        print(f"\n❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def test_google_calendar_status():
    """Test 3: Verifica status token Google"""
    print("\n" + "="*80)
    print("TEST 3: Verifica status token Google Calendar")
    print("="*80)

    db = SessionLocal()
    try:
        from app.domain.google.models import AdminGoogleSettings

        settings = db.query(AdminGoogleSettings).filter(
            AdminGoogleSettings.admin_id == 1
        ).first()

        if not settings:
            print("❌ Nessuna configurazione Google trovata per admin_id=1")
            return False

        print(f"\n📊 Token Status:")
        print(f"   Access Token: {'✅ Presente' if settings.access_token else '❌ Mancante'}")
        print(f"   Refresh Token: {'✅ Presente' if settings.refresh_token else '❌ Mancante'}")
        print(f"   Scadenza: {settings.token_expires_at}")
        print(f"   Scopes: {settings.scopes[:100]}..." if settings.scopes else "   Scopes: ❌ Mancanti")

        # Check if expired
        now = datetime.now(timezone.utc)
        if settings.token_expires_at and settings.token_expires_at < now:
            print(f"\n⚠️  Token SCADUTO (scaduto da {now - settings.token_expires_at})")
            if settings.refresh_token:
                print("   ✅ Refresh token presente - verrà rinnovato automaticamente")
            else:
                print("   ❌ Refresh token mancante - richiesta nuova autorizzazione")
        else:
            print(f"\n✅ Token VALIDO")

        # Check required scopes
        required_scopes = ["calendar", "calendar.events"]
        scopes_str = settings.scopes or ""

        print(f"\n🔐 Scope Check:")
        for scope in required_scopes:
            has_scope = scope in scopes_str.lower()
            status = "✅" if has_scope else "❌"
            print(f"   {status} {scope}")

        return True

    except Exception as e:
        print(f"❌ ERRORE: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


async def main():
    """Esegue tutti i test"""
    print("\n" + "="*80)
    print("🔍 markettina - Google Calendar Integration Test Suite")
    print("="*80)

    # Test 3: Status token
    status_ok = await test_google_calendar_status()

    if not status_ok:
        print("\n❌ Test suite interrotta - configura prima Google OAuth")
        return

    # Test 1: Connessione
    connection_ok = await test_google_calendar_connection()

    if not connection_ok:
        print("\n❌ Test suite interrotta - impossibile connettersi a Google Calendar")
        return

    # Test 2: Crea evento
    create_ok = await test_create_google_meet_event()

    # Summary
    print("\n" + "="*80)
    print("📊 RISULTATI TEST SUITE")
    print("="*80)
    print(f"Token Status: {'✅' if status_ok else '❌'}")
    print(f"Connessione Google Calendar: {'✅' if connection_ok else '❌'}")
    print(f"Creazione evento Google Meet: {'✅' if create_ok else '❌'}")
    print("="*80)

    if all([status_ok, connection_ok, create_ok]):
        print("\n🎉 TUTTI I TEST PASSATI!")
        print("   L'integrazione Google Calendar funziona correttamente.")
    else:
        print("\n⚠️  ALCUNI TEST FALLITI")
        print("   Controlla i messaggi di errore sopra per il troubleshooting.")


if __name__ == "__main__":
    asyncio.run(main())
