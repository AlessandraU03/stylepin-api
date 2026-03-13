"""
Interface del repositorio de Pins (Port)
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from core.database.models import PinModel, UserModel
from internal.pines.domain.entities.pin import Pin, PinResponse

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
        season: Optional[str] = None,
        price_range: Optional[str] = None
    ) -> List[Pin]:
        """Obtener lista de pins públicos con filtros opcionales"""
        pass
    
    @abstractmethod
    async def get_by_user(
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0,
        include_private: bool = False
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
    async def increment_likes(self, pin_id: str) -> None:
        """Incrementar contador de likes"""
    pass

    @abstractmethod
    async def decrement_likes(self, pin_id: str) -> None:
        """Decrementar contador de likes"""
        pass
    
    
    @abstractmethod
    async def increment_saves(self, pin_id: str) -> None:
        """Incrementar contador de guardados"""
        pass
    
    @abstractmethod
    async def decrement_saves(self, pin_id: str) -> None:
        """Decrementar contador de guardados"""
        pass
    
    @abstractmethod
    async def increment_comments(self, pin_id: str) -> None:
        """Incrementar contador de comentarios"""
        pass
    
    @abstractmethod
    async def decrement_comments(self, pin_id: str) -> None:
        """Decrementar contador de comentarios"""
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
    
    @abstractmethod
    async def get_feed(
    self,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
        ) -> List[PinResponse]:
        query = (
        self._db.query(PinModel, UserModel)
        .join(UserModel, PinModel.user_id == UserModel.id)
        .filter(
            PinModel.is_private == False,
            PinModel.user_id != user_id,
        )
        .order_by(PinModel.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
        models = query.all()

        return [self._to_entity_with_user(pin, user) for pin, user in models]
    
    @abstractmethod
    async def get_trending(
        self,
        limit: int = 20,
        hours: int = 24
    ) -> List[Pin]:
        """
        Obtener pins trending (más likes/views en últimas X horas)
        """
        pass