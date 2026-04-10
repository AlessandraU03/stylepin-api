"""
Caso de uso: Crear comentario
"""
from datetime import datetime, timezone
from app.core.notifications import notify_new_comment
from internal.comments.domain.entities.comment import Comment
from internal.comments.domain.repositories.comment_repository import CommentRepository
from internal.users.domain.repositories.user_repository import UserRepository
from internal.pines.domain.repositories.pin_repository import PinRepository
import logging

logger = logging.getLogger(__name__)

class CreateCommentUseCase:
    def __init__(
        self,
        comment_repository: CommentRepository,
        user_repository: UserRepository,
        pin_repository: PinRepository
    ):
        self._repo = comment_repository
        self._user_repo = user_repository
        self._pin_repo = pin_repository

    async def execute(
        self,
        user_id: str,
        pin_id: str,
        content: str
    ) -> Comment:
        """
        Ejecutar el caso de uso de crear comentario
        """
        # Validar que el pin existe
        pin = await self._pin_repo.get_by_id(pin_id)
        if not pin:
            raise ValueError("Pin no encontrado")

        # Validar que el usuario existe
        commenter = await self._user_repo.get_by_id(user_id)
        if not commenter:
            raise ValueError("Usuario no encontrado")

        # Crear comentario
        now = datetime.now(timezone.utc)
        comment = Comment(
            id="",
            pin_id=pin_id,
            user_id=user_id,
            content=content,
            created_at=now,
        )

        created = await self._repo.create(comment)

        # 🔔 Notificar al dueño del pin si no es el mismo usuario
        if pin.user_id != user_id:
            pin_owner = await self._user_repo.get_by_id(pin.user_id)
            
            if pin_owner:
                # ✅ OBTENER token FCM usando el repositorio
                fcm_token = await self._user_repo.get_fcm_token(pin.user_id)
                
                if fcm_token:
                    try:
                        await notify_new_comment(
                            token=fcm_token,
                            username=commenter.username,
                            comment=content[:100]
                        )
                        logger.info(f"✅ Notificación de comentario enviada a {pin_owner.username}")
                    except Exception as e:
                        logger.error(f"❌ Error enviando notificación de comentario: {e}")
                else:
                    logger.warning(f"⚠️ No FCM token found for user {pin.user_id}")

        return created