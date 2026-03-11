"""
Caso de uso: Obtener contadores de seguidores/seguidos
"""
from internal.follows.domain.repositories.follow_repository import FollowRepository


class GetFollowCountsUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self._repo = follow_repository

    async def execute(self, user_id: str) -> dict:
        followers_count = await self._repo.count_followers(user_id)
        following_count = await self._repo.count_following(user_id)

        return {
            "user_id": user_id,
            "followers_count": followers_count,
            "following_count": following_count,
        }