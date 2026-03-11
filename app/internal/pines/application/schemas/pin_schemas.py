"""
DTOs (Data Transfer Objects) para Pins
"""
from pydantic import BaseModel, Field
from typing import Optional, List

from internal.pines.domain.entities.pin import PinResponse, PinSummary


# ── Request DTOs ──────────────────────────────────────────────

class CreatePinRequest(BaseModel):
    """DTO para crear un pin"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        example="Outfit casual de primavera 🌸",
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        example="Look perfecto para una salida casual",
    )
    image_url: str = Field(
        ...,
        min_length=1,
        example="https://example.com/image.jpg",
    )
    category: str = Field(
        ...,
        min_length=1,
        example="casual",
        description="Categoría del outfit",
    )
    styles: List[str] = Field(
        default=[],
        example=["minimalista", "streetwear"],
    )
    occasions: List[str] = Field(
        default=[],
        example=["diario", "universidad"],
    )
    season: str = Field(
        default="todo_el_ano",
        example="primavera",
    )
    brands: List[str] = Field(
        default=[],
        example=["Zara", "H&M"],
    )
    price_range: str = Field(
        default="bajo_500",
        example="500_1000",
    )
    where_to_buy: Optional[str] = Field(
        None,
        example="Centro comercial Plaza",
    )
    purchase_link: Optional[str] = Field(
        None,
        example="https://example.com/producto",
    )
    colors: List[str] = Field(
        default=[],
        example=["blanco", "beige"],
    )
    tags: List[str] = Field(
        default=[],
        example=["moda", "primavera", "casual"],
    )
    is_private: bool = Field(
        default=False,
        example=False,
    )


class UpdatePinRequest(BaseModel):
    """DTO para actualizar un pin"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    category: Optional[str] = None
    styles: Optional[List[str]] = None
    occasions: Optional[List[str]] = None
    season: Optional[str] = None
    brands: Optional[List[str]] = None
    price_range: Optional[str] = None
    where_to_buy: Optional[str] = None
    purchase_link: Optional[str] = None
    colors: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_private: Optional[bool] = None


class PinFilters(BaseModel):
    """Filtros para búsqueda de pins"""
    category: Optional[str] = None
    season: Optional[str] = None
    price_range: Optional[str] = None


# ── Response DTOs ─────────────────────────────────────────────

class PinListResponse(BaseModel):
    """Respuesta paginada de pins completos"""
    pins: List[PinResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class PinSummaryListResponse(BaseModel):
    """Respuesta paginada de pins resumidos (para grids)"""
    pins: List[PinSummary]
    total: int
    limit: int
    offset: int
    has_more: bool


class PinFeedResponse(BaseModel):
    """Feed de pins"""
    pins: List[PinResponse]
    limit: int
    offset: int
    has_more: bool


class PinTrendingResponse(BaseModel):
    """Pins trending"""
    pins: List[PinSummary]
    hours: int


class MessageResponse(BaseModel):
    """Respuesta genérica"""
    message: str