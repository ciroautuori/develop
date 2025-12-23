"""
Script diretto per creare SuperAdmin - Bypassa i problemi di import.
"""

import psycopg2
from passlib.context import CryptContext

# Password hasher
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Connessione database
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="studiocentos",
    user="studiocentos",
    password="studiocentos2025"
)

cur = conn.cursor()

# Dati admin
email = "admin@studiocentos.it"
password = "studiocentos2025"
username = "admin"
full_name = "StudiocentOS Admin"

# Hash password
hashed_password = hash_password(password)

# Check se esiste già
cur.execute("SELECT id, email FROM users WHERE email = %s", (email,))
existing = cur.fetchone()

if existing:
    print(f"⚠️  Admin già esistente: {existing[1]} (ID: {existing[0]})")
    print("\n🔐 CREDENZIALI ADMIN:")
    print("=" * 50)
    print(f"📧 Email: {email}")
    print(f"🔑 Password: {password}")
else:
    # Crea admin
    cur.execute("""
        INSERT INTO users (
            email, password, username, full_name, role, 
            is_active, is_public, slug, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, 'admin', 
            true, false, %s, NOW(), NOW()
        ) RETURNING id, email
    """, (email, hashed_password, username, full_name, username))
    
    admin = cur.fetchone()
    conn.commit()
    
    print("\n✅ SUPERADMIN CREATO CON SUCCESSO!")
    print("=" * 50)
    print(f"🆔 ID: {admin[0]}")
    print(f"📧 Email: {admin[1]}")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {password}")

print("\n🚀 COME ACCEDERE:")
print("=" * 50)
print("1. Apri browser: http://localhost:3000/login")
print(f"2. Email: {email}")
print(f"3. Password: {password}")
print("\n📊 DASHBOARD ADMIN:")
print("   → http://localhost:3000/admin")
print("\n📝 GESTIONE PORTFOLIO:")
print("   → Progetti: http://localhost:3000/admin/projects")
print("   → Servizi: http://localhost:3000/admin/services")
print("\n🔧 API ENDPOINTS (con Bearer token):")
print("   POST /api/v1/auth/login  (ottieni token)")
print("   GET  /api/v1/portfolio/projects")
print("   POST /api/v1/portfolio/projects")
print("   PUT  /api/v1/portfolio/projects/{id}")
print("   GET  /api/v1/portfolio/services")
print("   POST /api/v1/portfolio/services")

cur.close()
conn.close()
