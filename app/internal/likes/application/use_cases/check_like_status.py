"""
Caso de uso: Verificar si un usuario dio like a un pin
"""
from internal.likes.domain.repositories.like_repository import LikeRepository


class CheckLikeStatusUseCase:
    def __init__(self, like_repository: LikeRepository):
        self._repo = like_repository

    async def execute(self, user_id: str, pin_id: str) -> dict:
        is_liked = await self._repo.exists(user_id, pin_id)
        likes_count = await self._repo.count_by_pin(pin_id)

        return {
            "pin_id": pin_id,
            "is_liked": is_liked,
            "likes_count": likes_count,
        }