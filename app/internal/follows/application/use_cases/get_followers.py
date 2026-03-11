"""
Caso de uso: Obtener seguidores de un usuario
"""
from internal.follows.domain.repositories.follow_repository import FollowRepository


class GetFollowersUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self._repo = follow_repository

    async def execute(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        followers = await self._repo.get_followers(
            user_id=user_id, limit=limit, offset=offset
        )
        total = await self._repo.count_followers(user_id)

        return {
            "followers": followers,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
        }