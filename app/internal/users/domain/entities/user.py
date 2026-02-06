from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_validator
import re

class User(BaseModel):
    """Entidad de dominio User - NUNCA exponer directamente en API"""
    id: str
    username: str
    email: EmailStr
    password_hash: str
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: str = "prefer_not_to_say"
    preferred_styles: List[str] = []
    is_verified: bool = False
    is_active: bool = True
    role: str = "user"
    email_verified_at: Optional[datetime] = None
    login_attempts: int = 0
    locked_until: Optional[datetime] = None
    password_reset_token: Optional[str] = None
    password_reset_token_expiry: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not v or len(v) < 3 or len(v) > 30:
            raise ValueError('Username must be between 3 and 30 characters')
        if not re.match(r'^[a-zA-Z0-9._]+$', v):
            raise ValueError('Username can only contain letters, numbers, dots and underscores')
        return v
    
    def is_locked(self) -> bool:
        """Verifica si la cuenta está bloqueada"""
        if self.locked_until is None:
            return False
        return datetime.utcnow() < self.locked_until
    
    class Config:
        from_attributes = True

class UserProfile(BaseModel):
    """Datos públicos del usuario - Para mostrar en perfiles"""
    id: str
    username: str
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_styles: List[str] = []
    is_verified: bool
    created_at: datetime
    
    # Estadísticas (se agregarán en Corte 2)
    total_pins: int = 0
    total_followers: int = 0
    total_following: int = 0
    
    class Config:
        from_attributes = True

class UserMe(BaseModel):
    """Datos del usuario autenticado - Incluye email pero no password"""
    id: str
    username: str
    email: EmailStr
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: str
    preferred_styles: List[str]
    is_verified: bool
    role: str
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True