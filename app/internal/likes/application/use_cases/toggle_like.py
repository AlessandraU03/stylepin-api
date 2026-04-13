"""
Caso de uso: Toggle Like (dar/quitar like) - CORREGIDO

PROBLEMA: Solo enviaba push FCM pero NO guardaba en la tabla notifications.
La pantalla de Notificaciones consulta la DB → siempre vacía.

CORRECCIÓN: Guardar en notifications PRIMERO, luego enviar push FCM.
"""
import uuid
import logging
from datetime import datetime, timezone

from app.core.notifications import notify_new_like
from internal.likes.domain.entities.like import Like
from internal.likes.domain.repositories.like_repository import LikeRepository
from internal.pines.domain.repositories.pin_repository import PinRepository
from internal.users.domain.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)


class ToggleLikeUseCase:

    def __init__(
        self,
        like_repository: LikeRepository,
        pin_repository: PinRepository,
        user_repository: UserRepository,
        notification_repository=None,   # ← NUEVO: para guardar en DB
    ):
        self.like_repository = like_repository
        self.pin_repository = pin_repository
        self.user_repository = user_repository
        self.notification_repository = notification_repository  # puede ser None sin romper

    async def execute(self, user_id: str, pin_id: str) -> dict:
        """Toggle like en un pin."""

        # 1. Verificar que el pin existe
        pin = await self.pin_repository.get_by_id(pin_id)
        if not pin:
            raise ValueError("Pin not found")

        # 2. Verificar si ya existe el like
        exists = await self.like_repository.exists(user_id, pin_id)

        if exists:
            # ── QUITAR LIKE ──────────────────────────────────────
            await self.like_repository.delete(user_id, pin_id)
            await self.pin_repository.decrement_likes(pin_id)
            updated_pin = await self.pin_repository.get_by_id(pin_id)
            return {
                "pin_id": pin_id,
                "is_liked": False,
                "likes_count": updated_pin.likes_count,
            }

        else:
            # ── DAR LIKE ─────────────────────────────────────────
            like = Like(
                id=str(uuid.uuid4()),
                user_id=user_id,
                pin_id=pin_id,
                created_at=datetime.now(timezone.utc),
            )
            await self.like_repository.create(like)
            await self.pin_repository.increment_likes(pin_id)

            # Obtener datos necesarios
            pin_owner    = await self.user_repository.get_by_id(pin.user_id)
            user_who_liked = await self.user_repository.get_by_id(user_id)
            updated_pin  = await self.pin_repository.get_by_id(pin_id)

            # Solo notificar si el que da like NO es el dueño del pin
            if pin_owner and user_who_liked and pin.user_id != user_id:

                # ── 1. GUARDAR EN TABLA notifications (lo que faltaba) ──
                if self.notification_repository:
                    try:
                        from internal.notifications.domain.entities.notification import (
                            Notification as NotificationEntity,
                        )
                        notif = NotificationEntity(
                            id=str(uuid.uuid4()),
                            user_id=pin.user_id,          # quién recibe
                            actor_id=user_id,             # quién hizo la acción
                            type="like",
                            title="Nuevo Like ❤️",
                            body=f"A {user_who_liked.username} le gustó tu pin",
                            pin_id=pin_id,
                            is_read=False,
                            created_at=datetime.now(timezone.utc),
                        )
                        await self.notification_repository.create(notif)
                        logger.info(f"✅ Notificación de like guardada en DB")
                    except Exception as e:
                        logger.error(f"❌ Error guardando notificación de like: {e}")

                # ── 2. Enviar push FCM ───────────────────────────────────
                fcm_token = await self.user_repository.get_fcm_token(pin.user_id)
                if fcm_token:
                    try:
                        await notify_new_like(
                            token=fcm_token,
                            username=user_who_liked.username,
                        )
                        logger.info(f"✅ Push de like enviado a {pin_owner.username}")
                    except Exception as e:
                        logger.error(f"❌ Error enviando push de like: {e}")
                else:
                    logger.warning(f"⚠️ Sin FCM token para usuario {pin.user_id}")

            return {
                "pin_id": pin_id,
                "is_liked": True,
                "likes_count": updated_pin.likes_count,
            }