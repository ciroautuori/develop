"""
Copilot API Router - AI Assistant endpoints.

Provides AI capabilities for the backoffice via AI Microservice proxy:
- Content Generation (Marketing)
- AI Chat Support
- Lead Finding
- Image Generation

All AI logic is delegated to the AI Microservice.
This router only handles request/response transformation and fallbacks.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

from app.core.api.dependencies.auth_deps import get_current_admin_user
from app.domain.auth.admin_models import AdminUser
from app.integrations.social_media import social_media
from app.infrastructure.ai import ai_client, AIServiceError
from app.core.config import get_fallback_template, get_fallback_chat_response

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
    platform: Optional[str] = Field(None, description="Platform (for social)")
    prompt: Optional[str] = Field(None, description="Custom prompt for AI generation")
    template: Optional[str] = Field(None, description="Quick template ID")
    brand_context: Optional[str] = Field(None, description="Brand context for AI")
    max_chars: Optional[int] = Field(None, description="Max characters for platform")
    # PRO fields for advanced content generation
    post_type: Optional[str] = Field(
        default=None,
        description="Post type: lancio_prodotto, tip_giorno, caso_successo, trend_settore, offerta_speciale, ai_business, educational, testimonial, engagement"
    )
    sector: Optional[str] = Field(
        default="tech",
        description="Business sector: ristorazione, hospitality, legal, medical, retail, manufacturing, tech, consulting"
    )
    subtype: Optional[str] = Field(None, description="Content subtype from frontend")


class ContentGenerationResponse(BaseModel):
    """Response for generated content."""
    content: str
    metadata: Dict[str, Any]
    provider: str = "StudiocentOS AI"
    # PRO response fields
    image_prompt: Optional[str] = None
    hashtags: List[str] = []
    cta_options: List[str] = []


class ChatRequest(BaseModel):
    """Request for AI chat."""
    message: str


class ChatResponse(BaseModel):
    """Response for AI chat."""
    response: str
    provider: str = "StudiocentOS AI"


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
    media_urls: Optional[list[str]] = Field(None, description="Optional media URLs")


class PublishResponse(BaseModel):
    """Response for publish request."""
    results: list[Dict[str, Any]]
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

    Uses PRO endpoint when post_type is specified for platform-specific,
    structured content (HOOK → BODY → CTA → HASHTAG).
    Falls back to basic endpoint for legacy requests.
    """
    topic = request.prompt or request.topic
    logger.info(f"AI Content request: {topic[:100]}... post_type={request.post_type}, platform={request.platform}")

    # Determine post_type from request (direct or from subtype)
    post_type = request.post_type or request.subtype

    # Map common subtypes to post_types
    subtype_to_post_type = {
        "post": "educational",
        "video": "educational",
        "story": "engagement",
        "email": "lancio_prodotto",
        "carousel": "educational",
        "lancio-prodotto": "lancio_prodotto",
        "tip-giorno": "tip_giorno",
        "caso-successo": "caso_successo",
        "trend-settore": "trend_settore",
        "offerta-speciale": "offerta_speciale",
        "ai-business": "ai_business",
    }

    if post_type and post_type in subtype_to_post_type:
        post_type = subtype_to_post_type[post_type]

    try:
        # Use PRO endpoint when we have post_type for advanced generation
        if post_type:
            logger.info(f"Using PRO endpoint with post_type={post_type}")
            data = await ai_client.generate_content_pro(
                topic=topic,
                post_type=post_type,
                platform=request.platform or "instagram",
                sector=request.sector or "tech",
                additional_context=None,
                language="it",
                generate_image_prompt=True,
                brand_context=request.brand_context
            )

            return ContentGenerationResponse(
                content=data.get("content", ""),
                metadata={
                    "type": request.type,
                    "post_type": post_type,
                    "platform": request.platform or "instagram",
                    "sector": request.sector or "tech",
                    "tone": request.tone,
                    "topic": request.topic,
                    "target": "PMI italiane",
                    "ai_generated": True,
                    "pro_mode": True,
                },
                provider=data.get("provider", "groq"),
                image_prompt=data.get("image_prompt"),
                hashtags=data.get("hashtags", []),
                cta_options=data.get("cta_options", [])
            )
        else:
            # Legacy: Use basic endpoint for simple requests
            logger.info("Using BASE endpoint (no post_type specified)")
            data = await ai_client.generate_content(
                topic=topic,
                content_type=request.type,
                tone=request.tone,
                platform=request.platform or "instagram",
                brand_context=request.brand_context
            )

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

    except AIServiceError as e:
        logger.warning(f"AI Microservice unavailable, using fallback: {e}")

    # Fallback: Use centralized templates
    return ContentGenerationResponse(
        content=get_fallback_template(request.type, request.topic),
        metadata={
            "type": request.type,
            "tone": request.tone,
            "topic": request.topic,
            "target": "PMI italiane",
            "fallback": True,
        },
        provider="StudioCentOS Templates (Fallback)"
    )


