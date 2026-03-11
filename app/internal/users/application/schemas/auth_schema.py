"""
DTOs de Autenticación
"""
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import List, Optional
from datetime import datetime
import re

from internal.users.domain.entities.user import UserMe


# ── Request DTOs ──────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """DTO para registro de usuario"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=30,
        example="fashionista",
    )
    email: EmailStr = Field(
        ...,
        example="user@amura.com",
    )
    password: str = Field(
        ...,
        min_length=8,
        example="SecurePass123!",
    )
    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Maria Lopez",
    )
    gender: Optional[str] = Field(
        None,
        example="female",
    )
    preferred_styles: Optional[List[str]] = Field(
        default=[],
        example=["Casual", "Minimalista"],
    )

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        return v

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ['male', 'female', 'non_binary', 'prefer_not_to_say']
            if v not in allowed:
                raise ValueError(f'Género debe ser uno de: {", ".join(allowed)}')
        return v


class LoginRequest(BaseModel):
    """DTO para login con email o username"""
    identity: str = Field(
        ...,
        example="fashionista",
        description="Email o username",
    )
    password: str = Field(
        ...,
        example="SecurePass123!",
    )


# ── Response DTOs ─────────────────────────────────────────────

class AuthResponse(BaseModel):
    """Respuesta de autenticación"""
    user: UserMe
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    """Respuesta genérica"""
    message: str