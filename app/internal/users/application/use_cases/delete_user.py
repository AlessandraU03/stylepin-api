"""
Caso de uso: Eliminar (desactivar) cuenta de usuario
"""
from internal.users.domain.repositories.user_repository import UserRepository


class DeleteUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute(self, user_id: str, requesting_user_id: str) -> bool:
        if user_id != requesting_user_id:
            raise PermissionError("No puedes eliminar la cuenta de otro usuario")

        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")

        # Soft delete
        return await self._repo.delete(user_id)