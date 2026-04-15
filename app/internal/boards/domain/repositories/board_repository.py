"""
Interfaz del repositorio de Boards
CORRECCIÓN: agregar get_collaborator() para verificar permisos individuales
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from internal.boards.domain.entities.board import (
    Board,
    BoardPin,
    BoardCollaborator,
)


class BoardRepository(ABC):

    @abstractmethod
    async def create(self, board: Board) -> Board:
        pass

    @abstractmethod
    async def get_by_id(self, board_id: str) -> Optional[Board]:
        pass

    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Board]:
        pass

    @abstractmethod
    async def update(self, board: Board) -> Board:
        pass

    @abstractmethod
    async def delete(self, board_id: str) -> bool:
        pass

    @abstractmethod
    async def increment_pins_count(self, board_id: str) -> None:
        pass

    @abstractmethod
    async def decrement_pins_count(self, board_id: str) -> None:
        pass

    @abstractmethod
    async def update_cover_image(self, board_id: str, image_url: str) -> None:
        pass

    # ── Board Pins ────────────────────────────────────────────

    @abstractmethod
    async def add_pin(self, board_pin: BoardPin) -> BoardPin:
        pass

    @abstractmethod
    async def remove_pin(self, board_id: str, pin_id: str) -> bool:
        pass

    @abstractmethod
    async def get_board_pins(self, board_id: str, limit: int = 20, offset: int = 0) -> List[BoardPin]:
        pass

    @abstractmethod
    async def is_pin_in_board(self, board_id: str, pin_id: str) -> bool:
        pass

    @abstractmethod
    async def get_boards_with_pin(self, pin_id: str, user_id: str) -> List[Board]:
        pass

    # ── Collaborators ─────────────────────────────────────────

    @abstractmethod
    async def add_collaborator(self, collaborator: BoardCollaborator) -> BoardCollaborator:
        pass

    @abstractmethod
    async def remove_collaborator(self, board_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def get_collaborators(self, board_id: str) -> List[BoardCollaborator]:
        pass

    @abstractmethod
    async def get_collaborator(self, board_id: str, user_id: str) -> Optional[BoardCollaborator]:
        """Obtiene el registro de un colaborador específico para verificar sus permisos."""
        pass

    @abstractmethod
    async def is_collaborator(self, board_id: str, user_id: str) -> bool:
        pass

    @abstractmethod
    async def update_collaborator_permissions(
        self, board_id: str, user_id: str,
        can_edit: bool, can_add_pins: bool, can_remove_pins: bool,
    ) -> BoardCollaborator:
        pass

    @abstractmethod
    async def get_collaborative_boards(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[Board]:
        pass

    @abstractmethod
    async def get_all(
        self, user_id: Optional[str] = None, limit: int = 20, offset: int = 0
    ) -> List[Board]:
        pass