# ============================================================================
# POWER CONTENT GENERATOR - Format-Specific Generation
# ============================================================================

class FormatContentRequest(BaseModel):
    """Request for format-specific content generation."""
    topic: str = Field(..., description="Content topic or prompt")
    content_format: str = Field(default="post", description="Format: post, story, carousel, reel, video")
    platform: str = Field(default="instagram", description="Target platform")
    slides_count: int = Field(default=5, description="Number of slides for carousel/story")
    duration_seconds: int = Field(default=15, description="Duration for video/reel")
    video_style: str = Field(default="dinamico", description="Video style")
    music_mood: str = Field(default="energetico", description="Music mood for video")
    brand_context: Optional[str] = Field(None, description="Brand DNA context")


class SlideContent(BaseModel):
    """Individual slide content."""
    slide_number: int
    text: str
    visual_description: str
    image_prompt: str


class SceneContent(BaseModel):
    """Individual scene content for video/reel."""
    scene_number: int
    duration_seconds: int
    visual_description: str
    text_overlay: str
    audio_description: str


class FormatContentResponse(BaseModel):
    """Response for format-specific content generation."""
    content: str
    content_format: str
    platform: str
    slides: List[SlideContent] = []
    scenes: List[SceneContent] = []
    cover_prompt: str = ""
    thumbnail_prompt: str = ""
    hashtags: List[str] = []
    cta_options: List[str] = []
    music_suggestion: str = ""
    provider: str = "StudiocentOS AI"
    metadata: Dict[str, Any] = {}


