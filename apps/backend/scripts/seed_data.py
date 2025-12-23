#!/usr/bin/env python3
"""
Script di seeding DISABILITATO per production.
Questo script conteneva dati mock/fittizi e non viene più utilizzato.

Per inizializzare il database production usa:
  python backend/scripts/clean_db.py

Per aggiungere contenuti reali, utilizza il pannello admin web.
"""
import sys

def main():
    print("❌ SCRIPT SEED DISABILITATO PER PRODUCTION")
    print("🔧 Usa 'python backend/scripts/clean_db.py' per database pulito")
    print("🌐 Aggiungi contenuti reali tramite pannello admin web")
    sys.exit(1)

if __name__ == "__main__":
    main()


def get_headers(token: str):
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def ensure_projects(token: str):
    url = f"{API_V1}/projects/"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    items = r.json()
    existing_slugs = {p['slug'] for p in items}
    print(f"Projects già presenti: {len(items)}")
    print("Aggiungo nuovi projects di esempio...")
    projects = [
        {
            "title": "Progetto Digitale",
            "slug": "progetto-digitale",
            "description": "Un progetto per la digitalizzazione dei servizi sociali",
            "excerpt": "Digitalizzazione innovativa per i servizi sociali del territorio",
            "content": "Contenuto dettagliato del progetto...",
            "image_url": "https://picsum.photos/seed/proj1/800/400",
            "status": "active",
            "start_date": datetime.now().date().isoformat(),
            "end_date": (datetime.now().date() + timedelta(days=180)).isoformat()
        },
        {
            "title": "Assistenza Anziani Smart",
            "slug": "assistenza-anziani-smart",
            "description": "Sistema innovativo di assistenza domiciliare per anziani",
            "excerpt": "Tecnologie IoT e AI per l'assistenza agli anziani",
            "content": "Utilizziamo tecnologie IoT e AI per migliorare la qualità della vita degli anziani...",
            "image_url": "https://picsum.photos/seed/proj2/800/400",
            "status": "active",
            "start_date": (datetime.now().date() - timedelta(days=30)).isoformat(),
            "end_date": (datetime.now().date() + timedelta(days=150)).isoformat()
        },
        {
            "title": "Hub Giovani Salerno",
            "slug": "hub-giovani-salerno",
            "description": "Spazio di coworking e formazione per giovani imprenditori",
            "excerpt": "Coworking e formazione per l'imprenditoria giovanile",
            "content": "Un luogo dove i giovani possono sviluppare le proprie idee imprenditoriali...",
            "image_url": "https://picsum.photos/seed/proj3/800/400",
            "status": "completed",
            "start_date": (datetime.now().date() - timedelta(days=365)).isoformat(),
            "end_date": (datetime.now().date() - timedelta(days=30)).isoformat()
        },
        {
            "title": "Rete Solidale Alimentare",
            "slug": "rete-solidale-alimentare",
            "description": "Distribuzione sostenibile di cibo alle famiglie bisognose",
            "excerpt": "Contrasto allo spreco alimentare e solidarietà sociale",
            "content": "Partnership con supermercati locali per recupero eccedenze alimentari...",
            "image_url": "https://picsum.photos/seed/proj4/800/400",
            "status": "active",
            "start_date": (datetime.now().date() - timedelta(days=60)).isoformat(),
            "end_date": (datetime.now().date() + timedelta(days=300)).isoformat()
        },
        {
            "title": "Formazione Digitale Senior",
            "slug": "formazione-digitale-senior",
            "description": "Corsi di alfabetizzazione digitale per over 65",
            "excerpt": "Colmare il divario digitale per la terza età",
            "content": "Programma formativo completo per avvicinare gli anziani al mondo digitale...",
            "image_url": "https://picsum.photos/seed/proj5/800/400",
            "status": "upcoming",
            "start_date": (datetime.now().date() + timedelta(days=30)).isoformat(),
            "end_date": (datetime.now().date() + timedelta(days=210)).isoformat()
        }
    ]
    added = 0
    for p in projects:
        if p['slug'] not in existing_slugs:
            pr = requests.post(url, headers=get_headers(token), data=json.dumps(p), timeout=10)
            if pr.status_code not in (200, 201):
                print(f"Errore creazione project: {pr.status_code} {pr.text}")
                sys.exit(1)
            added += 1
    print(f"Projects aggiunti: {added}")


