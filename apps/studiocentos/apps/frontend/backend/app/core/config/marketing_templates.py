"""
Marketing Fallback Templates - Used when AI service unavailable.

These templates provide basic content when the AI microservice is unreachable.
They are NOT a replacement for AI-generated content.
"""

from typing import Dict

# Standard hashtags for social media
HASHTAGS = "#PMI #DigitalizzazionePMI #MadeInItaly #Salerno #StudioCentOS"


def get_fallback_template(content_type: str, topic: str = "") -> str:
    """
    Get fallback template for content generation.

    Args:
        content_type: Type of content (blog, social, ad, video)
        topic: Optional topic to include

    Returns:
        Template string
    """
    templates = {
        "blog": f"""# {topic or 'Digitalizzazione PMI'}: Guida per PMI Italiane

StudioCentOS aiuta le PMI a digitalizzarsi con soluzioni accessibili.

**Servizi:**
- Sito Web Vetrina da 990€ (7 giorni)
- E-commerce da 2.490€ (21 giorni)
- App Mobile da 4.990€ (45 giorni)

Contattaci: info@studiocentos.it | studiocentos.it""",

        "social": f"""🚀 Il tuo business merita di essere online!

💻 Sito Web da 990€
🛒 E-commerce da 2.490€
📱 App Mobile da 4.990€

Preventivo GRATUITO → studiocentos.it

{HASHTAGS}""",

        "ad": f"""Gentile Imprenditore,

StudioCentOS offre soluzioni digitali per PMI:
• Sito Web da 990€ (7 giorni)
• E-commerce da 2.490€
• App Mobile da 4.990€

Preventivo gratuito: info@studiocentos.it

Ciro Autuori - StudioCentOS""",

        "video": """[SCRIPT VIDEO 30s]

[0:00] "Hai un'attività ma non sei online?"
[0:10] "Sito web da 990€, pronto in 7 giorni"
[0:20] "StudioCentOS - Software House Salerno"
[0:25] "studiocentos.it - Preventivo gratuito" """
    }

    return templates.get(content_type, templates["social"])


def get_fallback_chat_response(message: str) -> str:
    """
    Get fallback chat response when AI unavailable.

    Args:
        message: User message

    Returns:
        Fallback response string
    """
    msg_lower = message.lower()

    if any(w in msg_lower for w in ["prezzo", "costo", "quanto"]):
        return (
            "I nostri servizi partono da 990€ per un sito web vetrina. "
            "Per un preventivo personalizzato, contattaci a info@studiocentos.it "
            "o prenota una consulenza gratuita su studiocentos.it"
        )

    if any(w in msg_lower for w in ["servizi", "cosa fate", "offrite"]):
        return (
            "StudioCentOS offre: Sviluppo Web Enterprise, App Mobile, "
            "E-commerce, AI Integration, Automazione Processi. "
            "Visita studiocentos.it per maggiori dettagli."
        )

    if any(w in msg_lower for w in ["contatt", "email", "telefono"]):
        return (
            "Puoi contattarci: Email info@studiocentos.it | "
            "Tel: +39 340 321 7806 | Via Francesco Vernieri 20, Scafati (SA)"
        )

    if any(w in msg_lower for w in ["ciao", "buongiorno", "salve"]):
        return "Ciao! Come posso aiutarti oggi con il tuo progetto digitale?"

    return (
        "Grazie per il tuo messaggio! Per una risposta più dettagliata, "
        "contattaci a info@studiocentos.it o prenota una consulenza gratuita "
        "su studiocentos.it. Ti risponderemo entro 24h."
    )


# Need reasons for lead generation
LEAD_NEED_REASONS: Dict[str, str] = {
    "sito_web": "Nessuna presenza online rilevata, solo profilo Google My Business",
    "sito_obsoleto": "Sito web non responsive, non ottimizzato per mobile",
    "ecommerce": "Vendita solo in negozio fisico, nessun canale online",
    "prenotazioni": "Prenotazioni solo telefoniche, nessun sistema digitale",
    "social": "Profili social inattivi da oltre 6 mesi",
    "automazione": "Gestione manuale di fatturazione e contabilità",
    "app": "Clientela giovane ma nessuna app dedicata"
}


# Italian city coordinates for lead search
CITY_COORDINATES: Dict[str, Dict[str, float]] = {
    "Salerno": {"lat": 40.6824, "lng": 14.7681},
    "Napoli": {"lat": 40.8518, "lng": 14.2681},
    "Roma": {"lat": 41.9028, "lng": 12.4964},
    "Milano": {"lat": 45.4642, "lng": 9.1900},
    "Torino": {"lat": 45.0703, "lng": 7.6869},
    "Bologna": {"lat": 44.4949, "lng": 11.3426},
    "Firenze": {"lat": 43.7696, "lng": 11.2558},
    "Bari": {"lat": 41.1171, "lng": 16.8719},
    "Palermo": {"lat": 38.1157, "lng": 13.3615},
    "Catania": {"lat": 37.5079, "lng": 15.0830},
    "Genova": {"lat": 44.4056, "lng": 8.9463},
    "Venezia": {"lat": 45.4408, "lng": 12.3155},
    "Verona": {"lat": 45.4384, "lng": 10.9916},
    "Padova": {"lat": 45.4064, "lng": 11.8768},
}


# Industry to Google Places type mapping
INDUSTRY_PLACE_TYPES: Dict[str, list] = {
    "ristorazione": ["restaurant", "meal_takeaway", "bakery", "cafe"],
    "retail": ["clothing_store", "shoe_store", "jewelry_store", "book_store"],
    "studi_professionali": ["lawyer", "accounting"],
    "salute": ["doctor", "dentist", "physiotherapist", "hospital"],
    "beauty": ["beauty_salon", "hair_care", "spa"],
    "fitness": ["gym"],
    "immobiliare": ["real_estate_agency"],
    "automotive": ["car_repair", "car_dealer"],
    "turismo": ["lodging", "travel_agency"],
    "artigianato": ["electrician", "plumber", "roofing_contractor"],
    "formazione": ["school", "university"],
    "eventi": ["event_planner"]
}
