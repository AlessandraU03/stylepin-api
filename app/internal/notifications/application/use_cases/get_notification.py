"""
Caso de uso: Obtener notificaciones
"""
import logging
from typing import List

from internal.notifications.domain.entities.notification import Notification
from internal.notifications.domain.repository.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


class GetNotificationsUseCase:
    
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository
    
    async def execute(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> dict:
        """Obtener notificaciones del usuario"""
        try:
            notifications = await self.notification_repository.get_by_user_id(
                user_id,
                limit=limit,
                offset=offset
            )
            
            total = await self.notification_repository.count_by_user_id(user_id)
            
            return {
                "notifications": notifications,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": (offset + limit) < total
            }
        except Exception as e:
            logger.error(f"❌ Error obteniendo notificaciones: {e}")
            raise ValueError(f"Error al obtener notificaciones: {str(e)}")