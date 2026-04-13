"""
Caso de uso: Agregar un pin a un tablero
CORRECCIÓN: verificar can_add_pins además de is_collaborator
"""
from datetime import datetime, timezone
from internal.boards.domain.entities.board import BoardPin
from internal.boards.domain.repositories.board_repository import BoardRepository


class AddPinToBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(
        self,
        board_id: str,
        pin_id: str,
        user_id: str,
        notes: str = None,
    ) -> BoardPin:
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        # Dueño siempre puede agregar
        if board.user_id != user_id:
            is_collab = await self._repo.is_collaborator(board_id, user_id)
            if not is_collab:
                raise PermissionError("No tienes permiso para agregar pins a este tablero")

            # ← CORRECCIÓN: verificar permiso can_add_pins del colaborador
            collab = await self._repo.get_collaborator(board_id, user_id)
            if collab and not collab.can_add_pins:
                raise PermissionError("No tienes permiso de añadir pins a este tablero")

        already_exists = await self._repo.is_pin_in_board(board_id, pin_id)
        if already_exists:
            raise ValueError("El pin ya está en este tablero")

        now = datetime.now(timezone.utc)
        board_pin = BoardPin(
            id="",
            board_id=board_id,
            pin_id=pin_id,
            user_id=user_id,
            notes=notes,
            created_at=now,
        )

        result = await self._repo.add_pin(board_pin)
        await self._repo.increment_pins_count(board_id)

        return result