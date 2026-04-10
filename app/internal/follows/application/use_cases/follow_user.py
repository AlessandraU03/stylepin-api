"""
Caso de uso: Seguir a un usuario
"""
from datetime import datetime, timezone
from app.core.notifications import notify_new_follow
from internal.follows.domain.entities.follow import Follow
from internal.follows.domain.repositories.follow_repository import FollowRepository
from internal.users.domain.repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)

class FollowUserUseCase:
    def __init__(
        self,
        follow_repository: FollowRepository,
        user_repository: UserRepository
    ):
        self._repo = follow_repository
        self._user_repo = user_repository

    async def execute(self, follower_id: str, following_id: str) -> Follow:
        """
        Ejecutar el caso de uso de seguir a un usuario
        """
        if follower_id == following_id:
            raise ValueError("No puedes seguirte a ti mismo")

        already_following = await self._repo.exists(follower_id, following_id)
        if already_following:
            raise ValueError("Ya sigues a este usuario")

        # Crear follow
        now = datetime.now(timezone.utc)
        follow = Follow(
            id="",
            follower_id=follower_id,
            following_id=following_id,
            created_at=now,
        )

        created = await self._repo.create(follow)

        # 🔔 Notificar al usuario que fue seguido
        target_user = await self._user_repo.get_by_id(following_id)
        follower_user = await self._user_repo.get_by_id(follower_id)

        if target_user and follower_user:
            # ✅ OBTENER token FCM usando el repositorio
            fcm_token = await self._user_repo.get_fcm_token(following_id)
            
            if fcm_token:
                try:
                    await notify_new_follow(
                        token=fcm_token,
                        username=follower_user.username
                    )
                    logger.info(f"✅ Notificación de follow enviada a {target_user.username}")
                except Exception as e:
                    logger.error(f"❌ Error enviando notificación de follow: {e}")
            else:
                logger.warning(f"⚠️ No FCM token found for user {following_id}")

        return created