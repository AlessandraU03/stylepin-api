"""
DTOs (Data Transfer Objects) para Likes
"""
from pydantic import BaseModel, Field
from typing import List

from internal.likes.domain.entities.like import LikeResponse


# ── Request DTOs ──────────────────────────────────────────────

class LikePinRequest(BaseModel):
    """DTO para dar like a un pin"""
    pin_id: str = Field(
        ...,
        min_length=1,
        example="550e8400-e29b-41d4-a716-446655440000",
        description="ID del pin al que dar like"
    )


# ── Response DTOs ─────────────────────────────────────────────

class LikeStatusResponse(BaseModel):
    """Estado de like de un pin"""
    pin_id: str
    is_liked: bool
    likes_count: int


class LikesListResponse(BaseModel):
    """Respuesta paginada de likes"""
    likes: List[LikeResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class UserLikesListResponse(BaseModel):
    """Pins que un usuario ha dado like"""
    likes: List[LikeResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class MessageResponse(BaseModel):
    """Respuesta genérica"""
    message: str