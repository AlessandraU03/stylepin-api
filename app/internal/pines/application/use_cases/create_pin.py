"""
Caso de uso: Crear Pin
"""
import uuid
from datetime import datetime
from app.internal.pines.domain.entities.pin import Pin, PinResponse
from app.internal.pines.domain.repositories.pin_repository import PinRepository
from app.internal.users.domain.repositories.user_repository import UserRepository
from app.internal.pines.application.schemas.pin_schemas import CreatePinRequest

class CreatePinUseCase:
    """
    Caso de uso para crear un nuevo pin
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
        user_id: str, 
        request: CreatePinRequest
    ) -> PinResponse:
        """
        Ejecuta el caso de uso de crear pin
        
        Args:
            user_id: ID del usuario autenticado
            request: Datos del pin a crear
            
        Returns:
            PinResponse con el pin creado y datos del usuario
            
        Raises:
            Exception: Si el usuario no existe
        """
        # 1. Verificar que el usuario existe
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise Exception("User not found")
        
        # 2. Crear entidad Pin
        pin = Pin(
            id=str(uuid.uuid4()),
            user_id=user_id,
            image_url=request.image_url,
            title=request.title,
            description=request.description,
            category=request.category,
            styles=request.styles,
            occasions=request.occasions,
            season=request.season,
            brands=request.brands,
            price_range=request.price_range,
            where_to_buy=request.where_to_buy,
            purchase_link=request.purchase_link,
            colors=request.colors,
            tags=request.tags,
            is_private=request.is_private,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 3. Guardar en base de datos
        created_pin = await self.pin_repository.create(pin)
        
        # 4. Retornar respuesta con información del usuario
        return PinResponse(
            id=created_pin.id,
            user_id=created_pin.user_id,
            user_username=user.username,
            user_full_name=user.full_name,
            user_avatar_url=user.avatar_url,
            user_is_verified=user.is_verified,
            image_url=created_pin.image_url,
            title=created_pin.title,
            description=created_pin.description,
            category=created_pin.category,
            styles=created_pin.styles,
            occasions=created_pin.occasions,
            season=created_pin.season,
            brands=created_pin.brands,
            price_range=created_pin.price_range,
            where_to_buy=created_pin.where_to_buy,
            purchase_link=created_pin.purchase_link,
            likes_count=created_pin.likes_count,
            saves_count=created_pin.saves_count,
            comments_count=created_pin.comments_count,
            views_count=created_pin.views_count,
            colors=created_pin.colors,
            tags=created_pin.tags,
            is_private=created_pin.is_private,
            created_at=created_pin.created_at,
            updated_at=created_pin.updated_at
        )