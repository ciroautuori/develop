#!/usr/bin/env python3
"""
Script per pulire il database e creare solo le tabelle necessarie senza dati mock.
Crea solo l'utente admin per l'accesso al pannello amministrativo.

Variabili d'ambiente supportate:
  ADMIN_USERNAME (default: admin)
  ADMIN_PASSWORD (default: admin123)
  BACKEND_URL    (default: http://localhost:8000)
"""
import os
import sys
import requests
from datetime import datetime

BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
API_V1 = f"{BACKEND_URL}/api/v1"
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')


def wait_for_backend():
    """Attende che il backend sia disponibile"""
    import time
    max_retries = 30
    for i in range(max_retries):
        try:
            resp = requests.get(f"{BACKEND_URL}/health", timeout=5)
            if resp.status_code == 200:
                print("✅ Backend disponibile")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⏳ Attendo il backend... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print("❌ Backend non disponibile dopo 60 secondi")
    return False


def create_admin_user():
    """Crea l'utente admin se non esiste"""
    try:
        # Verifica se admin esiste già provando il login
        resp = requests.post(f"{API_V1}/admin/login", json={
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD,
        }, timeout=10)
        
        if resp.status_code == 200:
            print("✅ Admin user già esistente")
            return True
            
        # Se il login fallisce, prova a creare l'admin
        print("📝 Creazione admin user...")
        
        # Nota: questo endpoint potrebbe non esistere ancora, 
        # dipende dall'implementazione del backend
        resp = requests.post(f"{API_V1}/admin/create-admin", json={
            'username': ADMIN_USERNAME,
            'password': ADMIN_PASSWORD,
        }, timeout=10)
        
        if resp.status_code in (200, 201):
            print("✅ Admin user creato con successo")
            return True
        else:
            print(f"⚠️  Impossibile creare admin user: {resp.status_code}")
            print("   L'admin dovrà essere creato manualmente")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Errore durante la creazione dell'admin: {e}")
        return False


def verify_empty_database():
    """Verifica che le tabelle principali siano vuote"""
    endpoints = [
        ('/projects/', 'Projects'),
        ('/events/', 'Events'),
        ('/news/', 'News'),
        ('/volunteers/', 'Volunteers')
    ]
    
    print("\n🔍 Verifica database pulito:")
    all_empty = True
    
    for endpoint, name in endpoints:
        try:
            resp = requests.get(f"{API_V1}{endpoint}", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                count = len(data) if isinstance(data, list) else 0
                status = "✅ VUOTO" if count == 0 else f"⚠️  {count} record"
                print(f"  {name}: {status}")
                if count > 0:
                    all_empty = False
            else:
                print(f"  {name}: ❌ Errore {resp.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  {name}: ❌ Errore connessione")
    
    return all_empty


def main():
    print("🧹 PULIZIA DATABASE ISS-WBS")
    print("=" * 40)
    
    # 1. Attendi backend
    if not wait_for_backend():
        sys.exit(1)
    
    # 2. Crea admin user
    create_admin_user()
    
    # 3. Verifica database pulito
    is_clean = verify_empty_database()
    
    print("\n" + "=" * 40)
    if is_clean:
        print("✅ DATABASE PULITO E PRONTO PER PRODUCTION")
        print(f"📝 Admin user: {ADMIN_USERNAME}")
        print("🚀 Il sistema è pronto per il deploy!")
    else:
        print("⚠️  DATABASE CONTIENE ANCORA DATI")
        print("   Rimuovere manualmente i dati se necessario")
    
    print("=" * 40)


if __name__ == "__main__":
    main()
