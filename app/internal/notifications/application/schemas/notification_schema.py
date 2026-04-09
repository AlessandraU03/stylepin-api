"""
Esquemas de Notificaciones
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum


# ✅ AGREGAR ESTO
class NotificationType(str, Enum):
    LIKE = "like"
    FOLLOW = "follow"
    COMMENT = "comment"
    BOARD_COLLABORATION = "board_collaboration"


class RegisterFCMTokenRequest(BaseModel):
    device_token: str
    device_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "device_token": "f1234567890abcdef1234567890abcdef1234567",
                "device_name": "iPhone 14 Pro"
            }
        }


class NotificationResponse(BaseModel):
    id: str
    title: str
    body: str
    type: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "notif_123",
                "title": "Nuevo like",
                "body": "A alguien le gustó tu pin",
                "type": "like",
                "is_read": False,
                "created_at": "2026-04-08T10:30:00Z",
                "read_at": None
            }
        }


class FCMTokenResponse(BaseModel):
    id: str
    device_token: str
    device_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True