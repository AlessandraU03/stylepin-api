"""
Controlador HTTP de Likes
"""
import logging

from app.internal.likes.application.use_cases.toggle_like import ToggleLikeUseCase
from internal.likes.application.use_cases.like_pin import LikePinUseCase
from internal.likes.application.use_cases.unlike_pin import UnlikePinUseCase
from internal.likes.application.use_cases.get_pin_likes import GetPinLikesUseCase
from internal.likes.application.use_cases.get_user_likes import GetUserLikesUseCase
from internal.likes.application.use_cases.check_like_status import CheckLikeStatusUseCase

from internal.likes.domain.entities.like import Like, LikeResponse
from internal.likes.application.schemas.like_schemas import (
    LikePinRequest,
    LikeStatusResponse,
    LikesListResponse,
    UserLikesListResponse,
    MessageResponse,
)
from core.notifications import notify_new_like

logger = logging.getLogger(__name__)


class LikeController:
    def __init__(
        self,
        like_uc: LikePinUseCase,
        unlike_uc: UnlikePinUseCase,
        toggle_like_uc: ToggleLikeUseCase,
        get_pin_likes_uc: GetPinLikesUseCase,
        get_user_likes_uc: GetUserLikesUseCase,
        check_status_uc: CheckLikeStatusUseCase,
        db_session=None,
    ):
        self._like_uc = like_uc
        self._unlike_uc = unlike_uc
        self._toggle_like_uc = toggle_like_uc
        self._get_pin_likes_uc = get_pin_likes_uc
        self._get_user_likes_uc = get_user_likes_uc
        self._check_status_uc = check_status_uc
        self._db = db_session

    @staticmethod
    def _to_like_response(like: Like) -> LikeResponse:
        """Convierte entidad Like a LikeResponse"""
        return LikeResponse(
            id=like.id,
            user_id=like.user_id,
            user_username="",
            user_full_name="",
            user_avatar_url=None,
            pin_id=like.pin_id,
            created_at=like.created_at,
        )

    # ── Like / Unlike ─────────────────────────────────────────

    async def like_pin(self, body: LikePinRequest, user_id: str) -> LikeStatusResponse:
        await self._like_uc.execute(user_id=user_id, pin_id=body.pin_id)

        # Retornar estado actualizado
        result = await self._check_status_uc.execute(user_id, body.pin_id)

        # 🔔 Enviar notificación al dueño del pin
        try:
            await self._send_like_notification(user_id, body.pin_id)
        except Exception as e:
            logger.warning(f"⚠️ No se pudo enviar notificación de like: {e}")

        return LikeStatusResponse(
            pin_id=result["pin_id"],
            is_liked=result["is_liked"],
            likes_count=result["likes_count"],
        )
    
    async def toggle_like(self, body: LikePinRequest, user_id: str) -> LikeStatusResponse:
        result = await self._toggle_like_uc.execute(user_id=user_id, pin_id=body.pin_id)

        # 🔔 Enviar notificación solo si se acaba de dar like
        if result["is_liked"]:
            try:
                await self._send_like_notification(user_id, body.pin_id)
            except Exception as e:
                logger.warning(f"⚠️ No se pudo enviar notificación de like: {e}")

        return LikeStatusResponse(
            pin_id=result["pin_id"],
            is_liked=result["is_liked"],
            likes_count=result["likes_count"],
        )

    async def unlike_pin(self, pin_id: str, user_id: str) -> LikeStatusResponse:
        await self._unlike_uc.execute(user_id=user_id, pin_id=pin_id)

        result = await self._check_status_uc.execute(user_id, pin_id)
        return LikeStatusResponse(
            pin_id=result["pin_id"],
            is_liked=result["is_liked"],
            likes_count=result["likes_count"],
        )

    # ── Notificación ──────────────────────────────────────────

    async def _send_like_notification(self, liker_user_id: str, pin_id: str):
        """Obtiene info del pin y usuario, y envía notificación"""
        if not self._db:
            return

        from core.database.models import PinModel
        from core.database.models import UserModel

        # Obtener pin
        pin = self._db.query(PinModel).filter(PinModel.id == pin_id).first()
        if not pin or pin.user_id == liker_user_id:
            return  # No notificar si es tu propio pin

        # Obtener username del que dio like
        liker = self._db.query(UserModel).filter(UserModel.id == liker_user_id).first()
        liker_username = liker.username if liker else "alguien"

        await notify_new_like(
            pin_owner_id=pin.user_id,
            liker_username=liker_username,
            pin_id=pin_id,
            pin_title=pin.title or "tu pin",
        )
        logger.info(f"🔔 Notificación de like enviada a {pin.user_id}")

    # ── Listas ────────────────────────────────────────────────

    async def get_pin_likes(
        self, pin_id: str, limit: int = 50, offset: int = 0
    ) -> LikesListResponse:
        result = await self._get_pin_likes_uc.execute(
            pin_id=pin_id, limit=limit, offset=offset
        )

        responses = [self._to_like_response(like) for like in result["likes"]]

        return LikesListResponse(
            likes=responses,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    async def get_user_likes(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> UserLikesListResponse:
        result = await self._get_user_likes_uc.execute(
            user_id=user_id, limit=limit, offset=offset
        )

        responses = [self._to_like_response(like) for like in result["likes"]]

        return UserLikesListResponse(
            likes=responses,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    # ── Status ────────────────────────────────────────────────

    async def check_like_status(self, user_id: str, pin_id: str) -> LikeStatusResponse:
        result = await self._check_status_uc.execute(user_id, pin_id)
        return LikeStatusResponse(
            pin_id=result["pin_id"],
            is_liked=result["is_liked"],
            likes_count=result["likes_count"],
        )