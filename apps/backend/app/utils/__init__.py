"""
🛠️ Modulo Utils ISS Platform

Utilities e funzioni helper per il sistema ISS
"""

from .email import send_email
from .qr_code import generate_qr_code

__all__ = [
    "send_email",
    "generate_qr_code"
]
