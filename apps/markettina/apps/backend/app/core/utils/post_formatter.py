"""
📝 POST FORMATTER - Backend Formatting Utilities

Garantisce formattazione corretta del testo per ogni piattaforma social.

Problemi risolti:
- Line breaks non consistenti
- Hashtag mal posizionati
- Caratteri speciali problematici
- Emoji non bilanciate
- Limiti caratteri non rispettati
"""

import re
import unicodedata
from typing import Optional
from dataclasses import dataclass


@dataclass
class PlatformConfig:
    """Configurazione specifica per piattaforma."""
    id: str
    max_chars: int
    hashtag_position: str  # "inline", "bottom", "first_comment"
    emoji_style: str  # "rich", "minimal", "none"
    line_break_style: str  # "double", "single", "none"
    max_hashtags: int


PLATFORM_CONFIGS: dict[str, PlatformConfig] = {
    "instagram": PlatformConfig(
        id="instagram",
        max_chars=2200,
        hashtag_position="bottom",
        emoji_style="rich",
        line_break_style="double",
        max_hashtags=30
    ),
    "facebook": PlatformConfig(
        id="facebook",
        max_chars=63206,
        hashtag_position="bottom",
        emoji_style="rich",
        line_break_style="double",
        max_hashtags=10
    ),
    "twitter": PlatformConfig(
        id="twitter",
        max_chars=280,
        hashtag_position="inline",
        emoji_style="minimal",
        line_break_style="none",
        max_hashtags=3
    ),
    "linkedin": PlatformConfig(
        id="linkedin",
        max_chars=3000,
        hashtag_position="bottom",
        emoji_style="minimal",
        line_break_style="double",
        max_hashtags=5
    ),
    "tiktok": PlatformConfig(
        id="tiktok",
        max_chars=2200,
        hashtag_position="bottom",
        emoji_style="rich",
        line_break_style="single",
        max_hashtags=5
    ),
    "threads": PlatformConfig(
        id="threads",
        max_chars=500,
        hashtag_position="bottom",
        emoji_style="minimal",
        line_break_style="double",
        max_hashtags=5
    ),
}


def clean_text(text: str) -> str:
    """
    Pulisce il testo rimuovendo caratteri problematici.

    - Rimuove caratteri invisibili (zero-width spaces, etc.)
    - Normalizza gli spazi
    - Corregge punteggiatura
    """
    # Rimuovi caratteri invisibili problematici
    text = re.sub(r'[\u200B-\u200D\uFEFF]', '', text)

    # Normalizza Unicode (NFC per compatibilità)
    text = unicodedata.normalize('NFC', text)

    # Normalizza spazi multipli in singolo spazio
    text = re.sub(r'[ \t]+', ' ', text)

    # Rimuovi spazi prima della punteggiatura
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)

    # Aggiungi spazio dopo punteggiatura se mancante (eccetto numeri)
    text = re.sub(r'([.,!?;:])([A-Za-zÀ-ÿ])', r'\1 \2', text)

    return text.strip()


def normalize_line_breaks(text: str, platform: str) -> str:
    """
    Normalizza i line breaks per la piattaforma specificata.
    """
    config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["instagram"])

    # Converti tutti i tipi di line break in \n
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Rimuovi spazi prima dei line breaks
    text = re.sub(r'[ \t]+\n', '\n', text)

    # Rimuovi line breaks eccessivi (più di 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Applica stile specifico della piattaforma
    if config.line_break_style == "double":
        # Assicura doppio line break tra paragrafi
        paragraphs = text.split('\n\n')
        paragraphs = [p.replace('\n', ' ') for p in paragraphs]
        text = '\n\n'.join(paragraphs)

    elif config.line_break_style == "single":
        # Converti doppi in singoli
        text = text.replace('\n\n', '\n')

    elif config.line_break_style == "none":
        # Rimuovi tutti i line breaks
        text = re.sub(r'\n+', ' ', text)

    return text.strip()


def extract_hashtags(text: str) -> list[str]:
    """Estrae hashtag dal testo."""
    hashtag_pattern = r'#([a-zA-Z0-9_àèéìòùÀÈÉÌÒÙ]+)'
    matches = re.findall(hashtag_pattern, text)
    return list(dict.fromkeys(matches))  # Rimuovi duplicati mantenendo ordine


