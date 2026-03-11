"""
Caso de uso: Obtener un pin por ID
"""
from internal.pines.domain.entities.pin import Pin
from internal.pines.domain.repositories.pin_repository import PinRepository


class GetPinUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(self, pin_id: str, requesting_user_id: str = None) -> Pin:
        pin = await self._repo.get_by_id(pin_id)
        if not pin:
            raise ValueError("El pin no existe")

        # Si es privado, solo el dueño puede verlo
        if pin.is_private:
            if not requesting_user_id or pin.user_id != requesting_user_id:
                raise PermissionError("No tienes acceso a este pin")

        # Incrementar vistas
        await self._repo.increment_views(pin_id)

        return pin