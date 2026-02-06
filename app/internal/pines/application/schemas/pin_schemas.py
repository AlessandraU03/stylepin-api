"""
DTOs (Data Transfer Objects) para Pins
Esquemas de entrada y salida de la API
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class CreatePinRequest(BaseModel):
    """DTO para crear un pin"""
    image_url: str = Field(
        ..., 
        example="https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3",
        description="URL de la imagen del outfit"
    )
    title: str = Field(
        ..., 
        min_length=1, 
        max_length=200, 
        example="Look casual viernes",
        description="Título del pin"
    )
    description: Optional[str] = Field(
        None, 
        example="Perfecto para café con amigas ☕️",
        description="Descripción detallada"
    )
    
    # Categorización
    category: str = Field(
        ..., 
        example="outfit_completo",
        description="Categoría: outfit_completo, prenda_individual, accesorio, calzado"
    )
    styles: List[str] = Field(
        default=[], 
        example=["Casual", "Minimalista"],
        description="Estilos de moda"
    )
    occasions: List[str] = Field(
        default=[], 
        example=["Diario", "Trabajo"],
        description="Ocasiones de uso"
    )
    season: str = Field(
        default="todo_el_ano", 
        example="primavera",
        description="Temporada: primavera, verano, otono, invierno, todo_el_ano"
    )
    
    # Shopping
    brands: List[str] = Field(
        default=[], 
        example=["Zara", "H&M"],
        description="Marcas de las prendas"
    )
    price_range: str = Field(
        default="bajo_500", 
        example="500_1000",
        description="Rango de precio: bajo_500, 500_1000, 1000_2000, mas_2000"
    )
    where_to_buy: Optional[str] = Field(
        None, 
        example="Zara Plaza Boulevares",
        description="Dónde comprar"
    )
    purchase_link: Optional[str] = Field(
        None, 
        example="https://www.zara.com/mx/",
        description="Link de compra"
    )
    
    # Metadata
    colors: List[str] = Field(
        default=[], 
        example=["#000000", "#FFFFFF", "#808080"],
        description="Colores principales en hexadecimal"
    )
    tags: List[str] = Field(
        default=[], 
        example=["casual", "weekend", "comfortable"],
        description="Tags/hashtags personalizados"
    )
    is_private: bool = Field(
        default=False, 
        example=False,
        description="Pin privado o público"
    )

class UpdatePinRequest(BaseModel):
    """DTO para actualizar un pin (todos los campos opcionales)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
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
    """DTO para filtros de búsqueda en el feed"""
    category: Optional[str] = Field(
        None,
        description="Filtrar por categoría"
    )
    season: Optional[str] = Field(
        None,
        description="Filtrar por temporada"
    )
    user_id: Optional[str] = Field(
        None,
        description="Filtrar por ID de usuario"
    )
    limit: int = Field(
        default=20, 
        ge=1, 
        le=100,
        description="Número de resultados"
    )
    offset: int = Field(
        default=0, 
        ge=0,
        description="Offset para paginación"
    )