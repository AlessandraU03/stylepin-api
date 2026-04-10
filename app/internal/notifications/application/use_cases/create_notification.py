"""
Caso de uso: Crear notificación
"""
import logging
import uuid
from datetime import datetime, timezone

from internal.notifications.domain.entities.notification import Notification
from internal.notifications.domain.repository.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


class CreateNotificationUseCase:
    
    def __init__(self, notification_repository: NotificationRepository):
        self.notification_repository = notification_repository
    
    async def execute(
        self,
        user_id: str,
        actor_id: str,
        notification_type: str,
        title: str,
        body: str,
        pin_id: str = None,
        comment_id: str = None,
        board_id: str = None
    ) -> Notification:
        """Crear una notificación"""
        try:
            notification = Notification(
                id=str(uuid.uuid4()),
                user_id=user_id,
                actor_id=actor_id,
                type=notification_type,
                title=title,
                body=body,
                pin_id=pin_id,
                comment_id=comment_id,
                board_id=board_id,
                is_read=False,
                created_at=datetime.now(timezone.utc)
            )
            
            result = await self.notification_repository.create(notification)
            logger.info(f"✅ Notificación creada: {notification.id}")
            
            return result
        except Exception as e:
            logger.error(f"❌ Error creando notificación: {e}")
            raise ValueError(f"Error al crear notificación: {str(e)}")