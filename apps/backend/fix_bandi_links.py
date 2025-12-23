#!/usr/bin/env python3
"""
🔗 Script per trovare e fixare i link mancanti dei bandi usando AI
Usa Gemini con Google Search grounding per trovare i link REALI
"""

import asyncio
import os
import sys
import json
import re
import httpx
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Database connection
import psycopg2
from psycopg2.extras import RealDictCursor

# Config
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/iss_wbs")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")


def get_db_connection():
    """Connessione al database"""
    # Parse URL
    if DATABASE_URL.startswith("postgresql://"):
        # Extract components
        parts = DATABASE_URL.replace("postgresql://", "").split("@")
        user_pass = parts[0].split(":")
        host_db = parts[1].split("/")
        host_port = host_db[0].split(":")

        return psycopg2.connect(
            host=host_port[0],
            port=host_port[1] if len(host_port) > 1 else 5432,
            database=host_db[1],
            user=user_pass[0],
            password=user_pass[1],
            cursor_factory=RealDictCursor
        )
    return None


async def find_real_link_gemini(client: httpx.AsyncClient, bando_title: str, ente: str) -> dict:
    """Usa Gemini con Google Search per trovare il link reale del bando"""

    if not GOOGLE_API_KEY:
        print("⚠️  GOOGLE_API_KEY non configurata")
        return {"link": None, "fonte_verificata": False}

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GOOGLE_API_KEY}"

    prompt = f"""Trova il link ESATTO e DIRETTO alla pagina ufficiale di questo bando:

TITOLO BANDO: {bando_title}
ENTE EROGATORE: {ente}

ISTRUZIONI CRITICHE:
1. Cerca il bando sui siti ufficiali (regione.campania.it, sviluppocampania.it, fondazioneconilsud.it, etc)
2. Trova l'URL DIRETTO alla pagina del bando, NON la homepage
3. Verifica che il link sia ancora attivo
4. Se il bando è scaduto, trova comunque il link all'archivio

Rispondi SOLO con questo JSON (nessun altro testo):
{{
    "link": "URL completo e diretto al bando",
    "fonte": "Nome del sito dove hai trovato il bando",
    "stato": "attivo" o "scaduto" o "non_trovato",
    "note": "eventuali note sul bando"
}}

Se NON trovi il link diretto, rispondi:
{{
    "link": null,
    "fonte": null,
    "stato": "non_trovato",
    "note": "Motivo per cui non è stato trovato"
}}
"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024
        },
        "tools": [{
            "google_search": {}
        }]
    }

    try:
        response = await client.post(url, json=payload, timeout=60.0)

        if response.status_code == 200:
            data = response.json()

            if "candidates" in data and len(data["candidates"]) > 0:
                content = data["candidates"][0].get("content", {})
                parts = content.get("parts", [])

                for part in parts:
                    text = part.get("text", "")

                    # Estrai JSON dalla risposta
                    json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
                    if json_match:
                        try:
                            result = json.loads(json_match.group())
                            return result
                        except json.JSONDecodeError:
                            pass
        else:
            print(f"   ❌ Errore Gemini: {response.status_code}")

    except Exception as e:
        print(f"   ❌ Errore: {e}")

    return {"link": None, "fonte": None, "stato": "errore"}


async def find_real_link_groq(client: httpx.AsyncClient, bando_title: str, ente: str) -> dict:
    """Usa Groq come fallback per suggerire dove cercare"""

    if not GROQ_API_KEY:
        return {"link": None, "suggerimento": None}

    url = "https://api.groq.com/openai/v1/chat/completions"

    prompt = f"""Per questo bando, suggerisci dove trovare il link ufficiale:

TITOLO: {bando_title}
ENTE: {ente}

