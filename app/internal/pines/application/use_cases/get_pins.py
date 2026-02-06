"""
Casos de uso: Obtener Pins
"""
from typing import List
from app.internal.pines.domain.entities.pin import PinResponse, PinSummary
from app.internal.pines.domain.repositories.pin_repository import PinRepository
from app.internal.users.domain.repositories.user_repository import UserRepository
from app.internal.pines.application.schemas.pin_schemas import PinFilters

class GetPinsUseCase:
    """
    Caso de uso para obtener lista de pins (feed)
    """
    
    def __init__(
        self,
        pin_repository: PinRepository,
        user_repository: UserRepository
    ):
        self.pin_repository = pin_repository
        self.user_repository = user_repository
    
    async def execute(self, filters: PinFilters) -> List[PinSummary]:
        """
        Obtiene lista de pins con filtros
        
        Args:
            filters: Filtros de búsqueda (categoría, temporada, usuario, etc.)
            
        Returns:
            Lista de PinSummary con información resumida
        """
        # 1. Obtener pins con filtros
        pins = await self.pin_repository.get_all(
            limit=filters.limit,
            offset=filters.offset,
            user_id=filters.user_id,
            category=filters.category,
            season=filters.season
        )
        
        # 2. Para cada pin, obtener info del usuario
        result = []
        for pin in pins:
            user = await self.user_repository.get_by_id(pin.user_id)
            if user:
                result.append(PinSummary(
                    id=pin.id,
                    user_id=pin.user_id,
                    user_username=user.username,
                    user_avatar_url=user.avatar_url,
                    image_url=pin.image_url,
                    title=pin.title,
                    category=pin.category,
                    likes_count=pin.likes_count,
                    saves_count=pin.saves_count,
                    created_at=pin.created_at
                ))
        
        return result

class GetPinByIdUseCase:
    """
    Caso de uso para obtener un pin por ID
    """
    
    def __init__(
        self,
        pin_repository: PinRepository,
        user_repository: UserRepository
    ):
        self.pin_repository = pin_repository
        self.user_repository = user_repository
    
    async def execute(self, pin_id: str) -> PinResponse:
        """
        Obtiene un pin por su ID
        
        Args:
            pin_id: ID del pin a buscar
            
        Returns:
            PinResponse con información completa del pin
            
        Raises:
            Exception: Si el pin o usuario no se encuentra
        """
        # 1. Obtener pin
        pin = await self.pin_repository.get_by_id(pin_id)
        if not pin:
            raise Exception("Pin not found")
        
        # 2. Incrementar contador de vistas
        await self.pin_repository.increment_views(pin_id)
        
        # 3. Obtener información del usuario
        user = await self.user_repository.get_by_id(pin.user_id)
        if not user:
            raise Exception("User not found")
        
        # 4. Retornar respuesta completa
        return PinResponse(
            id=pin.id,
            user_id=pin.user_id,
            user_username=user.username,
            user_full_name=user.full_name,
            user_avatar_url=user.avatar_url,
            user_is_verified=user.is_verified,
            image_url=pin.image_url,
            title=pin.title,
            description=pin.description,
            category=pin.category,
            styles=pin.styles,
            occasions=pin.occasions,
            season=pin.season,
            brands=pin.brands,
            price_range=pin.price_range,
            where_to_buy=pin.where_to_buy,
            purchase_link=pin.purchase_link,
            likes_count=pin.likes_count,
            saves_count=pin.saves_count,
            comments_count=pin.comments_count,
            views_count=pin.views_count + 1,  # Ya incrementado
            colors=pin.colors,
            tags=pin.tags,
            is_private=pin.is_private,
            created_at=pin.created_at,
            updated_at=pin.updated_at
        )