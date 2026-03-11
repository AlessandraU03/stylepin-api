"""
Caso de uso: Dejar de seguir a un usuario
"""
from internal.follows.domain.repositories.follow_repository import FollowRepository


class UnfollowUserUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self._repo = follow_repository

    async def execute(self, follower_id: str, following_id: str) -> bool:
        if follower_id == following_id:
            raise ValueError("No puedes dejar de seguirte a ti mismo")

        exists = await self._repo.exists(follower_id, following_id)
        if not exists:
            raise ValueError("No sigues a este usuario")

        return await self._repo.delete(follower_id, following_id)