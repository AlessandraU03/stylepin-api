"""
Interface del repositorio de Likes (Port)
"""
from abc import ABC, abstractmethod
from typing import List
from internal.likes.domain.entities.like import Like

class LikeRepository(ABC):
    """Repositorio de Likes - Interface"""
    
    @abstractmethod
    async def create(self, like: Like) -> Like:
        """Crear un nuevo like"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str, pin_id: str) -> bool:
        """Eliminar like"""
        pass
    
    @abstractmethod
    async def get_by_pin(self, pin_id: str, limit: int = 50) -> List[Like]:
        """Obtener likes de un pin"""
        pass
    
    @abstractmethod
    async def get_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[Like]:
        """Obtener likes que un usuario ha dado"""
        pass
    
    @abstractmethod
    async def exists(self, user_id: str, pin_id: str) -> bool:
        """Verificar si existe un like"""
        pass
    
    @abstractmethod
    async def count_by_pin(self, pin_id: str) -> int:
        """Contar likes de un pin"""
        pass
    
    @abstractmethod
    async def count_by_user(self, user_id: str) -> int:
        """Contar likes que un usuario ha dado"""
        pass