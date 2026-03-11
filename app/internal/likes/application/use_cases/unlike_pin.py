"""
Caso de uso: Quitar like de un pin
"""
from internal.likes.domain.repositories.like_repository import LikeRepository


class UnlikePinUseCase:
    def __init__(self, like_repository: LikeRepository):
        self._repo = like_repository

    async def execute(self, user_id: str, pin_id: str) -> bool:
        exists = await self._repo.exists(user_id, pin_id)
        if not exists:
            raise ValueError("No has dado like a este pin")

        return await self._repo.delete(user_id, pin_id)