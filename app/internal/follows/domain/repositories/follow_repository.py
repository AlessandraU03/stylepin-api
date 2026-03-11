"""
Interface del repositorio de Follows (Port)
"""
from abc import ABC, abstractmethod
from typing import List
from internal.follows.domain.entities.follow import Follow

class FollowRepository(ABC):
    """Repositorio de Follows - Interface"""
    
    @abstractmethod
    async def create(self, follow: Follow) -> Follow:
        """Crear un nuevo follow"""
        pass
    
    @abstractmethod
    async def delete(self, follower_id: str, following_id: str) -> bool:
        """Eliminar follow (dejar de seguir)"""
        pass
    
    @abstractmethod
    async def get_followers(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Follow]:
        """Obtener seguidores de un usuario"""
        pass
    
    @abstractmethod
    async def get_following(
        self, 
        user_id: str, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[Follow]:
        """Obtener usuarios que sigue un usuario"""
        pass
    
    @abstractmethod
    async def exists(self, follower_id: str, following_id: str) -> bool:
        """Verificar si existe un follow"""
        pass
    
    @abstractmethod
    async def count_followers(self, user_id: str) -> int:
        """Contar seguidores de un usuario"""
        pass
    
    @abstractmethod
    async def count_following(self, user_id: str) -> int:
        """Contar usuarios que sigue un usuario"""
        pass
    @abstractmethod
    async def get_follower_ids(self, user_id: str) -> List[str]:
        """
        Obtener IDs de seguidores de un usuario
        (útil para notificaciones de nuevos pins)
        """
        pass
    
    @abstractmethod
    async def get_following_ids(self, user_id: str) -> List[str]:
        """
        Obtener IDs de usuarios que sigue un usuario
        (útil para generar feed personalizado)
        """
        pass
    
    @abstractmethod
    async def are_mutual_followers(self, user_id_1: str, user_id_2: str) -> bool:
        """Verificar si dos usuarios se siguen mutuamente"""
        pass