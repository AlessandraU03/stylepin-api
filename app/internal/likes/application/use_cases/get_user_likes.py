"""
Caso de uso: Obtener pins que un usuario ha dado like
"""
from internal.likes.domain.repositories.like_repository import LikeRepository


class GetUserLikesUseCase:
    def __init__(self, like_repository: LikeRepository):
        self._repo = like_repository

    async def execute(
        self,
        user_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        likes = await self._repo.get_by_user(
            user_id=user_id, limit=limit, offset=offset
        )
        total = await self._repo.count_by_user(user_id)

        return {
            "likes": likes,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
        }