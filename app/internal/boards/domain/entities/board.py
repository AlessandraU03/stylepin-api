"""
Entidades de dominio para Boards
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

class Board(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_private: bool = False
    is_collaborative: bool = False
    pins_count: int = 0
    created_at: datetime
    updated_at: datetime

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Board name cannot be empty')
        if len(v) > 100:
            raise ValueError('Board name cannot exceed 100 characters')
        return v.strip()

    class Config:
        from_attributes = True


class BoardResponse(BaseModel):
    id: str
    user_id: str
    user_username: str
    user_full_name: str
    user_avatar_url: Optional[str] = None
    name: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    is_private: bool
    is_collaborative: bool
    pins_count: int
    created_at: datetime
    updated_at: datetime
    is_owner: bool = False
    is_collaborator: bool = False

    class Config:
        from_attributes = True


class BoardSummary(BaseModel):
    """Versión resumida para listas — todos los campos opcionales para compatibilidad"""
    id: str
    user_id: str
    user_username: str = ""
    user_full_name: str = ""        # ← agregado con default
    user_avatar_url: Optional[str] = None
    name: str
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    pins_count: int = 0
    is_private: bool = False
    is_collaborative: bool = False  # ← agregado con default
    created_at: datetime
    updated_at: Optional[datetime] = None  # ← agregado con default None

    class Config:
        from_attributes = True


class BoardPin(BaseModel):
    id: str
    board_id: str
    pin_id: str
    user_id: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class BoardCollaborator(BaseModel):
    id: str
    board_id: str
    user_id: str
    can_edit: bool = False
    can_add_pins: bool = True
    can_remove_pins: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class BoardCollaboratorResponse(BaseModel):
    id: str
    board_id: str
    user_id: str
    user_username: str
    user_full_name: str
    user_avatar_url: Optional[str] = None
    can_edit: bool
    can_add_pins: bool
    can_remove_pins: bool
    created_at: datetime

    class Config:
        from_attributes = True