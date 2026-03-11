"""
Caso de uso: Obtener feed personalizado del usuario
"""
from internal.pines.domain.repositories.pin_repository import PinRepository


class GetFeedUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        pins = await self._repo.get_feed(
            user_id=user_id, limit=limit, offset=offset
        )

        return {
            "pins": pins,
            "limit": limit,
            "offset": offset,
            "has_more": len(pins) >= limit,
        }