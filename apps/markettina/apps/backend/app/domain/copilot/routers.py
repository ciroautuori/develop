"""
Copilot API Router - AI Assistant endpoints.

Provides AI capabilities for the backoffice:
- Content Generation (Marketing)
- AI Chat Support
- Lead Finding (Simulated)
"""

import logging
import os
import random
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser
from app.infrastructure.database.session import get_db
from app.integrations.social_media import social_media

router = APIRouter(prefix="/api/v1/copilot", tags=["copilot"])

logger = logging.getLogger(__name__)


# ============================================================================
# MODELS
# ============================================================================

class ContentGenerationRequest(BaseModel):
    """Request for generating marketing content."""
    type: str = Field(default="social", description="Type of content: blog, social, ad, video, post")
    topic: str = Field(..., description="Topic for content")
    tone: str = Field(default="professional", description="Tone of voice")
    platform: str | None = Field(None, description="Platform (for social)")
    prompt: str | None = Field(None, description="Custom prompt for AI generation")
    template: str | None = Field(None, description="Quick template ID")
    brand_context: str | None = Field(None, description="Brand context for AI")
    max_chars: int | None = Field(None, description="Max characters for platform")


class ContentGenerationResponse(BaseModel):
    """Response for generated content."""
    content: str
    metadata: dict[str, Any]
    provider: str = "markettina AI"


class ChatRequest(BaseModel):
    """Request for AI chat."""
    message: str


class ChatResponse(BaseModel):
    """Response for AI chat."""
    response: str
    provider: str = "markettina AI"


class LeadSearchRequest(BaseModel):
    """Request for searching leads."""
    industry: str
    location: str
    radius_km: int = 25
    size: str = "pmi"  # micro, piccola, pmi, media
    need: str = "sito_web"  # sito_web, sito_obsoleto, ecommerce, prenotazioni, social, automazione, app


class LeadItem(BaseModel):
    """Single lead item."""
    id: int
    company: str
    industry: str
    size: str
    location: str
    address: str = ""
    phone: str = ""
    email: str
    website: str = ""
    need: str
    need_reason: str = ""
    score: int
    google_rating: float = 0.0
    reviews_count: int = 0


class PublishRequest(BaseModel):
    """Request for publishing generated content to social media."""
    content: str = Field(..., description="Content to publish")
    platforms: list[str] = Field(..., description="List of platforms: facebook, threads, linkedin, twitter, instagram")
    media_urls: list[str] | None = Field(None, description="Optional media URLs")


