"""
Caso de uso: Eliminar un tablero
"""
from internal.boards.domain.repositories.board_repository import BoardRepository


class DeleteBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(self, board_id: str, user_id: str) -> bool:
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        if board.user_id != user_id:
            raise PermissionError("No tienes permiso para eliminar este tablero")

        return await self._repo.delete(board_id)