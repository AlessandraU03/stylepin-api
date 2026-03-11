"""
Caso de uso: Agregar colaborador a un tablero
"""
from datetime import datetime, timezone
from internal.boards.domain.entities.board import BoardCollaborator
from internal.boards.domain.repositories.board_repository import BoardRepository


class AddCollaboratorUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(
        self,
        board_id: str,
        owner_id: str,
        collaborator_user_id: str,
        can_edit: bool = False,
        can_add_pins: bool = True,
        can_remove_pins: bool = False,
    ) -> BoardCollaborator:
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        if board.user_id != owner_id:
            raise PermissionError("Solo el dueño puede agregar colaboradores")

        if not board.is_collaborative:
            raise ValueError("Este tablero no permite colaboradores")

        # No puede agregarse a sí mismo
        if owner_id == collaborator_user_id:
            raise ValueError("No puedes agregarte como colaborador de tu propio tablero")

        # Verificar que no sea ya colaborador
        already = await self._repo.is_collaborator(board_id, collaborator_user_id)
        if already:
            raise ValueError("El usuario ya es colaborador de este tablero")

        now = datetime.now(timezone.utc)
        collaborator = BoardCollaborator(
            id="",
            board_id=board_id,
            user_id=collaborator_user_id,
            can_edit=can_edit,
            can_add_pins=can_add_pins,
            can_remove_pins=can_remove_pins,
            created_at=now,
        )

        return await self._repo.add_collaborator(collaborator)