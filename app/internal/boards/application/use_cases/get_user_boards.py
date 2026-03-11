"""
Caso de uso: Obtener tableros de un usuario
"""
from typing import List
from internal.boards.domain.entities.board import Board
from internal.boards.domain.repositories.board_repository import BoardRepository


class GetUserBoardsUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(
        self,
        user_id: str,
        requesting_user_id: str = None,
        limit: int = 20,
        offset: int = 0,
        include_collaborative: bool = True,
    ) -> dict:
        # Tableros propios
        boards: List[Board] = await self._repo.get_by_user(
            user_id=user_id, limit=limit, offset=offset
        )

        # Si no es el dueño, filtrar los privados
        if requesting_user_id != user_id:
            boards = [b for b in boards if not b.is_private]

        # Tableros colaborativos (opcional)
        collaborative = []
        if include_collaborative:
            collaborative = await self._repo.get_collaborative_boards(
                user_id=user_id, limit=limit, offset=0
            )

        all_boards = boards + collaborative

        return {
            "boards": all_boards,
            "total": len(all_boards),
            "limit": limit,
            "offset": offset,
            "has_more": len(boards) >= limit,
        }