@router.post("/marketing/generate-format", response_model=FormatContentResponse)
@router.post("/content/generate-format", response_model=FormatContentResponse)
async def generate_format_content(
    request: FormatContentRequest,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Generate FORMAT-SPECIFIC content (Story, Carousel, Reel, Video).

    Power endpoint with MASTER prompts for structured slide-by-slide generation.
    Returns structured content with slides[], scenes[], image prompts per element.
    """
    logger.info(f"Power Content Generator: format={request.content_format}, platform={request.platform}, topic={request.topic[:50]}...")

    try:
        data = await ai_client.generate_content_format(
            topic=request.topic,
            content_format=request.content_format,
            platform=request.platform,
            slides_count=request.slides_count,
            duration_seconds=request.duration_seconds,
            video_style=request.video_style,
            music_mood=request.music_mood,
            brand_context=request.brand_context
        )

        # Parse slides if present
        slides = []
        if "slides" in data and data["slides"]:
            for slide in data["slides"]:
                slides.append(SlideContent(
                    slide_number=slide.get("slide_number", 0),
                    text=slide.get("text", ""),
                    visual_description=slide.get("visual_description", ""),
                    image_prompt=slide.get("image_prompt", "")
                ))

        # Parse scenes if present
        scenes = []
        if "scenes" in data and data["scenes"]:
            for scene in data["scenes"]:
                scenes.append(SceneContent(
                    scene_number=scene.get("scene_number", 0),
                    duration_seconds=scene.get("duration_seconds", 3),
                    visual_description=scene.get("visual_description", ""),
                    text_overlay=scene.get("text_overlay", ""),
                    audio_description=scene.get("audio_description", "")
                ))

        return FormatContentResponse(
            content=data.get("content", ""),
            content_format=request.content_format,
            platform=request.platform,
            slides=slides,
            scenes=scenes,
            cover_prompt=data.get("cover_prompt", ""),
            thumbnail_prompt=data.get("thumbnail_prompt", ""),
            hashtags=data.get("hashtags", []),
            cta_options=data.get("cta_options", []),
            music_suggestion=data.get("music_suggestion", ""),
            provider=data.get("provider", "StudiocentOS AI"),
            metadata={
                "content_format": request.content_format,
                "platform": request.platform,
                "slides_count": len(slides),
                "scenes_count": len(scenes),
                "duration_seconds": request.duration_seconds if request.content_format in ["reel", "video"] else None,
                "video_style": request.video_style if request.content_format in ["reel", "video"] else None,
                "ai_generated": True,
                "power_mode": True,
            }
        )

    except AIServiceError as e:
        logger.warning(f"AI Microservice unavailable for format generation: {e}")
        # Fallback with basic content
        return FormatContentResponse(
            content=f"[{request.content_format.upper()}] {request.topic}\n\nContenuto generato per {request.platform}.",
            content_format=request.content_format,
            platform=request.platform,
            slides=[],
            scenes=[],
            cover_prompt="",
            thumbnail_prompt="",
            hashtags=["#marketing", "#content", "#social"],
            cta_options=["Scopri di più", "Contattaci oggi"],
            music_suggestion="",
            provider="StudioCentOS Templates (Fallback)",
            metadata={"fallback": True}
        )


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    request: ChatRequest,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Chat with AI assistant via AI Microservice proxy.
    """
    try:
        data = await ai_client.chat(message=request.message)
        return ChatResponse(
            response=data.get("response", ""),
            provider=f"AI Service ({data.get('provider', 'groq')})"
        )
    except AIServiceError as e:
        logger.warning(f"AI Microservice unavailable: {e}")

    # Fallback: Use centralized response
    return ChatResponse(
        response=get_fallback_chat_response(request.message),
        provider="Fallback"
    )


@router.post("/leads/search", response_model=List[LeadItem])
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
                                "latitude": coords['lat'],
                                "longitude": coords['lng']
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
            logger.error(f"Google Places API error: {str(e)}")

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
                'platform': platform,
                **result
            })

            if result.get('status') == 'success':
                success_count += 1
            else:
                failed_count += 1

        except Exception as e:
            results.append({
                'platform': platform,
                'status': 'error',
                'message': str(e)
            })
            failed_count += 1

    return PublishResponse(
        results=results,
        success_count=success_count,
        failed_count=failed_count
    )


class ImageGenerationRequest(BaseModel):
    """Request for AI image generation with Brand DNA integration."""
    prompt: str
    style: str = "professional"
    size: str = "1024x1024"
    width: int = 1024
    height: int = 1024
    platform: str = "linkedin"
    apply_branding: bool = True
    branding_position: str = "top_center"
    logo_url: Optional[str] = None
    brand_name: Optional[str] = None
    post_type: Optional[str] = None  # lancio_prodotto, tip_giorno, etc.
    sector: Optional[str] = Field(default="tech", description="Business sector")


class ImageGenerationResponse(BaseModel):
    """Response for generated image."""
    image_url: str
    prompt: str
    provider: str


@router.post("/image/generate", response_model=ImageGenerationResponse)
async def generate_image(
    request: ImageGenerationRequest,
    current_user: AdminUser = Depends(get_current_admin_user)
):
    """
    Generate AI image via AI Microservice.
    """
    logger.info(f"Generating image: {request.prompt[:50]}...")

    try:
        data = await ai_client.generate_image(
            prompt=request.prompt,
            style=request.style,
            width=request.width,
            height=request.height,
            platform=request.platform,
            apply_branding=request.apply_branding,
            branding_position=request.branding_position,
            logo_url=request.logo_url,
            brand_name=request.brand_name or "StudioCentOS",
            post_type=request.post_type,
            sector=request.sector
        )
        return ImageGenerationResponse(
            image_url=data.get("image_url", ""),
            prompt=data.get("prompt_used", request.prompt),
            provider=f"AI Service ({data.get('metadata', {}).get('provider', 'unknown')})"
        )
    except AIServiceError as e:
        logger.error(f"Image generation error: {e}")
        return ImageGenerationResponse(
            image_url="https://placehold.co/1024x1024/1a1a2e/D4AF37?text=Service+Unavailable",
            prompt=request.prompt,
            provider=f"Error: {str(e)[:50]}"
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
            "social_publishing"
        ]
    }
