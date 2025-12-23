#!/usr/bin/env python3
"""
Seed Portfolio via API - Inserisce progetti e servizi tramite API admin
"""
import requests
import json

API_BASE = "https://studiocentos.it/api/v1/admin/portfolio"

# Login admin per ottenere token
def get_admin_token():
    """Login e ottieni token admin"""
    login_url = "https://studiocentos.it/api/v1/admin/auth/login"
    
    response = requests.post(login_url, json={
        "email": "admin@studiocentos.it",
        "password": "admin123"
    })
    
    if response.status_code != 200:
        raise Exception(f"Login fallito: {response.status_code} - {response.text}")
    
    data = response.json()
    print(f"  Token: {data['access_token'][:30]}...")
    return data["access_token"]


def seed_projects(token):
    """Inserisce i 2 progetti dalla landing originale"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    projects_data = [
        {
            "title": "CV-Lab Pro",
            "slug": "cv-lab-pro",
            "description": "Portfolio builder con AI per professionisti",
            "year": 2024,
            "category": "SaaS Platform",
            "live_url": "https://cv-lab.pro",
            "technologies": ["React 19", "FastAPI", "PostgreSQL 16", "AI Agents"],
            "metrics": {
                "File production-ready": "850+",
                "Domini business": "11",
                "Time to market": "45gg"
            },
            "status": "active",
            "is_featured": True,
            "is_public": True,
            "order": 1
        },
        {
            "title": "Phoenix AI",
            "slug": "phoenix-ai",
            "description": "Piattaforma multi-agent per automazione enterprise",
            "year": 2024,
            "category": "AI Platform",
            "live_url": "https://phoenix-ai.duckdns.org",
            "technologies": ["Python 3.12", "LangChain", "ChromaDB", "GPT-4"],
            "metrics": {
                "Enterprise AI tools": "78",
                "Vector search": "RAG",
                "Monitoring": "24/7"
            },
            "status": "active",
            "is_featured": True,
            "is_public": True,
            "order": 2
        }
    ]
    
    print("🚀 Inserimento progetti...")
    for proj_data in projects_data:
        response = requests.post(
            f"{API_BASE}/projects",
            headers=headers,
            json=proj_data
        )
        
        if response.status_code == 201 or response.status_code == 200:
            print(f"  ✅ Aggiunto: {proj_data['title']}")
        elif response.status_code == 400 and "già esistente" in response.text:
            print(f"  ⚠️  Progetto '{proj_data['title']}' già esistente, skip")
        else:
            print(f"  ❌ Errore: {response.status_code} - {response.text}")
    
    print("✅ Progetti completati!\n")


def seed_services(token):
    """Inserisce i 6 servizi dalla landing originale"""
    
    headers = {"Authorization": f"Bearer {token}"}
    
    services_data = [
        {
            "title": "STUDIOCENTOS Framework",
            "slug": "studiocentos-framework",
            "description": "Enterprise full-stack framework production-ready con 850+ file e 11 domini business.",
            "icon": "⚡",
            "category": "framework",
            "features": [
                "React 19 + FastAPI",
                "PostgreSQL 16 + Redis 7",
                "DDD Architecture",
                "Docker + CI/CD ready",
                "MVP in 45 giorni"
            ],
            "value_indicator": "€100K valore codice",
            "cta_text": "Scopri di più →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": True,
            "order": 1
        },
        {
            "title": "AgentVanilla",
            "slug": "agentvanilla",
            "description": "Suite di 78 enterprise AI tools con monitoring Prometheus e Grafana integrato.",
            "icon": "🤖",
            "category": "ai_tools",
            "features": [
                "78 AI Tools pronti",
                "Multi-provider support",
                "Real-time monitoring",
                "Orchestrazione agents",
                "Production-tested"
            ],
            "value_indicator": "€50K valore tools",
            "cta_text": "Scopri di più →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": True,
            "order": 2
        },
        {
            "title": "fastBank",
            "slug": "fastbank",
            "description": "Component library con 50+ componenti React + FastAPI riutilizzabili e production-ready.",
            "icon": "🧩",
            "category": "components",
            "features": [
                "50+ Componenti UI",
                "TypeScript + Storybook",
                "30+ Makefile commands",
                "Automation completa",
                "Enterprise-tested"
            ],
            "value_indicator": "-90% dev time",
            "cta_text": "Scopri di più →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": True,
            "order": 3
        },
        {
            "title": "Sviluppo Custom",
            "slug": "sviluppo-custom",
            "description": "Siti web, app mobile e soluzioni su misura con tecnologie moderne.",
            "icon": "🌐",
            "category": "custom_dev",
            "features": [
                "Landing page & Corporate",
                "E-commerce completi",
                "Web app custom",
                "SEO ottimizzato"
            ],
            "cta_text": "Richiedi Preventivo →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": False,
            "order": 4
        },
        {
            "title": "App Mobile",
            "slug": "app-mobile",
            "description": "Applicazioni iOS e Android con React Native ed Expo 52.",
            "icon": "📱",
            "category": "mobile",
            "features": [
                "iOS + Android native",
                "Offline-first",
                "Push notifications",
                "Backend integration"
            ],
            "cta_text": "Richiedi Preventivo →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": False,
            "order": 5
        },
        {
            "title": "AI Integration",
            "slug": "ai-integration",
            "description": "Integrazione AI nei tuoi prodotti con ChatGPT, agents custom e RAG.",
            "icon": "🔮",
            "category": "ai_integration",
            "features": [
                "Chatbot intelligenti",
                "AI Agents custom",
                "Document analysis (RAG)",
                "Automation workflows"
            ],
            "cta_text": "Richiedi Preventivo →",
            "cta_url": "#contatti",
            "is_active": True,
            "is_featured": False,
            "order": 6
        }
    ]
    
    print("🚀 Inserimento servizi...")
    for serv_data in services_data:
        response = requests.post(
            f"{API_BASE}/services",
            headers=headers,
            json=serv_data
        )
        
        if response.status_code == 201 or response.status_code == 200:
            print(f"  ✅ Aggiunto: {serv_data['title']}")
        elif response.status_code == 400 and "già esistente" in response.text:
            print(f"  ⚠️  Servizio '{serv_data['title']}' già esistente, skip")
        else:
            print(f"  ❌ Errore: {response.status_code} - {response.text}")
    
    print("✅ Servizi completati!\n")


def main():
    """Main function"""
    print("\n" + "="*60)
    print("  SEED PORTFOLIO VIA API - StudiocentOS")
    print("="*60 + "\n")
    
    try:
        # Login
        print("🔐 Login admin...")
        token = get_admin_token()
        print("✅ Token ottenuto!\n")
        
        # Seed
        seed_projects(token)
        seed_services(token)
        
        # Verifica
        print("🔍 Verifica dati...")
        headers = {"Authorization": f"Bearer {token}"}
        
        projects_resp = requests.get(f"{API_BASE}/projects", headers=headers)
        services_resp = requests.get(f"{API_BASE}/services", headers=headers)
        
        if projects_resp.status_code == 200:
            projects_count = projects_resp.json().get("total", 0)
            print(f"  Progetti totali nel DB: {projects_count}")
        
        if services_resp.status_code == 200:
            services_count = services_resp.json().get("total", 0)
            print(f"  Servizi totali nel DB: {services_count}")
        
        print("\n" + "="*60)
        print("✅ COMPLETATO!")
        print("="*60 + "\n")
        
        print("🌐 Testa la landing: https://studiocentos.it")
        print("🔧 Testa il back-office: https://studiocentos.it/admin/portfolio\n")
        
    except Exception as e:
        print(f"\n❌ ERRORE: {e}\n")
        raise


if __name__ == "__main__":
    main()
