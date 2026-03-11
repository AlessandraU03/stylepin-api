"""
Caso de uso: Obtener likes de un pin
"""
from internal.likes.domain.repositories.like_repository import LikeRepository


class GetPinLikesUseCase:
    def __init__(self, like_repository: LikeRepository):
        self._repo = like_repository

    async def execute(
        self,
        pin_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        likes = await self._repo.get_by_pin(pin_id, limit=limit)
        total = await self._repo.count_by_pin(pin_id)

        return {
            "likes": likes,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total,
        }