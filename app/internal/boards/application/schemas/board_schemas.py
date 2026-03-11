"""
DTOs (Data Transfer Objects) para Boards
Esquemas de entrada y salida de la API
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
    """DTO para crear un tablero"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        example="Outfits de verano 🌴",
        description="Nombre del tablero"
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        example="Mis looks favoritos para la playa",
        description="Descripción del tablero"
    )
    is_private: bool = Field(
        default=False,
        example=False,
        description="Tablero privado o público"
    )
    is_collaborative: bool = Field(
        default=False,
        example=False,
        description="Permitir colaboradores"
    )


class UpdateBoardRequest(BaseModel):
    """DTO para actualizar un tablero"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_private: Optional[bool] = None
    is_collaborative: Optional[bool] = None
    cover_image_url: Optional[str] = None


class AddPinToBoardRequest(BaseModel):
    """DTO para agregar un pin a un tablero"""
    pin_id: str = Field(
        ...,
        min_length=1,
        example="550e8400-e29b-41d4-a716-446655440000",
        description="ID del pin a agregar"
    )
    notes: Optional[str] = Field(
        None,
        max_length=500,
        example="Perfecto para la boda de Ana",
        description="Notas opcionales sobre el pin"
    )


class AddCollaboratorRequest(BaseModel):
    """DTO para agregar un colaborador"""
    user_id: str = Field(
        ...,
        min_length=1,
        example="550e8400-e29b-41d4-a716-446655440001",
        description="ID del usuario a agregar como colaborador"
    )
    can_edit: bool = Field(default=False, description="Puede editar el tablero")
    can_add_pins: bool = Field(default=True, description="Puede agregar pins")
    can_remove_pins: bool = Field(default=False, description="Puede quitar pins")


class UpdateCollaboratorRequest(BaseModel):
    """DTO para actualizar permisos de un colaborador"""
    can_edit: bool = Field(default=False)
    can_add_pins: bool = Field(default=True)
    can_remove_pins: bool = Field(default=False)


# ── Response DTOs ─────────────────────────────────────────────

class BoardListResponse(BaseModel):
    """Respuesta paginada de tableros"""
    boards: List[BoardResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class BoardSummaryListResponse(BaseModel):
    """Respuesta paginada de tableros resumidos"""
    boards: List[BoardSummary]
    total: int
    limit: int
    offset: int
    has_more: bool


class BoardPinListResponse(BaseModel):
    """Respuesta paginada de pins en un tablero"""
    pins: List[BoardPin]
    total: int
    limit: int
    offset: int
    has_more: bool


class CollaboratorListResponse(BaseModel):
    """Lista de colaboradores"""
    collaborators: List[BoardCollaboratorResponse]


class MessageResponse(BaseModel):
    """Respuesta genérica"""
    message: str