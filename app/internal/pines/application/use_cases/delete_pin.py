"""
Caso de uso: Eliminar un pin
"""
from internal.pines.domain.repositories.pin_repository import PinRepository


class DeletePinUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(self, pin_id: str, user_id: str) -> bool:
        pin = await self._repo.get_by_id(pin_id)
        if not pin:
            raise ValueError("El pin no existe")

        if pin.user_id != user_id:
            raise PermissionError("No tienes permiso para eliminar este pin")

        return await self._repo.delete(pin_id)