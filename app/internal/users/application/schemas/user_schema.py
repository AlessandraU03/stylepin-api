"""
DTOs de Usuario
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

from internal.users.domain.entities.user import UserProfile, UserMe


# ── Request DTOs ──────────────────────────────────────────────

class UpdateProfileRequest(BaseModel):
    """DTO para actualizar perfil"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    gender: Optional[str] = None
    preferred_styles: Optional[List[str]] = None

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ['male', 'female', 'non_binary', 'prefer_not_to_say']
            if v not in allowed:
                raise ValueError(f'Género debe ser uno de: {", ".join(allowed)}')
        return v


class ChangePasswordRequest(BaseModel):
    """DTO para cambiar contraseña"""
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v


# ── Response DTOs ─────────────────────────────────────────────

class UserProfileResponse(BaseModel):
    """Perfil público completo con stats"""
    user: UserProfile
    is_following: bool = False
    is_followed_by: bool = False


class UserSearchResult(BaseModel):
    """Resultado de búsqueda resumido"""
    id: str
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    is_verified: bool = False


class UserListResponse(BaseModel):
    """Respuesta paginada de usuarios"""
    users: List[UserSearchResult]
    total: int
    limit: int
    offset: int
    has_more: bool


class UserStatsResponse(BaseModel):
    """Estadísticas del usuario"""
    total_pins: int = 0
    total_followers: int = 0
    total_following: int = 0
    total_boards: int = 0


class MessageResponse(BaseModel):
    """Respuesta genérica"""
    message: str