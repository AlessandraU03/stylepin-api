"""
Caso de uso: Obtener lista de pins con filtros
"""
from typing import Optional
from internal.pines.domain.repositories.pin_repository import PinRepository


class GetPinsUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(
        self,
        limit: int = 20,
        offset: int = 0,
        category: Optional[str] = None,
        season: Optional[str] = None,
        price_range: Optional[str] = None,
    ) -> dict:
        pins = await self._repo.get_all(
            limit=limit,
            offset=offset,
            category=category,
            season=season,
            price_range=price_range,
        )

        return {
            "pins": pins,
            "total": len(pins),
            "limit": limit,
            "offset": offset,
            "has_more": len(pins) >= limit,
        }