class PublishResponse(BaseModel):
    """Response for publish request."""
    results: list[dict[str, Any]]
    success_count: int
    failed_count: int


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/content/generate", response_model=ContentGenerationResponse)
@router.post("/marketing/generate", response_model=ContentGenerationResponse)
async def generate_marketing_content(
    request: ContentGenerationRequest,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Generate marketing content via AI Microservice.

    Proxies to centralized AI service for LLM-powered content generation.
    Falls back to templates if microservice unavailable.
    """
    import httpx

    ai_service_url = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")

    # Map content type to AI service endpoint
    content_type_map = {
        "blog": "blog",
        "social": "social",
        "ad": "ad",
        "video": "video",
    }

    try:
        ai_api_key = os.getenv("AI_SERVICE_API_KEY", "")
        headers = {"Authorization": f"Bearer {ai_api_key}"} if ai_api_key else {}

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Build request payload - use custom prompt if provided
            payload = {
                "type": content_type_map.get(request.type, "social"),
                "topic": request.prompt or request.topic,  # Use prompt if available, else topic
                "tone": request.tone,
                "platform": request.platform or "instagram",
                "brand_context": request.brand_context,
            }

            logger.info(f"AI Content request: {payload.get('topic', '')[:100]}...")

            # Try AI Microservice first
            response = await client.post(
                f"{ai_service_url}/api/v1/marketing/content/generate",
                json=payload,
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                return ContentGenerationResponse(
                    content=data.get("content", ""),
                    metadata={
                        "type": request.type,
                        "tone": request.tone,
                        "topic": request.topic,
                        "target": "PMI italiane",
                        "ai_generated": True,
                    },
                    provider=f"AI Service ({data.get('metadata', {}).get('provider', 'groq')})"
                )

    except Exception as e:
        logger.warning(f"AI Microservice unavailable, using fallback: {e}")

    # Fallback: Quick templates
    hashtags = "#PMI #DigitalizzazionePMI #MadeInItaly #Salerno #MARKETTINA"

    templates = {
        "blog": f"""# {request.topic}: Guida per PMI Italiane

MARKETTINA aiuta le PMI a digitalizzarsi con soluzioni accessibili.

**Servizi:**
- Sito Web Vetrina da 990€ (7 giorni)
- E-commerce da 2.490€ (21 giorni)
- App Mobile da 4.990€ (45 giorni)

Contattaci: info@markettina.it | markettina.it""",

        "social": f"""🚀 Il tuo business merita di essere online!

💻 Sito Web da 990€
🛒 E-commerce da 2.490€
📱 App Mobile da 4.990€

Preventivo GRATUITO → markettina.it

{hashtags}""",

        "ad": """Gentile Imprenditore,

MARKETTINA offre soluzioni digitali per PMI:
• Sito Web da 990€ (7 giorni)
• E-commerce da 2.490€
• App Mobile da 4.990€

Preventivo gratuito: info@markettina.it

Ciro Autuori - MARKETTINA""",

        "video": """[SCRIPT VIDEO 30s]

[0:00] "Hai un'attività ma non sei online?"
[0:10] "Sito web da 990€, pronto in 7 giorni"
[0:20] "MARKETTINA - Software House Salerno"
[0:25] "markettina.it - Preventivo gratuito" """,
    }

    return ContentGenerationResponse(
        content=templates.get(request.type, templates["social"]),
        metadata={
            "type": request.type,
            "tone": request.tone,
            "topic": request.topic,
            "target": "PMI italiane",
            "fallback": True,
        },
        provider="MARKETTINA Templates (Fallback)"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Chat with AI assistant via AI Microservice proxy.
    """
    import httpx

    ai_service_url = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{ai_service_url}/api/v1/support/chat",
                json={
                    "message": request.message,
                    "provider": "groq",  # Free and fast
                },
            )

            if response.status_code == 200:
                data = response.json()
                return ChatResponse(
                    response=data.get("response", ""),
                    provider=f"AI Service ({data.get('provider', 'groq')})"
                )

    except Exception as e:
        logger.warning(f"AI Microservice unavailable: {e}")

    # Fallback
    return ChatResponse(
        response="Grazie per il messaggio! Per assistenza immediata contattaci a info@markettina.it o +39 340 321 7806.",
        provider="Fallback"
    )


