"""
Security utilities for authentication and password management.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import secrets
import re

from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status

# Password hashing context (Argon2 - più sicuro di bcrypt)
pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,
    argon2__parallelism=4
)

# JWT Configuration
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY  # SEMPRE usa settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES  # 7 days from config
REFRESH_TOKEN_EXPIRE_DAYS = 30  # 30 days for refresh


class PasswordValidator:
    """Validatore password sicure."""

    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGITS = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    @classmethod
    def validate(cls, password: str) -> tuple[bool, Optional[str]]:
        """
        Valida una password secondo i criteri di sicurezza.

        Returns:
            tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password deve essere almeno {cls.MIN_LENGTH} caratteri"

        if cls.REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password deve contenere almeno una lettera maiuscola"

        if cls.REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password deve contenere almeno una lettera minuscola"

        if cls.REQUIRE_DIGITS and not re.search(r'\d', password):
            return False, "Password deve contenere almeno un numero"

        if cls.REQUIRE_SPECIAL and not re.search(f'[{re.escape(cls.SPECIAL_CHARS)}]', password):
            return False, f"Password deve contenere almeno un carattere speciale ({cls.SPECIAL_CHARS})"

        # Check password comuni (top 1000)
        if cls._is_common_password(password):
            return False, "Password troppo comune, scegline una più sicura"

        return True, None

    @staticmethod
    def _is_common_password(password: str) -> bool:
        """Check se la password è tra le più comuni."""
        common_passwords = {
            "password", "123456", "12345678", "qwerty", "abc123",
            "monkey", "1234567", "letmein", "trustno1", "dragon",
            "baseball", "iloveyou", "master", "sunshine", "ashley",
            "bailey", "passw0rd", "shadow", "123123", "654321",
            "superman", "qazwsx", "michael", "football", "password1"
        }
        return password.lower() in common_passwords

    @classmethod
    def generate_strong_password(cls, length: int = 16) -> str:
        """Genera una password sicura casuale."""
        import string

        chars = string.ascii_letters + string.digits + cls.SPECIAL_CHARS
        while True:
            password = ''.join(secrets.choice(chars) for _ in range(length))
            is_valid, _ = cls.validate(password)
            if is_valid:
                return password


def hash_password(password: str) -> str:
    """
    Hash di una password usando Argon2.

    Args:
        password: Password in chiaro

    Returns:
        str: Password hashata
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una password contro il suo hash.

    Args:
        plain_password: Password in chiaro
        hashed_password: Password hashata

    Returns:
        bool: True se la password è corretta
    """
    try:
        # Use bcrypt directly to avoid passlib bug
        import bcrypt
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # Fallback to passlib
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False


def create_access_token(
    data: Dict[str, Any],
    secret_key: str = SECRET_KEY,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un JWT access token.

    Args:
        data: Dati da includere nel token
        secret_key: Chiave segreta per firmare il token
        expires_delta: Durata del token (default: ACCESS_TOKEN_EXPIRE_MINUTES)

    Returns:
        str: JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: Dict[str, Any],
    secret_key: str = SECRET_KEY,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crea un JWT refresh token.

    Args:
        data: Dati da includere nel token
        secret_key: Chiave segreta per firmare il token
        expires_delta: Durata del token (default: REFRESH_TOKEN_EXPIRE_DAYS)

    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str, secret_key: str = SECRET_KEY) -> Dict[str, Any]:
    """
    Decodifica e valida un JWT token.

    Args:
        token: JWT token da decodificare
        secret_key: Chiave segreta per verificare il token

    Returns:
        Dict[str, Any]: Payload del token

    Raises:
        HTTPException: Se il token è invalido o scaduto
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )


def generate_reset_token() -> str:
    """
    Genera un token sicuro per reset password.

    Returns:
        str: Token casuale (32 caratteri hex)
    """
    return secrets.token_urlsafe(32)


def generate_2fa_secret() -> str:
    """
    Genera un secret per 2FA (TOTP).

    Returns:
        str: Secret base32 per TOTP
    """
    import pyotp
    return pyotp.random_base32()


def verify_2fa_token(secret: str, token: str) -> bool:
    """
    Verifica un token 2FA (TOTP).

    Args:
        secret: Secret TOTP dell'utente
        token: Token a 6 cifre inserito dall'utente

    Returns:
        bool: True se il token è valido
    """
    import pyotp
    totp = pyotp.TOTP(secret)
    return totp.verify(token, valid_window=1)  # ±30 secondi


class RateLimiter:
    """Rate limiter per prevenire brute force attacks."""

    def __init__(self, max_attempts: int = 5, window_seconds: int = 300):
        """
        Args:
            max_attempts: Numero massimo di tentativi
            window_seconds: Finestra temporale in secondi (default: 5 minuti)
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: Dict[str, list] = {}

    def is_allowed(self, identifier: str) -> bool:
        """
        Verifica se un identifier può fare un tentativo.

        Args:
            identifier: Identificatore univoco (es. IP, username)

        Returns:
            bool: True se il tentativo è permesso
        """
        now = datetime.utcnow()

        if identifier not in self._attempts:
            self._attempts[identifier] = []

        # Rimuovi tentativi vecchi
        cutoff = now - timedelta(seconds=self.window_seconds)
        self._attempts[identifier] = [
            attempt for attempt in self._attempts[identifier]
            if attempt > cutoff
        ]

        # Verifica se ha superato il limite
        if len(self._attempts[identifier]) >= self.max_attempts:
            return False

        # Registra tentativo
        self._attempts[identifier].append(now)
        return True

    def reset(self, identifier: str):
        """Reset dei tentativi per un identifier."""
        if identifier in self._attempts:
            del self._attempts[identifier]


