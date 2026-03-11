"""
Caso de uso: Actualizar perfil de usuario
"""
from datetime import datetime, timezone
from internal.users.domain.entities.user import User
from internal.users.domain.repositories.user_repository import UserRepository


class UpdateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute(
        self,
        user_id: str,
        requesting_user_id: str,
        **fields,
    ) -> User:
        if user_id != requesting_user_id:
            raise PermissionError("No puedes editar el perfil de otro usuario")

        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        # Solo actualizar campos que vienen con valor (no None)
        update_data = {k: v for k, v in fields.items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)

        updated_user = user.model_copy(update=update_data)
        return await self._repo.update(updated_user)

    async def change_password(
        self,
        user_id: str,
        new_password_hash: str,
    ) -> None:
        """Actualiza el password hash del usuario"""
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        updated_user = user.model_copy(update={
            "password_hash": new_password_hash,
            "updated_at": datetime.now(timezone.utc),
        })
        await self._repo.update(updated_user)