def remove_hashtags_from_text(text: str) -> str:
    """Rimuove hashtag dal testo."""
    text = re.sub(r'#[a-zA-Z0-9_àèéìòùÀÈÉÌÒÙ]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def format_hashtags(hashtags: list[str], platform: str) -> str:
    """
    Formatta gli hashtag per la piattaforma.
    """
    config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["instagram"])

    # Pulisci hashtag
    clean_hashtags = []
    for h in hashtags:
        # Rimuovi # iniziale se presente
        h = h.lstrip('#')
        # Rimuovi spazi
        h = h.replace(' ', '')
        # Rimuovi caratteri non validi
        h = re.sub(r'[^a-zA-Z0-9_àèéìòùÀÈÉÌÒÙ]', '', h)
        if h:
            clean_hashtags.append(h)

    # Rimuovi duplicati
    clean_hashtags = list(dict.fromkeys(clean_hashtags))

    # Limita al numero massimo per piattaforma
    clean_hashtags = clean_hashtags[:config.max_hashtags]

    # Formatta con #
    return ' '.join(f'#{h}' for h in clean_hashtags)


def format_post_for_platform(
    text: str,
    platform: str,
    hashtags: Optional[list[str]] = None,
    link: Optional[str] = None
) -> dict:
    """
    Formatta un post per una specifica piattaforma.

    Args:
        text: Testo del post
        platform: ID della piattaforma (instagram, facebook, etc.)
        hashtags: Lista di hashtag (opzionale)
        link: URL da includere (opzionale)

    Returns:
        Dict con content, raw_text, hashtags, char_count, is_valid, warnings
    """
    config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["instagram"])
    warnings = []

    # 1. Pulisci il testo
    text = clean_text(text)

    # 2. Estrai e rimuovi hashtag esistenti
    existing_hashtags = extract_hashtags(text)
    text = remove_hashtags_from_text(text)

    # 3. Combina hashtag
    all_hashtags = list(dict.fromkeys((hashtags or []) + existing_hashtags))

    # 4. Normalizza line breaks
    text = normalize_line_breaks(text, platform)

    # 5. Formatta hashtag
    formatted_hashtags = format_hashtags(all_hashtags, platform)

    # 6. Componi contenuto finale
    if config.hashtag_position == "inline":
        # Twitter style
        if formatted_hashtags:
            final_content = f"{text} {formatted_hashtags}"
        else:
            final_content = text

    elif config.hashtag_position == "first_comment":
        # Solo testo, hashtag separati
        final_content = text
        if formatted_hashtags:
            warnings.append(f"Hashtag per primo commento: {formatted_hashtags}")

    else:  # "bottom"
        if formatted_hashtags:
            if config.line_break_style == "double":
                final_content = f"{text}\n\n{formatted_hashtags}"
            elif config.line_break_style == "single":
                final_content = f"{text}\n{formatted_hashtags}"
            else:
                final_content = f"{text} {formatted_hashtags}"
        else:
            final_content = text

    # 7. Aggiungi link se supportato
    if link:
        if platform == "instagram":
            warnings.append("Link in bio consigliato per Instagram")
        else:
            if config.line_break_style == "double":
                final_content = f"{final_content}\n\n🔗 {link}"
            else:
                final_content = f"{final_content}\n🔗 {link}"

    # 8. Verifica limiti
    char_count = len(final_content)
    is_valid = char_count <= config.max_chars

    if not is_valid:
        warnings.append(f"Superato limite: {char_count}/{config.max_chars} caratteri")

    return {
        "content": final_content,
        "raw_text": text,
        "hashtags": formatted_hashtags,
        "char_count": char_count,
        "is_valid": is_valid,
        "warnings": warnings,
        "platform": platform
    }


def format_for_all_platforms(
    text: str,
    platforms: list[str],
    hashtags: Optional[list[str]] = None,
    link: Optional[str] = None
) -> dict[str, dict]:
    """
    Formatta un post per tutte le piattaforme specificate.
    """
    results = {}
    for platform in platforms:
        results[platform] = format_post_for_platform(text, platform, hashtags, link)
    return results


