"""
Caso de uso: Actualizar un tablero
"""
from datetime import datetime, timezone
from internal.boards.domain.entities.board import Board
from internal.boards.domain.repositories.board_repository import BoardRepository


class UpdateBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(
        self,
        board_id: str,
        user_id: str,
        **fields,
    ) -> Board:
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        if board.user_id != user_id:
            raise PermissionError("No tienes permiso para editar este tablero")

        # Solo actualizar campos que vienen con valor
        update_data = {k: v for k, v in fields.items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc)

        updated_board = board.model_copy(update=update_data)
        return await self._repo.update(updated_board)