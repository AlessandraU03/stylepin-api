"""
Caso de uso: Marcar notificación como leída
"""
import logging

from internal.notifications.domain.repository.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


class MarkNotificationAsReadUseCase:
    
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository
    
    async def execute(self, notification_id: str, user_id: str):
        """Marcar notificación como leída"""
        try:
            notification = await self.notification_repository.get_by_id(notification_id)
            
            if not notification or notification.user_id != user_id:
                raise ValueError("Notificación no encontrada o acceso denegado")
            
            result = await self.notification_repository.mark_as_read(notification_id)
            logger.info(f"✅ Notificación {notification_id} marcada como leída")
            
            return result
        except Exception as e:
            logger.error(f"❌ Error marcando notificación como leída: {e}")
            raise ValueError(f"Error: {str(e)}")