def ensure_events(token: str):
    url = f"{API_V1}/events/"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    items = r.json()
    existing_slugs = {e['slug'] for e in items}
    print(f"Events già presenti: {len(items)}")
    print("Aggiungo nuovi events di esempio...")
    events = [
        {
            "title": "Hackathon Sociale",
            "slug": "hackathon-sociale",
            "description": "48 ore di innovazione per il sociale",
            "excerpt": "Maratona di programmazione per l'innovazione sociale",
            "content": "Contenuto dettagliato dell'evento...",
            "image_url": "https://picsum.photos/seed/ev1/800/400",
            "location": "Centro Sociale, Salerno",
            "event_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "registration_link": "https://forms.example.com/hackathon"
        },
        {
            "title": "Conferenza Innovazione Sociale",
            "slug": "conferenza-innovazione-sociale",
            "description": "Esperti internazionali discutono il futuro del terzo settore",
            "excerpt": "Speaker internazionali per il futuro del non profit",
            "content": "Una giornata dedicata all'innovazione nel sociale con speaker di rilievo...",
            "image_url": "https://picsum.photos/seed/ev2/800/400",
            "location": "Palazzo Fruscione, Salerno",
            "event_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "registration_link": "https://forms.example.com/conferenza"
        },
        {
            "title": "Workshop Design Thinking",
            "slug": "workshop-design-thinking",
            "description": "Metodologie innovative per la progettazione sociale",
            "excerpt": "Impara il design thinking applicato al sociale",
            "content": "Workshop pratico su come applicare il design thinking ai progetti sociali...",
            "image_url": "https://picsum.photos/seed/ev3/800/400",
            "location": "ISS Hub, Salerno",
            "event_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "registration_link": "https://forms.example.com/workshop"
        },
        {
            "title": "Festa del Volontariato",
            "slug": "festa-volontariato",
            "description": "Celebriamo i nostri volontari con musica e divertimento",
            "excerpt": "Una serata per ringraziare i nostri volontari",
            "content": "Una serata speciale per ringraziare tutti i volontari ISS...",
            "image_url": "https://picsum.photos/seed/ev4/800/400",
            "location": "Villa Comunale, Salerno",
            "event_date": (datetime.now() - timedelta(days=10)).isoformat(),
            "registration_link": "https://forms.example.com/festa"
        },
        {
            "title": "Corso Fundraising Base",
            "slug": "corso-fundraising-base",
            "description": "Tecniche e strategie per la raccolta fondi nel non profit",
            "excerpt": "Impara le basi del fundraising per il terzo settore",
            "content": "Corso intensivo di 2 giorni sul fundraising per organizzazioni non profit...",
            "image_url": "https://picsum.photos/seed/ev5/800/400",
            "location": "Aula Formazione ISS, Salerno",
            "event_date": (datetime.now() + timedelta(days=45)).isoformat(),
            "registration_link": "https://forms.example.com/fundraising"
        }
    ]
    added = 0
    for e in events:
        if e['slug'] not in existing_slugs:
            er = requests.post(url, headers=get_headers(token), data=json.dumps(e), timeout=10)
            if er.status_code not in (200, 201):
                print(f"Errore creazione event: {er.status_code} {er.text}")
                sys.exit(1)
            added += 1
    print(f"Events aggiunti: {added}")


def ensure_news(token: str):
    url = f"{API_V1}/news/"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    items = r.json()
    existing_slugs = {n['slug'] for n in items}
    print(f"News già presenti: {len(items)}")
    print("Aggiungo nuove news di esempio...")
    news = [
        {
            "title": "Nuova partnership con università",
            "slug": "partnership-universita",
            "summary": "ISS firma accordo con UNISA per progetti di ricerca sociale",
            "excerpt": "Collaborazione strategica con l'Università di Salerno",
            "content": "Contenuto dettagliato della notizia...",
            "author": "Redazione ISS",
            "image_url": "https://picsum.photos/seed/news1/800/400",
            "is_published": True,
            "published_at": (datetime.now()).isoformat()
        },
        {
            "title": "Premio nazionale per il volontariato",
            "slug": "premio-nazionale-volontariato",
            "summary": "ISS riceve riconoscimento dal Ministero del Lavoro",
            "excerpt": "Importante riconoscimento ministeriale per ISS",
            "content": "Grande soddisfazione per il premio ricevuto...",
            "author": "Ufficio Stampa",
            "image_url": "https://picsum.photos/seed/news2/800/400",
            "is_published": True,
            "published_at": (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            "title": "Apertura nuovo centro diurno",
            "slug": "nuovo-centro-diurno",
            "summary": "Inaugurato il nuovo centro diurno per persone con disabilità",
            "excerpt": "Nuovo spazio inclusivo per persone con disabilità",
            "content": "Un nuovo spazio dedicato all'inclusione e al supporto delle persone con disabilità...",
            "author": "Comunicazione ISS",
            "image_url": "https://picsum.photos/seed/news3/800/400",
            "is_published": True,
            "published_at": (datetime.now() - timedelta(days=5)).isoformat()
        },
        {
            "title": "Raccolta fondi supera obiettivi",
            "slug": "raccolta-fondi-successo",
            "summary": "La campagna natalizia ha raccolto 50.000 euro",
            "excerpt": "Successo straordinario per la campagna natalizia",
            "content": "Grazie alla generosità dei donatori...",
            "author": "Team Fundraising",
            "image_url": "https://picsum.photos/seed/news4/800/400",
            "is_published": True,
            "published_at": (datetime.now() - timedelta(days=12)).isoformat()
        },
        {
            "title": "Nuovi corsi formazione volontari",
            "slug": "corsi-formazione-volontari",
            "summary": "Partono i nuovi corsi di formazione per aspiranti volontari",
            "excerpt": "Al via il nuovo ciclo formativo per volontari",
            "content": "Calendario completo dei corsi di formazione per il primo trimestre 2025...",
            "author": "Coordinamento Volontari",
            "image_url": "https://picsum.photos/seed/news6/800/400",
            "is_published": True,
            "published_at": (datetime.now() - timedelta(days=1)).isoformat()
        }
    ]
    added = 0
    for n in news:
        if n['slug'] not in existing_slugs:
            nr = requests.post(url, headers=get_headers(token), data=json.dumps(n), timeout=10)
            if nr.status_code not in (200, 201):
                print(f"Errore creazione news: {nr.status_code} {nr.text}")
                sys.exit(1)
            added += 1
    print(f"News aggiunte: {added}")


def main():
    print("➡️  Login admin...")
    token = login()
    print("✅ Login OK")

    ensure_projects(token)
    ensure_events(token)
    ensure_news(token)

    print("✅ Seed completato")


if __name__ == '__main__':
    main()
