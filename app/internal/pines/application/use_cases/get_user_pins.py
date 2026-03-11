"""
Caso de uso: Obtener pins de un usuario
"""
from internal.pines.domain.repositories.pin_repository import PinRepository


class GetUserPinsUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(
        self,
        user_id: str,
        requesting_user_id: str = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        # Si es el propio usuario, incluir privados
        include_private = (requesting_user_id == user_id)

        pins = await self._repo.get_by_user(
            user_id=user_id,
            limit=limit,
            offset=offset,
            include_private=include_private,
        )

        return {
            "pins": pins,
            "total": len(pins),
            "limit": limit,
            "offset": offset,
            "has_more": len(pins) >= limit,
        }