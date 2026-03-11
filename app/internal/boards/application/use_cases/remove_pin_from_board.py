"""
Caso de uso: Quitar un pin de un tablero
"""
from internal.boards.domain.repositories.board_repository import BoardRepository


class RemovePinFromBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(
        self,
        board_id: str,
        pin_id: str,
        user_id: str,
    ) -> bool:
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        # Verificar permisos
        if board.user_id != user_id:
            is_collab = await self._repo.is_collaborator(board_id, user_id)
            if not is_collab:
                raise PermissionError("No tienes permiso para quitar pins de este tablero")

        # Verificar que el pin esté en el tablero
        exists = await self._repo.is_pin_in_board(board_id, pin_id)
        if not exists:
            raise ValueError("El pin no está en este tablero")

        result = await self._repo.remove_pin(board_id, pin_id)

        if result:
            await self._repo.decrement_pins_count(board_id)

        return result