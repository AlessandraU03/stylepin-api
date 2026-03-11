"""
DTOs (Data Transfer Objects) para Follows
"""
from pydantic import BaseModel, Field
from typing import List

from internal.follows.domain.entities.follow import (
    FollowerProfile,
    FollowingProfile,
)


# ── Request DTOs ──────────────────────────────────────────────

class FollowUserRequest(BaseModel):
    """DTO para seguir a un usuario"""
    user_id: str = Field(
        ...,
        min_length=1,
        example="550e8400-e29b-41d4-a716-446655440001",
        description="ID del usuario a seguir"
    )


# ── Response DTOs ─────────────────────────────────────────────

class FollowersListResponse(BaseModel):
    """Respuesta paginada de seguidores"""
    followers: List[FollowerProfile]
    total: int
    limit: int
    offset: int
    has_more: bool


class FollowingListResponse(BaseModel):
    """Respuesta paginada de seguidos"""
    following: List[FollowingProfile]
    total: int
    limit: int
    offset: int
    has_more: bool


class FollowStatusResponse(BaseModel):
    """Estado de follow entre dos usuarios"""
    is_following: bool
    is_followed_by: bool
    are_mutual: bool


class FollowCountsResponse(BaseModel):
    """Contadores de seguidores/seguidos"""
    user_id: str
    followers_count: int
    following_count: int


class MessageResponse(BaseModel):
    """Respuesta genérica"""
    message: str