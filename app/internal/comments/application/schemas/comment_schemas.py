from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from internal.comments.domain.entities.comment import CommentResponse


# ── Request DTOs ──────────────────────────────────────────────

class CreateCommentRequest(BaseModel):
    """DTO para crear un comentario"""
    pin_id: str = Field(
        ...,
        min_length=1,
        example="507f1f77bcf86cd799439011",
        description="ID del pin donde se comenta"
    )
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        example="¡Me encanta este outfit! ¿Dónde compraste la blusa?",
        description="Contenido del comentario"
    )
    parent_comment_id: Optional[str] = Field(
        None,
        example="507f1f77bcf86cd799439022",
        description="ID del comentario padre (si es respuesta)"
    )


class UpdateCommentRequest(BaseModel):
    """DTO para editar un comentario"""
    text: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        example="¡Me encanta este outfit! Editado.",
        description="Nuevo contenido del comentario"
    )


class CommentFilters(BaseModel):
    """DTO para filtros de búsqueda de comentarios"""
    pin_id: Optional[str] = Field(
        None,
        description="Filtrar por ID de pin"
    )
    user_id: Optional[str] = Field(
        None,
        description="Filtrar por ID de usuario"
    )
    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Número de resultados"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset para paginación"
    )


# ── Response DTOs ─────────────────────────────────────────────

class CommentListResponse(BaseModel):
    """Respuesta paginada de comentarios"""
    comments: List[CommentResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class RepliesListResponse(BaseModel):
    """Respuesta paginada de respuestas"""
    replies: List[CommentResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class MessageResponse(BaseModel):
    """Respuesta genérica con mensaje"""
    message: str