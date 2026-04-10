"""
Interfaz del repositorio de Notificaciones
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from internal.notifications.domain.entities.notification import Notification


class NotificationRepository(ABC):
    
    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        """Crear una notificación"""
        pass
    
    @abstractmethod
    async def get_by_id(self, notification_id: str) -> Optional[Notification]:
        """Obtener notificación por ID"""
        pass
    
    @abstractmethod
    async def get_by_user_id(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """Obtener notificaciones de un usuario"""
        pass
    
    @abstractmethod
    async def count_by_user_id(self, user_id: str) -> int:
        """Contar notificaciones de un usuario"""
        pass
    
    @abstractmethod
    async def mark_as_read(self, notification_id: str) -> Notification:
        """Marcar notificación como leída"""
        pass
    
    @abstractmethod
    async def delete(self, notification_id: str) -> bool:
        """Eliminar una notificación"""
        pass