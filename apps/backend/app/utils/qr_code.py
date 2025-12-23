"""
🔲 QR Code Generator per ISS Platform - Versione Semplificata

Generazione QR codes con fallback per sviluppo
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def generate_qr_code(
    data: str,
    format: str = 'base64',
    size: int = 10,
    border: int = 4,
    error_correction: str = 'M'
) -> Optional[str]:
    """
    🔲 Genera QR Code (versione fallback per sviluppo)
    
    Args:
        data: Dati da codificare
        format: Formato output ('png', 'svg', 'base64')
        size: Dimensione (1-40)
        border: Bordo (pixel)
        error_correction: Livello correzione errori ('L', 'M', 'Q', 'H')
        
    Returns:
        str: QR code base64 simulato per sviluppo
    """
    try:
        logger.info(f"🔲 [DEV] QR Code simulato per: {data[:50]}...")
        
        # Restituisce un QR code base64 di esempio (1x1 pixel trasparente)
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
    except Exception as e:
        logger.error(f"❌ Errore generazione QR code: {e}")
        return None


def generate_event_qr(event_id: int, event_title: str, base_url: str = "https://iss-salerno.it") -> Optional[str]:
    """🎫 Genera QR code per evento"""
    event_url = f"{base_url}/eventi/{event_id}"
    return generate_qr_code(event_url)


def generate_course_qr(course_id: int, course_title: str, base_url: str = "https://iss-salerno.it") -> Optional[str]:
    """📚 Genera QR code per corso"""
    course_url = f"{base_url}/corsi/{course_id}"
    return generate_qr_code(course_url)
