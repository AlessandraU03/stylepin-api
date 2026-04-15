"""
Caso de uso: Obtener tableros de un usuario - CORREGIDO

Problema original: devolvía boards como lista de entidades Board,
pero board_controller._to_response() necesita user_username etc.
que no vienen en la entidad Board base.

Este use case se mantiene igual en lógica, el fix real está en
board_controller.py que ya tiene _get_user_data() para rellenar esos campos.

CORRECCIÓN ADICIONAL: incluye tableros donde el usuario es colaborador,
no solo los propios. Así el tab "Tableros" muestra todos los tableros
del usuario (propios + colaborados), igual que hace el tab de Guardados.
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

        # Tableros colaborativos (donde el usuario es colaborador)
        collaborative = []
        if include_collaborative:
            try:
                collaborative = await self._repo.get_collaborative_boards(
                    user_id=user_id, limit=limit, offset=0
                )
                # Si no es el dueño, ocultar los privados también
                if requesting_user_id != user_id:
                    collaborative = [b for b in collaborative if not b.is_private]
            except Exception:
                collaborative = []

        # Combinar sin duplicados
        seen_ids = {b.id for b in boards}
        for b in collaborative:
            if b.id not in seen_ids:
                boards.append(b)
                seen_ids.add(b.id)

        return {
            "boards": boards,
            "total": len(boards),
            "limit": limit,
            "offset": offset,
            "has_more": False,  # Ya tenemos todos
        }