def validate_post(content: str, platform: str) -> dict:
    """
    Valida un post per una piattaforma.

    Returns:
        Dict con valid (bool) e errors (list)
    """
    config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["instagram"])
    errors = []

    # Check lunghezza
    if len(content) > config.max_chars:
        errors.append(f"Testo troppo lungo: {len(content)}/{config.max_chars}")

    # Check contenuto vuoto
    if not content.strip():
        errors.append("Il post non può essere vuoto")

    # Check hashtag count
    hashtag_count = content.count('#')
    if hashtag_count > config.max_hashtags:
        errors.append(f"Troppi hashtag: {hashtag_count}/{config.max_hashtags}")

    # Check link in Instagram
    if platform == "instagram" and re.search(r'https?://', content):
        errors.append("Link non cliccabili in Instagram - usa Link in bio")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def truncate_to_limit(text: str, platform: str, preserve_hashtags: bool = True) -> str:
    """
    Tronca il testo al limite della piattaforma.
    """
    config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["instagram"])

    if len(text) <= config.max_chars:
        return text

    if preserve_hashtags:
        # Estrai hashtag
        hashtags = extract_hashtags(text)
        text_only = remove_hashtags_from_text(text)

        # Calcola spazio disponibile per hashtag
        hashtag_str = format_hashtags(hashtags, platform)
        available = config.max_chars - len(hashtag_str) - 5  # 5 per "\n\n..." o spazi

        # Tronca testo
        if len(text_only) > available:
            text_only = text_only[:available-3] + "..."

        # Ricomponi
        if hashtag_str:
            if config.line_break_style == "double":
                return f"{text_only}\n\n{hashtag_str}"
            else:
                return f"{text_only} {hashtag_str}"
        return text_only

    # Troncatura semplice
    return text[:config.max_chars-3] + "..."


# =============================================================================
# SMART POST GENERATION HELPERS
# =============================================================================

def build_structured_post(
    hook: str,
    body: str,
    cta: str,
    hashtags: list[str],
    platform: str
) -> str:
    """
    Costruisce un post strutturato con Hook → Body → CTA → Hashtag.
    """
    config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["instagram"])

    # Pulisci componenti
    hook = clean_text(hook)
    body = clean_text(body)
    cta = clean_text(cta)

    # Costruisci post
    if config.line_break_style == "double":
        post = f"{hook}\n\n{body}\n\n{cta}"
    elif config.line_break_style == "single":
        post = f"{hook}\n{body}\n{cta}"
    else:
        post = f"{hook} {body} {cta}"

    # Formatta e aggiungi hashtag
    result = format_post_for_platform(post, platform, hashtags)
    return result["content"]


def optimize_for_engagement(text: str, platform: str) -> str:
    """
    Ottimizza il testo per massimo engagement.
    """
    config = PLATFORM_CONFIGS.get(platform, PLATFORM_CONFIGS["instagram"])

    # Aggiungi emoji strategiche se non presenti
    emoji_pattern = r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\u2600-\u26FF\u2700-\u27BF]'
    has_emoji = bool(re.search(emoji_pattern, text))

    if not has_emoji and config.emoji_style != "none":
        # Aggiungi emoji all'inizio per catturare attenzione
        engagement_emojis = ["✨", "🚀", "💡", "🎯", "⭐"]
        import random
        text = f"{random.choice(engagement_emojis)} {text}"

    # Assicura che ci sia una CTA se mancante
    cta_patterns = [
        r'(commenta|condividi|seguici|scopri|clicca|visita|contattaci)',
        r'(comment|share|follow|discover|click|visit|contact)',
        r'[?!]$'  # Domanda o esclamazione finale
    ]

    has_cta = any(re.search(p, text.lower()) for p in cta_patterns)

    if not has_cta:
        if platform == "instagram":
            text = f"{text}\n\n💬 Cosa ne pensi? Commenta qui sotto! 👇"
        elif platform == "linkedin":
            text = f"{text}\n\n🤝 Connettiti per saperne di più."
        elif platform == "facebook":
            text = f"{text}\n\n👍 Ti è stato utile? Condividi!"

    return text
