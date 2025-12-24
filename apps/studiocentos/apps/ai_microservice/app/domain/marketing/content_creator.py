"""
Content Creator Agent - AI-Powered Content Generation.

PRODUCTION-READY with:
- NanoBananaPRO (Imagen 4 Ultra) for image generation
- Veo 3.1 for video generation
- Specific templates for: Posts, Stories, Video, Carousel, Reels
- Brand DNA integration
- SEO optimization

This agent specializes in creating high-quality marketing content across
multiple formats: blog posts, social media, ads, video scripts, and newsletters.

Features:
    - Multi-format content generation
    - Brand voice consistency
    - SEO optimization
    - A/B testing variants
    - Content calendar integration
    - Compliance checking
    - Image generation via NanoBananaPRO
    - Video generation via Veo 3.1

Tools:
    1. generate_blog_post() - Long-form blog content
    2. generate_social_post() - Platform-specific social posts
    3. generate_ad_copy() - Advertising copy with CTAs
    4. generate_video_script() - Video content scripts
    5. generate_story_content() - Instagram/Facebook Stories
    6. generate_carousel() - Multi-slide carousel posts
    7. generate_reel_content() - Short-form video content
    8. optimize_for_seo() - SEO optimization
    9. check_brand_compliance() - Brand guidelines validation

Example:
    >>> agent = ContentCreatorAgent(config=config)
    >>>
    >>> # Generate complete social post with image
    >>> result = await agent.generate_social_post(
    ...     SocialPostConfig(
    ...         platform=SocialPlatform.INSTAGRAM,
    ...         message="Launching new AI features!",
    ...         post_type="lancio_prodotto",
    ...         generate_image=True,
    ...     )
    ... )
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

from app.infrastructure.agents.base_agent import BaseAgent, AgentConfig, AgentCapability
from app.infrastructure.agents.task import Task, TaskInput, TaskOutput

# Content Enhancement Module - Few-shot, Validation, RAG, Topic Rotation
from app.domain.marketing.content_enhancer import (
    content_enhancer,
    get_content_enhancer,
    ContentEnhancer,
    BrandVoiceValidator,
    EXAMPLE_POSTS,
    HOOK_VARIATIONS,
    STYLE_VARIATIONS,
    NEGATIVE_PROMPTS,
    POSITIVE_STYLE_ADDITIONS,
)

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS
# ============================================================================


class ContentType(str, Enum):
    """Content type enumeration."""

    BLOG_POST = "blog_post"
    SOCIAL_POST = "social_post"
    AD_COPY = "ad_copy"
    VIDEO_SCRIPT = "video_script"
    NEWSLETTER = "newsletter"
    LANDING_PAGE = "landing_page"


class ContentTone(str, Enum):
    """Content tone/voice enumeration."""

    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    HUMOROUS = "humorous"
    INSPIRATIONAL = "inspirational"
    URGENT = "urgent"


class SocialPlatform(str, Enum):
    """Social media platforms."""

    TWITTER = "twitter"
    FACEBOOK = "facebook"
    LINKEDIN = "linkedin"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"


# ============================================================================
# BRAND DNA - STUDIOCENTOS COMPLETE BRAND IDENTITY
# ============================================================================

BRAND_DNA = {
    "identity": {
        "name": "StudioCentOS",
        "tagline": "Tecnologia enterprise per la tua PMI, senza la complessità enterprise",
        "industry": "Software Development & AI Solutions",
        "location": "Salerno, Campania, Italia",
    },
    "colors": {
        "primary": "#D4AF37",      # Oro - Eccellenza
        "secondary": "#0A0A0A",    # Nero - Professionalità
        "accent": "#FAFAFA",       # Bianco - Pulizia
    },
    "voice": {
        "primary": "Professionale ma accessibile",
        "style": "Diretto e concreto",
        "emotion": "Positivo ma realistico",
        "approach": "Empatico con le sfide delle PMI italiane",
    },
    "values": [
        "Innovazione Accessibile",
        "Affidabilità",
        "Trasparenza",
        "Risultati Misurabili",
        "Italianità",
    ],
    "target": {
        "primary": "PMI Campania (1-50 dipendenti)",
        "sectors": ["Ristorazione", "Studi professionali", "Commercio", "Manifatturiero"],
    },
    "messaging": {
        "mission": "Rendere accessibili le tecnologie più avanzate (AI, automazione, cloud) alle piccole e medie imprese italiane",
        "value_proposition": "Soluzioni AI pronte all'uso, supporto in italiano, risultati misurabili in 30 giorni",
    },
    "hashtags": {
        "brand": ["#StudioCentOS", "#AIperPMI", "#DigitalizzazionePMI"],
        "industry": ["#SviluppoSoftware", "#Automazione", "#CloudItalia"],
        "local": ["#TechSalerno", "#InnovazioneItalia", "#PMIdigitale"],
    },
    "avoid_words": ["Disruptive", "Cutting-edge", "Best-in-class", "Sinergia"],
    "content_pillars": ["Tech Tips", "Case Studies", "AI Explained", "Local Business"],
}


def get_brand_dna_prompt() -> str:
    """Generate the complete Brand DNA system prompt."""
    return f"""
BRAND DNA - STUDIOCENTOS

IDENTITÀ:
- Nome: {BRAND_DNA["identity"]["name"]}
- Settore: {BRAND_DNA["identity"]["industry"]}
- Location: {BRAND_DNA["identity"]["location"]}
- Tagline: {BRAND_DNA["identity"]["tagline"]}

MISSION: {BRAND_DNA["messaging"]["mission"]}

VALUE PROPOSITION: {BRAND_DNA["messaging"]["value_proposition"]}

TONE OF VOICE:
- Stile: {BRAND_DNA["voice"]["primary"]}
- Approccio: {BRAND_DNA["voice"]["approach"]}
- Emozione: {BRAND_DNA["voice"]["emotion"]}

DA FARE:
• Usare esempi concreti e numeri reali
• Parlare dei benefici, non solo delle feature
• Rispondere alle obiezioni proattivamente
• Usare il "tu" per creare vicinanza
• Citare casi di successo locali
• Spiegare i tecnicismi quando necessario
• Essere trasparenti su tempi e costi

DA EVITARE:
• Usare gergo tecnico non necessario
• Fare promesse vaghe o esagerate
• Usare anglicismi quando esiste l'equivalente italiano
• Essere paternalistici o presuntuosi
• Parole vietate: {", ".join(BRAND_DNA["avoid_words"])}

TARGET:
- Primario: {BRAND_DNA["target"]["primary"]}
- Settori: {", ".join(BRAND_DNA["target"]["sectors"])}

VALORI:
{chr(10).join([f"• {v}" for v in BRAND_DNA["values"]])}

HASHTAG BRAND: {" ".join(BRAND_DNA["hashtags"]["brand"])}
""".strip()


# ============================================================================
# POST TYPE PROMPTS - Struttura HOOK → BODY → CTA → HASHTAG
# ============================================================================

POST_TYPE_PROMPTS = {
    "lancio_prodotto": """
TIPO: LANCIO PRODOTTO/SERVIZIO

STRUTTURA OBBLIGATORIA:
🔥 HOOK: Domanda provocatoria o statistica shock che evidenzia il problema risolto
📝 BODY:
  - Problema che risolve
  - Beneficio principale per la PMI
  - Differenziatore vs soluzioni esistenti
  - Risultato atteso (numero o percentuale)
✨ CTA: Invito all'azione chiaro (prenota demo, richiedi info)
🏷️ HASHTAG: Brand + prodotto + settore

TONO: Entusiasta ma professionale, focus sui benefici non sulle feature
""",

    "tip_giorno": """
TIPO: TIP DEL GIORNO

STRUTTURA OBBLIGATORIA:
💡 HOOK: "Sapevi che [problema comune]? Ecco come risolverlo:"
📝 BODY:
  1️⃣ Primo step semplice
  2️⃣ Secondo step
  3️⃣ Terzo step con risultato
💰 BONUS: Beneficio concreto (tempo risparmiato, costi ridotti)
💬 CTA: "Quale tip vorresti vedere la prossima volta? 👇"
🏷️ HASHTAG: Brand + #TechTips + #ConsigliPMI

TONO: Utile, pratico, senza fronzoli
""",

    "caso_successo": """
TIPO: CASO DI SUCCESSO / CASE STUDY

STRUTTURA OBBLIGATORIA:
🏆 HOOK: "[Cliente/Settore] ha ottenuto [risultato numerico] in [tempo]"
📊 SITUAZIONE PRIMA:
  - Problema principale
  - Impatto sul business
  - Tentativi falliti precedenti
🚀 SOLUZIONE:
  - Cosa abbiamo implementato
  - Come lo abbiamo fatto
📈 RISULTATI:
  - +X% metrica principale
  - €X risparmiati
  - Tempo recuperato
💬 TESTIMONIANZA: "Citazione diretta del cliente"
🎯 CTA: "Vuoi risultati simili? Parliamone →"

TONO: Narrativo, concreto, numeri reali
""",

    "trend_settore": """
TIPO: TREND DEL SETTORE / ANALISI

STRUTTURA OBBLIGATORIA:
📊 HOOK: "Il X% delle PMI italiane [statistica rilevante]. Ecco cosa sta cambiando:"
🔍 IL TREND:
  - Cosa sta accadendo nel settore
  - Perché ora è importante
  - Chi sta già adottando
💡 IMPATTO SULLE PMI:
  - Opportunità immediate
  - Rischi del non adottare
🛠️ COME PREPARARSI:
  1. Azione pratica 1
  2. Azione pratica 2
  3. Azione pratica 3
🎯 CTA: "La tua azienda è pronta? Confrontati con noi →"

TONO: Autorevole, informato, pratico
""",

    "offerta_speciale": """
TIPO: OFFERTA SPECIALE / PROMOZIONE

STRUTTURA OBBLIGATORIA:
🔥 HOOK: "[SCADENZA] Solo X giorni per [beneficio] a [condizione speciale]"
💰 L'OFFERTA:
  - Cosa include
  - Valore normale vs prezzo promo
  - Risparmio in € o %
✅ PERFETTO PER:
  - Target 1
  - Target 2
  - Target 3
⏰ URGENZA:
  - Scadenza precisa
  - Posti/quantità limitata
🎯 CTA: "Blocca il prezzo ORA → [link/azione]"

TONO: Urgente ma onesto, trasparente sul valore
""",

    "ai_business": """
TIPO: AI PER BUSINESS

STRUTTURA OBBLIGATORIA:
🤖 HOOK: "L'AI può [azione sorprendente] per la tua PMI. Ecco come:"
❌ MITO DA SFATARE: "Molti pensano che l'AI sia [pregiudizio]. In realtà..."
✅ LA REALTÀ:
  - Cosa può fare OGGI l'AI per le PMI
  - Costi reali (accessibili)
  - Tempistiche di implementazione
💡 ESEMPI PRATICI:
  1. Caso d'uso 1 - settore specifico
  2. Caso d'uso 2 - settore specifico
  3. Caso d'uso 3 - settore specifico
📊 RISULTATI TIPICI:
  - Metrica 1
  - Metrica 2
🎯 CTA: "Vuoi scoprire cosa può fare l'AI per te? →"

TONO: Semplice, onesto su limiti e potenzialità, focus su ROI
""",

    "educational": """
TIPO: EDUCATIONAL / FORMATIVO

STRUTTURA OBBLIGATORIA:
❓ HOOK: "[Domanda comune] Ecco la risposta completa:"
📖 SPIEGAZIONE:
  - Cos'è [concetto]
  - Perché è importante
  - A chi serve
📝 GUIDA PRATICA:
  1️⃣ Step 1
  2️⃣ Step 2
  3️⃣ Step 3
  4️⃣ Step 4
  5️⃣ Step 5
⚠️ ERRORI COMUNI:
  - Errore 1 da evitare
  - Errore 2 da evitare
💡 PRO TIP: Consiglio avanzato
🎯 CTA: "Salva questo post e condividilo con chi ne ha bisogno 📌"

TONO: Didattico, chiaro, strutturato
""",

    "testimonial": """
TIPO: TESTIMONIAL / RECENSIONE

STRUTTURA OBBLIGATORIA:
⭐ HOOK: "Citazione diretta più impattante del cliente"
👤 CHI È:
  - Nome/Ruolo/Azienda
  - Settore
  - Sfida affrontata
📈 RISULTATI:
  - Metrica principale
  - Beneficio tangibile
💬 CITAZIONE COMPLETA: "Testimonianza estesa"
🎯 CTA: "La prossima recensione potrebbe essere la tua →"

TONO: Gratitudine, professionale, numeri concreti
""",

    "engagement": """
TIPO: ENGAGEMENT / INTERAZIONE

STRUTTURA OBBLIGATORIA:
🎤 HOOK: "[Domanda provocatoria o sondaggio]"
💭 CONTESTO: 1-2 frasi che spiegano perché chiediamo
🗳️ OPZIONI (se sondaggio):
  A) Opzione 1
  B) Opzione 2
  C) Altra risposta nei commenti
🎯 CTA: "Commenta con la tua risposta! 👇"

TONO: Curioso, inclusivo, conversazionale
""",
}


# ============================================================================
# CONTENT FORMAT TEMPLATES - STORIES, CAROUSEL, REELS, VIDEO
# ============================================================================

CONTENT_FORMAT_TEMPLATES = {
    "story": {
        "instagram": {
            "duration": 15,  # seconds per slide
            "max_slides": 10,
            "structure": """
INSTAGRAM STORY - {num_slides} SLIDE

SLIDE 1 - HOOK (3 sec):
📱 Visual: Sfondo #{colors[primary]} con testo grande
📝 Testo: Domanda provocatoria o statistica shock
🎵 Audio: Trending sound o musica brand
🔗 Sticker: Sondaggio/Quiz/Countdown

SLIDE 2-{mid_slides} - CONTENUTO:
📱 Visual: Foto/Video del concetto
📝 Testo: Bullet point o step
🎵 Audio: Continua musica
🔗 Sticker: Progressione visuale

SLIDE FINALE - CTA:
📱 Visual: Logo StudioCentOS + CTA
📝 Testo: "Swipe up" / "Link in bio" / "DM per info"
🎵 Audio: Sound finale impattante
🔗 Sticker: Link/Contact/DM
""",
            "image_prompt_template": """
STORY VISUAL - SLIDE {slide_num}
Tema: {topic}
Stile: Moderno, mobile-first, vertical 9:16
Colori: Oro #D4AF37, Nero #0A0A0A, Bianco #FAFAFA
Testo overlay: {text_overlay}
Mood: Dinamico, engaging, scroll-stopping
Qualità: Alta risoluzione, ottimizzato per mobile
""",
        },
        "facebook": {
            "duration": 20,
            "max_slides": 6,
            "structure": """
