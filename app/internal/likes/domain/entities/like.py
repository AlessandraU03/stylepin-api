"""
Entidades de dominio para Likes
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Like(BaseModel):
    """
    Entidad de dominio Like
    """
    id: str
    user_id: str
    pin_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LikeResponse(BaseModel):
    """Like con información del usuario"""
    id: str
    user_id: str
    user_username: str
    user_full_name: str
    user_avatar_url: Optional[str] = None
    pin_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True