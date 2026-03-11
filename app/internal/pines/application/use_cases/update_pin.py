"""
Caso de uso: Actualizar un pin
"""
from datetime import datetime, timezone
from internal.pines.domain.entities.pin import Pin
from internal.pines.domain.repositories.pin_repository import PinRepository


class UpdatePinUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(
        self,
        pin_id: str,
        user_id: str,
        **fields,
    ) -> Pin:
        pin = await self._repo.get_by_id(pin_id)
        if not pin:
            raise ValueError("El pin no existe")

        if pin.user_id != user_id:
            raise PermissionError("No tienes permiso para editar este pin")

        # Solo actualizar campos que vienen con valor
        update_data = {k: v for k, v in fields.items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)

        updated_pin = pin.model_copy(update=update_data)
        return await self._repo.update(updated_pin)