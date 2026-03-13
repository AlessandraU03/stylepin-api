from app.internal.pines.domain.repositories.pin_repository import PinRepository
from internal.likes.domain.repositories.like_repository import LikeRepository

class UnlikePinUseCase:
    def __init__(self, like_repository: LikeRepository, pin_repository: PinRepository):
        self._repo = like_repository
        self._pin_repo = pin_repository

    async def execute(self, user_id: str, pin_id: str) -> bool:
        exists = await self._repo.exists(user_id, pin_id)
        if not exists:
            raise ValueError("No has dado like a este pin")

        deleted = await self._repo.delete(user_id, pin_id)
        if deleted:
            await self._pin_repo.decrement_likes(pin_id)  # <-- AGREGA ESTA LÍNEA
        return deleted