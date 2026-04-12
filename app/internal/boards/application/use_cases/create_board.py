"""
Caso de uso: Crear un tablero
"""
from datetime import datetime, timezone
from internal.boards.domain.entities.board import Board
from internal.boards.domain.repositories.board_repository import BoardRepository


class CreateBoardUseCase:
    def __init__(self, board_repository: BoardRepository):
        self._repo = board_repository

    async def execute(
        self,
        user_id: str,
        name: str,
        description: str = None,
        is_private: bool = False,
        is_collaborative: bool = False,
    ) -> Board:
        now = datetime.now(timezone.utc)

        board = Board(
            id="",
            user_id=user_id,
            name=name,
            description=description,
            cover_image_url=None,
            is_private=is_private,
            is_collaborative=is_collaborative,
            pins_count=0,
            created_at=now,
            updated_at=now,
        )

        return await self._repo.create(board)