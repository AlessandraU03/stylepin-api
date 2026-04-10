"""
Inyección de dependencias para Notificaciones
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from core.connection import get_db
from internal.notifications.infrastructure.http.mysql_notificarion_repository import (
    MySQLNotificationRepository
)
from internal.notifications.infrastructure.http.notification_controller import (
    NotificationController
)
from internal.notifications.application.use_cases.get_notification import GetNotificationsUseCase
from internal.notifications.application.use_cases.mark_notification_read import MarkNotificationAsReadUseCase
from internal.notifications.application.use_cases.create_notification import CreateNotificationUseCase


def get_notification_controller(
    db: Session = Depends(get_db)
) -> NotificationController:
    notification_repo = MySQLNotificationRepository(db)
    
    return NotificationController(
        get_notifications_uc=GetNotificationsUseCase(notification_repo),
        mark_as_read_uc=MarkNotificationAsReadUseCase(notification_repo),
        create_notification_uc=CreateNotificationUseCase(notification_repo)
    )