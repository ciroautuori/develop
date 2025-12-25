"""
🤖 AI Bandi Agent - Agente Intelligente per trovare Bandi per APS Campania
Usa Google Gemini, Groq e ricerca web per trovare automaticamente opportunità di finanziamento
"""

import asyncio
import logging
import json
import re
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from urllib.parse import urljoin, urlparse

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.bando import Bando, BandoSource, BandoStatus

logger = logging.getLogger(__name__)


class AIBandiAgent:
    """
    Agente AI che cerca automaticamente bandi per APS della Campania.
    Usa:
    - Google Gemini per analisi intelligente
    - Groq per elaborazione veloce
    - Web scraping avanzato con AI
    """

    def __init__(self):
        self.google_api_key = settings.google_api_key
        self.groq_api_key = settings.groq_api_key
        self.openrouter_api_key = settings.openrouter_api_key
        
        # Ollama config
        self.ollama_url = f"http://{settings.ollama_host}:{settings.ollama_port}/api/generate"
        self.ollama_model = settings.ollama_model
        
        self.session: Optional[httpx.AsyncClient] = None

        # Keywords specifiche per APS Campania
        self.keywords_aps = [
            "bando APS", "bando ETS", "bando terzo settore",
            "finanziamento associazioni", "contributi volontariato",
            "bando Campania sociale", "finanziamento ODV",
            "bando inclusione sociale", "bando giovani Campania",
            "bando cultura Campania", "bando ambiente Campania",
            "fondazione con il sud", "fondazione comunità salernitana",
            "regione campania bandi", "sviluppo campania bandi"
        ]

        # 🏛️ TUTTI I COMUNI CAPOLUOGO DELLA CAMPANIA
        self.comuni_campania = {
            # Capoluoghi di Provincia
            "salerno": {
                "url": "https://www.comune.salerno.it",
                "bandi_url": "https://www.comune.salerno.it/client/scheda.aspx?schession=c_bandi",
                "albo_url": "https://www.comune.salerno.it/albo-pretorio"
            },
            "napoli": {
                "url": "https://www.comune.napoli.it",
                "bandi_url": "https://www.comune.napoli.it/bandi",
                "albo_url": "https://www.comune.napoli.it/albo-pretorio"
            },
            "avellino": {
                "url": "https://www.comune.avellino.it",
                "bandi_url": "https://www.comune.avellino.it/it/page/bandi-e-gare",
                "albo_url": "https://www.comune.avellino.it/albo-pretorio"
            },
            "benevento": {
                "url": "https://www.comune.benevento.it",
                "bandi_url": "https://www.comune.benevento.it/bandi-e-gare",
                "albo_url": "https://www.comune.benevento.it/albo-pretorio"
            },
            "caserta": {
                "url": "https://www.comune.caserta.it",
                "bandi_url": "https://www.comune.caserta.it/bandi",
                "albo_url": "https://www.comune.caserta.it/albo-pretorio"
            },
            # Altri comuni importanti provincia Salerno
            "cava_de_tirreni": {
                "url": "https://www.comune.cavadetirreni.sa.it",
                "bandi_url": "https://www.comune.cavadetirreni.sa.it/bandi"
            },
            "battipaglia": {
                "url": "https://www.comune.battipaglia.sa.it",
                "bandi_url": "https://www.comune.battipaglia.sa.it/bandi"
            },
            "eboli": {
                "url": "https://www.comune.eboli.sa.it",
                "bandi_url": "https://www.comune.eboli.sa.it/bandi"
            },
            "nocera_inferiore": {
                "url": "https://www.comune.nocera-inferiore.sa.it",
                "bandi_url": "https://www.comune.nocera-inferiore.sa.it/bandi"
            },
            "scafati": {
                "url": "https://www.comune.scafati.sa.it",
                "bandi_url": "https://www.comune.scafati.sa.it/bandi"
            },
            # Altri comuni importanti provincia Napoli
            "torre_del_greco": {
                "url": "https://www.comune.torredelgreco.na.it",
                "bandi_url": "https://www.comune.torredelgreco.na.it/bandi"
            },
            "giugliano": {
                "url": "https://www.comune.giugliano.na.it",
                "bandi_url": "https://www.comune.giugliano.na.it/bandi"
            },
            "castellammare_di_stabia": {
                "url": "https://www.comune.castellammare-di-stabia.na.it",
                "bandi_url": "https://www.comune.castellammare-di-stabia.na.it/bandi"
            },
            "portici": {
                "url": "https://www.comune.portici.na.it",
                "bandi_url": "https://www.comune.portici.na.it/bandi"
            },
            "ercolano": {
                "url": "https://www.comune.ercolano.na.it",
                "bandi_url": "https://www.comune.ercolano.na.it/bandi"
            },
            "pozzuoli": {
                "url": "https://www.comune.pozzuoli.na.it",
                "bandi_url": "https://www.comune.pozzuoli.na.it/bandi"
            },
        }

        # Fonti prioritarie per la ricerca
        self.priority_sources = [
            "regione.campania.it",
            "sviluppocampania.it",
            "fondazioneconilsud.it",
            "csvnapoli.it",
            "csvsalerno.it",
            "comune.salerno.it",
            "comune.napoli.it",
            "comune.avellino.it",
            "comune.benevento.it",
            "comune.caserta.it",
            "fondazionecomunita.it",
            "italianonprofit.it",
            "infobandi.csvnet.it",
            "cantiereterzosettore.it"
        ]

        # 📅 Intervallo di ricerca automatica
        self.search_interval_hours = 24  # Cerca ogni 24 ore

    async def __aenter__(self):
        self.session = httpx.AsyncClient(
            timeout=60.0,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            },
            follow_redirects=True
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.aclose()

    def generate_hash(self, title: str, ente: str, link: str) -> str:
        """Genera hash univoco per un bando"""
        content = f"{title}_{ente}_{link}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    async def search_with_gemini(self, query: str) -> List[Dict]:
        """Cerca bandi usando Google Gemini AI con grounding"""
        if not self.google_api_key:
            logger.warning("Google API key non configurata")
            return []

        bandi = []
        try:
            # Usa Gemini con Google Search grounding
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_api_key}"

            prompt = f"""Sei un esperto di bandi e finanziamenti per il Terzo Settore italiano.

Cerca e trova tutti i BANDI DI FINANZIAMENTO ATTIVI per:
- Associazioni di Promozione Sociale (APS) in Campania
- Enti del Terzo Settore (ETS) in Campania
- Organizzazioni di Volontariato (ODV) in Campania
- Associazioni culturali e sociali campane

Query specifica: {query}

Per ogni bando trovato, fornisci ESATTAMENTE in formato JSON:
{{
    "bandi": [
        {{
            "titolo": "Nome completo del bando",
            "ente": "Ente che eroga il finanziamento",
            "scadenza": "Data scadenza (formato: GG/MM/AAAA o 'Sempre aperto')",
            "importo": "Importo disponibile o range",
            "link": "URL diretto al bando",
            "descrizione": "Breve descrizione (max 200 parole)",
            "destinatari": "Chi può partecipare",
            "ambito": "Settore (sociale/cultura/ambiente/giovani/etc)"
        }}
    ]
}}

IMPORTANTE:
- Includi SOLO bandi REALMENTE ATTIVI con scadenza futura
- Preferisci bandi della Regione Campania, Province di Salerno, Napoli, etc
- Includi anche bandi nazionali aperti alle APS campane
- Verifica che i link siano funzionanti
- NON inventare bandi, usa solo informazioni reali e verificabili
"""

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 8192
                },
                "tools": [{
                    "google_search": {}
                }]
            }

            response = await self.session.post(url, json=payload)

            if response.status_code == 200:
                data = response.json()

                # Estrai il testo dalla risposta
                if "candidates" in data and len(data["candidates"]) > 0:
                    content = data["candidates"][0].get("content", {})
                    parts = content.get("parts", [])

                    for part in parts:
                        text = part.get("text", "")

                        # Cerca JSON nella risposta
                        json_match = re.search(r'\{[\s\S]*"bandi"[\s\S]*\}', text)
                        if json_match:
                            try:
                                result = json.loads(json_match.group())
                                if "bandi" in result:
                                    for b in result["bandi"]:
                                        bandi.append({
                                            'title': b.get('titolo', '')[:500],
                                            'ente': b.get('ente', 'Non specificato'),
                                            'scadenza_raw': b.get('scadenza', ''),
                                            'importo': b.get('importo', ''),
                                            'link': b.get('link', ''),
                                            'descrizione': b.get('descrizione', '')[:1000],
                                            'destinatari': b.get('destinatari', ''),
                                            'categoria': b.get('ambito', 'sociale'),
                                            'fonte': BandoSource.REGIONE_CAMPANIA,
                                            'ai_source': 'gemini'
                                        })
                            except json.JSONDecodeError:
                                logger.warning("Errore parsing JSON da Gemini")

                logger.info(f"✅ Gemini ha trovato {len(bandi)} bandi")
            else:
                logger.error(f"Errore Gemini API: {response.status_code} - {response.text[:200]}")

        except Exception as e:
            logger.error(f"Errore ricerca Gemini: {e}")

        return bandi

    async def search_with_groq(self, query: str) -> List[Dict]:
        """Cerca bandi usando Groq AI (veloce)"""
        if not self.groq_api_key:
            logger.warning("Groq API key non configurata")
            return []

        bandi = []
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"

            prompt = f"""Sei un esperto di bandi per il Terzo Settore in Campania.

Basandoti sulle tue conoscenze, elenca i bandi di finanziamento più comuni e ricorrenti per APS campane.

Query: {query}

Rispondi SOLO in JSON valido con questo formato:
{{"bandi": [
    {{"titolo": "...", "ente": "...", "scadenza": "...", "link": "...", "descrizione": "...", "tipologia": "..."}}
]}}

Includi bandi di:
- Regione Campania (FSE, FESR, bandi cultura/sociale)
- Fondazione Con il Sud
- Fondazione Comunità Salernitana
- CSV Campania
- Ministero del Lavoro (bandi nazionali)
- Comuni principali (Salerno, Napoli, etc)
"""

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Sei un assistente esperto di bandi per il Terzo Settore italiano. Rispondi sempre in JSON valido."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2,
                "max_tokens": 4096
            }

            response = await self.session.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                # Parse JSON
                json_match = re.search(r'\{[\s\S]*"bandi"[\s\S]*\}', content)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        if "bandi" in result:
                            for b in result["bandi"]:
                                bandi.append({
                                    'title': b.get('titolo', '')[:500],
                                    'ente': b.get('ente', 'Non specificato'),
                                    'scadenza_raw': b.get('scadenza', ''),
                                    'link': b.get('link', ''),
                                    'descrizione': b.get('descrizione', '')[:1000],
                                    'categoria': b.get('tipologia', 'sociale'),
                                    'fonte': BandoSource.FONDAZIONE_COMUNITA,
                                    'ai_source': 'groq'
                                })
                    except json.JSONDecodeError:
                        pass

                logger.info(f"✅ Groq ha trovato {len(bandi)} bandi")
            else:
                logger.error(f"Errore Groq API: {response.status_code}")

        except Exception as e:
            logger.error(f"Errore ricerca Groq: {e}")

        return bandi

    async def search_with_ollama(self, query: str) -> List[Dict]:
        """Cerca bandi usando Ollama Local LLM (Privato e Primario)"""
        bandi = []
        try:
            logger.info(f"🦙 Chiamata Ollama ({self.ollama_model}) per: {query}")
            
            prompt = f"""Sei un esperto di bandi per il Terzo Settore in Campania.
            
            Basandoti sulle tue conoscenze, elenca i bandi di finanziamento più recenti e importanti per APS (Associazioni di Promozione Sociale) campane.
            
            Query: {query}
            
            Rispondi ESATTAMENTE in formato JSON valido:
            {{"bandi": [
                {{"titolo": "...", "ente": "...", "scadenza": "...", "link": "...", "descrizione": "...", "tipologia": "..."}}
            ]}}
            
            Includi bandi reali di:
            - Regione Campania
            - Fondazioni Bancarie (Sud, Salerno, Napoli)
            - CSV Campania
            - Bandi Ministeriali
            """
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }
            
            response = await self.session.post(self.ollama_url, json=payload, timeout=120.0)
            
            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                
                # Parse JSON
                try:
                    result = json.loads(response_text)
                    if "bandi" in result:
                        for b in result["bandi"]:
                            bandi.append({
                                'title': b.get('titolo', '')[:500],
                                'ente': b.get('ente', 'Ollama Insight'),
                                'scadenza_raw': b.get('scadenza', ''),
                                'link': b.get('link', ''),
                                'descrizione': b.get('descrizione', '')[:1000],
                                'categoria': b.get('tipologia', 'sociale'),
                                'fonte': BandoSource.REGIONE_CAMPANIA,
                                'ai_source': 'ollama'
                            })
                except json.JSONDecodeError:
                    logger.error("❌ Errore parsing JSON da Ollama")
                
                logger.info(f"✅ Ollama ha trovato {len(bandi)} bandi")
            else:
                logger.error(f"❌ Errore Ollama API: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ Errore ricerca Ollama: {e}")
            
        return bandi


    async def search_google_custom(self, query: str) -> List[Dict]:
        """Cerca bandi con Google Custom Search API"""
        if not self.google_api_key:
            return []

        bandi = []
        try:
            # Costruisci query ottimizzata
            search_query = f"{query} site:regione.campania.it OR site:sviluppocampania.it OR site:fondazioneconilsud.it bando finanziamento APS"

            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_api_key,
                "cx": "017576662512468239146:omuauf_gy2o",  # CSE pubblico
                "q": search_query,
                "num": 10,
                "lr": "lang_it"
            }

            response = await self.session.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])

                for item in items:
                    title = item.get("title", "")
                    link = item.get("link", "")
                    snippet = item.get("snippet", "")

                    # Filtra solo risultati rilevanti
                    if any(kw in title.lower() or kw in snippet.lower()
                           for kw in ['bando', 'finanziamento', 'contributo', 'aps', 'ets']):
                        bandi.append({
                            'title': title[:500],
                            'ente': self._extract_ente_from_url(link),
                            'scadenza_raw': '',
                            'link': link,
                            'descrizione': snippet[:1000],
                            'fonte': BandoSource.REGIONE_CAMPANIA,
                            'ai_source': 'google_search'
                        })

                logger.info(f"✅ Google Search ha trovato {len(bandi)} risultati")

        except Exception as e:
            logger.error(f"Errore Google Custom Search: {e}")

        return bandi

    async def _search_comuni_campania(self) -> List[Dict]:
        """🏛️ Cerca bandi da TUTTI i comuni campani usando Gemini con Google Search"""

        all_bandi = []

        if not self.google_api_key:
            logger.warning("⚠️ Google API key non configurata, skip ricerca comuni")
            return []

        # Lista completa dei comuni da cercare
        comuni_da_cercare = [
            # Capoluoghi di provincia
            ("Salerno", "comune.salerno.it"),
            ("Napoli", "comune.napoli.it"),
            ("Avellino", "comune.avellino.it"),
            ("Benevento", "comune.benevento.it"),
            ("Caserta", "comune.caserta.it"),
            # Comuni importanti provincia Salerno
            ("Cava de' Tirreni", "comune.cavadetirreni.sa.it"),
            ("Battipaglia", "comune.battipaglia.sa.it"),
            ("Eboli", "comune.eboli.sa.it"),
            ("Nocera Inferiore", "comune.nocera-inferiore.sa.it"),
            ("Scafati", "comune.scafati.sa.it"),
            ("Pagani", "comune.pagani.sa.it"),
            ("Angri", "comune.angri.sa.it"),
            ("Sarno", "comune.sarno.sa.it"),
            ("Mercato San Severino", "comune.mercatosanseverino.sa.it"),
            # Comuni importanti provincia Napoli
            ("Torre del Greco", "comune.torredelgreco.na.it"),
            ("Giugliano in Campania", "comune.giugliano.na.it"),
            ("Castellammare di Stabia", "comune.castellammare-di-stabia.na.it"),
            ("Portici", "comune.portici.na.it"),
            ("Ercolano", "comune.ercolano.na.it"),
            ("Pozzuoli", "comune.pozzuoli.na.it"),
            ("Afragola", "comune.afragola.na.it"),
            ("Casoria", "comune.casoria.na.it"),
            ("Marano di Napoli", "comune.marano.na.it"),
            # Comuni importanti provincia Caserta
            ("Aversa", "comune.aversa.ce.it"),
            ("Maddaloni", "comune.maddaloni.ce.it"),
            ("Marcianise", "comune.marcianise.ce.it"),
            ("Mondragone", "comune.mondragone.ce.it"),
            # Comuni provincia Avellino
            ("Ariano Irpino", "comune.arianoirpino.av.it"),
            ("Atripalda", "comune.atripalda.av.it"),
            # Comuni provincia Benevento
            ("Montesarchio", "comune.montesarchio.bn.it"),
            ("San Giorgio del Sannio", "comune.sangiorgodelsannio.bn.it"),
        ]

        logger.info(f"🏛️ Ricerca bandi da {len(comuni_da_cercare)} comuni campani...")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.google_api_key}"

        # Fai una ricerca aggregata per gruppi di comuni
        for i in range(0, len(comuni_da_cercare), 5):
            gruppo_comuni = comuni_da_cercare[i:i+5]
            nomi_comuni = ", ".join([c[0] for c in gruppo_comuni])

            prompt = f"""Sei un esperto di bandi e finanziamenti per il Terzo Settore italiano.

CERCA TUTTI I BANDI DI FINANZIAMENTO ATTIVI pubblicati dai seguenti Comuni della Campania:
{nomi_comuni}

Cerca su:
- Siti ufficiali dei comuni (.comune.*.it)
- Albi pretori
- Sezioni bandi e avvisi pubblici
- Sezioni contributi e finanziamenti

Trova bandi per:
- Associazioni di Promozione Sociale (APS)
- Enti del Terzo Settore (ETS)
- Organizzazioni di Volontariato (ODV)
- Associazioni culturali, sportive, sociali
- Contributi per eventi e manifestazioni
- Sostegno ad attività sociali

Per ogni bando trovato, fornisci ESATTAMENTE in formato JSON:
{{
    "bandi": [
        {{
            "titolo": "Nome completo del bando",
            "ente": "Comune di [nome]",
            "scadenza": "Data scadenza (GG/MM/AAAA o 'Sempre aperto')",
            "importo": "Importo disponibile",
            "link": "URL DIRETTO E COMPLETO al bando (deve iniziare con https://)",
            "descrizione": "Breve descrizione (max 150 parole)",
            "destinatari": "Chi può partecipare",
            "ambito": "sociale/cultura/sport/ambiente/giovani"
        }}
    ]
}}

REGOLE CRITICHE:
1. I link DEVONO essere URL completi e funzionanti (https://www.comune.*.it/...)
2. NON inventare bandi - usa SOLO informazioni verificate dalla ricerca
3. Includi SOLO bandi con scadenza futura o sempre aperti
4. Se non trovi bandi per un comune, non inventarli
"""

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 8192
                },
                "tools": [{
                    "google_search": {}
                }]
            }

            try:
                response = await self.session.post(url, json=payload, timeout=90.0)

                if response.status_code == 200:
                    data = response.json()

                    if "candidates" in data and len(data["candidates"]) > 0:
                        content = data["candidates"][0].get("content", {})
                        parts = content.get("parts", [])

                        for part in parts:
                            text = part.get("text", "")

                            # Cerca JSON nella risposta
                            json_match = re.search(r'\{[\s\S]*"bandi"[\s\S]*\}', text)
                            if json_match:
                                try:
                                    result = json.loads(json_match.group())
                                    if "bandi" in result:
                                        for b in result["bandi"]:
                                            link = b.get('link', '')
                                            # Verifica che il link sia valido
                                            if link and link.startswith('https://'):
                                                all_bandi.append({
                                                    'title': b.get('titolo', '')[:500],
                                                    'ente': b.get('ente', 'Comune'),
                                                    'scadenza_raw': b.get('scadenza', ''),
                                                    'importo': b.get('importo', ''),
                                                    'link': link,
                                                    'descrizione': b.get('descrizione', '')[:1000],
                                                    'destinatari': b.get('destinatari', ''),
                                                    'categoria': b.get('ambito', 'sociale'),
                                                    'fonte': BandoSource.COMUNE_SALERNO,
                                                    'ai_source': 'gemini_comuni'
                                                })
                                                logger.info(f"   ✅ Trovato: {b.get('titolo', '')[:50]}...")
                                except json.JSONDecodeError:
                                    pass
                else:
                    logger.warning(f"   ⚠️ Errore API Gemini: {response.status_code}")

            except Exception as e:
                logger.warning(f"   ❌ Errore ricerca comuni {nomi_comuni}: {e}")

            # Rate limiting tra gruppi
            await asyncio.sleep(2)

        logger.info(f"🏛️ Ricerca comuni completata: {len(all_bandi)} bandi trovati")
        return all_bandi

    def _extract_ente_from_url(self, url: str) -> str:
        """Estrae l'ente dal dominio URL"""
        domain = urlparse(url).netloc.lower()

        ente_map = {
            'regione.campania.it': 'Regione Campania',
            'sviluppocampania.it': 'Sviluppo Campania',
            'fondazioneconilsud.it': 'Fondazione Con il Sud',
            'csvnapoli.it': 'CSV Napoli',
            'csvsalerno.it': 'CSV Salerno',
            'comune.salerno.it': 'Comune di Salerno',
            'comune.napoli.it': 'Comune di Napoli',
            'comune.avellino.it': 'Comune di Avellino',
            'comune.benevento.it': 'Comune di Benevento',
            'comune.caserta.it': 'Comune di Caserta',
            'infobandi.csvnet.it': 'CSVnet Italia',
            'italianonprofit.it': 'Italia Non Profit'
        }

        for domain_key, ente_name in ente_map.items():
            if domain_key in domain:
                return ente_name

        # Estrai nome comune da URL
        if 'comune.' in domain:
            parts = domain.replace('www.', '').split('.')
            if len(parts) >= 2:
                nome_comune = parts[1].replace('-', ' ').title()
                return f"Comune di {nome_comune}"

        return domain.replace('www.', '').split('.')[0].title()

    async def scrape_with_ai_analysis(self, url: str) -> List[Dict]:
        """Scrapa una pagina e usa AI per estrarre bandi"""
        bandi = []
        try:
            response = await self.session.get(url, timeout=30)
            response.raise_for_status()

            # Estrai testo dalla pagina
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')

            # Rimuovi script e style
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()

            text = soup.get_text(separator='\n', strip=True)[:10000]

            # Usa Groq per analizzare il contenuto (più veloce)
            if self.groq_api_key:
                analysis = await self._analyze_page_with_ai(text, url)
                bandi.extend(analysis)

        except Exception as e:
            logger.warning(f"Errore scraping {url}: {e}")

        return bandi

    async def _analyze_page_with_ai(self, text: str, source_url: str) -> List[Dict]:
        """Analizza il testo di una pagina con AI per estrarre bandi"""
        bandi = []

        try:
            url = "https://api.groq.com/openai/v1/chat/completions"

            prompt = f"""Analizza questo testo estratto da una pagina web e identifica tutti i BANDI DI FINANZIAMENTO per APS/ETS.

TESTO:
{text[:5000]}

URL FONTE: {source_url}

Estrai SOLO bandi reali con informazioni concrete. Rispondi in JSON:
{{"bandi": [
    {{"titolo": "...", "ente": "...", "scadenza": "...", "importo": "...", "descrizione": "..."}}
]}}

Se non trovi bandi validi, rispondi: {{"bandi": []}}
"""

            headers = {
                "Authorization": f"Bearer {self.groq_api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": "llama-3.1-8b-instant",  # Modello veloce
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 2048
            }

            response = await self.session.post(url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")

                json_match = re.search(r'\{[\s\S]*"bandi"[\s\S]*\}', content)
                if json_match:
                    result = json.loads(json_match.group())
                    for b in result.get("bandi", []):
                        if b.get("titolo"):
                            bandi.append({
                                'title': b.get('titolo', '')[:500],
                                'ente': b.get('ente', self._extract_ente_from_url(source_url)),
                                'scadenza_raw': b.get('scadenza', ''),
                                'importo': b.get('importo', ''),
                                'link': source_url,
                                'descrizione': b.get('descrizione', '')[:1000],
                                'fonte': BandoSource.REGIONE_CAMPANIA,
                                'ai_source': 'page_analysis'
                            })

        except Exception as e:
            logger.warning(f"Errore analisi AI pagina: {e}")

        return bandi

    async def run_full_search(self, db: AsyncSession, keywords: List[str] = None) -> Dict:
        """Esegue una ricerca completa con tutti i metodi AI"""

        logger.info("🤖 Avvio AI Bandi Agent - Ricerca Completa Campania")

        all_bandi = []
        results = {
            'status': 'running',
            'started_at': datetime.now().isoformat(),
            'sources': {}
        }

        # Keywords di default se non specificate
        if not keywords:
            keywords = self.keywords_aps

        try:
            # 1. 🏛️ RICERCA BANDI DAI COMUNI CAMPANI (PRIORITÀ)
            logger.info("🏛️ Fase 1: Ricerca bandi dai Comuni della Campania")
            comuni_bandi = await self._search_comuni_campania()
            all_bandi.extend(comuni_bandi)
            results['sources']['comuni_campania'] = len(comuni_bandi)

            # 2. 🦙 RICERCA CON OLLAMA (PRIMARIO)
            if settings.use_ollama:
                logger.info(f"🦙 Fase 2: Ricerca con Ollama (Primario - {self.ollama_model})")
                for query in keywords[:5]:
                    ollama_results = await self.search_with_ollama(query)
                    all_bandi.extend(ollama_results)
                    results['sources']['ollama'] = results['sources'].get('ollama', 0) + len(ollama_results)

            # 3. Ricerca con Gemini (Fallback 1)
            logger.info("🔍 Fase 3: Ricerca con Gemini AI + Google Search (Fallback)")
            for query in keywords[:3]:  # Ridotto se Ollama è attivo
                logger.info(f"🔍 Cercando con Gemini: {query}")
                gemini_results = await self.search_with_gemini(query)
                all_bandi.extend(gemini_results)
                results['sources']['gemini'] = results['sources'].get('gemini', 0) + len(gemini_results)
                await asyncio.sleep(1)

            # 4. Ricerca con Groq (Fallback 2)
            logger.info("⚡ Fase 4: Ricerca con Groq AI (Fallback)")
            for query in keywords[:2]:
                logger.info(f"⚡ Cercando con Groq: {query}")
                groq_results = await self.search_with_groq(query)
                all_bandi.extend(groq_results)
                results['sources']['groq'] = results['sources'].get('groq', 0) + len(groq_results)

        except Exception as e:
            logger.error(f"❌ Errore durante loop ricerca completa: {e}")
            results['status'] = 'error'
            results['error'] = str(e)

        # Rimuovi duplicati basati su link o titolo
        unique_bandi = []
        seen_links = set()
        seen_titles = set()

        for b in all_bandi:
            link = b.get('link', '').strip()
            title = b.get('title', '').strip().lower()
            
            if link and link not in seen_links and title not in seen_titles:
                seen_links.add(link)
                seen_titles.add(title)
                unique_bandi.append(b)

        logger.info(f"✅ Ricerca completata. Trovati {len(unique_bandi)} bandi unici.")
        
        # Salva nel DB e analizza
        saved_count = 0
        from app.crud.bando import bando_crud
        from app.schemas.bando import BandoCreate, BandoUpdate
        from app.services.match_service import ISS_PROFILE
        
        for b in unique_bandi:
            try:
                # Crea schema 
                bando_in = BandoCreate(
                    title=b['title'],
                    ente=b['ente'],
                    scadenza_raw=b.get('scadenza_raw'),
                    link=b['link'],
                    descrizione=b.get('descrizione'),
                    fonte=b['fonte'],
                    importo=b.get('importo'),
                    categoria=b.get('categoria'),
                    keyword_match=b.get('keyword_match', str(b.get('ai_source', 'ai')))
                )
                
                # Salva (gestisce duplicati internamente)
                bando_obj = await bando_crud.create_bando(db, bando_in)
                if bando_obj:
                    # Analisi immediata del match per persistenza
                    tender_text = f"TITOLO: {bando_obj.title}\nENTE: {bando_obj.ente}\nDESCRIZIONE: {bando_obj.descrizione or ''}"
                    analysis = await self.analyze_match(tender_text, ISS_PROFILE)
                    
                    await bando_crud.update_bando(db, bando_obj.id, BandoUpdate(
                        ai_score=analysis.get('score', 0),
                        ai_reasoning=analysis.get('reasoning', '')
                    ))
                    saved_count += 1
            except Exception as e:
                logger.warning(f"Errore salvataggio/analisi bando {b.get('title')}: {e}")

        results['status'] = 'completed'
        results['completed_at'] = datetime.now().isoformat()
        results['total_found'] = len(unique_bandi)
        results['new_saved'] = saved_count
        
        return results

    async def analyze_match(self, tender_text: str, association_profile: str) -> Dict[str, Any]:
        """
        🧠 Analizza il match tra un bando e il profilo dell'associazione.
        Restituisce un punteggio (0-100) e una spiegazione.
        """
        match_result = {
            "score": 0,
            "reasoning": "Analisi non riuscita",
            "strengths": [],
            "weaknesses": []
        }

        # Usa Ollama se disponibile (gratis e privato), altrimenti Groq (veloce) o Gemini
        try:
            # 0. Recupera contesto da RAG (Personal Knowledge)
            from app.services.rag_service import rag_service
            rag_results = rag_service.query(tender_text[:1000]) # Query with first 1000 chars of tender
            
            rag_context = ""
            if rag_results and rag_results['documents']:
                rag_context = "\n".join(rag_results['documents'][0])
                logger.info(f"📚 RAG Context retrieved: {len(rag_results['documents'][0])} chunks")

            prompt = f"""Sei un consulente esperto per il Terzo Settore. Analizza la compatibilità tra questo bando e l'associazione.

--- PROFILO ASSOCIAZIONE ---
{association_profile}

--- CONTESTO OPERATIVO (LINEE GUIDA INTERNE) ---
{rag_context}

--- BANDO ---
{tender_text[:3000]}

--- TASK ---
Valuta quanto questo bando è adatto all'associazione.
Assegna un punteggio da 0 a 100.
0 = Completamente fuori target
100 = Bando perfetto

Rispondi SOLO in JSON:
{{
    "score": <numero 0-100>,
    "reasoning": "<breve spiegazione discorsiva>",
    "strengths": ["<punto di forza 1>", "<punto di forza 2>"],
    "weaknesses": ["<punto debole 1>", "<punto debole 2>"]
}}
"""
            
            # 1. Prova con Ollama (Llama 3)
            if settings.use_ollama:
                payload = {
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
                response = await self.session.post(self.ollama_url, json=payload, timeout=60.0)
                if response.status_code == 200:
                    data = response.json()
                    json_str = data.get("response", "")
                    match_result = json.loads(json_str)
                    return match_result

            # 2. Fallback su Groq
            if self.groq_api_key:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {self.groq_api_key}"}
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": "Rispondi sempre in JSON valido."},
                        {"role": "user", "content": prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }
                response = await self.session.post(url, json=payload, headers=headers)
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    match_result = json.loads(content)
                    return match_result

        except Exception as e:
            logger.error(f"Errore durante analyze_match [{type(e).__name__}]: {str(e)}")
            match_result["reasoning"] = f"Errore analisi AI: {str(e)}"

        return match_result

    def _parse_date(self, date_string: str) -> Optional[datetime]:
        """Parse data in vari formati"""
        if not date_string:
            return None

        patterns = [
            (r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', lambda m: datetime(int(m[3]), int(m[2]), int(m[1]))),
            (r'(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})', lambda m: datetime(int(m[1]), int(m[2]), int(m[3]))),
        ]

        mesi = {
            'gennaio': 1, 'febbraio': 2, 'marzo': 3, 'aprile': 4,
            'maggio': 5, 'giugno': 6, 'luglio': 7, 'agosto': 8,
            'settembre': 9, 'ottobre': 10, 'novembre': 11, 'dicembre': 12
        }

        # Prova pattern con mese testuale
        month_pattern = r'(\d{1,2})\s+(gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)\s+(\d{4})'
        match = re.search(month_pattern, date_string.lower())
        if match:
            try:
                return datetime(int(match.group(3)), mesi[match.group(2)], int(match.group(1)))
            except:
                pass

        for pattern, parser in patterns:
            match = re.search(pattern, date_string)
            if match:
                try:
                    return parser(match.groups())
                except:
                    continue

        return None

    def _parse_importo(self, importo_str: str) -> Optional[float]:
        """Estrae importo numerico da stringa"""
        if not importo_str:
            return None

        # Cerca numeri
        numbers = re.findall(r'[\d.,]+', importo_str.replace('.', '').replace(',', '.'))
        if numbers:
            try:
                return float(numbers[0])
            except:
                pass

        return None


# Istanza singleton
ai_bandi_agent = AIBandiAgent()
