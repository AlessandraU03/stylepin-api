"""
Caso de uso: Obtener pins trending
"""
from internal.pines.domain.repositories.pin_repository import PinRepository


class GetTrendingUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(
        self,
        limit: int = 20,
        hours: int = 24,
    ) -> dict:
        pins = await self._repo.get_trending(limit=limit, hours=hours)

        return {
            "pins": pins,
            "hours": hours,
        }