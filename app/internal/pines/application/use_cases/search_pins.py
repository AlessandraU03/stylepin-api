"""
Caso de uso: Buscar pins
"""
from internal.pines.domain.repositories.pin_repository import PinRepository


class SearchPinsUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        if not query or len(query.strip()) == 0:
            raise ValueError("El término de búsqueda no puede estar vacío")

        pins = await self._repo.search(
            query=query.strip(), limit=limit, offset=offset
        )

        return {
            "pins": pins,
            "total": len(pins),
            "limit": limit,
            "offset": offset,
            "has_more": len(pins) >= limit,
        }