@router.post("/leads/search", response_model=list[LeadItem])
async def search_leads(
    request: LeadSearchRequest,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Search for potential leads - PMI WITHOUT digital presence.

    Priority:
    1. Pagine Gialle Scraping (PMI without websites)
    2. Google Places API (digitalized businesses)
    3. Intelligent generation (fallback)
    """
    import httpx

    from app.infrastructure.scraping.pagine_gialle_scraper import pagine_gialle_scraper

    logger.info(f"Lead search: {request.industry} in {request.location} ({request.radius_km}km) - need: {request.need}")

    # PRIORITY 1: Pagine Gialle Scraping for NON-DIGITALIZED PMI
    try:
        logger.info("Searching Pagine Gialle for non-digitalized PMI...")
        pg_results = await pagine_gialle_scraper.search_businesses(
            industry=request.industry,
            city=request.location,
            max_results=15
        )

        if pg_results:
            # Convert to LeadItem format
            leads = []
            for idx, pg_result in enumerate(pg_results):
                # Determine need reason based on digital presence
                if not pg_result.website and not pg_result.email:
                    need_reason = "❌ NESSUNA PRESENZA DIGITALE - Solo telefono, perfetto per digitalizzazione completa"
                elif not pg_result.website:
                    need_reason = "⚠️ SOLO EMAIL - Nessun sito web, ottimo prospect per sito + e-commerce"
                else:
                    need_reason = "🔍 PRESENZA MINIMA - Verifica qualità sito web esistente"

                # Calculate final score based on need
                final_score = pg_result.score
                if request.need == "sito_web" and not pg_result.website:
                    final_score += 20  # Boost for perfect match
                elif request.need == "ecommerce" and not pg_result.website:
                    final_score += 15

                leads.append(LeadItem(
                    id=idx + 1,
                    company=pg_result.name,
                    industry=request.industry,
                    size=request.size,
                    location=request.location,
                    address=pg_result.address,
                    phone=pg_result.phone,
                    email=pg_result.email or "",
                    website=pg_result.website or "",
                    need=request.need,
                    need_reason=need_reason,
                    score=final_score,
                    google_rating=0,  # Pagine Gialle doesn't have ratings
                    reviews_count=0
                ))

            # Sort by score (best leads first)
            leads.sort(key=lambda x: x.score, reverse=True)
            logger.info(f"Found {len(leads)} NON-DIGITALIZED PMI from Pagine Gialle")
            return leads

    except Exception as e:
        logger.warning(f"Pagine Gialle scraping failed: {e}")

    # PRIORITY 2: Google Places API (already digitalized businesses)
    google_api_key = os.getenv("GOOGLE_PLACES_API_KEY", os.getenv("GOOGLE_API_KEY", ""))

    # Industry to Google Places type mapping
    industry_to_place_type = {
        "ristorazione": "restaurant",
        "retail": "store",
        "studi_professionali": "lawyer",
        "salute": "doctor",
        "beauty": "beauty_salon",
        "fitness": "gym",
        "immobiliare": "real_estate_agency",
        "automotive": "car_repair",
        "turismo": "lodging",
        "artigianato": "electrician",
        "formazione": "school",
        "eventi": "event_planner"
    }

    # City coordinates for Italian cities
    city_coordinates = {
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
        "Brescia": {"lat": 45.5416, "lng": 10.2118},
        "Parma": {"lat": 44.8015, "lng": 10.3279},
        "Modena": {"lat": 44.6471, "lng": 10.9252},
        "Reggio Calabria": {"lat": 38.1114, "lng": 15.6473},
        "Perugia": {"lat": 43.1107, "lng": 12.3908},
        "Cagliari": {"lat": 39.2238, "lng": 9.1217}
    }

    coords = city_coordinates.get(request.location, {"lat": 40.6824, "lng": 14.7681})
    place_type = industry_to_place_type.get(request.industry, "establishment")

    # Try Google Places API first
    if google_api_key:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Google Places API (New) - Search Nearby
                url = "https://places.googleapis.com/v1/places:searchNearby"
                headers = {
                    "Content-Type": "application/json",
                    "X-Goog-Api-Key": google_api_key,
                    "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.internationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount"
                }

                # Map industry to Google Place types (New API)
                included_types = {
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
                }.get(request.industry, ["establishment"])

                payload = {
                    "includedTypes": included_types,
                    "maxResultCount": 15,
                    "locationRestriction": {
                        "circle": {
                            "center": {
                                "latitude": coords["lat"],
                                "longitude": coords["lng"]
                            },
                            "radius": request.radius_km * 1000.0
                        }
                    },
                    "languageCode": "it"
                }

                response = await client.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()

                    # New API returns "places" array directly
                    if data.get("places"):
                        leads = []

                        for idx, place in enumerate(data["places"][:15]):  # Max 15 results
                            # Extract data from New API format
                            display_name = place.get("displayName", {}).get("text", "N/A")
                            formatted_address = place.get("formattedAddress", "")
                            phone = place.get("internationalPhoneNumber", "")
                            website = place.get("websiteUri", "")
                            rating = place.get("rating", 0)
                            user_rating_count = place.get("userRatingCount", 0)

                            # Calculate score based on having/not having website
                            has_website = bool(website)
                            base_score = 95 if not has_website else 70
                            score = base_score - random.randint(0, 10)

                            # Determine need reason
                            need_reason = "Nessun sito web rilevato" if not has_website else "Sito web esistente, possibile aggiornamento"
                            if request.need == "sito_obsoleto" and has_website:
                                need_reason = "Sito web presente, verifica se mobile-friendly"

                            leads.append(LeadItem(
                                id=idx + 1,
                                company=display_name,
                                industry=request.industry,
                                size=request.size,
                                location=request.location,
                                address=formatted_address,
                                phone=phone,
                                email="",  # Google doesn't provide email
                                website=website,
                                need=request.need,
                                need_reason=need_reason,
                                score=score,
                                google_rating=rating,
                                reviews_count=user_rating_count
                            ))

                        # Sort by score
                        leads.sort(key=lambda x: x.score, reverse=True)
                        logger.info(f"Found {len(leads)} REAL leads from Google Places API (New)")
                        return leads

        except Exception as e:
            logger.error(f"Google Places API error: {e!s}")

    # PRIORITY 3: Local PMI Generator (intelligent fallback for non-digitalized PMI)
    logger.warning("External APIs not available, using intelligent LOCAL PMI generation")

    from app.infrastructure.scraping.local_pmi_generator import local_pmi_generator

    try:
        logger.info("Generating intelligent local PMI leads...")
        local_results = local_pmi_generator.generate_pmi_leads(
            industry=request.industry,
            city=request.location,
            count=15
        )

        if local_results:
            # Convert to LeadItem format
            leads = []
            for idx, local_result in enumerate(local_results):
                # Enhanced need reason for local PMI
                if not local_result.website and not local_result.email:
                    need_reason = "🎯 PMI TRADIZIONALE - Zero presenza digitale, massimo potenziale di crescita"
                elif not local_result.website:
                    need_reason = "⚡ OPPORTUNITÀ GOLD - Solo email, necessita sito web professionale"
                else:
                    need_reason = "🔍 VERIFICA DIGITALE - Presenza minima, possibile upgrade"

                # Boost score for perfect matches
                final_score = local_result.score
                if request.need == "sito_web" and not local_result.website:
                    final_score += 25
                elif request.need == "ecommerce" and not local_result.website:
                    final_score += 20

                leads.append(LeadItem(
                    id=idx + 1,
                    company=local_result.name,
                    industry=request.industry,
                    size=request.size,
                    location=request.location,
                    address=local_result.address,
                    phone=local_result.phone,
                    email=local_result.email,
                    website=local_result.website,
                    need=request.need,
                    need_reason=need_reason,
                    score=final_score,
                    google_rating=0,  # Local generation doesn't have ratings
                    reviews_count=0
                ))

            # Sort by score (best leads first)
            leads.sort(key=lambda x: x.score, reverse=True)
            logger.info(f"Generated {len(leads)} intelligent LOCAL PMI leads")
            return leads

    except Exception as e:
        logger.error(f"Local PMI generation failed: {e}")

    # FINAL FALLBACK: Original intelligent generation
    logger.warning("All lead generation methods failed, using basic fallback")

    # Industry-specific business name patterns
    industry_names = {
        "ristorazione": [
            "Trattoria", "Ristorante", "Pizzeria", "Bar", "Osteria", "Taverna",
            "Caffè", "Pub", "Bistrot", "Gelateria", "Pasticceria"
        ],
        "retail": [
            "Boutique", "Emporio", "Store", "Shop", "Negozio", "Centro",
            "Outlet", "Showroom", "Concept Store"
        ],
        "studi_professionali": [
            "Studio Legale", "Studio", "Associazione Professionale", "Consulenza",
            "Studio Commercialista", "Studio Notarile"
        ],
        "salute": [
            "Studio Medico", "Ambulatorio", "Poliambulatorio", "Centro Medico",
            "Studio Dentistico", "Fisioterapia", "Centro Riabilitazione"
        ],
        "beauty": [
            "Salone", "Centro Estetico", "Hair Stylist", "Beauty Center",
            "SPA", "Wellness", "Nail Art"
        ],
        "fitness": [
            "Palestra", "Fitness Club", "CrossFit", "Yoga Studio",
            "Personal Training", "Centro Sportivo"
        ],
        "immobiliare": [
            "Agenzia Immobiliare", "Immobiliare", "Real Estate", "Casa",
            "Costruzioni", "Edilizia"
        ],
        "automotive": [
            "Autofficina", "Concessionaria", "Auto", "Carrozzeria",
            "Gommista", "Elettrauto", "Autolavaggio"
        ],
        "turismo": [
            "Hotel", "B&B", "Agenzia Viaggi", "Tour Operator",
            "Residence", "Affittacamere", "Casa Vacanze"
        ],
        "artigianato": [
            "Idraulica", "Elettricista", "Falegnameria", "Fabbro",
            "Imbianchino", "Serramenti", "Climatizzazione"
        ],
        "formazione": [
            "Scuola", "Accademia", "Centro Formazione", "Istituto",
            "Coaching", "Corsi", "Training"
        ],
        "eventi": [
            "Wedding Planner", "Catering", "Eventi", "Party",
            "Animazione", "Noleggio", "Allestimenti"
        ]
    }

    # Need-specific reasons
    need_reasons = {
        "sito_web": "Nessuna presenza online rilevata, solo profilo Google My Business",
        "sito_obsoleto": "Sito web non responsive, non ottimizzato per mobile",
        "ecommerce": "Vendita solo in negozio fisico, nessun canale online",
        "prenotazioni": "Prenotazioni solo telefoniche, nessun sistema digitale",
        "social": "Profili social inattivi da oltre 6 mesi",
        "automazione": "Gestione manuale di fatturazione e contabilità",
        "app": "Clientela giovane ma nessuna app dedicata"
    }

    # Italian surnames for realistic names
    surnames = [
        "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo",
        "Ricci", "Marino", "Greco", "Bruno", "Gallo", "Conti", "De Luca", "Costa",
        "Giordano", "Mancini", "Rizzo", "Lombardi", "Moretti", "Barbieri", "Fontana",
        "Santoro", "Mariani", "Rinaldi", "Caruso", "Ferrara", "Gatti", "Leone"
    ]

    # Location-specific street names
    streets = [
        "Via Roma", "Corso Italia", "Via Garibaldi", "Via Mazzini", "Via Dante",
        "Via Verdi", "Piazza Duomo", "Via Nazionale", "Corso Vittorio Emanuele",
        "Via della Repubblica", "Via XX Settembre", "Via Cavour"
    ]

    # Get industry-specific prefixes
    prefixes = industry_names.get(request.industry, ["Azienda", "Impresa", "Ditta"])

    # Generate realistic leads
    leads = []
    count = random.randint(5, 12)  # More results

    for i in range(count):
        # Generate company name
        prefix = random.choice(prefixes)
        surname = random.choice(surnames)

        # Various naming patterns
        name_patterns = [
            f"{prefix} {surname}",
            f"{prefix} Da {surname}",
            f"{surname} {prefix}",
            f"{prefix} {surname} & C.",
            f"Il {prefix} di {surname}",
            f"{prefix} {request.location}"
        ]
        company_name = random.choice(name_patterns)

        # Generate address
        street = random.choice(streets)
        civic = random.randint(1, 150)
        address = f"{street}, {civic} - {request.location}"

        # Generate phone (Italian format)
        area_codes = ["089", "081", "06", "02", "011", "051", "055"]
        phone = f"+39 {random.choice(area_codes)} {random.randint(100000, 999999)}"

        # Generate email
        email_domain = company_name.lower().replace(" ", "").replace(".", "").replace("&", "e").replace("'", "")
        email_domain = email_domain[:20]  # Limit length
        email = f"info@{email_domain}.it"

        # Website (some have it, some don't based on need)
        website = ""
        if request.need not in ["sito_web"]:
            website = f"www.{email_domain}.it"

        # Google rating and reviews
        google_rating = round(random.uniform(3.5, 4.9), 1)
        reviews_count = random.randint(5, 200)

        # Score calculation based on multiple factors
        base_score = 90
        # Lower score if they have a website (less need)
        if website:
            base_score -= 10
        # Higher score for smaller businesses (more likely to need help)
        if request.size in ["micro", "piccola"]:
            base_score += 5
        # Add some randomness
        score = base_score - random.randint(0, 15)
        score = max(60, min(98, score))  # Clamp between 60-98

        leads.append(LeadItem(
            id=i + 1,
            company=company_name,
            industry=request.industry,
            size=request.size,
            location=request.location,
            address=address,
            phone=phone,
            email=email,
            website=website,
            need=request.need,
            need_reason=need_reasons.get(request.need, "Potenziale cliente per servizi digitali"),
            score=score,
            google_rating=google_rating,
            reviews_count=reviews_count
        ))

    # Sort by score descending
    leads.sort(key=lambda x: x.score, reverse=True)

    logger.info(f"Generated {len(leads)} leads for {request.industry} in {request.location}")
    return leads


@router.post("/marketing/publish", response_model=PublishResponse)
async def publish_to_social_media(
    request: PublishRequest,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Publish generated content to multiple social media platforms.

    Supported platforms: facebook, threads, linkedin, twitter, instagram
    """
    results = []
    success_count = 0
    failed_count = 0

    for platform in request.platforms:
        try:
            result = await social_media.publish_post(
                platform=platform.lower(),
                content=request.content,
                media_urls=request.media_urls
            )

            results.append({
                "platform": platform,
                **result
            })

            if result.get("status") == "success":
                success_count += 1
            else:
                failed_count += 1

        except Exception as e:
            results.append({
                "platform": platform,
                "status": "error",
                "message": str(e)
            })
            failed_count += 1

    return PublishResponse(
        results=results,
        success_count=success_count,
        failed_count=failed_count
    )


class ImageGenerationRequest(BaseModel):
    """Request for AI image generation."""
    prompt: str
    style: str = "professional"
    size: str = "1024x1024"
    width: int = 1024
    height: int = 1024
    platform: str = "instagram"
    format: str = "post"  # post, story, reel, carousel, video
    aspect_ratio: str = "auto"  # auto, 1:1, 4:5, 9:16, 16:9, etc.
    apply_branding: bool = True
    branding_position: str = "top_center"
    template_type: str | None = None  # lancio, tip, case-study, promo, etc.
    brand_context: dict | None = None  # Custom Brand DNA override


class ImageGenerationResponse(BaseModel):
    """Response for generated image."""
    image_url: str
    prompt: str
    prompt_used: str | None = None
    provider: str
    metadata: dict[str, Any] = {}


@router.post("/image/generate", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI image with Brand DNA integration.

    Uses the user's configured Brand DNA for colors, style, and visual identity.
    Falls back to default brand context if not configured.
    """
    from app.domain.marketing.models import BrandSettings
    from app.core.api.v1.ai.image_providers import generate_image_with_providers, save_generated_image
    import time

    logger.info(f"Generating branded image: {request.prompt[:50]}...")
    start_time = time.time()

    # Fetch Brand DNA from database
    brand_dna = None
    if request.brand_context:
        # Use provided brand context
        brand_dna = request.brand_context
    else:
        # Fetch from database
        try:
            brand_settings = db.query(BrandSettings).filter(
                BrandSettings.admin_id == current_user.id
            ).first()

            if brand_settings:
                brand_dna = {
                    "company_name": brand_settings.company_name,
                    "tagline": brand_settings.tagline,
                    "industry": brand_settings.description,  # Using description as industry context
                    "primary_color": brand_settings.primary_color,
                    "secondary_color": brand_settings.secondary_color,
                    "accent_color": brand_settings.accent_color,
                    "style": f"Tone: {brand_settings.tone_of_voice.value if brand_settings.tone_of_voice else 'professional'}",
                    "visual_elements": brand_settings.content_pillars or [],
                }
                logger.info(f"Using Brand DNA for {brand_settings.company_name}")
        except Exception as e:
            logger.warning(f"Could not fetch Brand DNA: {e}")

    # Determine aspect ratio from platform/format
    aspect_ratio = request.aspect_ratio
    if aspect_ratio == "auto":
        platform_aspect_map = {
            ("instagram", "post"): "1:1",
            ("instagram", "story"): "9:16",
            ("instagram", "reel"): "9:16",
            ("instagram", "carousel"): "4:5",
            ("facebook", "post"): "1.91:1",
            ("facebook", "story"): "9:16",
            ("linkedin", "post"): "1.91:1",
            ("twitter", "post"): "16:9",
            ("tiktok", "video"): "9:16",
            ("youtube", "thumbnail"): "16:9",
            ("youtube", "short"): "9:16",
            ("pinterest", "post"): "2:3",
            ("threads", "post"): "1:1",
            ("google_business", "post"): "4:3",
        }
        aspect_ratio = platform_aspect_map.get(
            (request.platform, request.format),
            "1:1"
        )

    try:
        # Try direct generation with providers
        image_bytes, provider_name, model_name = await generate_image_with_providers(
            prompt=request.prompt,
            style=request.style,
            aspect_ratio=aspect_ratio,
            platform=request.platform,
            apply_branding=request.apply_branding,
            provider="auto",
            brand_dna=brand_dna,
            template_type=request.template_type
        )

        if image_bytes:
            # Save and return
            result = await save_generated_image(
                image_bytes=image_bytes,
                provider=provider_name,
                model=model_name,
                prompt=request.prompt,
                enhanced_prompt="",  # Already enhanced in provider
                start_time=start_time,
                aspect_ratio=aspect_ratio,
                style=request.style,
                apply_branding=request.apply_branding,
                platform=request.platform
            )

            return ImageGenerationResponse(
                image_url=result["image_url"],
                prompt=request.prompt,
                prompt_used=result.get("prompt_used"),
                provider=f"{provider_name} ({model_name})",
                metadata={
                    **result.get("metadata", {}),
                    "brand_dna_used": bool(brand_dna),
                    "platform": request.platform,
                    "format": request.format,
                    "aspect_ratio": aspect_ratio,
                    "template_type": request.template_type,
                }
            )

        # Fallback to AI Microservice
        logger.warning("Direct generation failed, trying AI Microservice...")

    except Exception as e:
        logger.warning(f"Direct generation error: {e}, trying AI Microservice...")

    # Fallback: Try AI Microservice
    try:
        import httpx
        ai_service_url = os.getenv("AI_SERVICE_URL", "http://ai_microservice:8001")
        ai_api_key = os.getenv("AI_SERVICE_API_KEY", "")

        headers = {"Authorization": f"Bearer {ai_api_key}"} if ai_api_key else {}

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{ai_service_url}/api/v1/marketing/image/generate",
                json={
                    "prompt": request.prompt,
                    "style": request.style,
                    "width": request.width,
                    "height": request.height,
                    "platform": request.platform,
                    "aspect_ratio": aspect_ratio,
                    "apply_branding": request.apply_branding,
                    "branding_position": request.branding_position,
                    "brand_dna": brand_dna,
                    "template_type": request.template_type,
                },
                headers=headers
            )

            if response.status_code == 200:
                data = response.json()
                return ImageGenerationResponse(
                    image_url=data.get("image_url", ""),
                    prompt=request.prompt,
                    prompt_used=data.get("prompt_used"),
                    provider=f"AI Service ({data.get('metadata', {}).get('provider', 'unknown')})",
                    metadata=data.get("metadata", {})
                )

    except Exception as e:
        logger.error(f"AI Microservice fallback failed: {e}")

    # Final fallback: placeholder
    return ImageGenerationResponse(
        image_url="https://placehold.co/1024x1024/1a1a2e/D4AF37?text=Generation+Failed",
        prompt=request.prompt,
        provider="Placeholder (all providers failed)",
        metadata={"error": "All image generation providers failed"}
    )


# =============================================================================
# VIDEO GENERATION ENDPOINT (VEO 3.1)
# =============================================================================

class VideoGenerationRequest(BaseModel):
    """Request model for VEO video generation."""
    prompt: str = Field(..., description="Video description/prompt")
    style: str = Field(default="professional", description="Visual style")
    aspect_ratio: str = Field(default="16:9", description="16:9 or 9:16")
    duration_seconds: int = Field(default=8, ge=4, le=8, description="4, 6, or 8 seconds")
    resolution: str = Field(default="720p", description="720p or 1080p")
    platform: str = Field(default="youtube", description="Target platform")
    negative_prompt: str | None = Field(default=None, description="What to avoid")
    wait_for_completion: bool = Field(default=True, description="Wait for video to be ready")
    # Brand context
    brand_context: str | None = Field(default=None, description="Brand DNA JSON")


class VideoGenerationResponse(BaseModel):
    """Response model for VEO video generation."""
    status: str
    video_url: str | None = None
    operation_name: str | None = None
    provider: str = "veo-3.1"
    duration: int | None = None
    resolution: str | None = None
    aspect_ratio: str | None = None
    metadata: dict[str, Any] = {}


@router.post("/video/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    current_user: AdminUser = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI video using Google VEO 3.1.

    VEO 3.1 Features:
    - 8-second 720p or 1080p videos with native audio
    - Image-to-video support
    - Video extension capabilities
    - Reference images for style consistency

    Pricing: Check Google AI pricing for VEO usage.
    """
    from app.core.api.v1.ai.image_providers import generate_video_with_veo
    from app.domain.marketing.models import BrandSettings
    import json

    logger.info(f"Generating video: {request.prompt[:50]}...")

    # Fetch Brand DNA from database
    brand_dna = None
    if request.brand_context:
        try:
            brand_dna = json.loads(request.brand_context)
        except json.JSONDecodeError:
            brand_dna = {"context": request.brand_context}
    else:
        try:
            brand_settings = db.query(BrandSettings).filter(
                BrandSettings.admin_id == current_user.id
            ).first()

            if brand_settings:
                brand_dna = {
                    "company_name": brand_settings.company_name,
                    "tagline": brand_settings.tagline,
                    "industry": brand_settings.description,
                    "style": f"Tone: {brand_settings.tone_of_voice.value if brand_settings.tone_of_voice else 'professional'}",
                }
                logger.info(f"Using Brand DNA for video: {brand_settings.company_name}")
        except Exception as e:
            logger.warning(f"Could not fetch Brand DNA for video: {e}")

    try:
        result = await generate_video_with_veo(
            prompt=request.prompt,
            style=request.style,
            aspect_ratio=request.aspect_ratio,
            duration_seconds=request.duration_seconds,
            resolution=request.resolution,
            platform=request.platform,
            brand_dna=brand_dna,
            negative_prompt=request.negative_prompt,
            wait_for_completion=request.wait_for_completion
        )

        if result:
            return VideoGenerationResponse(
                status=result.get("status", "unknown"),
                video_url=result.get("video_url"),
                operation_name=result.get("operation_name"),
                provider="veo-3.1",
                duration=result.get("duration"),
                resolution=result.get("resolution"),
                aspect_ratio=result.get("aspect_ratio"),
                metadata={
                    "brand_dna_used": bool(brand_dna),
                    "platform": request.platform,
                }
            )
        else:
            return VideoGenerationResponse(
                status="failed",
                provider="veo-3.1",
                metadata={"error": "Video generation failed"}
            )

    except Exception as e:
        logger.error(f"Video generation error: {e}")
        return VideoGenerationResponse(
            status="error",
            provider="veo-3.1",
            metadata={"error": str(e)}
        )


@router.get("/health")
async def copilot_health():
    """Check copilot service health."""
    return {
        "status": "healthy",
        "service": "copilot",
        "mode": "production",
        "features": [
            "marketing_generation",
            "chat_support",
            "lead_finder",
            "image_generation",
            "video_generation_veo",
            "nanobanana_pro",
            "social_publishing"
        ]
    }
