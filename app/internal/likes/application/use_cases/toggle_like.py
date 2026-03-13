"""
Caso de uso: Toggle Like (dar/quitar like)
"""
import uuid
from datetime import datetime
from internal.likes.domain.entities.like import Like
from internal.likes.domain.repositories.like_repository import LikeRepository
from internal.pines.domain.repositories.pin_repository import PinRepository

class ToggleLikeUseCase:
    
    def __init__(
        self,
        like_repository: LikeRepository,
        pin_repository: PinRepository  # ✅ NECESITAS ESTE
    ):
        self.like_repository = like_repository
        self.pin_repository = pin_repository
    
    async def execute(self, user_id: str, pin_id: str) -> dict:
        """
        Toggle like en un pin
        
        Returns:
            {"pin_id": str, "is_liked": bool, "likes_count": int}
        """
        # 1. Verificar que el pin existe
        pin = await self.pin_repository.get_by_id(pin_id)
        if not pin:
            raise ValueError("Pin not found")
        
        # 2. Verificar si ya existe el like
        exists = await self.like_repository.exists(user_id, pin_id)
        
        if exists:
            # ===== QUITAR LIKE =====
            await self.like_repository.delete(user_id, pin_id)
            
            # ✅ DECREMENTAR CONTADOR EN PIN
            await self.pin_repository.decrement_likes(pin_id)
            
            # Obtener el pin actualizado
            updated_pin = await self.pin_repository.get_by_id(pin_id)
            
            return {
                "pin_id": pin_id,
                "is_liked": False,
                "likes_count": updated_pin.likes_count
            }
        else:
            # ===== DAR LIKE =====
            like = Like(
                id=str(uuid.uuid4()),
                user_id=user_id,
                pin_id=pin_id,
                created_at=datetime.utcnow()
            )
            
            await self.like_repository.create(like)
            
            # ✅ INCREMENTAR CONTADOR EN PIN
            await self.pin_repository.increment_likes(pin_id)
            
            # Obtener el pin actualizado
            updated_pin = await self.pin_repository.get_by_id(pin_id)
            
            return {
                "pin_id": pin_id,
                "is_liked": True,
                "likes_count": updated_pin.likes_count
            }