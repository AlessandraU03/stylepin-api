from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import List, Optional
import re

class RegisterRequest(BaseModel):
    """DTO para registro de usuario"""
    username: str = Field(..., min_length=3, max_length=30, example="fashionista")
    email: EmailStr = Field(..., example="user@stylepin.com")
    password: str = Field(..., min_length=8, example="SecurePass123!")
    full_name: str = Field(..., min_length=2, example="Maria Lopez")
    gender: Optional[str] = Field(None, example="female")
    preferred_styles: Optional[List[str]] = Field(default=[], example=["Casual", "Minimalista"])
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        return v
    
    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ['male', 'female', 'non_binary', 'prefer_not_to_say']
            if v not in allowed:
                raise ValueError(f'Gender must be one of: {", ".join(allowed)}')
        return v

class LoginRequest(BaseModel):
    """DTO para login adaptado a email o username"""
    identity: str = Field(..., example="fashionista o user@stylepin.com")
    password: str = Field(..., example="SecurePass123!")

class AuthResponse(BaseModel):
    """DTO de respuesta de autenticación"""
    user: dict
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = "bearer"