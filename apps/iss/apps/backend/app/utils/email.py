"""
📧 Email Service per ISS Platform - Versione Semplificata

Sistema di invio email con fallback per sviluppo
"""

import logging
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)


async def send_email(
    to_emails: List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    template_vars: Optional[Dict[str, Any]] = None
) -> bool:
    """
    📤 Funzione di invio email con fallback per sviluppo
    
    Args:
        to_emails: Lista email destinatari
        subject: Oggetto email
        html_content: Contenuto HTML
        text_content: Contenuto testo (fallback)
        template_vars: Variabili per template
        
    Returns:
        bool: True (simulato per sviluppo)
    """
    try:
        # Sostituisci variabili template se presenti
        if template_vars:
            for key, value in template_vars.items():
                html_content = html_content.replace(f"{{{{{key}}}}}", str(value))
                if text_content:
                    text_content = text_content.replace(f"{{{{{key}}}}}", str(value))
        
        # In sviluppo, logga l'email invece di inviarla
        logger.info(f"📧 [DEV] Email simulata:")
        logger.info(f"   📬 A: {', '.join(to_emails)}")
        logger.info(f"   📝 Oggetto: {subject}")
        logger.info(f"   📄 Contenuto: {html_content[:100]}...")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore invio email: {e}")
        return False
