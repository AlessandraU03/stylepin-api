"""
DTOs (Data Transfer Objects) para Boards
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from internal.boards.domain.entities.board import (
    BoardResponse,
    BoardSummary,
    BoardPin,
    BoardCollaborator,
    BoardCollaboratorResponse,
)

# ── Request DTOs ──────────────────────────────────────────────

class CreateBoardRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_private: bool = Field(default=False)
    is_collaborative: bool = Field(default=False)


class UpdateBoardRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_private: Optional[bool] = None
    is_collaborative: Optional[bool] = None
    cover_image_url: Optional[str] = None


class AddPinToBoardRequest(BaseModel):
    pin_id: str = Field(..., min_length=1)
    notes: Optional[str] = Field(None, max_length=500)


class AddCollaboratorRequest(BaseModel):
    user_id: str = Field(..., min_length=1)
    can_edit: bool = Field(default=False)
    can_add_pins: bool = Field(default=True)
    can_remove_pins: bool = Field(default=False)


class UpdateCollaboratorRequest(BaseModel):
    can_edit: bool = Field(default=False)
    can_add_pins: bool = Field(default=True)
    can_remove_pins: bool = Field(default=False)


# ── Response DTOs ─────────────────────────────────────────────

class BoardListResponse(BaseModel):
    """Respuesta paginada — usa BoardSummary (campos opcionales) en lugar de BoardResponse"""
    boards: List[BoardSummary]   # ← CAMBIADO de BoardResponse a BoardSummary
    total: int
    limit: int
    offset: int
    has_more: bool


class BoardSummaryListResponse(BaseModel):
    boards: List[BoardSummary]
    total: int
    limit: int
    offset: int
    has_more: bool


class BoardPinListResponse(BaseModel):
    pins: List[BoardPin]
    total: int
    limit: int
    offset: int
    has_more: bool


class CollaboratorListResponse(BaseModel):
    collaborators: List[BoardCollaboratorResponse]


class MessageResponse(BaseModel):
    message: str