FACEBOOK STORY - {num_slides} SLIDE

SLIDE 1 - HOOK:
📱 Visual: Immagine accattivante con testo bold
📝 Testo: Headline diretta

SLIDE 2-{mid_slides} - SVILUPPO:
📱 Visual: Contenuto visuale
📝 Testo: Punti chiave

SLIDE FINALE - CTA:
📱 Visual: Branding + azione
📝 Testo: Call-to-action chiara
""",
        },
    },

    "carousel": {
        "instagram": {
            "max_slides": 10,
            "format": "1:1 o 4:5",
            "structure": """
INSTAGRAM CAROUSEL - {num_slides} SLIDE

SLIDE 1 - COVER (HOOK):
📱 Visual: Titolo grande su sfondo premium
📝 Testo: "X Modi per..." / "La guida a..." / Problema → Soluzione
🎨 Stile: Brand colors, tipografia bold
🎯 Obiettivo: Fermare lo scroll

SLIDE 2 - CONTESTO:
📱 Visual: Introduzione al problema/tema
📝 Testo: Perché questo argomento è importante
🎨 Stile: Immagine + testo overlay

SLIDE 3-{content_slides} - CONTENUTO:
📱 Visual: Un concetto per slide
📝 Testo: Titolo + 2-3 bullet points
🎨 Stile: Consistente, numerazione se lista
📊 Dati: Includere numeri/statistiche quando possibile

SLIDE {num_slides-1} - RECAP:
📱 Visual: Riassunto visuale dei punti chiave
📝 Testo: Lista numerata dei takeaway

SLIDE {num_slides} - CTA:
📱 Visual: Logo + CTA prominente
📝 Testo: "Salva per dopo 📌" / "Condividi con chi ne ha bisogno"
🎯 Azione: Salva, Condividi, Commenta, Segui
""",
            "image_prompt_template": """
CAROUSEL SLIDE {slide_num}/{total_slides}
Tipo: {slide_type}
Contenuto: {content}
Formato: Quadrato 1080x1080 o 4:5 (1080x1350)
Stile: Premium, professionale, brand StudioCentOS
Colori: Oro #D4AF37 accenti, Nero #0A0A0A sfondo, Bianco #FAFAFA testo
Tipografia: Sans-serif moderna, bold per titoli
Elementi: {elements}
""",
        },
        "linkedin": {
            "max_slides": 10,
            "format": "1:1 o 4:5",
            "structure": """
LINKEDIN CAROUSEL - {num_slides} SLIDE

SLIDE 1 - COVER PROFESSIONALE:
📱 Visual: Titolo professionale, sottotitolo, autore
📝 Testo: Value proposition chiara

SLIDE 2-{content_slides} - CONTENUTO BUSINESS:
📱 Visual: Insight, dati, framework
📝 Testo: Tono autorevole, basato su dati

SLIDE FINALE - CTA PROFESSIONALE:
📱 Visual: Credenziali + Next step
📝 Testo: "Connetti" / "Commenta la tua esperienza"
""",
        },
    },

    "reel": {
        "instagram": {
            "durations": [15, 30, 60, 90],
            "format": "9:16 vertical",
            "structure": """
INSTAGRAM REEL - {duration} SECONDI

