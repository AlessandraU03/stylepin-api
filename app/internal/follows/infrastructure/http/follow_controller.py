"""
Controlador HTTP de Follows
"""
import logging

from internal.follows.application.use_cases.follow_user import FollowUserUseCase
from internal.follows.application.use_cases.unfollow_user import UnfollowUserUseCase
from internal.follows.application.use_cases.get_followers import GetFollowersUseCase
from internal.follows.application.use_cases.get_following import GetFollowingUseCase
from internal.follows.application.use_cases.check_follow_status import CheckFollowStatusUseCase
from internal.follows.application.use_cases.get_follow_counts import GetFollowCountsUseCase

from internal.follows.domain.entities.follow import Follow, FollowerProfile, FollowingProfile
from internal.follows.application.schemas.follow_schemas import (
    FollowUserRequest,
    FollowersListResponse,
    FollowingListResponse,
    FollowStatusResponse,
    FollowCountsResponse,
    MessageResponse,
)
from core.notifications import notify_new_follow

logger = logging.getLogger(__name__)


class FollowController:
    def __init__(
        self,
        follow_uc: FollowUserUseCase,
        unfollow_uc: UnfollowUserUseCase,
        get_followers_uc: GetFollowersUseCase,
        get_following_uc: GetFollowingUseCase,
        check_status_uc: CheckFollowStatusUseCase,
        get_counts_uc: GetFollowCountsUseCase,
        db_session=None,
    ):
        self._follow_uc = follow_uc
        self._unfollow_uc = unfollow_uc
        self._get_followers_uc = get_followers_uc
        self._get_following_uc = get_following_uc
        self._check_status_uc = check_status_uc
        self._get_counts_uc = get_counts_uc
        self._db = db_session

    # ── Follow / Unfollow ─────────────────────────────────────

    async def follow_user(self, body: FollowUserRequest, current_user_id: str) -> MessageResponse:
        await self._follow_uc.execute(
            follower_id=current_user_id,
            following_id=body.user_id,
        )

        # 🔔 Notificar al usuario seguido
        try:
            await self._send_follow_notification(current_user_id, body.user_id)
        except Exception as e:
            logger.warning(f"⚠️ No se pudo enviar notificación de follow: {e}")

        return MessageResponse(message="Ahora sigues a este usuario")

    async def unfollow_user(self, target_user_id: str, current_user_id: str) -> MessageResponse:
        await self._unfollow_uc.execute(
            follower_id=current_user_id,
            following_id=target_user_id,
        )
        return MessageResponse(message="Dejaste de seguir a este usuario")

    # ── Notificación ──────────────────────────────────────────

    async def _send_follow_notification(self, follower_id: str, followed_id: str):
        """Obtiene username del follower y envía notificación"""
        if not self._db:
            return

        from core.database.models import UserModel

        follower = self._db.query(UserModel).filter(UserModel.id == follower_id).first()
        follower_username = follower.username if follower else "alguien"

        await notify_new_follow(
            followed_user_id=followed_id,
            follower_username=follower_username,
            follower_id=follower_id,
        )
        logger.info(f"🔔 Follow: {follower_username} → {followed_id}")

    # ── Listas ────────────────────────────────────────────────

    async def get_followers(
        self,
        user_id: str,
        current_user_id: str = None,
        limit: int = 50,
        offset: int = 0,
    ) -> FollowersListResponse:
        result = await self._get_followers_uc.execute(
            user_id=user_id, limit=limit, offset=offset
        )

        profiles = []
        for follow in result["followers"]:
            is_following_back = False
            if current_user_id:
                status = await self._check_status_uc.execute(
                    current_user_id, follow.follower_id
                )
                is_following_back = status["is_following"]

            profiles.append(FollowerProfile(
                user_id=follow.follower_id,
                username="",
                full_name="",
                avatar_url=None,
                is_verified=False,
                is_following_back=is_following_back,
            ))

        return FollowersListResponse(
            followers=profiles,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    async def get_following(
        self,
        user_id: str,
        current_user_id: str = None,
        limit: int = 50,
        offset: int = 0,
    ) -> FollowingListResponse:
        result = await self._get_following_uc.execute(
            user_id=user_id, limit=limit, offset=offset
        )

        profiles = []
        for follow in result["following"]:
            is_followed_by_me = False
            if current_user_id:
                status = await self._check_status_uc.execute(
                    current_user_id, follow.following_id
                )
                is_followed_by_me = status["is_following"]

            profiles.append(FollowingProfile(
                user_id=follow.following_id,
                username="",
                full_name="",
                avatar_url=None,
                is_verified=False,
                is_followed_by_me=is_followed_by_me,
            ))

        return FollowingListResponse(
            following=profiles,
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    # ── Status / Counts ───────────────────────────────────────

    async def check_follow_status(
        self, current_user_id: str, target_user_id: str
    ) -> FollowStatusResponse:
        result = await self._check_status_uc.execute(current_user_id, target_user_id)
        return FollowStatusResponse(
            is_following=result["is_following"],
            is_followed_by=result["is_followed_by"],
            are_mutual=result["are_mutual"],
        )

    async def get_follow_counts(self, user_id: str) -> FollowCountsResponse:
        result = await self._get_counts_uc.execute(user_id)
        return FollowCountsResponse(
            user_id=result["user_id"],
            followers_count=result["followers_count"],
            following_count=result["following_count"],
        )