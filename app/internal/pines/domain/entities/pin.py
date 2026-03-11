"""
Entidades de dominio para Pins
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

class Pin(BaseModel):
    """
    Entidad de dominio Pin - Publicación de moda
    """
    id: str
    user_id: str
    image_url: str
    title: str
    description: Optional[str] = None
    category: str
    styles: List[str] = []
    occasions: List[str] = []
    season: str = "todo_el_ano"
    brands: List[str] = []
    price_range: str = "bajo_500"
    where_to_buy: Optional[str] = None
    purchase_link: Optional[str] = None
    likes_count: int = 0
    saves_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    colors: List[str] = []
    tags: List[str] = []
    is_private: bool = False
    created_at: datetime
    updated_at: datetime
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Title cannot be empty')
        if len(v) > 200:
            raise ValueError('Title cannot exceed 200 characters')
        return v.strip()
    
    @field_validator('image_url')
    @classmethod
    def validate_image_url(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Image URL is required')
        return v.strip()
    
    class Config:
        from_attributes = True

class PinResponse(BaseModel):
    """Pin con información del usuario"""
    id: str
    user_id: str
    user_username: str
    user_full_name: str
    user_avatar_url: Optional[str] = None
    user_is_verified: bool = False
    image_url: str
    title: str
    description: Optional[str] = None
    category: str
    styles: List[str]
    occasions: List[str]
    season: str
    brands: List[str]
    price_range: str
    where_to_buy: Optional[str] = None
    purchase_link: Optional[str] = None
    likes_count: int
    saves_count: int
    comments_count: int
    views_count: int
    colors: List[str]
    tags: List[str]
    is_private: bool
    created_at: datetime
    updated_at: datetime
    is_liked_by_me: bool = False
    is_saved_by_me: bool = False
    
    class Config:
        from_attributes = True

class PinSummary(BaseModel):
    """Versión resumida para listas/grids"""
    id: str
    user_id: str
    user_username: str
    user_avatar_url: Optional[str] = None
    image_url: str
    title: str
    category: str
    likes_count: int
    saves_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True