#!/usr/bin/env python3
"""
Script per creare utenti di test per il sistema ISS
Crea tutti i tipi di utenti con credenziali note per testing
"""

import sys
import os
from datetime import datetime, timedelta

# Aggiungi il path dell'app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database.database import SessionLocal, engine
from app.models.user import User, UserRole, UserStatus, AccessibilityNeeds, UserPreferences
from app.core.security import get_password_hash
from app.models import Base

# Crea tutte le tabelle
Base.metadata.create_all(bind=engine)

def create_test_users():
    """Crea utenti di test per tutti i ruoli"""
    db = SessionLocal()
    
    try:
        # Lista utenti di test
        test_users = [
            # 1. SUPER ADMIN
            {
                "email": "admin@iss.salerno.it",
                "password": "AdminISS2025!",
                "nome": "Mario",
                "cognome": "Rossi",
                "username": "admin_iss",
                "role": UserRole.ADMIN,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.NONE,
                "telefono": "+39 089 123456",
                "bio": "Super Admin del sistema ISS - Accesso completo a tutte le funzionalità",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 1000,
                "level": 10
            },
            
            # 2. MODERATOR/STAFF
            {
                "email": "staff@iss.salerno.it", 
                "password": "StaffISS2025!",
                "nome": "Giulia",
                "cognome": "Bianchi",
                "username": "staff_giulia",
                "role": UserRole.MODERATOR,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.NONE,
                "telefono": "+39 089 234567",
                "bio": "Staff ISS - Gestione contenuti e moderazione",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 500,
                "level": 5
            },
            
            # 3. APS RESPONSABILE
            {
                "email": "responsabile@aps-esempio.it",
                "password": "ApsResp2025!",
                "nome": "Francesco",
                "cognome": "Verdi",
                "username": "aps_francesco",
                "role": UserRole.APS_RESPONSABILE,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.NONE,
                "telefono": "+39 089 345678",
                "bio": "Responsabile APS Nuove Rotte - Progetti per l'inclusione sociale",
                "aps_nome_organizzazione": "APS Nuove Rotte",
                "aps_partita_iva": "12345678901",
                "aps_codice_fiscale_org": "12345678901",
                "aps_indirizzo": "Via Roma 123, Salerno",
                "aps_citta": "Salerno",
                "aps_cap": "84100",
                "aps_provincia": "SA",
                "aps_settore_attivita": "Inclusione sociale e formazione",
                "aps_website": "https://www.nuoverotte.it",
                "aps_descrizione": "APS impegnata nell'inclusione sociale attraverso formazione digitale e progetti innovativi",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 300,
                "level": 3
            },
            
            # 4. APS OPERATORE
            {
                "email": "operatore@aps-esempio.it",
                "password": "ApsOper2025!",
                "nome": "Laura",
                "cognome": "Neri",
                "username": "aps_laura",
                "role": UserRole.APS_OPERATORE,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.NONE,
                "telefono": "+39 089 456789",
                "bio": "Operatore APS Nuove Rotte - Gestione progetti e volontari",
                "aps_nome_organizzazione": "APS Nuove Rotte",
                "aps_citta": "Salerno",
                "aps_settore_attivita": "Inclusione sociale e formazione",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 150,
                "level": 2
            },
            
            # 5. CITTADINO NORMALE
            {
                "email": "cittadino@example.com",
                "password": "Cittadino2025!",
                "nome": "Marco",
                "cognome": "Blu",
                "username": "marco_cittadino",
                "role": UserRole.CITTADINO,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.NONE,
                "telefono": "+39 089 567890",
                "bio": "Cittadino interessato ai corsi di formazione digitale",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 50,
                "level": 1
            },
            
            # 6. VOLONTARIO ATTIVO
            {
                "email": "volontario@example.com",
                "password": "Volontario2025!",
                "nome": "Sara",
                "cognome": "Rosa",
                "username": "sara_volontaria",
                "role": UserRole.VOLONTARIO,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.NONE,
                "telefono": "+39 089 678901",
                "bio": "Volontaria attiva nei progetti di alfabetizzazione digitale",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 200,
                "level": 2
            },
            
            # 7. UTENTE CON ESIGENZE ACCESSIBILITÀ - SCREEN READER
            {
                "email": "accessibile@example.com",
                "password": "Access2025!",
                "nome": "Giuseppe",
                "cognome": "Giallo",
                "username": "giuseppe_access",
                "role": UserRole.CITTADINO,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.SCREEN_READER,
                "telefono": "+39 089 789012",
                "bio": "Cittadino non vedente, utilizza screen reader per navigazione",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 75,
                "level": 1
            },
            
            # 8. UTENTE CON DISABILITÀ MOTORIE
            {
                "email": "motorio@example.com",
                "password": "Motor2025!",
                "nome": "Anna",
                "cognome": "Viola",
                "username": "anna_motor",
                "role": UserRole.CITTADINO,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.MOTOR_IMPAIRMENT,
                "telefono": "+39 089 890123",
                "bio": "Cittadina con disabilità motorie, utilizza solo tastiera",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 60,
                "level": 1
            },
            
            # 9. UTENTE PENDING (NON VERIFICATO)
            {
                "email": "pending@example.com",
                "password": "Pending2025!",
                "nome": "Luca",
                "cognome": "Grigio",
                "username": "luca_pending",
                "role": UserRole.CITTADINO,
                "status": UserStatus.PENDING,
                "is_email_verified": False,
                "email_verification_token": "test_token_123",
                "accessibility_needs": AccessibilityNeeds.NONE,
                "telefono": "+39 089 901234",
                "bio": "Account in attesa di verifica email",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 0,
                "level": 1
            },
            
            # 10. APS GRANDE ORGANIZZAZIONE
            {
                "email": "direttore@aps-grande.it",
                "password": "ApsGrande2025!",
                "nome": "Roberto",
                "cognome": "Marrone",
                "username": "roberto_direttore",
                "role": UserRole.APS_RESPONSABILE,
                "status": UserStatus.ACTIVE,
                "is_email_verified": True,
                "accessibility_needs": AccessibilityNeeds.NONE,
                "telefono": "+39 089 012345",
                "bio": "Direttore APS Campania Solidale - 500+ volontari",
                "aps_nome_organizzazione": "APS Campania Solidale",
                "aps_partita_iva": "98765432109",
                "aps_codice_fiscale_org": "98765432109",
                "aps_indirizzo": "Corso Vittorio Emanuele 456, Salerno",
                "aps_citta": "Salerno",
                "aps_cap": "84100",
                "aps_provincia": "SA",
                "aps_settore_attivita": "Assistenza sociale e sanitaria",
                "aps_website": "https://www.campaniasolidale.org",
                "aps_descrizione": "Grande APS regionale con focus su assistenza sociale, formazione e progetti europei",
                "privacy_policy_accepted": True,
                "privacy_policy_accepted_at": datetime.utcnow(),
                "points": 800,
                "level": 7
            }
        ]
        
        created_users = []
        
        for user_data in test_users:
            # Verifica se utente esiste già
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                print(f"⚠️  Utente {user_data['email']} già esistente, skip...")
                continue
            
            # Hash password
            password = user_data.pop("password")
            user_data["hashed_password"] = get_password_hash(password)
            
            # Crea utente
            user = User(**user_data)
            db.add(user)
            db.flush()  # Per ottenere l'ID
            
            # Crea preferenze default
            preferences = UserPreferences(
                user_id=user.id,
                theme="light",
                font_size="large" if user.accessibility_needs in [AccessibilityNeeds.LARGE_TEXT, AccessibilityNeeds.MULTIPLE] else "medium",
                high_contrast=user.accessibility_needs == AccessibilityNeeds.HIGH_CONTRAST,
                reduced_motion=user.accessibility_needs in [AccessibilityNeeds.MOTOR_IMPAIRMENT, AccessibilityNeeds.MULTIPLE],
                notify_new_bandi=True,
                notify_bandi_expiring=True,
                alert_frequency="daily"
            )
            db.add(preferences)
            
            created_users.append({
                "email": user.email,
                "password": password,
                "role": user.role.value,
                "status": user.status.value,
                "accessibility": user.accessibility_needs.value,
                "id": user.id
            })
            
            print(f"✅ Creato utente: {user.email} ({user.role.value})")
        
        db.commit()
        
        # Stampa riepilogo credenziali
        print("\n" + "="*80)
        print("🎯 UTENTI DI TEST CREATI - CREDENZIALI PER LOGIN")
        print("="*80)
        
        for user in created_users:
            print(f"""
📧 Email: {user['email']}
🔑 Password: {user['password']}
👤 Ruolo: {user['role']}
📊 Status: {user['status']}
♿ Accessibilità: {user['accessibility']}
🆔 ID: {user['id']}
{'-'*50}""")
        
        print(f"\n🎉 TOTALE UTENTI CREATI: {len(created_users)}")
        print("\n🚀 ENDPOINTS API DISPONIBILI:")
        print("- POST /api/v1/auth/login - Login utente")
        print("- GET /api/v1/auth/me - Info utente corrente")
        print("- GET /api/v1/users/me - Profilo completo")
        print("- GET /api/v1/users/ - Lista utenti (solo admin)")
        print("- GET /api/v1/users/stats - Statistiche (solo admin)")
        
        print("\n📋 ESEMPI CURL PER TEST:")
        print(f"""
# Login Admin
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "admin@iss.salerno.it", "password": "AdminISS2025!"}}'

# Login APS Responsabile  
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "responsabile@aps-esempio.it", "password": "ApsResp2025!"}}'

# Login Cittadino con Screen Reader
curl -X POST "http://localhost:8000/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{{"email": "accessibile@example.com", "password": "Access2025!"}}'
""")
        
        return created_users
        
    except Exception as e:
        print(f"❌ Errore durante creazione utenti: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("🚀 Creazione utenti di test per sistema ISS...")
    users = create_test_users()
    print(f"\n✅ Script completato! {len(users)} utenti pronti per il testing.")
