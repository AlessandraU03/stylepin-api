"""
Caso de uso: Actualizar permisos de un colaborador
"""
from internal.boards.domain.entities.board import BoardCollaborator
from internal.boards.domain.repositories.board_repository import BoardRepository


class UpdateCollaboratorUseCase:
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
            raise PermissionError("Solo el dueño puede modificar permisos")

        is_collab = await self._repo.is_collaborator(board_id, collaborator_user_id)
        if not is_collab:
            raise ValueError("El usuario no es colaborador de este tablero")

        return await self._repo.update_collaborator_permissions(
            board_id=board_id,
            user_id=collaborator_user_id,
            can_edit=can_edit,
            can_add_pins=can_add_pins,
            can_remove_pins=can_remove_pins,
        )