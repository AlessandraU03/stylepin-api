"""
Interface del repositorio de Comments (Port)
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from internal.comments.domain.entities.comment import Comment

class CommentRepository(ABC):
    """Repositorio de Comments - Interface"""
    
    @abstractmethod
    async def create(self, comment: Comment) -> Comment:
        """Crear un comentario"""
        pass
    
    @abstractmethod
    async def get_by_id(self, comment_id: str) -> Optional[Comment]:
        """Obtener comentario por ID"""
        pass
    
    @abstractmethod
    async def get_by_pin(
        self, 
        pin_id: str, 
        limit: int = 50, 
        offset: int = 0,
        parent_only: bool = True
    ) -> List[Comment]:
        """
        Obtener comentarios de un pin
        
        Args:
            pin_id: ID del pin
            limit: Límite de resultados
            offset: Offset para paginación
            parent_only: Si True, solo devuelve comentarios padre (no respuestas)
        """
        pass
    
    @abstractmethod
    async def get_replies(
        self, 
        comment_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Comment]:
        """Obtener respuestas a un comentario"""
        pass
    
    @abstractmethod
    async def update(self, comment: Comment) -> Comment:
        """Actualizar un comentario existente"""
        pass
    
    @abstractmethod
    async def delete(self, comment_id: str) -> bool:
        """Eliminar un comentario"""
        pass
    
    @abstractmethod
    async def count_by_pin(self, pin_id: str) -> int:
        """Contar comentarios de un pin"""
        pass
    
    @abstractmethod
    async def count_replies(self, comment_id: str) -> int:
        """Contar respuestas de un comentario"""
        pass
    
    @abstractmethod
    async def increment_likes(self, comment_id: str) -> None:
        """Incrementar contador de likes"""
        pass
    
    @abstractmethod
    async def decrement_likes(self, comment_id: str) -> None:
        """Decrementar contador de likes"""
        pass
    
    @abstractmethod
    async def get_by_user(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Comment]:
        """Obtener comentarios hechos por un usuario"""
        pass