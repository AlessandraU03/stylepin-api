"""
Caso de uso: Obtener pins de un tablero
"""
from typing import List
from internal.boards.domain.entities.board import BoardPin
from internal.boards.domain.repositories.board_repository import BoardRepository


class GetBoardPinsUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(
        self,
        board_id: str,
        requesting_user_id: str = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict:
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        # Si es privado, verificar acceso
        if board.is_private and requesting_user_id:
            if board.user_id != requesting_user_id:
                is_collab = await self._repo.is_collaborator(board_id, requesting_user_id)
                if not is_collab:
                    raise PermissionError("No tienes acceso a este tablero")

        pins: List[BoardPin] = await self._repo.get_board_pins(
            board_id=board_id, limit=limit, offset=offset
        )

        return {
            "pins": pins,
            "total": board.pins_count,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < board.pins_count,
        }