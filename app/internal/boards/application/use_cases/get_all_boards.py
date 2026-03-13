"""
Caso de uso: Obtener todos los boards públicos
"""
from typing import List, Optional
from internal.boards.domain.entities.board import BoardSummary
from internal.boards.domain.repositories.board_repository import BoardRepository
from internal.users.domain.repositories.user_repository import UserRepository

class GetAllBoardsUseCase:
    """
    Obtiene todos los boards públicos del sistema
    """
    
    def __init__(
        self,
        board_repository: BoardRepository,
        user_repository: UserRepository
    ):
        self.board_repository = board_repository
        self.user_repository = user_repository
    
    async def execute(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None
    ) -> List[BoardSummary]:
        """
        Ejecuta el caso de uso
        
        Args:
            limit: Número de resultados
            offset: Offset para paginación
            user_id: (Opcional) Filtrar por usuario específico
            
        Returns:
            Lista de BoardSummary con información básica
        """
        # Obtener boards públicos
        boards = await self.board_repository.get_all(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        # Convertir a BoardSummary con información del usuario
        result = []
        for board in boards:
            # Obtener información del usuario dueño del board
            user = await self.user_repository.get_by_id(board.user_id)
            
            if user:
                result.append(BoardSummary(
                    id=board.id,
                    user_id=board.user_id,
                    user_username=user.username,
                    name=board.name,
                    cover_image_url=board.cover_image_url,
                    pins_count=board.pins_count,
                    is_private=board.is_private,
                    created_at=board.created_at
                ))
        
        return result