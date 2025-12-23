from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.user import UserRole, UserStatus, AccessibilityNeeds


# ========== BASE SCHEMAS ==========

class UserBase(BaseModel):
    """Schema base per User"""
    email: EmailStr
    nome: str = Field(..., min_length=1, max_length=100)
    cognome: str = Field(..., min_length=1, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    role: UserRole = UserRole.CITTADINO
    accessibility_needs: AccessibilityNeeds = AccessibilityNeeds.NONE
    preferred_language: str = Field(default="it", max_length=5)
    timezone: str = Field(default="Europe/Rome", max_length=50)


class UserCreate(UserBase):
    """Schema per creazione User"""
    password: str = Field(..., min_length=8, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    
    # Informazioni APS (opzionali)
    aps_nome_organizzazione: Optional[str] = Field(None, max_length=200)
    aps_partita_iva: Optional[str] = Field(None, max_length=11)
    aps_codice_fiscale_org: Optional[str] = Field(None, max_length=16)
    aps_indirizzo: Optional[str] = None
    aps_citta: Optional[str] = Field(None, max_length=100)
    aps_cap: Optional[str] = Field(None, max_length=5)
    aps_provincia: Optional[str] = Field(None, max_length=2)
    aps_settore_attivita: Optional[str] = Field(None, max_length=200)
    aps_website: Optional[str] = Field(None, max_length=255)
    aps_descrizione: Optional[str] = None
    
    # Privacy e consensi
    privacy_policy_accepted: bool = Field(..., description="Deve accettare privacy policy")
    newsletter_subscription: bool = Field(default=True)
    marketing_consent: bool = Field(default=False)

    @validator('password')
    def validate_password(cls, v):
        """Validazione password forte"""
        if len(v) < 8:
            raise ValueError('Password deve essere almeno 8 caratteri')
        if not any(c.isupper() for c in v):
            raise ValueError('Password deve contenere almeno una maiuscola')
        if not any(c.islower() for c in v):
            raise ValueError('Password deve contenere almeno una minuscola')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password deve contenere almeno un numero')
        return v

    @validator('aps_partita_iva')
    def validate_partita_iva(cls, v):
        """Validazione Partita IVA italiana"""
        if v is not None and len(v) != 11:
            raise ValueError('Partita IVA deve essere 11 cifre')
        if v is not None and not v.isdigit():
            raise ValueError('Partita IVA deve contenere solo numeri')
        return v


class UserUpdate(BaseModel):
    """Schema per aggiornamento User"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    cognome: Optional[str] = Field(None, min_length=1, max_length=100)
    telefono: Optional[str] = Field(None, max_length=20)
    data_nascita: Optional[datetime] = None
    codice_fiscale: Optional[str] = Field(None, max_length=16)
    
    # Informazioni APS
    aps_nome_organizzazione: Optional[str] = Field(None, max_length=200)
    aps_partita_iva: Optional[str] = Field(None, max_length=11)
    aps_codice_fiscale_org: Optional[str] = Field(None, max_length=16)
    aps_indirizzo: Optional[str] = None
    aps_citta: Optional[str] = Field(None, max_length=100)
    aps_cap: Optional[str] = Field(None, max_length=5)
    aps_provincia: Optional[str] = Field(None, max_length=2)
    aps_settore_attivita: Optional[str] = Field(None, max_length=200)
    aps_website: Optional[str] = Field(None, max_length=255)
    aps_descrizione: Optional[str] = None
    
    # Accessibilità e preferenze
    accessibility_needs: Optional[AccessibilityNeeds] = None
    preferred_language: Optional[str] = Field(None, max_length=5)
    timezone: Optional[str] = Field(None, max_length=50)
    
    # Notifiche e privacy
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    newsletter_subscription: Optional[bool] = None
    marketing_consent: Optional[bool] = None
    
    # Bio e social
    bio: Optional[str] = None
    avatar_url: Optional[str] = Field(None, max_length=500)
    linkedin_url: Optional[str] = Field(None, max_length=255)
    twitter_url: Optional[str] = Field(None, max_length=255)
    facebook_url: Optional[str] = Field(None, max_length=255)


class UserResponse(UserBase):
    """Schema per risposta User (senza dati sensibili)"""
    id: int
    username: Optional[str]
    status: UserStatus
    is_email_verified: bool
    
    # Informazioni APS (se presenti)
    aps_nome_organizzazione: Optional[str]
    aps_citta: Optional[str]
    aps_settore_attivita: Optional[str]
    aps_website: Optional[str]
    aps_descrizione: Optional[str]
    
    # Timestamps
    created_at: datetime
    last_login: Optional[datetime]
    
    # Stats e gamification
    points: int = 0
    level: int = 1
    badges: Optional[str]  # JSON string
    login_count: int = 0
    
    # Properties calcolate
    full_name: str
    is_aps: bool
    is_staff: bool
    needs_accessibility_support: bool

    class Config:
        from_attributes = True


class UserProfileResponse(UserResponse):
    """Schema esteso per profilo utente completo"""
    data_nascita: Optional[datetime]
    telefono: Optional[str]
    bio: Optional[str]
    avatar_url: Optional[str]
    linkedin_url: Optional[str]
    twitter_url: Optional[str]
    facebook_url: Optional[str]
    
    # Preferenze notifiche
    email_notifications: bool
    sms_notifications: bool
    newsletter_subscription: bool
    marketing_consent: bool
    
    # Audit info
    updated_at: datetime
    last_activity: Optional[datetime]


class UserListResponse(BaseModel):
    """Schema per lista utenti (admin)"""
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    status: UserStatus
    is_email_verified: bool
    aps_nome_organizzazione: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    login_count: int

    class Config:
        from_attributes = True


# ========== AUTH SCHEMAS ==========

class UserLogin(BaseModel):
    """Schema per login"""
    email: EmailStr
    password: str
    remember_me: bool = Field(default=False)


class TokenResponse(BaseModel):
    """Schema per risposta token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # secondi
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Schema per refresh token"""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Schema per cambio password"""
    current_password: str
    new_password: str = Field(..., min_length=8)

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validazione nuova password"""
        if len(v) < 8:
            raise ValueError('Password deve essere almeno 8 caratteri')
        if not any(c.isupper() for c in v):
            raise ValueError('Password deve contenere almeno una maiuscola')
        if not any(c.islower() for c in v):
            raise ValueError('Password deve contenere almeno una minuscola')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password deve contenere almeno un numero')
        return v


class PasswordResetRequest(BaseModel):
    """Schema per richiesta reset password"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema per conferma reset password"""
    token: str
    new_password: str = Field(..., min_length=8)

    @validator('new_password')
    def validate_new_password(cls, v):
        """Validazione nuova password"""
        if len(v) < 8:
            raise ValueError('Password deve essere almeno 8 caratteri')
        return v


class EmailVerificationRequest(BaseModel):
    """Schema per richiesta verifica email"""
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    """Schema per conferma verifica email"""
    token: str


# ========== USER PREFERENCES SCHEMAS ==========

class UserPreferencesBase(BaseModel):
    """Schema base per preferenze utente"""
    # Preferenze UI
    theme: str = Field(default="light", pattern="^(light|dark|auto)$")
    font_size: str = Field(default="medium", pattern="^(small|medium|large|xl)$")
    reduced_motion: bool = Field(default=False)
    high_contrast: bool = Field(default=False)
    
    # Preferenze bandi
    preferred_bandi_sources: Optional[List[str]] = Field(default=None)
    preferred_categories: Optional[List[str]] = Field(default=None)
    min_importo_interesse: Optional[int] = Field(default=None, ge=0)
    max_importo_interesse: Optional[int] = Field(default=None, ge=0)
    
    # Preferenze notifiche
    notify_new_bandi: bool = Field(default=True)
    notify_bandi_expiring: bool = Field(default=True)
    notify_corsi_available: bool = Field(default=True)
    notify_eventi_upcoming: bool = Field(default=True)
    
    # Alert personalizzati
    custom_keywords: Optional[List[str]] = Field(default=None)
    alert_frequency: str = Field(default="daily", pattern="^(instant|daily|weekly)$")

    @validator('max_importo_interesse')
    def validate_importo_range(cls, v, values):
        """Validazione range importi"""
        if v is not None and 'min_importo_interesse' in values:
            min_val = values['min_importo_interesse']
            if min_val is not None and v <= min_val:
                raise ValueError('Importo massimo deve essere maggiore del minimo')
        return v


class UserPreferencesCreate(UserPreferencesBase):
    """Schema per creazione preferenze"""
    pass


class UserPreferencesUpdate(BaseModel):
    """Schema per aggiornamento preferenze"""
    theme: Optional[str] = Field(None, pattern="^(light|dark|auto)$")
    font_size: Optional[str] = Field(None, pattern="^(small|medium|large|xl)$")
    reduced_motion: Optional[bool] = None
    high_contrast: Optional[bool] = None
    
    preferred_bandi_sources: Optional[List[str]] = None
    preferred_categories: Optional[List[str]] = None
    min_importo_interesse: Optional[int] = Field(None, ge=0)
    max_importo_interesse: Optional[int] = Field(None, ge=0)
    
    notify_new_bandi: Optional[bool] = None
    notify_bandi_expiring: Optional[bool] = None
    notify_corsi_available: Optional[bool] = None
    notify_eventi_upcoming: Optional[bool] = None
    
    custom_keywords: Optional[List[str]] = None
    alert_frequency: Optional[str] = Field(None, pattern="^(instant|daily|weekly)$")


class UserPreferencesResponse(UserPreferencesBase):
    """Schema per risposta preferenze"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ========== STATISTICS SCHEMAS ==========

class UserStatsResponse(BaseModel):
    """Schema per statistiche utenti (admin)"""
    total_users: int
    users_by_role: Dict[str, int]
    users_by_status: Dict[str, int]
    new_registrations_today: int
    new_registrations_week: int
    new_registrations_month: int
    active_users_today: int
    active_users_week: int
    aps_organizations: int
    accessibility_users: int


class UserActivityResponse(BaseModel):
    """Schema per attività utente"""
    user_id: int
    bandi_viewed: int
    bandi_saved: int
    searches_performed: int
    exports_generated: int
    corsi_attended: int
    eventi_participated: int
    last_activity: Optional[datetime]
    total_points: int
    current_level: int

    class Config:
        from_attributes = True


# ========== BULK OPERATIONS ==========

class BulkUserOperation(BaseModel):
    """Schema per operazioni bulk utenti"""
    user_ids: List[int]
    action: str = Field(..., pattern="^(activate|suspend|delete|change_role)$")
    parameters: Optional[Dict[str, Any]] = None


class BulkUserResponse(BaseModel):
    """Schema per risposta operazioni bulk"""
    success_count: int
    error_count: int
    errors: List[Dict[str, Any]]
    processed_users: List[int]
