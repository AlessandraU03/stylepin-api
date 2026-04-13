"""
Caso de uso: Seguir usuario - CORREGIDO
Guarda notificación en DB + envía push FCM
"""
import uuid
import logging
from datetime import datetime, timezone

from app.core.notifications import notify_new_follow
from internal.follows.domain.entities.follow import Follow
from internal.follows.domain.repositories.follow_repository import FollowRepository
from internal.users.domain.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class FollowUserUseCase:

    def __init__(
        self,
        follow_repository: FollowRepository,
        user_repository: UserRepository,
        notification_repository=None,
    ):
        self._repo              = follow_repository
        self._user_repo         = user_repository
        self._notification_repo = notification_repository

    async def execute(self, follower_id: str, following_id: str) -> Follow:
        if follower_id == following_id:
            raise ValueError("No puedes seguirte a ti mismo")

        already_following = await self._repo.exists(follower_id, following_id)
        if already_following:
            raise ValueError("Ya sigues a este usuario")

        now = datetime.now(timezone.utc)
        follow = Follow(id="", follower_id=follower_id, following_id=following_id, created_at=now)
        created = await self._repo.create(follow)

        target_user   = await self._user_repo.get_by_id(following_id)
        follower_user = await self._user_repo.get_by_id(follower_id)

        if target_user and follower_user:

            # 1. Guardar en tabla notifications
            if self._notification_repo:
                try:
                    from internal.notifications.domain.entities.notification import Notification as NotificationEntity
                    notif = NotificationEntity(
                        id=str(uuid.uuid4()),
                        user_id=following_id,
                        actor_id=follower_id,
                        type="follow",
                        title="Nuevo seguidor 👤",
                        body=f"{follower_user.username} empezó a seguirte",
                        is_read=False,
                        created_at=datetime.now(timezone.utc),
                    )
                    await self._notification_repo.create(notif)
                    logger.info("✅ Notificación de follow guardada en DB")
                except Exception as e:
                    logger.error(f"❌ Error guardando notificación de follow: {e}")

            # 2. Enviar push FCM
            fcm_token = await self._user_repo.get_fcm_token(following_id)
            if fcm_token:
                try:
                    await notify_new_follow(token=fcm_token, username=follower_user.username)
                    logger.info(f"✅ Push de follow enviado a {target_user.username}")
                except Exception as e:
                    logger.error(f"❌ Error enviando push de follow: {e}")

        return created