⏱️ 0-3 sec - HOOK VISIVO:
🎬 Visual: Pattern interrupt, movimento, zoom
📝 Caption: Domanda o statement shock
🎵 Audio: Trending sound (aggancia l'algoritmo)
✏️ Testo: Grande, leggibile, centro schermo

⏱️ 3-{hook_end} sec - PROBLEMA/AGITAZIONE:
🎬 Visual: Situazione riconoscibile
📝 Caption: "Ti è mai capitato di..."
🎵 Audio: Build-up musicale
✏️ Testo: Pain points

⏱️ {hook_end}-{solution_end} sec - SOLUZIONE:
🎬 Visual: Dimostrazione/Tutorial/Reveal
📝 Caption: Step by step o spiegazione
🎵 Audio: Peak momento
✏️ Testo: Bullet points animati

⏱️ {solution_end}-{duration} sec - CTA:
🎬 Visual: Logo, call-to-action
📝 Caption: "Segui per altri tips" / "Salva per dopo"
🎵 Audio: Chiusura musicale
✏️ Testo: CTA + handle @studiocentos
""",
            "video_prompt_template": """
REEL VIDEO SCRIPT
Durata: {duration} secondi
Formato: 9:16 verticale (1080x1920)
Tema: {topic}
Hook: {hook}
Stile: {style}
Musica: {music_mood}
Transizioni: Dinamiche, veloci
Testo on-screen: Sottotitoli sempre visibili
Brand: StudioCentOS - Oro #D4AF37, Nero #0A0A0A
CTA finale: {cta}
""",
        },
        "tiktok": {
            "durations": [15, 30, 60, 180, 600],
            "format": "9:16 vertical",
            "structure": """
TIKTOK VIDEO - {duration} SECONDI

⏱️ 0-1 sec - HOOK IMMEDIATO:
🎬 Visual: Primo frame = concetto chiave
📝 Caption: Statement controverse o curiosità
🎵 Audio: Trending sound TikTok
✏️ Testo: Headline che ferma lo scroll

⏱️ 1-{mid} sec - VALORE IMMEDIATO:
🎬 Visual: Contenuto rapidissimo
📝 Caption: Info-dense, no filler
🎵 Audio: Beat drop per enfasi
✏️ Testo: Keywords evidenziate

⏱️ {mid}-{duration} sec - LOOP/CTA:
🎬 Visual: Collegamento al primo frame (loop)
📝 Caption: "Parte 2?" / "Commenta per più"
🎵 Audio: Loop-friendly
✏️ Testo: Handle + CTA
""",
        },
    },

    "video_long": {
        "youtube": {
            "durations": [300, 600, 900, 1800],  # 5, 10, 15, 30 minuti
            "format": "16:9 horizontal",
            "structure": """
YOUTUBE VIDEO - {duration_min} MINUTI

⏱️ 0:00-0:30 - COLD OPEN (Hook):
🎬 Visual: Clip più impattante del video
📝 Script: "In questo video scoprirai..."
🎵 Audio: Teaser musicale

⏱️ 0:30-1:00 - INTRO:
🎬 Visual: Bumper StudioCentOS + host
📝 Script: Presentazione argomento
🎵 Audio: Jingle brand

⏱️ 1:00-{content_end} - CONTENUTO PRINCIPALE:
🎬 Visual: Tutorial/Spiegazione/Demo
📝 Script: Sezioni con timestamp
🎵 Audio: Background music leggera
📊 Elementi: B-roll, grafiche, screenshot

⏱️ {content_end}-{outro_start} - RECAP:
🎬 Visual: Slide riassuntiva
📝 Script: "Ricapitoliamo i punti chiave..."
🎵 Audio: Transizione musicale

⏱️ {outro_start}-{duration} - OUTRO + CTA:
🎬 Visual: End screen con subscribe + video consigliati
📝 Script: "Se ti è piaciuto, iscriviti..."
🎵 Audio: Outro music
🔔 CTA: Subscribe, Like, Commento, Campana
""",
        },
    },
}


# ============================================================================
# NANOBANANA PRO + VEO 3.1 IMAGE/VIDEO PROMPTS
# ============================================================================

VISUAL_GENERATION_PROMPTS = {
    "nanobanana_pro": {
        "model": "nano-banana-pro-preview",
        "fallback": "gemini-2.5-flash-image",
        "post": """
NANOBANANA PRO - POST IMAGE
Prompt Base: {base_prompt}
Stile: Fotografia professionale, moderno, premium
Formato: {format} ({dimensions})
Colori Brand: Oro #D4AF37 (accenti), Nero #0A0A0A (sfondo), Bianco #FAFAFA (testo)
Lighting: Luce naturale, soft shadows, warm tones
Composizione: Clean, balanced, focus on subject
Mood: Professionale ma accessibile, innovativo
Elementi: {elements}
Text Overlay: {text_overlay}
NO: Stock photos generiche, colori freddi, eccessivo clutter
Quality: Ultra HD, 4K, sharp details, professional grade
""",
        "story": """
NANOBANANA PRO - STORY IMAGE
Prompt Base: {base_prompt}
Formato: Vertical 9:16 (1080x1920)
Stile: Dinamico, eye-catching, mobile-first
Colori: Brand palette con contrasto alto
Elementi: Spazio per testo overlay, stickers area
Mood: Engaging, urgente, scroll-stopping
Quality: Ottimizzato per mobile, caricamento veloce
""",
        "carousel": """
NANOBANANA PRO - CAROUSEL SLIDE
Prompt Base: {base_prompt}
Slide: {slide_num} di {total_slides}
Formato: {format} ({dimensions})
Stile: Coerente con altre slide, series feel
Elementi: Numerazione visibile, progressione logica
Tipografia: Sans-serif bold, leggibile
Brand: Logo corner, colori consistenti
""",
        "cover": """
NANOBANANA PRO - COVER IMAGE
Prompt Base: {base_prompt}
Formato: {format} ({dimensions})
Stile: Thumbnail ottimizzato per CTR
Elementi: Titolo grande, volto se possibile, contrasto
Colori: Alta saturazione, brand colors prominenti
Text: Max 3 parole, font 100pt+
Expression: Curiosità, sorpresa, urgenza
""",
    },

    "veo_31": {
        "model": "veo-3.1",
        "fallback": "imagen-4-ultra-animation",
        "reel": """
VEO 3.1 - REEL VIDEO GENERATION
Prompt Base: {base_prompt}
Durata: {duration} secondi
Formato: Vertical 9:16 (1080x1920)
Stile: {style}
Transizioni: Smooth, dinamiche, modern
Musica Mood: {music_mood}

SCENE BREAKDOWN:
{scenes}

ELEMENTI VISIVI:
- Sottotitoli: Sempre presenti, font leggibile
- Branding: Logo in chiusura
- Colori: Oro #D4AF37, Nero #0A0A0A
- Movimento: Dinamico ma non frenetico

AUDIO SYNC:
- Beat-sync per transizioni
- Voice-over: Italiano, professionale
- Sound effects: Minimi, moderni
""",
        "story_video": """
VEO 3.1 - STORY VIDEO
Prompt Base: {base_prompt}
Durata: {duration} secondi (max 15)
Formato: Vertical 9:16
Stile: Quick, punchy, attention-grabbing
Loop: Ottimizzato per auto-play

STRUTTURA:
- 0-1s: Visual hook
- 1-12s: Core message
- 12-15s: CTA

ELEMENTI:
- Movimento costante
- Testo animato
- Brand elements
""",
        "youtube_intro": """
VEO 3.1 - YOUTUBE INTRO
Prompt Base: {base_prompt}
Durata: 5-10 secondi
Formato: Horizontal 16:9 (1920x1080)
Stile: Premium, professionale
Elementi: Logo animation, tagline, colors

SEQUENZA:
1. Logo reveal (2s)
2. Tagline animation (2s)
3. Transition to content (1s)

AUDIO:
- Jingle StudioCentOS
- Sound design premium
""",
    },
}


# ============================================================================
# PLATFORM FORMAT RULES
# ============================================================================

PLATFORM_FORMAT_RULES = {
    "linkedin": {
        "max_chars": 3000,
        "max_hashtags": 5,
        "emoji_density": "low",
        "structure": "paragraphs",
        "prompt": """
Scrivi per LinkedIn con tono PROFESSIONALE e autorevole.
STRUTTURA:
1. HOOK: Prima riga che cattura attenzione (senza emoji iniziale)
2. CORPO: 2-3 paragrafi con insights di valore
3. LISTA: Usa bullet points (✅ o •) per punti chiave
4. CTA: Domanda engaging o call-to-action professionale
5. HASHTAG: Massimo 3-5, rilevanti al settore

STILE:
- Paragrafi brevi (2-3 righe)
- Una riga vuota tra paragrafi
- Emoji moderati (max 3-4 nel post)
- Tono esperto ma accessibile
"""
    },
    "instagram": {
        "max_chars": 2200,
        "max_hashtags": 20,
        "emoji_density": "high",
        "structure": "spaced",
        "prompt": """
Scrivi per Instagram con tono CASUAL e coinvolgente.
STRUTTURA:
1. HOOK: Emoji + frase catchy che ferma lo scroll
2. CORPO: Storytelling personale o valore immediato
3. CTA: Invita all'interazione (commenta, salva, condividi)
4. HASHTAG: 15-20 rilevanti, mix popolari e di nicchia

STILE:
- Usa MOLTI emoji (ogni 1-2 frasi)
- Line breaks frequenti per leggibilità
- Tono amichevole, come parlassi a un amico
- Domande dirette al pubblico
"""
    },
    "facebook": {
        "max_chars": 63206,
        "max_hashtags": 3,
        "emoji_density": "medium",
        "structure": "paragraphs",
        "prompt": """
Scrivi per Facebook con tono CONVERSAZIONALE e storytelling.
STRUTTURA:
1. HOOK: Domanda o affermazione che invita alla lettura
2. STORIA: Racconta un'esperienza, un caso, un insight
3. VALORE: Cosa può imparare chi legge
4. CTA: Invita alla discussione nei commenti

STILE:
- Storytelling naturale
- Emoji moderati ma presenti
- Paragrafi di 3-4 righe
- Domande retoriche per engagement
"""
    },
    "twitter": {
        "max_chars": 280,
        "max_hashtags": 2,
        "emoji_density": "low",
        "structure": "minimal",
        "prompt": """
Scrivi per X (Twitter) con MASSIMA CONCISIONE.
REGOLE:
1. MAX 280 caratteri TOTALI (inclusi hashtag e spazi)
2. Un solo concetto chiaro e memorabile
3. Max 1-2 hashtag (contano nei caratteri!)
4. Emoji solo se aggiunge valore

STILE:
- Diretto e impattante
- No filler words
- Punchline immediata
"""
    },
    "tiktok": {
        "max_chars": 150,
        "max_hashtags": 5,
        "emoji_density": "high",
        "structure": "minimal",
        "prompt": """
Scrivi per TikTok caption con tono GIOVANILE e trending.
REGOLE:
1. HOOK: Cattura in 1 secondo (frase shock o curiosità)
2. BREVITÀ: Max 150 caratteri per caption efficace
3. HASHTAG: Mix trending + nicchia
4. CTA: "Salva per dopo" / "Commenta se..."

STILE:
- Ultra-casual, slang accettato
- Emoji trendy (🔥💀✨)
- Call-to-action virali
"""
    },
    "youtube_shorts": {
        "max_chars": 100,
        "max_hashtags": 3,
        "emoji_density": "medium",
        "structure": "minimal",
        "format": "9:16",
        "duration_max": 60,
        "prompt": """
Scrivi per YouTube Shorts con tono ENERGICO e hook immediato.
REGOLE:
1. HOOK: Primi 3 secondi = cattura o perdi (pattern interrupt)
2. MAX 60 secondi di contenuto, valore IMMEDIATO
3. Max 3 hashtag ultra-rilevanti (#Shorts sempre incluso)
4. Sottotitoli sempre presenti per accessibilità

STRUTTURA:
- 0-3 sec: Visual hook + testo shock
- 3-50 sec: Contenuto di valore rapidissimo
- 50-60 sec: CTA (iscriviti, like, commenta)

STILE:
- Pattern interrupt visivo
- Testo grande, leggibile, centro schermo
- Beat-sync per engagement
- Loop-friendly quando possibile
"""
    },
    "threads": {
        "max_chars": 500,
        "max_hashtags": 0,
        "emoji_density": "low",
        "structure": "conversational",
        "prompt": """
Scrivi per Threads con tono CONVERSAZIONALE autentico.
REGOLE:
1. NO hashtag (non funzionano efficacemente su Threads)
2. Max 500 caratteri per post singolo
3. Thread multipli per contenuti lunghi (indica con 1/X)
4. Tono personale, come se parlassi a un collega

STRUTTURA:
- Opinione/osservazione genuina
- Contesto breve se necessario
- Domanda che stimola discussione

STILE:
- Autentico, non promozionale
- Opinioni genuine, prendi posizione
- Domande aperte che invitano al dialogo
- NO call-to-action aggressivi
- Max 2-3 emoji, se proprio necessari
"""
    },
    "pinterest": {
        "max_chars": 500,
        "max_hashtags": 5,
        "emoji_density": "none",
        "structure": "seo_focused",
        "format": "2:3",
        "prompt": """
Scrivi per Pinterest con focus SEO e descrizione ricca.
REGOLE:
1. TITOLO: Keyword principale all'inizio (max 100 char)
2. DESCRIZIONE: Ricca di keyword, informativa, 300-500 char
3. HASHTAG: 3-5 keyword rilevanti come hashtag
4. NO emoji (non sono in linea con estetica Pinterest)

STRUTTURA:
- Titolo SEO-ottimizzato
- Descrizione con value proposition
- Call-to-action per il click
- Keywords naturalmente integrate

STILE:
- Aspirazionale
- Informativo
- Search-friendly
- Professionale
"""
    },
}


# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class BlogPostConfig(BaseModel):
    """Configuration for blog post generation."""

    topic: str = Field(..., description="Blog post topic")
    tone: ContentTone = Field(
        default=ContentTone.PROFESSIONAL, description="Writing tone"
    )
    length: int = Field(default=1000, ge=300, le=5000, description="Word count")
    keywords: List[str] = Field(
        default_factory=list, description="SEO keywords to include"
    )
    include_images: bool = Field(
        default=True, description="Include image suggestions"
    )
    target_audience: Optional[str] = Field(
        default=None, description="Target audience description"
    )
    call_to_action: Optional[str] = Field(
        default=None, description="CTA to include"
    )
    brand_context: Optional[str] = Field(
        default=None, description="Brand DNA context"
    )


class SocialPostConfig(BaseModel):
    """Configuration for social media post generation."""

    platform: SocialPlatform = Field(..., description="Target platform")
    message: str = Field(..., description="Core message")
    tone: ContentTone = Field(default=ContentTone.CASUAL, description="Post tone")
    include_hashtags: bool = Field(default=True, description="Add hashtags")
    include_emojis: bool = Field(default=True, description="Add emojis")
    max_length: Optional[int] = Field(
        default=None, description="Max character count"
    )
    call_to_action: Optional[str] = Field(default=None, description="CTA link")
    post_type: str = Field(default="educational", description="Post type template (lancio_prodotto, etc)")
    brand_context: Optional[str] = Field(
        default=None, description="Brand DNA context"
    )
    generate_image: bool = Field(default=False, description="Generate image with NanoBanana Pro")
    image_style: str = Field(default="professional", description="Image style: professional, elegant, tech, minimal")
    sector: str = Field(default="generic", description="Industry sector (ristorazione, legal, tech, real_estate)")



class AdCopyConfig(BaseModel):
    """Configuration for ad copy generation."""

    product: str = Field(..., description="Product/service name")
    value_proposition: str = Field(..., description="Main value prop")
    target_audience: str = Field(..., description="Target audience")
    tone: ContentTone = Field(default=ContentTone.URGENT, description="Ad tone")
    max_length: int = Field(default=150, description="Max characters")
    include_cta: bool = Field(default=True, description="Include CTA")
    platform: str = Field(default="google_ads", description="Ad platform")
    brand_context: Optional[str] = Field(
        default=None, description="Brand DNA context"
    )



class ReelScriptConfig(BaseModel):
    """Configuration for Reel generation from script."""
    
    script: str = Field(..., description="Full video script")
    style: Optional[str] = Field("cinematic", description="Visual style")
    transition_style: str = Field(default="none", description="Transition type: fade, zoom, blur, none")
    duration_per_scene: int = Field(5, description="Default duration per scene in seconds")
    platform: SocialPlatform = Field(SocialPlatform.INSTAGRAM, description="Target platform")

    brand_context: Optional[str] = Field(None, description="Brand DNA context")


class PlannedPost(BaseModel):
    """A single planned post in the calendar."""
    date: str = Field(..., description="YYYY-MM-DD")
    topic: str = Field(..., description="Core topic")
    angle: str = Field(..., description="Marketing angle/hook")
    format: str = Field(..., description="reel, carousel, static_image, text")
    platform: str = Field(..., description="instagram, linkedin, etc")
    notes: Optional[str] = Field(None, description="Strategy notes")

class CalendarConfig(BaseModel):
    """Configuration for generating a content calendar plan."""
    month: str = Field(..., description="Month name (e.g. October)")
    year: int = Field(..., description="Year")
    industry: str = Field(..., description="Client industry sector")
    goal: str = Field("brand_awareness", description="Main marketing goal")
    posts_per_week: int = Field(3, description="Frequency")
    brand_context: Optional[str] = Field(None, description="Brand DNA context")
    target_audience: Optional[str] = Field(None, description="Specific audience")

class CalendarResult(BaseModel):
    """Result of calendar generation."""
    month: str
    year: int
    plan: List[PlannedPost]
    strategy_summary: str


class StoryboardFrame(BaseModel):
    """A single frame in the storyboard."""
    scene_number: int
    visual_description: str
    voiceover_text: str
    duration: int = 5  # seconds
    camera_angle: Optional[str] = None
    notes: Optional[str] = None

class StoryboardConfig(BaseModel):
    """Configuration for storyboard generation."""
    script: str = Field(..., description="The full video script")
    style: str = Field("minimalist_brand", description="storyboard style")
    brand_context: Optional[str] = None

class StoryboardResult(BaseModel):
    """Result of storyboard generation."""
    frames: List[StoryboardFrame]
    total_duration: int
    summary: str


class VideoScriptConfig(BaseModel):
    """Configuration for video script generation."""

    topic: str = Field(..., description="Video topic")
    duration_seconds: int = Field(
        default=60, ge=15, le=600, description="Video duration"
    )
    tone: ContentTone = Field(default=ContentTone.FRIENDLY, description="Script tone")
    include_hook: bool = Field(default=True, description="Include opening hook")
    include_cta: bool = Field(default=True, description="Include CTA")
    format: str = Field(
        default="educational", description="Video format (educational, promotional, etc.)"
    )
    brand_context: Optional[str] = Field(
        default=None, description="Brand DNA context"
    )


class StoryConfig(BaseModel):
    """Configuration for Stories generation (Instagram/Facebook)."""

    platform: SocialPlatform = Field(
        default=SocialPlatform.INSTAGRAM, description="Target platform"
    )
    topic: str = Field(..., description="Story topic/message")
    num_slides: int = Field(default=5, ge=1, le=10, description="Number of story slides")
    post_type: str = Field(
        default="tip_giorno", description="Post type template to use"
    )
    tone: ContentTone = Field(default=ContentTone.CASUAL, description="Story tone")
    generate_images: bool = Field(default=True, description="Generate images with NanoBananaPRO")
    generate_video: bool = Field(default=False, description="Generate video with Veo 3.1")
    include_stickers: bool = Field(default=True, description="Include sticker suggestions")
    include_music: bool = Field(default=True, description="Include music suggestions")
    cta: Optional[str] = Field(default=None, description="Final call-to-action")
    brand_context: Optional[str] = Field(default=None, description="Additional brand context")


class CarouselConfig(BaseModel):
    """Configuration for Carousel post generation."""

    platform: SocialPlatform = Field(
        default=SocialPlatform.INSTAGRAM, description="Target platform"
    )
    topic: str = Field(..., description="Carousel topic")
    num_slides: int = Field(default=7, ge=3, le=10, description="Number of slides")
    post_type: str = Field(
        default="educational", description="Post type template"
    )
    tone: ContentTone = Field(default=ContentTone.PROFESSIONAL, description="Content tone")
    format: str = Field(default="1:1", description="Image format (1:1, 4:5)")
    generate_images: bool = Field(default=True, description="Generate slide images")
    include_data: bool = Field(default=True, description="Include statistics/data points")
    keywords: List[str] = Field(default_factory=list, description="Keywords to include")
    cta: Optional[str] = Field(default="Salva per dopo 📌", description="Final CTA")
    brand_context: Optional[str] = Field(default=None, description="Additional brand context")


class ReelConfig(BaseModel):
    """Configuration for Reels/TikTok video generation."""

    platform: SocialPlatform = Field(
        default=SocialPlatform.INSTAGRAM, description="Target platform (Instagram/TikTok)"
    )
    topic: str = Field(..., description="Reel topic")
    duration_seconds: int = Field(default=30, ge=15, le=90, description="Reel duration")
    post_type: str = Field(default="tip_giorno", description="Post type template")
    tone: ContentTone = Field(default=ContentTone.CASUAL, description="Content tone")
    style: str = Field(
        default="educational",
        description="Video style (educational, promotional, entertaining, tutorial)"
    )
    generate_video: bool = Field(default=True, description="Generate video with Veo 3.1")
    music_mood: str = Field(
        default="upbeat",
        description="Music mood (upbeat, chill, dramatic, trending)"
    )
    include_subtitles: bool = Field(default=True, description="Include subtitle suggestions")
    hook: Optional[str] = Field(default=None, description="Custom hook text")
    cta: Optional[str] = Field(default="Segui per altri tips!", description="Final CTA")
    brand_context: Optional[str] = Field(default=None, description="Additional brand context")


class VisualGenerationResult(BaseModel):
    """Result from image/video generation."""

    prompt_used: str = Field(..., description="Final prompt sent to AI")
    model_used: str = Field(..., description="AI model used")
    image_url: Optional[str] = Field(default=None, description="Generated image URL")
    video_url: Optional[str] = Field(default=None, description="Generated video URL")
    generation_time: float = Field(..., description="Time taken in seconds")
    cost_estimate: float = Field(default=0.0, description="Estimated cost")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ContentResult(BaseModel):
    """Result from content generation."""

    content: str = Field(..., description="Generated content")
    content_type: ContentType = Field(..., description="Content type")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )
    seo_score: Optional[float] = Field(
        default=None, ge=0.0, le=100.0, description="SEO quality score"
    )
    brand_compliance: bool = Field(
        default=True, description="Passes brand guidelines"
    )
    suggestions: List[str] = Field(
        default_factory=list, description="Improvement suggestions"
    )
    images: List[VisualGenerationResult] = Field(
        default_factory=list, description="Generated images"
    )
    videos: List[VisualGenerationResult] = Field(
        default_factory=list, description="Generated videos"
    )
    slides: List[Dict[str, Any]] = Field(
        default_factory=list, description="Slide content for carousel/stories"
    )
    image_url: Optional[str] = Field(
        default=None, description="Primary generated image URL (NanoBanana Pro)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Creation timestamp"
    )


# ============================================================================
# CONTENT CREATOR AGENT
# ============================================================================


class ContentCreatorAgent(BaseAgent):
    """
    Content Creator Agent for marketing content generation.

    PRODUCTION-READY with:
    - NanoBananaPRO (Imagen 4 Ultra) for image generation
    - Veo 3.1 for video generation
    - Specific templates for all content types

    Specializes in creating high-quality, SEO-optimized content across
    multiple formats while maintaining brand voice consistency.

    Capabilities:
        - Blog post generation (300-5000 words)
        - Social media posts (platform-optimized)
        - Stories (Instagram/Facebook)
        - Carousels (multi-slide educational content)
        - Reels/TikToks (short-form video)
        - Ad copy (concise, compelling)
        - Video scripts (15-600 seconds)
        - Newsletter content
        - Landing page copy

    Visual Generation:
        - NanoBananaPRO: Imagen 4 Ultra for static images
        - Veo 3.1: Video generation for Reels/Stories

    Example:
        >>> config = AgentConfig(
        ...     id="content_creator_1",
        ...     name="Content Creator",
        ...     model="gpt-4",
        ...     temperature=0.7,
        ... )
        >>> agent = ContentCreatorAgent(config=config)
        >>>
        >>> # Generate complete carousel with images
        >>> result = await agent.generate_carousel(
        ...     CarouselConfig(
        ...         platform=SocialPlatform.INSTAGRAM,
        ...         topic="5 Modi per Automatizzare la Tua PMI",
        ...         num_slides=7,
        ...         generate_images=True,
        ...     )
        ... )
    """

    def __init__(self, config: AgentConfig):
        """
        Initialize Content Creator Agent with NanoBananaPRO and Veo 3.1.

        Args:
            config: Agent configuration
        """
        super().__init__(config)

        # Brand guidelines (loaded from config)
        self.brand_guidelines: Dict[str, Any] = {}
        self.seo_config: Dict[str, Any] = {}

        # Image Generator (NanoBananaPRO)
        self.image_generator = None

        # Video Generator (Veo 3.1)
        self.video_generator = None

    async def on_start(self) -> None:
        """Initialize agent resources including image/video generators and ContentEnhancer."""
        # Note: BaseAgent has no on_start() method, so we don't call super()

        # Initialize Content Enhancer for few-shot, validation, RAG, topic rotation
        self.content_enhancer = await get_content_enhancer()
        logger.info("ContentEnhancer initialized with few-shot learning and RAG")

        # Load Brand DNA guidelines
        self.brand_guidelines = {
            "name": BRAND_DNA["identity"]["name"],
            "tone": BRAND_DNA["voice"]["primary"],
            "avoid_words": BRAND_DNA["avoid_words"],
            "values": BRAND_DNA["values"],
            "hashtags": BRAND_DNA["hashtags"],
            "target": BRAND_DNA["target"],
            "voice_examples": [
                "Professionale ma accessibile",
                "Diretto e concreto",
                "Positivo ma realistico",
            ],
        }

        # Load SEO configuration
        self.seo_config = {
            "min_keyword_density": 1.0,
            "max_keyword_density": 3.0,
            "min_readability_score": 60.0,
        }

        # Initialize Image Generator (NanoBanana Pro)
        try:
            from app.domain.marketing.image_generator_agent import ImageGenerationAgent
            from app.infrastructure.agents.base_agent import AgentConfig as ImgAgentConfig
            self.image_generator = ImageGenerationAgent(
                config=ImgAgentConfig(
                    agent_id="content_image_gen",
                    agent_type="image_generation",
                    model="nano-banana-pro-preview",
                    temperature=0.7
                )
            )
            logger.info("ImageGenerationAgent initialized with NanoBanana Pro")
        except Exception as e:
            logger.warning(f"ImageGenerationAgent initialization failed: {e}")
            self.image_generator = None

        # Initialize Video Generator (Veo)
        try:
            from app.domain.marketing.video_generator_agent import VideoGenerationAgent
            self.video_generator = VideoGenerationAgent(
                config=AgentConfig(
                    agent_id="content_video_gen",
                    agent_type="video_generation",
                    model="veo-2.0-generate-preview",
                    temperature=0.7
                )
            )
            logger.info("VideoGenerationAgent initialized with Veo")
        except Exception as e:
            logger.warning(f"VideoGenerationAgent initialization failed: {e}")
            self.video_generator = None


    def get_capabilities(self) -> List[AgentCapability]:
        """Get list of content creation capabilities."""
        return [
            AgentCapability(
                name="blog_generation",
                description="Generate SEO-optimized blog posts",
                input_schema={"topic": "str", "length": "int", "keywords": "list"},
                output_schema={"content": "str", "seo_score": "float"},
            ),
            AgentCapability(
                name="social_post",
                description="Generate platform-optimized social media posts",
                input_schema={"platform": "str", "message": "str", "post_type": "str"},
                output_schema={"content": "str", "hashtags": "list"},
            ),

            AgentCapability(
                name="story_generation",
                description="Generate Instagram/Facebook Stories with images via NanoBananaPRO",
                input_schema={"platform": "str", "topic": "str", "num_slides": "int", "generate_images": "bool"},
                output_schema={"content": "str", "slides": "list", "images": "list"},
            ),
            AgentCapability(
                name="carousel_generation",
                description="Generate multi-slide Carousel posts with images via NanoBananaPRO",
                input_schema={"platform": "str", "topic": "str", "num_slides": "int", "generate_images": "bool"},
                output_schema={"content": "str", "slides": "list", "images": "list"},
            ),
            AgentCapability(
                name="reel_generation",
                description="Generate Reels/TikTok video content with Veo 3.1",
                input_schema={"platform": "str", "topic": "str", "duration_seconds": "int", "generate_video": "bool"},
                output_schema={"content": "str", "scenes": "list", "videos": "list"},
            ),
            AgentCapability(
                name="ad_copy",
                description="Generate compelling ad copy with CTAs",
                input_schema={"product": "str", "target_audience": "str"},
                output_schema={"content": "str"},
            ),
            AgentCapability(
                name="video_script",
                description="Generate video scripts with timestamps",
                input_schema={"topic": "str", "duration": "int"},
                output_schema={"script": "str"},
            ),
        ]

    async def execute(self, task: Task) -> TaskOutput:
        """Execute content generation task based on type."""
        task_type = task.input.data.get("type", "blog")

        try:
            if task_type == "blog":
                config = BlogPostConfig(**task.input.data)
                result = await self.generate_blog_post(config)
            elif task_type == "social":
                config = SocialPostConfig(**task.input.data)
                result = await self.generate_social_post(config)
            elif task_type == "ad":
                config = AdCopyConfig(**task.input.data)
                result = await self.generate_ad_copy(config)
            elif task_type == "video":
                config = VideoScriptConfig(**task.input.data)
                result = await self.generate_video_script(config)
            elif task_type == "story":
                config = StoryConfig(**task.input.data)
                result = await self.generate_story(config)
            elif task_type == "carousel":
                config = CarouselConfig(**task.input.data)
                result = await self.generate_carousel(config)
            elif task_type == "reel":
                config = ReelConfig(**task.input.data)
                result = await self.generate_reel(config)
            else:
                raise ValueError(f"Unknown content type: {task_type}")

            return TaskOutput(
                result={
                    "content": result.content,
                    "metadata": result.metadata,
                    "slides": [dict(s) for s in result.slides] if result.slides else [],
                    "images": [img.model_dump() for img in result.images] if result.images else [],
                    "videos": [vid.model_dump() for vid in result.videos] if result.videos else [],
                },
                metadata={"content_type": task_type, "seo_score": result.seo_score}
            )

        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return TaskOutput(
                result={"error": str(e)},
                metadata={"status": "failed"}
            )

    async def generate_blog_post(
        self, config: BlogPostConfig
    ) -> ContentResult:
        """
        Generate SEO-optimized blog post.

        Args:
            config: Blog post configuration

        Returns:
            ContentResult with generated blog post

        Example:
            >>> result = await agent.generate_blog_post(
            ...     BlogPostConfig(
            ...         topic="AI Agents",
            ...         length=1000,
            ...         keywords=["AI", "agents", "automation"],
            ...     )
            ... )
        """
        # Build prompt
        prompt = self._build_blog_prompt(config)

        # Generate content via LLM
        content = await self._generate_content(prompt, config.brand_context)

        # Optimize for SEO
        optimized = await self._optimize_seo(content, config.keywords)

        # Calculate SEO score
        seo_score = self._calculate_seo_score(optimized, config.keywords)

        # Check brand compliance
        compliant = await self._check_brand_compliance(optimized)

        return ContentResult(
            content=optimized,
            content_type=ContentType.BLOG_POST,
            metadata={
                "topic": config.topic,
                "word_count": len(optimized.split()),
                "keywords": config.keywords,
                "tone": config.tone.value,
            },
            seo_score=seo_score,
            brand_compliance=compliant,
        )

    async def generate_social_post(
        self, config: SocialPostConfig
    ) -> ContentResult:
        """
        Generate platform-optimized social media post with enhanced quality.

        Args:
            config: Social post configuration

        Returns:
            ContentResult with social media post and brand validation scorecard
        """
        # Platform-specific constraints
        platform_limits = {
            SocialPlatform.TWITTER: 280,
            SocialPlatform.FACEBOOK: 63206,
            SocialPlatform.LINKEDIN: 3000,
            SocialPlatform.INSTAGRAM: 2200,
        }

        max_length = config.max_length or platform_limits.get(
            config.platform, 1000
        )

        # Build prompt (now with few-shot and enhanced creativity)
        prompt = self._build_social_prompt(config, max_length)

        # Generate content with higher temperature for creativity
        content = await self._generate_content(prompt, config.brand_context)

        # Add hashtags if requested
        if config.include_hashtags:
            content = await self._add_hashtags(content, config.platform)

        # Check brand compliance (legacy method)
        compliant = await self._check_brand_compliance(content)

        # === ENHANCED BRAND VALIDATION ===
        # Use BrandVoiceValidator for detailed quality scorecard
        validation_result = None
        brand_scorecard = {}
        if hasattr(self, 'content_enhancer') and self.content_enhancer:
            validation_result = self.content_enhancer.validate_content(
                content, config.platform.value.lower()
            )
            brand_scorecard = {
                "brand_score": validation_result.score,
                "passed": validation_result.passed,
                "issues": validation_result.issues,
                "suggestions": validation_result.suggestions,
                "details": validation_result.details,
            }
            logger.info(f"Brand validation score: {validation_result.score}/100")

        # === IMAGE GENERATION WITH NANOBANANA PRO ===
        image_url = None
        if config.generate_image and self.image_generator:
            try:
                from app.domain.marketing.image_generator_agent import ImageGenerationConfig, get_platform_dimensions
                # STRICT BRAND-COMPLIANT PROMPT based on official_brand_guidelines.md
                image_prompt = f"""
STRICT BRAND GUIDELINES - DO NOT DEVIATE:

SUBJECT: Abstract professional visual for "{config.message}"

MANDATORY STYLE:
- Cinematic, Ultra-realistic, 8k resolution
- Volumetric Gold lighting on deep matte black
- Minimalist composition, clean negative space
- NO text, NO logos, NO watermarks (logo added separately)

MANDATORY COLORS (EXACT):
- Background: SOLID DEEP BLACK #0A0A0A (must dominate 80%+ of image)
- Accent: SUBTLE Gold #D4AF37 (only 10-20% as highlights/edges)
- NO bright gold, NO gold ribbons, NO gold gradients covering large areas

VISUAL ELEMENTS (choose one):
- Abstract neural network nodes in thin gold wireframe on black
- Minimalist futuristic glass interface with gold edge lighting
- Clean geometric shapes with gold rim lighting
- Professional office/tech scene with subtle gold accent light

FORBIDDEN (will ruin the brand):
- Cartoon style, Low poly, 3D renders looking fake
- Neon pink, Neon green, Rainbow colors
- Excessive gold covering entire image
- Gold ribbons, Gold waves, Gold swirls
- Any text or fake logos
- Cluttered busy compositions
- Stock photo generic look

Quality: Photorealistic, Professional Ad Campaign Level
"""
                # Auto-detect dimensions
                post_type_key = "story" if "story" in config.post_type else "post"
                dims = get_platform_dimensions(config.platform.value, post_type_key)

                img_config = ImageGenerationConfig(
                    prompt=image_prompt,
                    style=config.image_style,
                    content_type="social_post",
                    width=dims["width"],
                    height=dims["height"],
                    apply_branding=True
                )
                
                # Check for A/B testing request (default False)
                generate_variants = getattr(config, "generate_variants", False)
                if generate_variants:
                    variants = await self.image_generator.generate_ab_variants(img_config)
                    
                    # For main image_url, pick the first one
                    if variants:
                        image_url = variants[0].image_url
                        logger.info(f"Generated {len(variants)} A/B variants")
                else:
                    img_result = await self.image_generator.generate_image(img_config)
                    if img_result:
                        image_url = img_result.image_url
                        logger.info(f"Image generated via NanoBanana Pro: {image_url}")
                        variants = [img_result]
            except Exception as e:
                logger.warning(f"Failed to generate social post image: {e}")
                variants = []

        # === SEO & READABILITY & SENTIMENT (StudioCentOS 4.3/4.4/4.5) ===
        seo_metrics = {}
        readability_metrics = {}
        sentiment_analysis = {}
        
        if hasattr(self, 'content_enhancer') and self.content_enhancer:
             seo_metrics = self.content_enhancer.calculate_seo_metrics(
                 content, 
                 config.platform.value,
                 topic=config.message if len(config.message) < 50 else ""
             )
             readability_metrics = self.content_enhancer.calculate_readability_italian(content)
             sentiment_analysis = self.content_enhancer.analyze_sentiment(content, config.tone.value)
             
             sentiment_analysis = self.content_enhancer.analyze_sentiment(content, config.tone.value)
             competitor_check = self.content_enhancer.check_competitor_avoidance(content, getattr(config, 'sector', 'generic'))
             engagement_metrics = self.content_enhancer.predict_engagement_score(content, config.platform.value)
             
        return ContentResult(
            content=content,
            content_type=ContentType.SOCIAL_POST,
            metadata={
                "platform": config.platform.value,
                "character_count": len(content),
                "tone": config.tone.value,
                "brand_scorecard": brand_scorecard,
                "enhanced_generation": True,
                "image_url": image_url,
                "post_type": config.post_type,
                "target": config.target_audience if hasattr(config, "target_audience") else "general",
                "ab_variants": len(variants) if 'variants' in locals() else 0,
                "readability": readability_metrics,
                "seo_suggestions": seo_metrics.get("suggestions", []),
                "sentiment_validation": sentiment_analysis,
                "competitor_check": locals().get("competitor_check", {}),
                "engagement_score": locals().get("engagement_metrics", {})
            },
            seo_score=seo_metrics.get("score"),
            suggestions=seo_metrics.get("suggestions", []) + brand_scorecard.get("suggestions", []) + locals().get("competitor_check", {}).get("issues", []) + locals().get("engagement_metrics", {}).get("suggestions", []),
            brand_compliance=compliant and sentiment_analysis.get("match", True) and locals().get("competitor_check", {}).get("is_compliant", True),
            image_url=image_url,
            images=variants if 'variants' in locals() else []
        )

    async def generate_reel_from_script(self, config: ReelScriptConfig) -> ContentResult:
        """
        Generate full Reel (video clips) from a text script using Veo.
        
        Orchestration:
        1. Parse Script -> Visual Scenes (LLM)
        2. Generate Video for each scene (Veo)
        3. Collect and return clips
        
        Args:
            config: ReelScriptConfig with script and style
            
        Returns:
            ContentResult with list of generated videos
        """
        logger.info("Starting Script-to-Video workflow (Veo)...")
        
        # 1. Parse Script to Scenes
        parsing_prompt = f"""
        ANALYZE this video script and create a Visual Storyboard for AI Video Generation.
        
        SCRIPT:
        "{config.script}"
        
        INSTRUCTIONS:
        - Break the script into logical visual scenes/shots
        - Convert text to detailed cinematic visual descriptions for the AI
        - Keep visual style consistent: {config.style}
        - Estimates duration for each shot (default {config.duration_per_scene}s)
        
        OUTPUT FORMAT (Strict JSON list):
        [
            {{"visual_prompt": "Cinematic 4k shot of...", "duration": 4}},
            {{"visual_prompt": "Close up of...", "duration": 5}}
        ]
        """
        
        scenes_json_str = await self._generate_content(parsing_prompt, brand_context=config.brand_context, use_rag=False)
        
        # Robust JSON parsing
        import json
        import re
        scenes = []
        try:
            # Clean markdown code blocks if present
            clean_json = scenes_json_str
            if "```" in clean_json:
                clean_json = re.sub(r"```(?:json)?\s*(.*?)\s*```", r"\1", clean_json, flags=re.DOTALL)
            
            scenes = json.loads(clean_json.strip())
            
            if not isinstance(scenes, list):
                logger.warning("Parsed scenes JSON is not a list. Fallback to single scene.")
                scenes = [{"visual_prompt": f"Cinematic visualization of: {config.script[:100]}", "duration": config.duration_per_scene}]
                
        except Exception as e:
            logger.error(f"Failed to parse storyboard JSON: {e}. Raw: {scenes_json_str[:100]}...")
            # Fallback
            scenes = [{"visual_prompt": f"Cinematic visualization of: {config.script[:100]}", "duration": config.duration_per_scene}]

        logger.info(f"Parsed {len(scenes)} scenes from script.")

        # 2. Generate Video Clips (Veo)
        generated_videos = []
        
        # Import internally to avoid circular dependency
        try:
            from app.domain.marketing.video_generator_agent import VideoGenerationConfig, VideoAspectRatio
            
            for i, scene in enumerate(scenes):
                try:
                    prompt = scene.get("visual_prompt", "")
                    
                    # Add Transition Instruction if requested
                    if config.transition_style and config.transition_style != "none":
                        # Add instruction to end of start of clip depending on style
                        # For generated video clips, often "Start with..." or "End with..." helps
                        if config.transition_style == "fade":
                            prompt += ". End with a subtle fade to black."
                        elif config.transition_style == "zoom":
                             prompt += ". Camera slowly zooms in towards the end."
                        elif config.transition_style == "blur":
                             prompt += ". End with a motion blur transition."
                    
                    duration = int(scene.get("duration", config.duration_per_scene))
                    # Clamp duration 
                    duration = max(1, min(60, duration))
                    
                    vid_config = VideoGenerationConfig(
                        prompt=prompt,
                        duration_seconds=duration,
                        aspect_ratio=VideoAspectRatio.PORTRAIT, # Reels are 9:16
                        style=config.style
                    )
                    
                    if self.video_generator:
                        logger.info(f"Generating Clip {i+1}/{len(scenes)}...")
                        result = await self.video_generator.generate_video(vid_config)
                        
                        # Enrich result metadata
                        result.metadata["scene_index"] = i + 1
                        result.metadata["total_scenes"] = len(scenes)
                        result.metadata["script_segment"] = prompt[:50]
                        
                        generated_videos.append(result)
                    
                except Exception as ex:
                    logger.error(f"Failed to generate scene {i}: {ex}")
                    
        except ImportError:
            logger.error("Could not import VideoGenerationAgent types")
            
        return ContentResult(
            content=config.script,
            content_type=ContentType.VIDEO_SCRIPT, # Return as script type or equivalent
            videos=generated_videos,
            metadata={
                "total_clips": len(generated_videos),
                "workflow": "script_to_video_veo"
            }
        )

    async def generate_ad_copy(
        self, config: AdCopyConfig
    ) -> ContentResult:
        """
        Generate compelling ad copy with CTA.

        Args:
            config: Ad copy configuration

        Returns:
            ContentResult with ad copy
        """
        prompt = self._build_ad_prompt(config)
        content = await self._generate_content(prompt, config.brand_context)

        # Ensure CTA is present
        if config.include_cta and "call" not in content.lower():
            content = await self._add_cta(content)

        # Check compliance
        compliant = await self._check_brand_compliance(content)

        return ContentResult(
            content=content,
            content_type=ContentType.AD_COPY,
            metadata={
                "product": config.product,
                "platform": config.platform,
                "character_count": len(content),
            },
            brand_compliance=compliant,
        )

    async def generate_video_script(
        self, config: VideoScriptConfig
    ) -> ContentResult:
        """
        Generate engaging video script.

        Args:
            config: Video script configuration

        Returns:
            ContentResult with video script
        """
        prompt = self._build_video_prompt(config)
        content = await self._generate_content(prompt, config.brand_context)

        # Format as script with timestamps
        formatted = await self._format_video_script(
            content, config.duration_seconds
        )

        compliant = await self._check_brand_compliance(formatted)

        return ContentResult(
            content=formatted,
            content_type=ContentType.VIDEO_SCRIPT,
            metadata={
                "duration_seconds": config.duration_seconds,
                "format": config.format,
            },
            brand_compliance=compliant,
        )

    # ========================================================================
    # STORY, CAROUSEL, REEL GENERATION - NanoBananaPRO + Veo 3.1
    # ========================================================================

    async def generate_story(
        self, config: StoryConfig
    ) -> ContentResult:
        """
        Generate complete Stories content with visuals.

        Uses NanoBananaPRO (Imagen 4 Ultra) for image generation
        and Veo 3.1 for video stories.

        Args:
            config: Story configuration

        Returns:
            ContentResult with slides, text, and visual assets
        """
        platform_key = config.platform.value.lower()
        story_template = CONTENT_FORMAT_TEMPLATES.get("story", {}).get(
            platform_key, CONTENT_FORMAT_TEMPLATES["story"]["instagram"]
        )

        slides = []
        images = []

        # Get post type template for content structure
        post_template = POST_TYPE_PROMPTS.get(config.post_type, POST_TYPE_PROMPTS["tip_giorno"])

        # Generate content for each slide
        for slide_num in range(1, config.num_slides + 1):
            slide_type = self._determine_slide_type(slide_num, config.num_slides)

            # Build prompt for this slide
            slide_prompt = await self._build_story_slide_prompt(
                config, slide_num, slide_type, post_template
            )

            # Generate slide content
            slide_content = await self._generate_content(slide_prompt, config.brand_context)

            slide_data = {
                "slide_num": slide_num,
                "type": slide_type,
                "content": slide_content,
                "duration": story_template.get("duration", 15),
            }

            # Generate image if requested
            if config.generate_images:
                image_result = await self._generate_story_image(
                    config, slide_num, slide_type, slide_content
                )
                if image_result:
                    slide_data["image"] = image_result
                    images.append(image_result)

            # Add sticker suggestions
            if config.include_stickers:
                slide_data["stickers"] = self._suggest_stickers(slide_type, slide_content)

            # Add music suggestions
            if config.include_music:
                slide_data["music"] = self._suggest_music(config.tone, slide_type)

            slides.append(slide_data)

        # Build combined content text
        combined_content = self._format_story_content(slides)

        # Check brand compliance
        compliant = await self._check_brand_compliance(combined_content)

        return ContentResult(
            content=combined_content,
            content_type=ContentType.SOCIAL_POST,
            metadata={
                "platform": config.platform.value,
                "format": "story",
                "num_slides": config.num_slides,
                "post_type": config.post_type,
                "has_images": config.generate_images,
                "has_video": config.generate_video,
            },
            slides=slides,
            images=images,
            brand_compliance=compliant,
        )

    async def generate_carousel(
        self, config: CarouselConfig
    ) -> ContentResult:
        """
        Generate complete Carousel post with all slides.

        Uses NanoBananaPRO (Imagen 4 Ultra) for slide image generation.

        Args:
            config: Carousel configuration

        Returns:
            ContentResult with slides, text, caption, and visual assets
        """
        platform_key = config.platform.value.lower()
        carousel_template = CONTENT_FORMAT_TEMPLATES.get("carousel", {}).get(
            platform_key, CONTENT_FORMAT_TEMPLATES["carousel"]["instagram"]
        )

        # Get post type template
        post_template = POST_TYPE_PROMPTS.get(config.post_type, POST_TYPE_PROMPTS["educational"])

        # Generate complete carousel structure first
        structure_prompt = self._build_carousel_structure_prompt(config, post_template)
        carousel_structure = await self._generate_content(structure_prompt, config.brand_context)

        slides = []
        slide_image_configs = [] # New: Collect configs for batch generation

        # Parse structure and generate individual slides
        slide_contents = self._parse_carousel_structure(carousel_structure, config.num_slides)

        # Auto-detect dimensions for carousel (portrait usually best)
        from app.domain.marketing.image_generator_agent import get_platform_dimensions, ImageGenerationConfig
        dims = get_platform_dimensions(config.platform.value, "carousel")
        
        # Series Consistency: Generate a unique visual thread description
        visual_thread = f"Visual Style: {config.image_style if config.image_style else 'Professional'} coherent series. Consistent lighting and color palette."

        for slide_num, slide_content in enumerate(slide_contents, 1):
            slide_type = self._determine_carousel_slide_type(slide_num, config.num_slides)

            slide_data = {
                "slide_num": slide_num,
                "type": slide_type,
                "title": slide_content.get("title", f"Slide {slide_num}"),
                "content": slide_content.get("body", ""),
                "bullets": slide_content.get("bullets", []),
            }
            slides.append(slide_data)

            # Prepare image config if requested
            if config.generate_images:
                # We use the internal helper to get the prompt, but NOT generate yet
                # We need to split _generate_carousel_image to separate prompt building
                img_prompt = self._build_carousel_image_prompt(config, slide_num, slide_type, slide_data, dims, visual_thread)
                
                slide_image_configs.append(
                    ImageGenerationConfig(
                        prompt=img_prompt,
                        style=config.image_style or "professional",
                        width=dims["width"],
                        height=dims["height"],
                        apply_branding=True
                    )
                )

        # Batch Generation with Consistency
        images = []
        if config.generate_images and self.image_generator:
            import random
            from app.core.logging import logger
            consistency_seed = random.randint(0, 1000000)
            logger.info(f"Generating carousel batch with seed {consistency_seed} for consistency")
            
            batch_results = await self.image_generator.generate_batch(
                configs=slide_image_configs,
                consistency_seed=consistency_seed
            )
            
            # Map results back to slides
            for i, result in enumerate(batch_results):
                if result:
                    slides[i]["image"] = result
                    images.append(result.model_dump())

        # Generate caption for the carousel
        caption = await self._generate_carousel_caption(config, slides)

        # Format complete content
        combined_content = self._format_carousel_content(slides, caption)

        # Calculate SEO score if keywords provided
        seo_score = None
        if config.keywords:
            seo_score = self._calculate_seo_score(combined_content, config.keywords)

        # Check brand compliance
        compliant = await self._check_brand_compliance(combined_content)

        return ContentResult(
            content=combined_content,
            content_type=ContentType.SOCIAL_POST,
            metadata={
                "platform": config.platform.value,
                "format": "carousel",
                "num_slides": len(slides),
                "post_type": config.post_type,
                "has_images": config.generate_images,
                "image_format": config.format,
                "keywords": config.keywords,
            },
            slides=slides,
            images=images,
            seo_score=seo_score,
            brand_compliance=compliant,
        )

    async def generate_reel(
        self, config: ReelConfig
    ) -> ContentResult:
        """
        Generate complete Reel/TikTok video content.

        Uses Veo 3.1 for video generation and NanoBananaPRO for thumbnails.

        Args:
            config: Reel configuration

        Returns:
            ContentResult with script, scenes, and video assets
        """
        platform_key = config.platform.value.lower()
        reel_template = CONTENT_FORMAT_TEMPLATES.get("reel", {}).get(
            platform_key, CONTENT_FORMAT_TEMPLATES["reel"]["instagram"]
        )

        # Get post type template
        post_template = POST_TYPE_PROMPTS.get(config.post_type, POST_TYPE_PROMPTS["tip_giorno"])

        # Calculate timing breakpoints
        duration = config.duration_seconds
        hook_end = min(5, int(duration * 0.15))
        solution_end = int(duration * 0.85)

        # Build the complete reel script prompt
        reel_prompt = self._build_reel_prompt(config, post_template, hook_end, solution_end)

        # Generate the script
        script = await self._generate_content(reel_prompt, config.brand_context)

        # Parse into scenes
        scenes = self._parse_reel_scenes(script, duration)

        videos = []
        images = []

        # Generate video if requested
        if config.generate_video:
            video_result = await self._generate_reel_video(config, scenes)
            if video_result:
                videos.append(video_result)

        # Generate thumbnail
        thumbnail_result = await self._generate_reel_thumbnail(config, scenes[0] if scenes else {})
        if thumbnail_result:
            images.append(thumbnail_result)

        # Generate caption
        caption = await self._generate_reel_caption(config, script)

        # Format complete content
        combined_content = self._format_reel_content(script, caption, scenes)

        # Check brand compliance
        compliant = await self._check_brand_compliance(combined_content)

        return ContentResult(
            content=combined_content,
            content_type=ContentType.VIDEO_SCRIPT,
            metadata={
                "platform": config.platform.value,
                "format": "reel",
                "duration_seconds": config.duration_seconds,
                "style": config.style,
                "music_mood": config.music_mood,
                "num_scenes": len(scenes),
                "has_video": config.generate_video,
            },
            slides=scenes,  # Scenes as slides
            images=images,
            videos=videos,
            brand_compliance=compliant,
        )

    # ========================================================================
    # STORY/CAROUSEL/REEL HELPER METHODS
    # ========================================================================

    def _determine_slide_type(self, slide_num: int, total_slides: int) -> str:
        """Determine the type of story slide based on position."""
        if slide_num == 1:
            return "hook"
        elif slide_num == total_slides:
            return "cta"
        else:
            return "content"

    def _determine_carousel_slide_type(self, slide_num: int, total_slides: int) -> str:
        """Determine the type of carousel slide based on position."""
        if slide_num == 1:
            return "cover"
        elif slide_num == 2:
            return "context"
        elif slide_num == total_slides - 1:
            return "recap"
        elif slide_num == total_slides:
            return "cta"
        else:
            return "content"

    async def _build_story_slide_prompt(
        self, config: StoryConfig, slide_num: int, slide_type: str, post_template: str
    ) -> str:
        """Build prompt for a single story slide."""
        brand_prompt = get_brand_dna_prompt()

        slide_instructions = {
            "hook": """
SLIDE HOOK - Cattura l'attenzione IMMEDIATA
- Domanda provocatoria O statistica shock
- Testo GRANDE e leggibile
- Max 10 parole
- Emoji iniziale accattivante""",
            "content": f"""
SLIDE CONTENUTO {slide_num}
- Un singolo punto/step/concetto
- Bullet point visivo
- Emoji descrittiva
- Max 20 parole""",
            "cta": """
SLIDE CTA FINALE
- Call-to-action chiara
- "Swipe up", "Link in bio", "DM per info"
- Urgenza/beneficio
- Emoji azione 👉 / 🔗 / 💬""",
        }

        return f"""{brand_prompt}

{post_template}

TASK: Genera il contenuto per la SLIDE {slide_num}/{config.num_slides} di una Story {config.platform.value.upper()}

ARGOMENTO: {config.topic}
TONO: {config.tone.value}

{slide_instructions.get(slide_type, slide_instructions["content"])}

FORMATO OUTPUT:
📱 TESTO PRINCIPALE: [testo per la slide - max 20 parole]
✏️ OVERLAY AGGIUNTIVO: [testo secondario se necessario]
🎯 AZIONE UTENTE: [cosa deve fare l'utente]
"""

    async def _generate_story_image(
        self, config: StoryConfig, slide_num: int, slide_type: str, content: str
    ) -> Optional[VisualGenerationResult]:
        """Generate image for a story slide using NanoBananaPRO."""
        import time
        start_time = time.time()

        try:
            from app.domain.marketing.image_generator_agent import ImageGenerationAgent, ImageGenerationConfig, get_platform_dimensions

            # Build image prompt from template
            image_template = VISUAL_GENERATION_PROMPTS["nanobanana_pro"]["story"]

            # Extract text overlay from content
            text_overlay = content[:50] if content else ""

            image_prompt = f"""
Story slide per {config.topic}
Tipo: {slide_type}
Formato: Vertical 9:16 per {config.platform.value}
Stile: Premium, brand StudioCentOS
Colori: Oro #D4AF37, Nero #0A0A0A, Bianco
Testo overlay area: "{text_overlay}"
Mood: {config.tone.value}, engaging, mobile-first
NO: Stock generiche, testo illeggibile, colori freddi
"""
            # Auto-detect dimensions
            dims = get_platform_dimensions(config.platform.value, "story")

            # Use existing image generator if available
            if self.image_generator:
                result = await self.image_generator.generate_image(
                    ImageGenerationConfig(prompt=image_prompt, style="professional", width=dims["width"], height=dims["height"])
                )
                return VisualGenerationResult(
                    prompt_used=image_prompt,
                    model_used="nano-banana-pro-preview",
                    image_url=result.image_url if result else None,
                    generation_time=time.time() - start_time,
                )

            # Fallback: return prompt for manual generation
            return VisualGenerationResult(
                prompt_used=image_prompt,
                model_used="nanobanana-pro-pending",
                generation_time=time.time() - start_time,
                metadata={"status": "prompt_ready", "requires_generation": True}
            )

        except Exception as e:
            logger.warning(f"Story image generation failed: {e}")
            return None

    def _suggest_stickers(self, slide_type: str, content: str) -> List[str]:
        """Suggest Instagram/Facebook stickers for a slide."""
        sticker_map = {
            "hook": ["quiz", "poll", "countdown", "question"],
            "content": ["emoji_slider", "mention", "hashtag"],
            "cta": ["link", "contact", "dm_me", "shop"],
        }
        return sticker_map.get(slide_type, ["emoji_slider"])

    def _suggest_music(self, tone: ContentTone, slide_type: str) -> Dict[str, str]:
        """Suggest music for story slides."""
        music_map = {
            ContentTone.PROFESSIONAL: {"mood": "corporate", "tempo": "medium", "genre": "ambient"},
            ContentTone.CASUAL: {"mood": "upbeat", "tempo": "fast", "genre": "pop"},
            ContentTone.FRIENDLY: {"mood": "warm", "tempo": "medium", "genre": "acoustic"},
            ContentTone.URGENT: {"mood": "dramatic", "tempo": "fast", "genre": "electronic"},
            ContentTone.INSPIRATIONAL: {"mood": "epic", "tempo": "building", "genre": "cinematic"},
        }
        return music_map.get(tone, {"mood": "neutral", "tempo": "medium", "genre": "background"})

    def _format_story_content(self, slides: List[Dict[str, Any]]) -> str:
        """Format all story slides into a single content string."""
        formatted = "📱 INSTAGRAM STORY CONTENT\n" + "=" * 40 + "\n\n"

        for slide in slides:
            formatted += f"SLIDE {slide['slide_num']} ({slide['type'].upper()}):\n"
            formatted += f"{slide['content']}\n"
            if slide.get('stickers'):
                formatted += f"Stickers suggeriti: {', '.join(slide['stickers'])}\n"
            if slide.get('music'):
                formatted += f"Musica: {slide['music'].get('mood', 'neutral')} - {slide['music'].get('genre', '')}\n"
            formatted += "\n---\n\n"

        return formatted

    def _build_carousel_structure_prompt(self, config: CarouselConfig, post_template: str) -> str:
        """Build prompt for complete carousel structure."""
        brand_prompt = get_brand_dna_prompt()

        return f"""{brand_prompt}

{post_template}

TASK: Crea la struttura completa di un CAROUSEL {config.platform.value.upper()} con {config.num_slides} slide

ARGOMENTO: {config.topic}
TONO: {config.tone.value}
{"KEYWORDS da includere: " + ", ".join(config.keywords) if config.keywords else ""}
{"DATI/STATISTICHE: Sì, includi numeri concreti" if config.include_data else ""}

STRUTTURA RICHIESTA:
1. SLIDE 1 (COVER): Titolo accattivante + hook
2. SLIDE 2 (CONTESTO): Perché questo argomento è importante
3. SLIDE 3-{config.num_slides - 2} (CONTENUTO): Un punto per slide con bullet
4. SLIDE {config.num_slides - 1} (RECAP): Riassunto punti chiave
5. SLIDE {config.num_slides} (CTA): Call-to-action finale

FORMATO OUTPUT (per ogni slide):
---SLIDE X---
TITOLO: [titolo della slide]
CORPO: [contenuto principale]
BULLET: [punto 1] | [punto 2] | [punto 3]
VISUAL: [descrizione visiva suggerita]
---

Genera tutte le {config.num_slides} slide:"""

    def _parse_carousel_structure(self, structure: str, num_slides: int) -> List[Dict[str, Any]]:
        """Parse carousel structure text into slide data."""
        slides = []

        # Split by slide markers
        slide_sections = structure.split("---SLIDE")

        for i, section in enumerate(slide_sections[1:num_slides + 1], 1):  # Skip first empty split
            slide_data = {
                "title": "",
                "body": "",
                "bullets": [],
                "visual": "",
            }

            lines = section.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("TITOLO:"):
                    slide_data["title"] = line.replace("TITOLO:", "").strip()
                elif line.startswith("CORPO:"):
                    slide_data["body"] = line.replace("CORPO:", "").strip()
                elif line.startswith("BULLET:"):
                    bullets = line.replace("BULLET:", "").strip()
                    slide_data["bullets"] = [b.strip() for b in bullets.split("|") if b.strip()]
                elif line.startswith("VISUAL:"):
                    slide_data["visual"] = line.replace("VISUAL:", "").strip()

            slides.append(slide_data)

        # Ensure we have the right number of slides
        while len(slides) < num_slides:
            slides.append({
                "title": f"Slide {len(slides) + 1}",
                "body": "",
                "bullets": [],
                "visual": "",
            })

        return slides[:num_slides]

    def _build_carousel_image_prompt(
        self, 
        config: CarouselConfig, 
        slide_num: int, 
        slide_type: str, 
        slide_data: Dict[str, Any], 
        dims: Dict[str, int],
        visual_thread: str
    ) -> str:
        """Build consistent prompt for carousel slide."""
        # Build image prompt
        dimensions = f"{dims['width']}x{dims['height']}"

        image_prompt = f"""
Carousel slide {slide_num}/{config.num_slides}
Series Context: {visual_thread}
Tipo: {slide_type}
Titolo: {slide_data.get('title', '')}
Contenuto: {slide_data.get('body', '')[:100]}
Formato: {config.format} ({dimensions})
Stile: Premium, professionale, brand StudioCentOS
Colori: Sfondo nero/grigio scuro, accenti oro #D4AF37, testo bianco
Tipografia: Sans-serif moderna, bold per titoli
Layout: Pulito, spazio per testo, numerazione visibile
NO: Troppo testo, immagini stock, colori freddi
"""
        return image_prompt

    async def _generate_carousel_caption(
        self, config: CarouselConfig, slides: List[Dict[str, Any]]
    ) -> str:
        """Generate caption for the carousel post."""
        brand_prompt = get_brand_dna_prompt()
        platform_rules = PLATFORM_FORMAT_RULES.get(config.platform.value.lower(), {})

        prompt = f"""{brand_prompt}

{platform_rules.get("prompt", "")}

TASK: Genera la CAPTION per questo carousel

ARGOMENTO: {config.topic}
NUMERO SLIDE: {len(slides)}
TONO: {config.tone.value}

SLIDE CONTENUTI:
{chr(10).join([f"- Slide {i+1}: {s.get('title', '')}" for i, s in enumerate(slides)])}

REQUISITI:
- HOOK iniziale che invita a scorrere
- Valore aggiunto rispetto alle slide
- CTA: "{config.cta}"
- Hashtag brand: {" ".join(BRAND_DNA["hashtags"]["brand"][:3])}

GENERA LA CAPTION:"""

        caption = await self._generate_content(prompt, config.brand_context)
        return caption

    def _format_carousel_content(self, slides: List[Dict[str, Any]], caption: str) -> str:
        """Format carousel slides and caption into complete content."""
        formatted = "📸 INSTAGRAM CAROUSEL\n" + "=" * 40 + "\n\n"

        formatted += "SLIDES:\n\n"
        for slide in slides:
            formatted += f"[SLIDE {slide['slide_num']}] {slide['type'].upper()}\n"
            formatted += f"Titolo: {slide.get('title', '')}\n"
            formatted += f"Contenuto: {slide.get('content', slide.get('body', ''))}\n"
            if slide.get('bullets'):
                formatted += "Punti:\n"
                for bullet in slide['bullets']:
                    formatted += f"  • {bullet}\n"
            formatted += "\n"

        formatted += "=" * 40 + "\n"
        formatted += "CAPTION:\n\n"
        formatted += caption

        return formatted

    def _build_reel_prompt(
        self, config: ReelConfig, post_template: str, hook_end: int, solution_end: int
    ) -> str:
        """Build prompt for reel video script."""
        brand_prompt = get_brand_dna_prompt()

        return f"""{brand_prompt}

{post_template}

TASK: Crea lo SCRIPT VIDEO per un Reel {config.platform.value.upper()}

ARGOMENTO: {config.topic}
DURATA: {config.duration_seconds} secondi
STILE: {config.style}
TONO: {config.tone.value}
MUSICA: {config.music_mood}
{"HOOK PERSONALIZZATO: " + config.hook if config.hook else ""}

STRUTTURA TEMPORALE:
⏱️ 0-3 sec: HOOK - Ferma lo scroll IMMEDIATAMENTE
⏱️ 3-{hook_end} sec: PROBLEMA/CURIOSITÀ - Crea tensione
⏱️ {hook_end}-{solution_end} sec: SOLUZIONE/CONTENUTO - Valore principale
⏱️ {solution_end}-{config.duration_seconds} sec: CTA - "{config.cta}"

FORMATO OUTPUT (per ogni scena):
[XX:XX-XX:XX] NOME_SCENA
🎬 Visual: [cosa si vede]
🎤 Narrazione: "[testo esatto da dire]"
✏️ Testo on-screen: [testo che appare]
🎵 Audio: [indicazioni musica/effetti]
🎞️ Transizione: [tipo transizione]
---

GENERA LO SCRIPT COMPLETO:"""

    def _parse_reel_scenes(self, script: str, duration: int) -> List[Dict[str, Any]]:
        """Parse reel script into individual scenes."""
        scenes = []

        # Split by scene markers
        scene_sections = script.split("[")

        for section in scene_sections[1:]:  # Skip first empty split
            if "]" not in section:
                continue

            scene_data = {
                "timestamp": "",
                "name": "",
                "visual": "",
                "narration": "",
                "text_overlay": "",
                "audio": "",
                "transition": "",
            }

            # Extract timestamp and name
            header_end = section.find("]")
            if header_end > 0:
                header = section[:header_end]
                parts = header.split(" ", 1)
                scene_data["timestamp"] = parts[0] if parts else ""
                scene_data["name"] = parts[1].strip() if len(parts) > 1 else ""

            # Parse body
            body = section[header_end + 1:].strip()
            lines = body.split("\n")

            for line in lines:
                line = line.strip()
                if line.startswith("🎬 Visual:"):
                    scene_data["visual"] = line.replace("🎬 Visual:", "").strip()
                elif line.startswith("🎤 Narrazione:"):
                    scene_data["narration"] = line.replace("🎤 Narrazione:", "").strip().strip('"')
                elif line.startswith("✏️ Testo on-screen:"):
                    scene_data["text_overlay"] = line.replace("✏️ Testo on-screen:", "").strip()
                elif line.startswith("🎵 Audio:"):
                    scene_data["audio"] = line.replace("🎵 Audio:", "").strip()
                elif line.startswith("🎞️ Transizione:"):
                    scene_data["transition"] = line.replace("🎞️ Transizione:", "").strip()

            if scene_data["timestamp"] or scene_data["narration"]:
                scenes.append(scene_data)

        return scenes

    async def _generate_reel_video(
        self, config: ReelConfig, scenes: List[Dict[str, Any]]
    ) -> Optional[VisualGenerationResult]:
        """Generate video for reel using Veo."""
        if not self.video_generator:
            return None

        try:
            from app.domain.marketing.video_generator_agent import VideoGenerationConfig, VideoAspectRatio
            
            # Build prompt
            scenes_text = "\n".join([
                 f"Scene {i+1}: {s.get('visual', '')} - {s.get('narration', '')[:50]}"
                 for i, s in enumerate(scenes[:5])
            ])
             
            video_prompt = VISUAL_GENERATION_PROMPTS["veo_31"]["reel"].format(
                base_prompt=config.topic,
                duration=config.duration_seconds,
                style=config.style,
                music_mood=config.music_mood,
                scenes=scenes_text,
            )

            result = await self.video_generator.generate_video(
                VideoGenerationConfig(
                    prompt=video_prompt[:500], # Veo prompt length limit safety
                    duration_seconds=min(config.duration_seconds, 60),
                    aspect_ratio=VideoAspectRatio.PORTRAIT, # Reel is 9:16
                    style=config.style
                )
            )
            return result
            
        except Exception as e:
            logger.warning(f"Reel video generation failed: {e}")
            return None

    async def _generate_reel_thumbnail(
        self, config: ReelConfig, first_scene: Dict[str, Any]
    ) -> Optional[VisualGenerationResult]:
        """Generate thumbnail for reel using NanoBananaPRO."""
        import time
        start_time = time.time()

        try:
            thumbnail_prompt = f"""
Reel thumbnail per {config.topic}
Visual hook: {first_scene.get('visual', config.topic)}
Formato: 9:16 vertical (1080x1920)
Stile: Accattivante, CTR-optimized
Elementi: Volto espressivo (se possibile), testo grande, colori vivaci
Testo overlay: Max 3 parole bold
Colori: Brand StudioCentOS - Oro #D4AF37 accenti
Mood: Curioso, urgente, click-worthy
NO: Troppo testo, immagini generiche
"""

            return VisualGenerationResult(
                prompt_used=thumbnail_prompt,
                model_used="nano-banana-pro-preview",
                generation_time=time.time() - start_time,
                metadata={
                    "type": "thumbnail",
                    "status": "prompt_ready",
                }
            )

        except Exception as e:
            logger.warning(f"Reel thumbnail generation failed: {e}")
            return None

    async def _generate_reel_caption(self, config: ReelConfig, script: str) -> str:
        """Generate caption for the reel."""
        brand_prompt = get_brand_dna_prompt()
        platform_rules = PLATFORM_FORMAT_RULES.get(config.platform.value.lower(), {})

        prompt = f"""{brand_prompt}

TASK: Genera la CAPTION per questo Reel

ARGOMENTO: {config.topic}
SCRIPT RIASSUNTO: {script[:300]}...
TONO: {config.tone.value}

REQUISITI:
- Max 150 caratteri (TikTok) o 2200 (Instagram)
- HOOK iniziale
- CTA: "{config.cta}"
- Hashtag trending + brand

GENERA LA CAPTION:"""

        caption = await self._generate_content(prompt, config.brand_context)
        return caption

    def _format_reel_content(
        self, script: str, caption: str, scenes: List[Dict[str, Any]]
    ) -> str:
        """Format reel script, caption, and scenes into complete content."""
        formatted = "🎬 REEL VIDEO CONTENT\n" + "=" * 40 + "\n\n"

        formatted += "SCRIPT:\n\n"
        formatted += script

        formatted += "\n\n" + "=" * 40 + "\n"
        formatted += "SCENE BREAKDOWN:\n\n"

        for i, scene in enumerate(scenes, 1):
            formatted += f"[SCENE {i}] {scene.get('timestamp', '')}\n"
            formatted += f"Visual: {scene.get('visual', '')}\n"
            formatted += f"Narrazione: \"{scene.get('narration', '')}\"\n"
            formatted += f"Testo: {scene.get('text_overlay', '')}\n"
            formatted += "\n"

        formatted += "=" * 40 + "\n"
        formatted += "CAPTION:\n\n"
        formatted += caption

        return formatted

    # ========================================================================
    # HELPER METHODS (Private)
    # ========================================================================

    def _build_blog_prompt(self, config: BlogPostConfig) -> str:
        """Build prompt for blog post generation with Brand DNA."""
        brand_prompt = get_brand_dna_prompt()
        post_type = getattr(config, 'post_type', 'educational')
        post_structure = POST_TYPE_PROMPTS.get(post_type, POST_TYPE_PROMPTS.get('educational', ''))

        return f"""{brand_prompt}

{post_structure}

TASK: Scrivi un articolo blog su: {config.topic}

REQUISITI:
- Lunghezza: circa {config.length} parole
- Tono: {config.tone.value}
- Keywords da includere: {', '.join(config.keywords)}
- Target audience: {config.target_audience or BRAND_DNA["target"]["primary"]}
- Includi titoli e sottotitoli (H2, H3)
- Struttura: Introduzione → Sviluppo (3-5 sezioni) → Conclusione con CTA
- Rendi il contenuto pratico e actionable
{f"- Call-to-action finale: {config.call_to_action}" if config.call_to_action else "- Includi una CTA per contattare StudioCentOS"}

FORMATO OUTPUT:
# [Titolo SEO-friendly]

[Introduzione accattivante - 100 parole]

## [Sezione 1]
[Contenuto]

## [Sezione 2]
[Contenuto]

...

## Conclusione
[CTA finale]
"""

    def _build_social_prompt(
        self, config: SocialPostConfig, max_length: int
    ) -> str:
        """Build prompt for social post generation with Brand DNA, few-shot examples, and platform rules."""
        brand_prompt = get_brand_dna_prompt()
        platform_key = config.platform.value.lower()
        platform_rules = PLATFORM_FORMAT_RULES.get(platform_key, PLATFORM_FORMAT_RULES["instagram"])
        platform_prompt = platform_rules.get("prompt", "")

        # Get post type structure if available
        post_type = getattr(config, 'post_type', None)
        post_structure = ""
        if post_type and post_type in POST_TYPE_PROMPTS:
            post_structure = POST_TYPE_PROMPTS[post_type]

        # Platform-specific hashtags
        hashtag_limit = platform_rules.get("max_hashtags", 5)
        brand_hashtags = " ".join(BRAND_DNA["hashtags"]["brand"][:3])

        # === FEW-SHOT LEARNING ===
        # Aggiungi esempi reali per guidare la generazione
        few_shot_section = ""
        if hasattr(self, 'content_enhancer') and self.content_enhancer:
            few_shot_prompt = self.content_enhancer.build_few_shot_prompt(
                post_type=post_type or "educational",
                platform=platform_key,
                topic=config.message,
            )
            if few_shot_prompt:
                few_shot_section = f"\n{few_shot_prompt}\n"

            # Get random hook template for creativity
            random_hook = self.content_enhancer.get_random_hook(post_type or "educational")
            hook_guidance = f"\nHOOK TEMPLATE SUGGERITO (adatta al contesto): \"{random_hook}\"\n"
        else:
            hook_guidance = ""

        # === STYLE VARIATION ===
        style_guidance = ""
        if post_type in ["lancio_prodotto", "offerta_speciale"]:
            style_guidance = "\nSTILE: Urgente ma onesto, focus su benefici concreti con numeri reali.\n"
        elif post_type in ["caso_successo", "testimonial"]:
            style_guidance = "\nSTILE: Narrativo, racconta una storia vera con numeri e citazioni.\n"
        elif post_type in ["tip_giorno", "educational"]:
            style_guidance = "\nSTILE: Didattico, strutturato, pratico e actionable.\n"
        elif post_type == "engagement":
            style_guidance = "\nSTILE: Conversazionale, curioso, invita alla discussione.\n"

        return f"""{brand_prompt}

PIATTAFORMA: {config.platform.value.upper()}
{platform_prompt}
{style_guidance}
{post_structure}
{few_shot_section}
{hook_guidance}

TASK: Crea un post social ECCEZIONALE per {config.platform.value} sul seguente argomento:
"{config.message}"

REQUISITI CREATIVITÀ (IMPORTANTE):
- Sii SPECIFICO: usa numeri, percentuali, tempi concreti (es. "in 30 giorni", "-40%", "2 ore/giorno")
- Sii ORIGINALE: evita frasi generiche come "nell'era digitale", "al giorno d'oggi"
- Sii CONCRETO: descrivi situazioni reali, non astratte
- HOOK POTENTE: la prima riga DEVE fermare lo scroll
- VALORE IMMEDIATO: ogni frase deve aggiungere qualcosa

REQUISITI TECNICI:
- Lunghezza massima: {max_length} caratteri
- Tono: {config.tone.value}
- {"Includi emoji appropriati alla piattaforma" if config.include_emojis else "NON usare emoji"}
- {"Includi hashtag rilevanti (max " + str(hashtag_limit) + ")" if config.include_hashtags else "NON includere hashtag"}
{f"- Link/CTA: {config.call_to_action}" if config.call_to_action else ""}

STRUTTURA POST (OBBLIGATORIA):
1. HOOK - Prima riga che cattura l'attenzione (domanda, statistica shock, o affermazione provocatoria)
2. BODY - Contenuto di valore con DATI CONCRETI
3. CTA - Call-to-action chiara e specifica
4. HASHTAG - {brand_hashtags} + hashtag specifici al topic

GENERA UN POST DI ALTISSIMA QUALITÀ:"""

    def _build_ad_prompt(self, config: AdCopyConfig) -> str:
        """Build prompt for ad copy generation with Brand DNA."""
        brand_prompt = get_brand_dna_prompt()

        return f"""{brand_prompt}

TIPO: COPY PUBBLICITARIO

TASK: Scrivi copy pubblicitario per: {config.product}

DETTAGLI:
- Value proposition: {config.value_proposition}
- Target audience: {config.target_audience}
- Tono: {config.tone.value}
- Piattaforma: {config.platform}
- Lunghezza massima: {config.max_length} caratteri
- {"Includi CTA forte e persuasiva" if config.include_cta else ""}

STRUTTURA AD COPY:
1. HEADLINE - Cattura attenzione immediata
2. BODY - Beneficio principale + urgenza
3. CTA - Azione chiara e diretta

REGOLE:
- Focus su benefici, non feature
- Usa numeri specifici quando possibile
- Crea urgenza senza essere ingannevole
- Parla direttamente al target

GENERA IL COPY:"""

    def _build_video_prompt(self, config: VideoScriptConfig) -> str:
        """Build prompt for video script generation with Brand DNA."""
        brand_prompt = get_brand_dna_prompt()

        # Determine video format based on duration
        if config.duration_seconds <= 30:
            format_guide = """
FORMATO: Reel/TikTok 30 secondi
⏱️ 0-3 sec: HOOK (testo a schermo + voce) - Cattura IMMEDIATA
⏱️ 3-15 sec: PROBLEMA + AGITAZIONE
⏱️ 15-25 sec: SOLUZIONE + BENEFICI
⏱️ 25-30 sec: CTA + FOLLOW
"""
        elif config.duration_seconds <= 60:
            format_guide = """
FORMATO: Reel/Short 60 secondi
⏱️ 0-5 sec: HOOK (pattern interrupt) - Ferma lo scroll!
⏱️ 5-20 sec: PROBLEMA (storytelling)
⏱️ 20-40 sec: SOLUZIONE (step by step o demo)
⏱️ 40-55 sec: RISULTATI (numeri, prove)
⏱️ 55-60 sec: CTA
"""
        elif config.duration_seconds <= 120:
            format_guide = """
FORMATO: Tutorial/Video 2 minuti
⏱️ 0-10 sec: HOOK + cosa impareranno
⏱️ 10-30 sec: Contesto e perché è importante
⏱️ 30-90 sec: STEP BY STEP (3-5 step)
⏱️ 90-110 sec: RISULTATO FINALE
⏱️ 110-120 sec: CTA + BONUS TIP
"""
        else:
            format_guide = f"""
FORMATO: Video lungo ({config.duration_seconds} secondi)
STRUTTURA:
- INTRO (10%): Hook + presentazione argomento
- SVILUPPO (70%): Contenuto principale in sezioni
- CONCLUSIONE (15%): Recap + risultati
- CTA (5%): Call-to-action finale
"""

        return f"""{brand_prompt}

TIPO: SCRIPT VIDEO

{format_guide}

TASK: Scrivi uno script video su: {config.topic}

DETTAGLI:
- Durata: {config.duration_seconds} secondi
- Tono: {config.tone.value}
- Formato: {config.format}
- {"HOOK obbligatorio nei primi 3 secondi" if config.include_hook else ""}
- {"CTA finale obbligatoria" if config.include_cta else ""}

STILE STUDIOCENTOS:
- Colori brand: Oro #D4AF37, Nero #0A0A0A
- Sottotitoli sempre visibili
- Logo in chiusura
- Tono: professionale ma accessibile

FORMATO OUTPUT:
[TIMESTAMP] TIPO SCENA
Visual: [descrizione di cosa si vede]
Audio: [musica/effetti se presenti]
Narrazione: "testo esatto da dire"
Testo on-screen: [testo che appare]

---

GENERA LO SCRIPT COMPLETO:"""

    
    async def generate_monthly_plan(self, config: CalendarConfig) -> CalendarResult:
        """
        Generate a strategic content plan for a month (Just-in-Time architecture).
        Does NOT generate full assets, only the topic/angle roadmap.
        """
        logger.info(f"Generating content plan for {config.month} {config.year} ({config.industry})")
        
        prompt = f"""
        Act as a Senior Social Media Strategist. 
        Create a detailed Content Calendar Plan for: {config.industry}
        
        CONTEXT:
        - Month: {config.month} {config.year}
        - Goal: {config.goal}
        - Frequency: {config.posts_per_week} posts/week
        - Target Audience: {config.target_audience or 'General'}
        
        INSTRUCTIONS:
        1. Define a strategy that mixes educational, engaging, and promotional content.
        2. For each post, define the core TOPIC and the specific ANGLE (Hook).
        3. Do NOT write the full caption. Just the plan.
        4. Use a mix of formats: Reel, Carousel, Static Image.
        
        OUTPUT FORMAT (Strict JSON list of objects):
        {{
            "strategy_summary": "Brief explanation of the strategy...",
            "plan": [
                {{
                    "date": "YYYY-MM-DD",
                    "topic": "Topic Name",
                    "angle": "Specific hook or angle to take",
                    "format": "reel/carousel/static",
                    "platform": "instagram", 
                    "notes": "Visual idea or strategic note"
                }}
            ]
        }}
        """
        
        response_json = await self._generate_content(prompt, brand_context=config.brand_context, use_rag=False)
        
        try:
            # Parse JSON from response
            import json
            # Sanitize minimal markdown if present
            clean_json = response_json.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            planned_posts = [PlannedPost(**p) for p in data.get("plan", [])]
            
            return CalendarResult(
                month=config.month,
                year=config.year,
                plan=planned_posts,
                strategy_summary=data.get("strategy_summary", "Plan generated by AI.")
            )
            
        except Exception as e:
            logger.error(f"Failed to parse calendar plan: {e}")
            # Fallback empty plan
            return CalendarResult(month=config.month, year=config.year, plan=[], strategy_summary="Error generating plan.")



    async def generate_storyboard(self, config: StoryboardConfig) -> StoryboardResult:
        """
        Generate a visual storyboard from a video script.
        Outputs scene-by-scene breakdown with visual descriptions and camera notes.
        """
        logger.info(f"Generating storyboard from script (style={config.style})")
        
        prompt = f"""
        You are a professional Video Director.
        Convert the following video script into a detailed STORYBOARD.
        
        SCRIPT:
        ---
        {config.script}
        ---
        
        For EACH scene/section, define:
        1. Scene Number
        2. Visual Description (what camera sees)
        3. Voiceover Text (exact words narrated)
        4. Suggested Duration (seconds)
        5. Camera Angle (wide, close-up, POV, etc.)
        6. Notes (transitions, mood, text overlays)
        
        OUTPUT FORMAT (Strict JSON list):
        {{
            "frames": [
                {{
                    "scene_number": 1,
                    "visual_description": "...",
                    "voiceover_text": "...",
                    "duration": 5,
                    "camera_angle": "...",
                    "notes": "..."
                }}
            ],
            "total_duration": 60,
            "summary": "Brief overview of the video"
        }}
        """
        
        response_json = await self._generate_content(prompt, brand_context=config.brand_context, use_rag=False)
        
        try:
            import json
            clean_json = response_json.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            frames = [StoryboardFrame(**f) for f in data.get("frames", [])]
            
            return StoryboardResult(
                frames=frames,
                total_duration=data.get("total_duration", sum(f.duration for f in frames)),
                summary=data.get("summary", "Storyboard generated.")
            )
        except Exception as e:
            logger.error(f"Failed to parse storyboard: {e}")
            return StoryboardResult(frames=[], total_duration=0, summary="Error generating storyboard.")

    async def _generate_content(
        self,
        prompt: str,
        brand_context: Optional[str] = None,
        use_rag: bool = True
    ) -> str:
        """
        Generate content using LLM with RAG context enrichment and Brand DNA.

        Uses Custom StudioCentOS model by default, falls back to GROQ if disabled.
        Enriches with RAG knowledge base context when available.
        Always includes Brand DNA for consistent voice.
        """
        from app.core.config import settings

        # Check if custom model is enabled
        if settings.USE_CUSTOM_MODEL:
            try:
                from app.domain.marketing.custom_model_service import custom_model_service

                logger.info("Using custom StudioCentOS model for generation")

                # Build system message with Brand DNA
                system_message = f"""Sei l'AI Content Creator di {BRAND_DNA["identity"]["name"]}, software house italiana specializzata in AI per PMI.

TONE OF VOICE:
- {BRAND_DNA["voice"]["primary"]}
- {BRAND_DNA["voice"]["style"]}
- {BRAND_DNA["voice"]["approach"]}

REGOLE FONDAMENTALI:
1. Scrivi SEMPRE in italiano corretto
2. Usa la struttura HOOK → BODY → CTA → HASHTAG
3. Parla di benefici, non solo feature
4. Usa numeri e dati concreti
5. Evita: {", ".join(BRAND_DNA["avoid_words"])}
6. Target: {BRAND_DNA["target"]["primary"]}

Genera contenuti professionali, coinvolgenti e ottimizzati.
Usa formattazione markdown quando appropriato."""

                # Fetch RAG context if enabled
                rag_context = ""
                if use_rag:
                    try:
                        from app.domain.rag.service import rag_service
                        rag_context = await rag_service.get_context(
                            query=prompt[:500],
                            max_tokens=1500
                        )
                        if rag_context:
                            rag_context = f"\n\n## Knowledge Base Aziendale:\n{rag_context}"
                    except Exception as rag_error:
                        logger.warning(f"RAG context fetch failed: {rag_error}")

                # Add contexts to system message
                if brand_context:
                    system_message = f"{system_message}\n\n## Brand Context Aggiuntivo:\n{brand_context}"
                if rag_context:
                    system_message = f"{system_message}{rag_context}"

                # Generate with custom model
                content = custom_model_service.generate(
                    prompt=prompt,
                    system_message=system_message,
                    max_new_tokens=2000,
                    temperature=0.8
                )

                return content.strip()

            except Exception as e:
                logger.warning(f"Custom model generation failed, falling back to Ollama: {e}")
                # Fall through to Ollama fallback

        # === OLLAMA PRIMARY (FREE, LOCAL, NO RATE LIMITS) ===
        try:
            from app.core.llm.ollama_client import get_ollama_client

            logger.info("Using Ollama (PRIMARY) for content generation")
            client = get_ollama_client()
            
            # Check availability
            if await client.is_available():
                # Base system prompt with Brand DNA
                base_system_prompt = f"""Sei l'AI Content Creator di {BRAND_DNA["identity"]["name"]}, software house italiana specializzata in AI per PMI.

TONE OF VOICE:
- {BRAND_DNA["voice"]["primary"]}
- {BRAND_DNA["voice"]["style"]}
- {BRAND_DNA["voice"]["approach"]}

REGOLE FONDAMENTALI:
1. Scrivi SEMPRE in italiano corretto
2. Usa la struttura HOOK → BODY → CTA → HASHTAG
3. Parla di benefici, non solo feature
4. Usa numeri e dati concreti
5. Evita: {", ".join(BRAND_DNA["avoid_words"])}
6. Target: {BRAND_DNA["target"]["primary"]}

Genera contenuti professionali, coinvolgenti e ottimizzati.
Usa formattazione markdown quando appropriato."""

                # Fetch RAG context if enabled
                rag_context = ""
                if use_rag:
                    try:
                        from app.domain.rag.service import rag_service
                        rag_context = await rag_service.get_context(
                            query=prompt[:500],
                            max_tokens=1500
                        )
                        if rag_context:
                            rag_context = f"\n\n## Knowledge Base Aziendale:\n{rag_context}"
                    except Exception as rag_error:
                        logger.warning(f"RAG context fetch failed: {rag_error}")

                # Build system prompt with contexts
                system_prompt = base_system_prompt
                if brand_context:
                    system_prompt = f"{base_system_prompt}\n\n## Brand Context Aggiuntivo:\n{brand_context}"
                if rag_context:
                    system_prompt = f"{system_prompt}{rag_context}"

                content = await client.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    temperature=0.8,
                    max_tokens=2000
                )

                logger.info("✅ Content generated via Ollama (PRIMARY)")
                return content.strip()
            else:
                logger.warning("Ollama not available, falling back to GROQ")

        except Exception as ollama_e:
            logger.warning(f"Ollama failed, trying GROQ fallback: {ollama_e}")

        # === GROQ FALLBACK (CLOUD) ===
        try:
            from app.core.llm.groq_client import get_groq_client

            logger.info("Using GROQ (FALLBACK) for content generation")
            client = get_groq_client(model="llama-3.3-70b")

            # Base system prompt with Brand DNA
            base_system_prompt = f"""Sei l'AI Content Creator di {BRAND_DNA["identity"]["name"]}, software house italiana specializzata in AI per PMI.

TONE OF VOICE:
- {BRAND_DNA["voice"]["primary"]}
- {BRAND_DNA["voice"]["style"]}
- {BRAND_DNA["voice"]["approach"]}

REGOLE FONDAMENTALI:
1. Scrivi SEMPRE in italiano corretto
2. Usa la struttura HOOK → BODY → CTA → HASHTAG
3. Parla di benefici, non solo feature
4. Usa numeri e dati concreti
5. Evita: {", ".join(BRAND_DNA["avoid_words"])}
6. Target: {BRAND_DNA["target"]["primary"]}

Genera contenuti professionali, coinvolgenti e ottimizzati.
Usa formattazione markdown quando appropriato."""

            # Fetch RAG context if enabled
            rag_context = ""
            if use_rag:
                try:
                    from app.domain.rag.service import rag_service
                    rag_context = await rag_service.get_context(
                        query=prompt[:500],
                        max_tokens=1500
                    )
                    if rag_context:
                        rag_context = f"\n\n## Knowledge Base Aziendale:\n{rag_context}"
                except Exception as rag_error:
                    import logging
                    logging.getLogger(__name__).warning(f"RAG context fetch failed: {rag_error}")

            # Build system prompt with contexts
            system_prompt = base_system_prompt
            if brand_context:
                system_prompt = f"{base_system_prompt}\n\n## Brand Context Aggiuntivo:\n{brand_context}"
            if rag_context:
                system_prompt = f"{system_prompt}{rag_context}"

            content = await client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.8,
                max_tokens=2000
            )

            logger.info("✅ Content generated via GROQ (FALLBACK)")
            return content.strip()

        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"All LLM providers failed: {e}")
            return f"[Errore generazione contenuto. Riprova più tardi.]"

    async def _optimize_seo(
        self, content: str, keywords: List[str]
    ) -> str:
        """Optimize content for SEO."""
        if not keywords:
            return content

        import re
        optimized = content

        # Ensure keywords appear in content
        content_lower = optimized.lower()
        for keyword in keywords[:5]:  # Focus on top 5 keywords
            keyword_lower = keyword.lower()
            keyword_count = content_lower.count(keyword_lower)

            # If keyword appears less than 2 times, suggest more natural inclusion
            if keyword_count < 2:
                # Add keyword to first paragraph if missing
                paragraphs = optimized.split('\n\n')
                if paragraphs and keyword_lower not in paragraphs[0].lower():
                    # Find a sentence to enhance
                    sentences = paragraphs[0].split('. ')
                    if len(sentences) > 1:
                        # Enhance second sentence with keyword reference
                        sentences[1] = f"Quando parliamo di {keyword}, " + sentences[1][0].lower() + sentences[1][1:]
                        paragraphs[0] = '. '.join(sentences)
                        optimized = '\n\n'.join(paragraphs)

        # Ensure headings use keywords
        lines = optimized.split('\n')
        heading_count = 0
        for i, line in enumerate(lines):
            if line.startswith('#'):
                heading_count += 1
                # Check if any keyword is in heading
                if heading_count <= len(keywords):
                    keyword = keywords[min(heading_count - 1, len(keywords) - 1)]
                    if keyword.lower() not in line.lower():
                        # Try to naturally include keyword
                        if ': ' in line:
                            parts = line.split(': ')
                            if len(parts) == 2:
                                lines[i] = f"{parts[0]}: {keyword} - {parts[1]}"

        optimized = '\n'.join(lines)

        return optimized

    def _calculate_seo_score(
        self, content: str, keywords: List[str]
    ) -> float:
        """Calculate SEO quality score (0-100)."""
        import re
        score = 0.0
        max_score = 100.0

        content_lower = content.lower()
        word_count = len(content.split())

        # 1. Content length (max 20 points)
        if word_count >= 300:
            score += 10
        if word_count >= 600:
            score += 5
        if word_count >= 1000:
            score += 5

        # 2. Keyword presence and density (max 30 points)
        if keywords:
            keyword_scores = []
            for keyword in keywords[:5]:
                keyword_lower = keyword.lower()
                count = content_lower.count(keyword_lower)
                density = (count * len(keyword.split())) / max(1, word_count) * 100

                # Optimal density is 1-3%
                if 1.0 <= density <= 3.0:
                    keyword_scores.append(6)
                elif 0.5 <= density < 1.0 or 3.0 < density <= 4.0:
                    keyword_scores.append(4)
                elif count > 0:
                    keyword_scores.append(2)
                else:
                    keyword_scores.append(0)

            score += sum(keyword_scores[:5])
        else:
            score += 15  # No keywords to optimize for

        # 3. Heading structure (max 20 points)
        headings = re.findall(r'^#+\s+.+$', content, re.MULTILINE)
        if len(headings) >= 1:
            score += 5
        if len(headings) >= 3:
            score += 5
        if len(headings) >= 5:
            score += 5

        # Check heading hierarchy
        h1_count = len(re.findall(r'^#\s+', content, re.MULTILINE))
        h2_count = len(re.findall(r'^##\s+', content, re.MULTILINE))
        if h1_count == 1 and h2_count >= 2:
            score += 5

        # 4. Paragraph structure (max 10 points)
        paragraphs = [p for p in content.split('\n\n') if p.strip() and not p.startswith('#')]
        avg_para_length = sum(len(p.split()) for p in paragraphs) / max(1, len(paragraphs))
        if 50 <= avg_para_length <= 150:
            score += 10
        elif 30 <= avg_para_length <= 200:
            score += 5

        # 5. Internal linking potential (max 10 points)
        if '[' in content and '](' in content:
            score += 10
        elif '[' in content:
            score += 5

        # 6. Meta elements (max 10 points)
        if content.startswith('#'):
            score += 5  # Has title
        first_para = content.split('\n\n')[0] if '\n\n' in content else content[:200]
        if 50 <= len(first_para) <= 160:
            score += 5  # Good meta description length

        return min(score, max_score)

    async def _check_brand_compliance(self, content: str) -> bool:
        """Check if content complies with Brand DNA guidelines."""
        content_lower = content.lower()

        # Check for forbidden words
        for word in BRAND_DNA["avoid_words"]:
            if word.lower() in content_lower:
                import logging
                logging.getLogger(__name__).warning(f"Brand compliance: found forbidden word '{word}'")
                return False

        # Check for excessive anglicisms (basic check)
        anglicisms = ["disruptive", "cutting-edge", "best-in-class", "synergy", "leverage", "pivot"]
        for word in anglicisms:
            if word in content_lower:
                import logging
                logging.getLogger(__name__).warning(f"Brand compliance: found anglicism '{word}'")
                return False

        return True

    async def _add_hashtags(
        self, content: str, platform: SocialPlatform
    ) -> str:
        """Add relevant hashtags to social post using GROQ LLM with Brand DNA."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.1-8b")

            # Get platform-specific limits
            platform_key = platform.value.lower()
            platform_rules = PLATFORM_FORMAT_RULES.get(platform_key, {})
            limit = platform_rules.get("max_hashtags", 5)

            # Brand hashtags to always include
            brand_hashtags = BRAND_DNA["hashtags"]["brand"][:2]  # First 2 brand hashtags
            remaining_limit = limit - len(brand_hashtags)

            prompt = f"""Genera {remaining_limit} hashtag italiani rilevanti per questo contenuto social.

Contenuto: {content[:500]}
Piattaforma: {platform.value}
Settore: Software, AI, PMI, Digitalizzazione

REGOLE:
- Hashtag in italiano quando possibile
- Mix di popolari e nicchia
- Rilevanti al contenuto
- NO hashtag generici come #love #instagood

Rispondi SOLO con gli hashtag separati da spazio (es: #tech #marketing #business):"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=100
            )

            generated_hashtags = response.strip()

            # Combine brand + generated hashtags
            all_hashtags = " ".join(brand_hashtags) + " " + generated_hashtags

            return f"{content}\n\n{all_hashtags}"

        except Exception:
            # Fallback to brand hashtags only
            brand_tags = " ".join(BRAND_DNA["hashtags"]["brand"][:3])
            return f"{content}\n\n{brand_tags}"

    async def _add_cta(self, content: str) -> str:
        """Add call-to-action to content using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.1-8b")

            prompt = f"""Genera una call-to-action breve e persuasiva per questo contenuto pubblicitario.

Contenuto: {content[:500]}

CTA (max 15 parole, in italiano, deve essere urgente e motivante):"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.8,
                max_tokens=50
            )

            cta = response.strip()
            return f"{content}\n\n{cta}"

        except Exception:
            return content + "\n\n👉 Contattaci oggi per saperne di più!"

    async def _format_video_script(
        self, content: str, duration: int
    ) -> str:
        """Format content as video script with timestamps using GROQ LLM."""
        try:
            from app.core.llm.groq_client import get_groq_client

            client = get_groq_client(model="llama-3.3-70b")

            prompt = f"""Formatta questo contenuto come script video professionale.

Contenuto: {content}
Durata target: {duration} secondi

Formato richiesto:
[00:00-00:03] HOOK - descrizione scena
Narrazione: "testo da leggere"

[00:04-00:XX] SVILUPPO - descrizione scena
Narrazione: "testo"

[ultimi secondi] CTA - descrizione scena
Narrazione: "testo finale"

Script formattato:"""

            response = await client.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=1500
            )

            return response.strip()

        except Exception:
            return content

