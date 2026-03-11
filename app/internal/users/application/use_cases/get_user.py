"""
Caso de uso: Obtener un usuario
"""
from internal.users.domain.entities.user import User
from internal.users.domain.repositories.user_repository import UserRepository


class GetUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute_by_id(self, user_id: str) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        if not user.is_active:
            raise ValueError("Usuario no encontrado")
        return user

    async def execute_by_username(self, username: str) -> User:
        user = await self._repo.get_by_username(username.lower().strip())
        if not user:
            raise ValueError("Usuario no encontrado")
        if not user.is_active:
            raise ValueError("Usuario no encontrado")
        return user

    async def get_stats(self, user_id: str) -> dict:
        user = await self._repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        return await self._repo.get_user_stats(user_id)