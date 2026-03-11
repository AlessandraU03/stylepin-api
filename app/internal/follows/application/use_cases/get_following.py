"""
Caso de uso: Obtener usuarios que sigue un usuario
"""
from internal.follows.domain.repositories.follow_repository import FollowRepository


class GetFollowingUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self._repo = follow_repository

    async def execute(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        following = await self._repo.get_following(
            user_id=user_id, limit=limit, offset=offset
        )
        total = await self._repo.count_following(user_id)

        return {
            "following": following,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
        }