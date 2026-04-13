"""
Adaptador MySQL para Notificaciones
"""
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from core.database.models import Notification
from internal.notifications.domain.entities.notification import Notification as NotificationEntity
from internal.notifications.domain.repository.notification_repository import NotificationRepository

logger = logging.getLogger(__name__)


class MySQLNotificationRepository(NotificationRepository):
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, notification: NotificationEntity) -> NotificationEntity:
        try:
            db_notification = Notification(
                id=notification.id,
                user_id=notification.user_id,
                actor_id=notification.actor_id,
                type=notification.type,
                pin_id=notification.pin_id,
                comment_id=notification.comment_id,
                board_id=notification.board_id,
                title=notification.title,
                body=notification.body,
                is_read=False
            )
            self.db.add(db_notification)
            self.db.commit()
            self.db.refresh(db_notification)
            logger.info(f"✅ Notificación creada: {notification.id}")
            return self._to_domain(db_notification)
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error creando notificación: {e}")
            raise

    async def get_by_id(self, notification_id: str) -> Optional[NotificationEntity]:
        try:
            db_notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            if not db_notification:
                return None
            return self._to_domain(db_notification)
        except Exception as e:
            logger.error(f"❌ Error obteniendo notificación: {e}")
            raise

    async def get_by_user_id(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> List[NotificationEntity]:
        try:
            notifications = self.db.query(Notification).filter(
                Notification.user_id == user_id
            ).order_by(
                desc(Notification.created_at)
            ).limit(limit).offset(offset).all()
            return [self._to_domain(n) for n in notifications]
        except Exception as e:
            logger.error(f"❌ Error obteniendo notificaciones: {e}")
            raise

    async def count_by_user_id(self, user_id: str) -> int:
        try:
            return self.db.query(Notification).filter(
                Notification.user_id == user_id
            ).count()
        except Exception as e:
            logger.error(f"❌ Error contando notificaciones: {e}")
            raise

    async def mark_as_read(self, notification_id: str) -> NotificationEntity:
        try:
            db_notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            if not db_notification:
                raise ValueError("Notificación no encontrada")
            db_notification.is_read = True
            db_notification.read_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(db_notification)
            logger.info(f"✅ Notificación {notification_id} marcada como leída")
            return self._to_domain(db_notification)
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error marcando notificación como leída: {e}")
            raise

    async def delete(self, notification_id: str) -> bool:
        try:
            db_notification = self.db.query(Notification).filter(
                Notification.id == notification_id
            ).first()
            if not db_notification:
                raise ValueError("Notificación no encontrada")
            self.db.delete(db_notification)
            self.db.commit()
            logger.info(f"✅ Notificación {notification_id} eliminada")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"❌ Error eliminando notificación: {e}")
            raise

    @staticmethod
    def _to_domain(db_notification: Notification) -> NotificationEntity:
        # FIX: type es ahora String(50), NO tiene .value
        # Usar hasattr por seguridad en caso de que SQLAlchemy aún cachee el enum
        notification_type = db_notification.type or "like"
        if hasattr(notification_type, 'value'):
            notification_type = notification_type.value
        notification_type = str(notification_type).lower()

        return NotificationEntity(
            id=db_notification.id,
            user_id=db_notification.user_id,
            actor_id=db_notification.actor_id,
            type=notification_type,
            pin_id=db_notification.pin_id,
            comment_id=db_notification.comment_id,
            board_id=db_notification.board_id,
            title=db_notification.title,
            body=db_notification.body,
            is_read=db_notification.is_read,
            created_at=db_notification.created_at,
            read_at=db_notification.read_at
        )