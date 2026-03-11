"""
Caso de uso: Quitar colaborador de un tablero
"""
from internal.boards.domain.repositories.board_repository import BoardRepository


class RemoveCollaboratorUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(
        self,
        board_id: str,
        owner_id: str,
        collaborator_user_id: str,
    ) -> bool:
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        # Solo el dueño o el propio colaborador pueden quitarse
        if board.user_id != owner_id and owner_id != collaborator_user_id:
            raise PermissionError("No tienes permiso para quitar este colaborador")

        is_collab = await self._repo.is_collaborator(board_id, collaborator_user_id)
        if not is_collab:
            raise ValueError("El usuario no es colaborador de este tablero")

        return await self._repo.remove_collaborator(board_id, collaborator_user_id)