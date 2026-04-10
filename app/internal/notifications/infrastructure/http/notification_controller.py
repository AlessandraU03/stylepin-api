"""
Controlador HTTP de Notificaciones
"""
import logging
from typing import List

from internal.notifications.domain.entities.notification import Notification
from internal.notifications.application.use_cases.get_notification import GetNotificationsUseCase
from internal.notifications.application.use_cases.mark_notification_read import MarkNotificationAsReadUseCase
from internal.notifications.application.use_cases.create_notification import CreateNotificationUseCase

logger = logging.getLogger(__name__)


class NotificationController:
    def __init__(
        self,
        get_notifications_uc: GetNotificationsUseCase,
        mark_as_read_uc: MarkNotificationAsReadUseCase,
        create_notification_uc: CreateNotificationUseCase
    ):
        self._get_notifications_uc = get_notifications_uc
        self._mark_as_read_uc = mark_as_read_uc
        self._create_notification_uc = create_notification_uc

    async def get_notifications(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ):
        """Obtener notificaciones del usuario"""
        try:
            result = await self._get_notifications_uc.execute(user_id, limit, offset)
            return result
        except Exception as e:
            logger.error(f"❌ Error getting notifications: {e}")
            raise

    async def mark_as_read(self, notification_id: str, user_id: str):
        """Marcar notificación como leída"""
        try:
            result = await self._mark_as_read_uc.execute(notification_id, user_id)
            logger.info(f"✅ Notificación {notification_id} marcada como leída")
            return result
        except Exception as e:
            logger.error(f"❌ Error marking notification as read: {e}")
            raise

    async def create_notification(
        self,
        user_id: str,
        actor_id: str,
        notification_type: str,
        title: str,
        body: str,
        pin_id: str = None,
        comment_id: str = None,
        board_id: str = None
    ):
        """Crear una notificación"""
        try:
            result = await self._create_notification_uc.execute(
                user_id=user_id,
                actor_id=actor_id,
                notification_type=notification_type,
                title=title,
                body=body,
                pin_id=pin_id,
                comment_id=comment_id,
                board_id=board_id
            )
            return result
        except Exception as e:
            logger.error(f"❌ Error creating notification: {e}")
            raise