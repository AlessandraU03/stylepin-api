"""
Caso de uso: Crear comentario - CORREGIDO
Guarda notificación en DB + envía push FCM
"""
import uuid
import logging
from datetime import datetime, timezone

from app.core.notifications import notify_new_comment
from internal.comments.domain.entities.comment import Comment
from internal.comments.domain.repositories.comment_repository import CommentRepository
from internal.users.domain.repositories.user_repository import UserRepository
from internal.pines.domain.repositories.pin_repository import PinRepository

logger = logging.getLogger(__name__)


class CreateCommentUseCase:

    def __init__(
        self,
        comment_repository: CommentRepository,
        user_repository: UserRepository,
        pin_repository: PinRepository,
        notification_repository=None,
    ):
        self._repo              = comment_repository
        self._user_repo         = user_repository
        self._pin_repo          = pin_repository
        self._notification_repo = notification_repository

    async def execute(self, user_id: str, pin_id: str, text: str, parent_comment_id: str = None) -> Comment:
        pin = await self._pin_repo.get_by_id(pin_id)
        if not pin:
            raise ValueError("Pin no encontrado")

        commenter = await self._user_repo.get_by_id(user_id)
        if not commenter:
            raise ValueError("Usuario no encontrado")

        now = datetime.now(timezone.utc)
        comment = Comment(
            id="", pin_id=pin_id, user_id=user_id, text=text,
            parent_comment_id=parent_comment_id, likes_count=0,
            created_at=now, updated_at=now,
        )
        created = await self._repo.create(comment)

        if pin.user_id != user_id:

            # 1. Guardar en tabla notifications
            if self._notification_repo:
                try:
                    from internal.notifications.domain.entities.notification import Notification as NotificationEntity
                    notif = NotificationEntity(
                        id=str(uuid.uuid4()),
                        user_id=pin.user_id,
                        actor_id=user_id,
                        type="comment",
                        title="Nuevo comentario 💬",
                        body=f"{commenter.username} comentó: {text[:80]}",
                        pin_id=pin_id,
                        comment_id=created.id if created.id else None,
                        is_read=False,
                        created_at=datetime.now(timezone.utc),
                    )
                    await self._notification_repo.create(notif)
                    logger.info("✅ Notificación de comentario guardada en DB")
                except Exception as e:
                    logger.error(f"❌ Error guardando notificación de comentario: {e}")

            # 2. Enviar push FCM
            fcm_token = await self._user_repo.get_fcm_token(pin.user_id)
            if fcm_token:
                try:
                    await notify_new_comment(token=fcm_token, username=commenter.username, comment=text[:100])
                    logger.info("✅ Push de comentario enviado")
                except Exception as e:
                    logger.error(f"❌ Error enviando push de comentario: {e}")

        return created