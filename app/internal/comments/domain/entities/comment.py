"""
Entidades de dominio para Comments
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

class Comment(BaseModel):
    """
    Entidad de dominio Comment
    """
    id: str
    pin_id: str
    user_id: str
    text: str
    parent_comment_id: Optional[str] = None
    likes_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if not v or len(v.strip()) == 0:
            raise ValueError('Comment text cannot be empty')
        if len(v) > 5000:
            raise ValueError('Comment text cannot exceed 5000 characters')
        return v.strip()
    
    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    """Comment con información del usuario"""
    id: str
    pin_id: str
    user_id: str
    user_username: str
    user_full_name: str
    user_avatar_url: Optional[str] = None
    user_is_verified: bool
    text: str
    parent_comment_id: Optional[str] = None
    likes_count: int
    created_at: datetime
    updated_at: datetime
    is_edited: bool = False
    can_edit: bool = False
    can_delete: bool = False
    replies_count: int = 0
    
    class Config:
        from_attributes = True

class CommentWithReplies(BaseModel):
    """Comment con respuestas anidadas"""
    id: str
    pin_id: str
    user_id: str
    user_username: str
    user_full_name: str
    user_avatar_url: Optional[str] = None
    user_is_verified: bool
    text: str
    parent_comment_id: Optional[str] = None
    likes_count: int
    created_at: datetime
    updated_at: datetime
    is_edited: bool = False
    can_edit: bool = False
    can_delete: bool = False
    replies: List['CommentWithReplies'] = []
    
    class Config:
        from_attributes = True

# Para resolver la referencia circular
CommentWithReplies.model_rebuild()