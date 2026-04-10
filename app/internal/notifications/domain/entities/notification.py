"""
Entidad: Notificación
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Notification:
    id: str
    user_id: str
    actor_id: str  # ✅ AGREGAR: Quién realiza la acción
    type: str  # "like", "follow", "comment", "board_collaboration"
    title: str
    body: str
    is_read: bool = False
    pin_id: Optional[str] = None  # ✅ AGREGAR
    comment_id: Optional[str] = None  # ✅ AGREGAR
    board_id: Optional[str] = None  # ✅ AGREGAR
    created_at: Optional[datetime] = None
    read_at: Optional[datetime] = None  # ✅ AGREGAR