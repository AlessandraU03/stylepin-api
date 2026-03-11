"""
Caso de uso: Dar like a un pin
"""
from datetime import datetime, timezone
from internal.likes.domain.entities.like import Like
from internal.likes.domain.repositories.like_repository import LikeRepository


class LikePinUseCase:
    def __init__(self, like_repository: LikeRepository):
        self._repo = like_repository

    async def execute(self, user_id: str, pin_id: str) -> Like:
        # Verificar si ya dio like
        already_liked = await self._repo.exists(user_id, pin_id)
        if already_liked:
            raise ValueError("Ya diste like a este pin")

        now = datetime.now(timezone.utc)
        like = Like(
            id="",
            user_id=user_id,
            pin_id=pin_id,
            created_at=now,
        )

        return await self._repo.create(like)