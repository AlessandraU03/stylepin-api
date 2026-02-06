"""
Interface del repositorio de Pins (Port)
Define el contrato que debe cumplir la implementación
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from app.internal.pines.domain.entities.pin import Pin

class PinRepository(ABC):
    """Repositorio de Pins - Interface"""
    
    @abstractmethod
    async def create(self, pin: Pin) -> Pin:
        """Crear un nuevo pin"""
        pass
    
    @abstractmethod
    async def get_by_id(self, pin_id: str) -> Optional[Pin]:
        """Obtener pin por ID"""
        pass
    
    @abstractmethod
    async def get_all(
        self, 
        limit: int = 20, 
        offset: int = 0,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        season: Optional[str] = None
    ) -> List[Pin]:
        """Obtener lista de pins con filtros opcionales"""
        pass
    
    @abstractmethod
    async def get_by_user(
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Pin]:
        """Obtener pins de un usuario específico"""
        pass
    
    @abstractmethod
    async def update(self, pin: Pin) -> Pin:
        """Actualizar un pin existente"""
        pass
    
    @abstractmethod
    async def delete(self, pin_id: str) -> bool:
        """Eliminar un pin"""
        pass
    
    @abstractmethod
    async def increment_views(self, pin_id: str) -> None:
        """Incrementar contador de vistas"""
        pass
    
    @abstractmethod
    async def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Pin]:
        """Buscar pins por título, descripción o tags"""
        pass