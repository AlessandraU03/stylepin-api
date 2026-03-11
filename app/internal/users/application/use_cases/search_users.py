"""
Caso de uso: Buscar usuarios
"""
from internal.users.domain.repositories.user_repository import UserRepository


class SearchUsersUseCase:
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        if not query or len(query.strip()) == 0:
            raise ValueError("El término de búsqueda no puede estar vacío")

        users = await self._repo.search_users(
            query=query.strip(), limit=limit, offset=offset
        )

        return {
            "users": users,
            "total": len(users),
            "limit": limit,
            "offset": offset,
            "has_more": len(users) >= limit,
        }