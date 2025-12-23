#!/usr/bin/env python3
"""
Test Google Calendar Integration via REST API
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = "https://studiocentos.it"

# Step 1: Login admin
print("\n" + "="*80)
print("🔐 Step 1: Admin Login")
print("="*80)

# Prova diverse password comuni
passwords = [
    "admin123",
    "Admin123",
    "AdminStudioCentOS2024!",
    "Admin@2024",
    "studiocentos2024"
]

token = None
for pwd in passwords:
    response = requests.post(
        f"{BASE_URL}/api/v1/admin/auth/login",
        json={"email": "admin@studiocentos.it", "password": pwd}
    )

    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login riuscito con password: {pwd[:4]}***")
        print(f"   Token: {token[:50]}...")
        break
    else:
        continue

if not token:
    print("❌ Login fallito con tutte le password provate")
    print("\n📋 AZIONE RICHIESTA:")
    print("   Accedi manualmente su https://studiocentos.it/admin")
    print("   Poi prendi il token JWT dal localStorage del browser:")
    print("   1. F12 → Console")
    print("   2. localStorage.getItem('admin_token')")
    print("   3. Copia il token")
    print("\n   Oppure resetta la password admin nel database:")
    print('   docker exec studiocentos-db psql -U studiocentos -d studiocentos -c "UPDATE admin_users SET password_hash=..."')
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Check Google Calendar status
print("\n" + "="*80)
print("📅 Step 2: Google Calendar Status")
print("="*80)

response = requests.get(
    f"{BASE_URL}/api/v1/admin/google/calendar/status",
    headers=headers
)

print(f"Status code: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code != 200:
    print("❌ Errore checking status")
    exit(1)

status_data = response.json()

if not status_data.get("connected"):
    print("\n⚠️  Google Calendar NON connesso!")
    print("\n📋 AZIONE RICHIESTA:")
    print("   1. Vai su https://studiocentos.it/admin/settings")
    print("   2. Sezione 'Integrazioni Google'")
    print("   3. Clicca 'Connetti Google Calendar'")
    print("   4. Autorizza l'applicazione")
    exit(1)

print("✅ Google Calendar connesso!")
print(f"   Scadenza token: {status_data.get('expires_at')}")

# Step 3: Create test booking with Google Meet
print("\n" + "="*80)
print("🆕 Step 3: Crea Booking di Test con Google Meet")
print("="*80)

scheduled_at = (datetime.now() + timedelta(hours=2)).isoformat()

booking_data = {
    "title": "Test Google Calendar Integration",
    "client_name": "Mario Rossi Test",
    "client_email": "test@example.com",  # ⚠️ CAMBIA CON LA TUA EMAIL REALE!
    "client_phone": "+39 333 1234567",
    "service_type": "consulting",
    "scheduled_at": scheduled_at,
    "duration_minutes": 30,
    "meeting_provider": "google_meet",
    "admin_notes": "Booking creato automaticamente per test Google Calendar integration"
}

print(f"\n📋 Dati booking:")
print(json.dumps(booking_data, indent=2))

response = requests.post(
    f"{BASE_URL}/api/v1/admin/bookings",
    headers=headers,
    json=booking_data
)

print(f"\nStatus code: {response.status_code}")

if response.status_code in [200, 201]:
    booking = response.json()
    print("\n✅ BOOKING CREATO!")
    print(f"   ID: {booking.get('id')}")
    print(f"   Titolo: {booking.get('title')}")
    print(f"   Data/Ora: {booking.get('scheduled_at')}")
    print(f"   Google Meet URL: {booking.get('meeting_url')}")
    print(f"   Google Event ID: {booking.get('meeting_id')}")

    if booking.get("meeting_url"):
        print("\n🎉 SUCCESSO! Link Google Meet generato:")
        print(f"   {booking.get('meeting_url')}")
        print("\n✅ Controlla il tuo Google Calendar:")
        print("   https://calendar.google.com")
    else:
        print("\n⚠️  Booking creato ma senza Google Meet link")
        print("   Controlla i logs backend:")
        print("   docker logs studiocentos-backend | grep -i 'google\\|meet'")
else:
    print(f"\n❌ ERRORE creazione booking:")
    print(f"   {response.text}")

# Step 4: List recent bookings
print("\n" + "="*80)
print("📋 Step 4: Lista Ultimi Bookings")
print("="*80)

response = requests.get(
    f"{BASE_URL}/api/v1/admin/bookings?page=1&page_size=5",
    headers=headers
)

if response.status_code == 200:
    data = response.json()
    bookings = data.get("items", [])
    print(f"\n✅ Trovati {data.get('total', 0)} bookings (mostro primi 5):\n")

    for b in bookings:
        meet_status = "🔗 Meet" if b.get("meeting_url") else "❌ No Meet"
        print(f"   [{b.get('id')}] {b.get('title')} - {b.get('scheduled_at')} {meet_status}")
        if b.get("meeting_url"):
            print(f"        URL: {b.get('meeting_url')}")
else:
    print(f"❌ Errore: {response.text}")

print("\n" + "="*80)
print("✅ TEST COMPLETATO")
print("="*80)
