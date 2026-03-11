"""
Caso de uso: Seguir a un usuario
"""
from datetime import datetime, timezone
from internal.follows.domain.entities.follow import Follow
from internal.follows.domain.repositories.follow_repository import FollowRepository


class FollowUserUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self._repo = follow_repository

    async def execute(self, follower_id: str, following_id: str) -> Follow:
        # No puedes seguirte a ti mismo
        if follower_id == following_id:
            raise ValueError("No puedes seguirte a ti mismo")

        # Verificar si ya lo sigues
        already_following = await self._repo.exists(follower_id, following_id)
        if already_following:
            raise ValueError("Ya sigues a este usuario")

        now = datetime.now(timezone.utc)
        follow = Follow(
            id="",
            follower_id=follower_id,
            following_id=following_id,
            created_at=now,
        )

        return await self._repo.create(follow)