Rispondi in JSON con:
{{
    "sito_probabile": "URL del sito dove probabilmente si trova",
    "percorso_suggerito": "Dove cercare nel sito",
    "bando_ricorrente": true/false,
    "periodo_tipico": "quando di solito esce questo bando"
}}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 500
    }

    try:
        response = await client.post(url, json=payload, headers=headers, timeout=30.0)

        if response.status_code == 200:
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            json_match = re.search(r'\{[^{}]*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

    except Exception as e:
        print(f"   ⚠️ Groq fallback error: {e}")

    return {}


async def verify_link(client: httpx.AsyncClient, link: str) -> bool:
    """Verifica che un link sia accessibile"""
    if not link or not link.startswith("http"):
        return False

    try:
        response = await client.head(link, timeout=10.0, follow_redirects=True)
        return response.status_code < 400
    except:
        try:
            response = await client.get(link, timeout=10.0, follow_redirects=True)
            return response.status_code < 400
        except:
            return False


async def fix_all_missing_links():
    """Trova e corregge tutti i link mancanti nel database"""

    print("=" * 70)
    print("🔗 ISS BANDI LINK FIXER - Trova link reali con AI")
    print("=" * 70)
    print(f"⏰ Avviato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Connessione database
    try:
        conn = get_db_connection()
        if not conn:
            print("❌ Impossibile connettersi al database")
            return
        cursor = conn.cursor()
        print("✅ Connesso al database")
    except Exception as e:
        print(f"❌ Errore connessione database: {e}")
        return

    # Trova bandi con link mancanti
    cursor.execute("""
        SELECT id, title, ente, link, fonte
        FROM bandi
        WHERE link LIKE '%non disponibile%'
           OR link LIKE '%Non disponibile%'
           OR link LIKE '%cercare%'
           OR link LIKE '%Cercare%'
           OR link IS NULL
           OR link = ''
        ORDER BY id
    """)

    bandi_da_fixare = cursor.fetchall()
    total = len(bandi_da_fixare)

    print(f"📋 Trovati {total} bandi con link da correggere")
    print()

    if total == 0:
        print("✅ Tutti i bandi hanno già link validi!")
        conn.close()
        return

    # HTTP client
    async with httpx.AsyncClient(
        timeout=60.0,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
        follow_redirects=True
    ) as client:

        fixed = 0
        errors = 0
        not_found = 0

        for i, bando in enumerate(bandi_da_fixare, 1):
            bando_id = bando['id']
            title = bando['title']
            ente = bando['ente'] or 'Regione Campania'

            print(f"[{i}/{total}] 🔍 Cercando: {title[:60]}...")

            # Prova con Gemini
            result = await find_real_link_gemini(client, title, ente)

            new_link = result.get("link")
            stato = result.get("stato", "non_trovato")

            if new_link and new_link.startswith("http"):
                # Verifica che il link funzioni
                is_valid = await verify_link(client, new_link)

                if is_valid:
                    # Aggiorna nel database
                    cursor.execute(
                        "UPDATE bandi SET link = %s WHERE id = %s",
                        (new_link, bando_id)
                    )
                    conn.commit()

                    print(f"   ✅ FIXATO: {new_link[:70]}...")
                    fixed += 1
                else:
                    print(f"   ⚠️ Link non raggiungibile: {new_link[:50]}...")

                    # Prova fallback Groq per suggerimento
                    groq_result = await find_real_link_groq(client, title, ente)
                    if groq_result.get("sito_probabile"):
                        fallback_link = groq_result["sito_probabile"]
                        cursor.execute(
                            "UPDATE bandi SET link = %s WHERE id = %s",
                            (fallback_link, bando_id)
                        )
                        conn.commit()
                        print(f"   🔄 Fallback: {fallback_link}")
                        fixed += 1
                    else:
                        errors += 1
            else:
                print(f"   ❌ Non trovato ({stato})")
                not_found += 1

            # Rate limiting
            await asyncio.sleep(1.5)

        print()
        print("=" * 70)
        print("📊 RIEPILOGO")
        print("=" * 70)
        print(f"   ✅ Link corretti: {fixed}")
        print(f"   ❌ Non trovati: {not_found}")
        print(f"   ⚠️ Errori: {errors}")
        print(f"   📋 Totale processati: {total}")
        print()

    conn.close()
    print("✅ Completato!")


# Link noti per bandi comuni (database locale)
KNOWN_BANDI_LINKS = {
    "bando global districts": "https://www.regione.campania.it/regione/it/tematiche/green-economy/global-districts",
    "piano di promozione culturale": "https://servizi-digitali.regione.campania.it/PromozioneCulturale",
    "bando pubblico per sostegno": "https://servizi-digitali.regione.campania.it/",
    "fondazione con il sud": "https://www.fondazioneconilsud.it/bandi/",
    "bando lettura per tutti": "https://www.cepell.it/bando-lettura-per-tutti/",
    "bando città che legge": "https://www.cepell.it/citta-che-legge/",
    "educare alla lettura": "https://www.cepell.it/educare-alla-lettura/",
    "servizio civile": "https://www.serviziocivile.gov.it/",
    "csv salerno": "https://www.csvsalerno.it/bandi/",
    "sviluppo campania": "https://www.sviluppocampania.it/bandi-aperti/",
    "premio giancarlo pignone": "https://www.fondazionegiancarloquarta.it/",
}


async def quick_fix_known_links():
    """Fix veloce per bandi con link noti"""

    print("🚀 Quick Fix - Link noti")
    print()

    conn = get_db_connection()
    if not conn:
        print("❌ Errore connessione")
        return

    cursor = conn.cursor()
    fixed = 0

    for keyword, link in KNOWN_BANDI_LINKS.items():
        cursor.execute("""
            UPDATE bandi
            SET link = %s
            WHERE LOWER(title) LIKE %s
              AND (link LIKE '%non disponibile%' OR link LIKE '%cercare%')
            RETURNING id, title
        """, (link, f"%{keyword}%"))

        updated = cursor.fetchall()
        if updated:
            for row in updated:
                print(f"   ✅ {row['title'][:50]}... → {link[:40]}...")
                fixed += 1

    conn.commit()
    conn.close()

    print()
    print(f"📊 Corretti {fixed} bandi con quick fix")
    return fixed


if __name__ == "__main__":
    print()
    print("🔗 ISS - BANDI LINK FIXER")
    print("=" * 50)

    # Prima prova quick fix
    asyncio.run(quick_fix_known_links())

    print()
    print("-" * 50)
    print()

    # Poi AI per i restanti
    asyncio.run(fix_all_missing_links())
