from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud import admin
from app.database.database import get_db
from app.models.admin import AdminUser
from app.models.user import User
from app.schemas.admin import TokenData

security = HTTPBearer()


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AdminUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await admin.get_admin_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    🔓 Dependency per utente opzionale
    
    Restituisce l'utente corrente se autenticato, altrimenti None.
    Utile per endpoint che funzionano sia per utenti autenticati che anonimi.
    """
    if not credentials:
        return None
    
    try:
        payload = jwt.decode(
            credentials.credentials, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
            
        # Per ora restituiamo un utente mock
        # TODO: Implementare get_user_by_username quando il sistema utenti sarà completo
        return User(
            id=1,
            username=username,
            email=f"{username}@example.com",
            is_active=True
        )
        
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    🔒 Dependency per utente obbligatorio
    
    Restituisce l'utente corrente autenticato o solleva un'eccezione.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            credentials.credentials, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
            
        # Per ora restituiamo un utente mock
        # TODO: Implementare get_user_by_username quando il sistema utenti sarà completo
        return User(
            id=1,
            username=username,
            email=f"{username}@example.com",
            is_active=True
        )
        
    except JWTError:
        raise credentials_exception


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    ✅ Dependency per utente attivo
    
    Verifica che l'utente sia attivo.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
