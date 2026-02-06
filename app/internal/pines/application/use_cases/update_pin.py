"""
Caso de uso: Actualizar Pin
"""
from datetime import datetime
from app.internal.pines.domain.entities.pin import Pin, PinResponse
from app.internal.pines.domain.repositories.pin_repository import PinRepository
from app.internal.users.domain.repositories.user_repository import UserRepository
from app.internal.pines.application.schemas.pin_schemas import UpdatePinRequest

class UpdatePinUseCase:
    """
    Caso de uso para actualizar un pin existente
    """
    
    def __init__(
        self,
        pin_repository: PinRepository,
        user_repository: UserRepository
    ):
        self.pin_repository = pin_repository
        self.user_repository = user_repository
    
    async def execute(
        self,
        pin_id: str,
        user_id: str,
        request: UpdatePinRequest
    ) -> PinResponse:
        """
        Actualiza un pin existente
        
        Args:
            pin_id: ID del pin a actualizar
            user_id: ID del usuario autenticado
            request: Datos a actualizar
            
        Returns:
            PinResponse con el pin actualizado
            
        Raises:
            Exception: Si el pin no existe o el usuario no es el dueño
        """
        # 1. Obtener pin existente
        pin = await self.pin_repository.get_by_id(pin_id)
        if not pin:
            raise Exception(f"Pin {pin_id} not found")
        
        # 2. Verificar que el usuario sea el dueño
        if pin.user_id != user_id:
            raise Exception("You can only edit your own pins")
        
        # 3. Actualizar solo los campos que vienen en el request
        if request.title is not None:
            pin.title = request.title
        if request.description is not None:
            pin.description = request.description
        if request.category is not None:
            pin.category = request.category
        if request.styles is not None:
            pin.styles = request.styles
        if request.occasions is not None:
            pin.occasions = request.occasions
        if request.season is not None:
            pin.season = request.season
        if request.brands is not None:
            pin.brands = request.brands
        if request.price_range is not None:
            pin.price_range = request.price_range
        if request.where_to_buy is not None:
            pin.where_to_buy = request.where_to_buy
        if request.purchase_link is not None:
            pin.purchase_link = request.purchase_link
        if request.colors is not None:
            pin.colors = request.colors
        if request.tags is not None:
            pin.tags = request.tags
        if request.is_private is not None:
            pin.is_private = request.is_private
        
        pin.updated_at = datetime.utcnow()
        
        # 4. Guardar cambios
        updated_pin = await self.pin_repository.update(pin)
        
        # 5. Obtener info del usuario
        user = await self.user_repository.get_by_id(updated_pin.user_id)
        if not user:
            raise Exception("User not found")
        
        # 6. Retornar respuesta
        return PinResponse(
            id=updated_pin.id,
            user_id=updated_pin.user_id,
            user_username=user.username,
            user_full_name=user.full_name,
            user_avatar_url=user.avatar_url,
            user_is_verified=user.is_verified,
            image_url=updated_pin.image_url,
            title=updated_pin.title,
            description=updated_pin.description,
            category=updated_pin.category,
            styles=updated_pin.styles,
            occasions=updated_pin.occasions,
            season=updated_pin.season,
            brands=updated_pin.brands,
            price_range=updated_pin.price_range,
            where_to_buy=updated_pin.where_to_buy,
            purchase_link=updated_pin.purchase_link,
            likes_count=updated_pin.likes_count,
            saves_count=updated_pin.saves_count,
            comments_count=updated_pin.comments_count,
            views_count=updated_pin.views_count,
            colors=updated_pin.colors,
            tags=updated_pin.tags,
            is_private=updated_pin.is_private,
            created_at=updated_pin.created_at,
            updated_at=updated_pin.updated_at
        )