# Rate limiter globale per login
login_rate_limiter = RateLimiter(max_attempts=5, window_seconds=300)


# ============================================================================
# PII ENCRYPTION UTILITIES
# ============================================================================

import os
from cryptography.fernet import Fernet
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


@lru_cache()
def get_encryption_key() -> bytes:
    """
    Get encryption key from environment.

    In production, use AWS KMS, Vault, or similar key management service.

    Returns:
        bytes: Encryption key for Fernet

    Raises:
        ValueError: If PII_ENCRYPTION_KEY is not set in production
    """
    key = os.getenv("PII_ENCRYPTION_KEY")

    if not key:
        # Development only - generate and warn
        if os.getenv("ENVIRONMENT") == "production":
            raise ValueError(
                "PII_ENCRYPTION_KEY must be set in production! "
                "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

        # Generate temporary key for development
        key = Fernet.generate_key().decode()
        logger.warning(f"⚠️ WARNING: Using generated encryption key for development: {key}")
        logger.warning("Set PII_ENCRYPTION_KEY environment variable in production!")

    return key.encode() if isinstance(key, str) else key


def encrypt_pii(value: str) -> str:
    """
    Encrypt PII data (email, phone, etc.) using Fernet symmetric encryption.

    Args:
        value: Plain text value to encrypt

    Returns:
        str: Encrypted value (base64 encoded)

    Example:
        >>> encrypt_pii("user@example.com")
        'gAAAAABhk...'
    """
    if not value:
        return value

    try:
        key = get_encryption_key()
        f = Fernet(key)

        encrypted = f.encrypt(value.encode('utf-8'))
        return encrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise ValueError(f"Failed to encrypt PII data: {str(e)}")


def decrypt_pii(encrypted_value: str) -> str:
    """
    Decrypt PII data encrypted with encrypt_pii().

    Args:
        encrypted_value: Encrypted value (base64 encoded)

    Returns:
        str: Decrypted plain text value

    Raises:
        ValueError: If decryption fails (wrong key or corrupted data)

    Example:
        >>> decrypt_pii('gAAAAABhk...')
        'user@example.com'
    """
    if not encrypted_value:
        return encrypted_value

    try:
        key = get_encryption_key()
        f = Fernet(key)

        decrypted = f.decrypt(encrypted_value.encode('utf-8'))
        return decrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        # In production, you might want to alert on decryption failures
        raise ValueError(f"Failed to decrypt PII data: {str(e)}")


def rotate_encryption_key(old_key: str, new_key: str, encrypted_value: str) -> str:
    """
    Rotate encryption key by decrypting with old key and re-encrypting with new key.

    This function is used during key rotation to re-encrypt all PII data.

    Args:
        old_key: Previous encryption key
        new_key: New encryption key
        encrypted_value: Value encrypted with old key

    Returns:
        str: Value re-encrypted with new key

    Example:
        >>> old_encrypted = encrypt_pii("test@example.com")
        >>> # Generate new key
        >>> new_encrypted = rotate_encryption_key(old_key, new_key, old_encrypted)
    """
    try:
        # Decrypt with old key
        old_fernet = Fernet(old_key.encode() if isinstance(old_key, str) else old_key)
        decrypted = old_fernet.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')

        # Re-encrypt with new key
        new_fernet = Fernet(new_key.encode() if isinstance(new_key, str) else new_key)
        new_encrypted = new_fernet.encrypt(decrypted.encode('utf-8'))

        return new_encrypted.decode('utf-8')
    except Exception as e:
        logger.error(f"Key rotation error: {e}")
        raise ValueError(f"Failed to rotate encryption key: {str(e)}")
