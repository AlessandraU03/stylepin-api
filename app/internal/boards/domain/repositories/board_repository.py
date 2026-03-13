"""
Interface del repositorio de Boards (Port)
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from internal.boards.domain.entities.board import Board, BoardPin, BoardCollaborator

class BoardRepository(ABC):
    """Repositorio de Boards - Interface"""
    
    @abstractmethod
    async def create(self, board: Board) -> Board:
        """Crear un nuevo tablero"""
        pass
    
    @abstractmethod
    async def get_by_id(self, board_id: str) -> Optional[Board]:
        """Obtener tablero por ID"""
        pass
    
    @abstractmethod
    async def get_by_user(
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Board]:
        """Obtener tableros de un usuario"""
        pass
    
    @abstractmethod
    async def update(self, board: Board) -> Board:
        """Actualizar tablero"""
        pass
    
    @abstractmethod
    async def delete(self, board_id: str) -> bool:
        """Eliminar tablero"""
        pass
    
    @abstractmethod
    async def increment_pins_count(self, board_id: str) -> None:
        """Incrementar contador de pins"""
        pass
    
    @abstractmethod
    async def decrement_pins_count(self, board_id: str) -> None:
        """Decrementar contador de pins"""
        pass
    
    @abstractmethod
    async def update_cover_image(self, board_id: str, image_url: str) -> None:
        """Actualizar imagen de portada"""
        pass
    
    # ==================== BOARD PINS ====================
    
    @abstractmethod
    async def add_pin(self, board_pin: BoardPin) -> BoardPin:
        """Agregar pin a tablero"""
        pass
    
    @abstractmethod
    async def remove_pin(self, board_id: str, pin_id: str) -> bool:
        """Quitar pin del tablero"""
        pass
    
    @abstractmethod
    async def get_board_pins(
        self, 
        board_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[BoardPin]:
        """Obtener pins de un tablero"""
        pass
    
    @abstractmethod
    async def is_pin_in_board(self, board_id: str, pin_id: str) -> bool:
        """Verificar si un pin está en el tablero"""
        pass
    
    @abstractmethod
    async def get_boards_with_pin(self, pin_id: str, user_id: str) -> List[Board]:
        """Obtener tableros que contienen un pin específico"""
        pass
    
    # ==================== COLLABORATORS ====================
    
    @abstractmethod
    async def add_collaborator(self, collaborator: BoardCollaborator) -> BoardCollaborator:
        """Agregar colaborador al tablero"""
        pass
    
    @abstractmethod
    async def remove_collaborator(self, board_id: str, user_id: str) -> bool:
        """Quitar colaborador del tablero"""
        pass
    
    @abstractmethod
    async def get_collaborators(self, board_id: str) -> List[BoardCollaborator]:
        """Obtener colaboradores de un tablero"""
        pass
    
    @abstractmethod
    async def is_collaborator(self, board_id: str, user_id: str) -> bool:
        """Verificar si un usuario es colaborador"""
        pass
    
    @abstractmethod
    async def update_collaborator_permissions(
        self, 
        board_id: str, 
        user_id: str,
        can_edit: bool,
        can_add_pins: bool,
        can_remove_pins: bool
    ) -> BoardCollaborator:
        """Actualizar permisos de colaborador"""
        pass
    
    @abstractmethod
    async def get_collaborative_boards(
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Board]:
        """Obtener tableros donde el usuario es colaborador"""
        pass

    @abstractmethod
    async def get_all(
        self, 
        limit: int = 20, 
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> List[Board]:
        """
        Obtener todos los boards públicos
        
        Args:
            limit: Número de resultados
            offset: Offset para paginación
            user_id: (Opcional) Filtrar por usuario específico
            
        Returns:
            Lista de boards públicos ordenados por más recientes
        """
        pass