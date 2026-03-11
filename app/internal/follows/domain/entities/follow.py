"""
Entidades de dominio para Follows
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Follow(BaseModel):
    """
    Entidad de dominio Follow
    """
    id: str
    follower_id: str
    following_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class FollowResponse(BaseModel):
    """Follow con información del usuario"""
    id: str
    follower_id: str
    follower_username: str
    follower_full_name: str
    follower_avatar_url: Optional[str] = None
    follower_is_verified: bool
    following_id: str
    following_username: str
    following_full_name: str
    following_avatar_url: Optional[str] = None
    following_is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class FollowerProfile(BaseModel):
    """Perfil de seguidor"""
    user_id: str
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    is_verified: bool
    is_following_back: bool = False
    
    class Config:
        from_attributes = True

class FollowingProfile(BaseModel):
    """Perfil de seguido"""
    user_id: str
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    is_verified: bool
    is_followed_by_me: bool = True
    
    class Config:
        from_attributes = True