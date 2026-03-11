"""
Caso de uso: Obtener un tablero por ID
"""
from typing import Optional
from internal.boards.domain.entities.board import Board
from internal.boards.domain.repositories.board_repository import BoardRepository


class GetBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(self, board_id: str, requesting_user_id: str = None) -> Board:
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        # Si es privado, solo el dueño o colaboradores pueden verlo
        if board.is_private and requesting_user_id:
            if board.user_id != requesting_user_id:
                is_collab = await self._repo.is_collaborator(board_id, requesting_user_id)
                if not is_collab:
                    raise PermissionError("No tienes acceso a este tablero")

        return board