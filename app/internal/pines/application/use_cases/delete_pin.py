"""
Caso de uso: Eliminar Pin
"""
from app.internal.pines.domain.repositories.pin_repository import PinRepository

class DeletePinUseCase:
    """
    Caso de uso para eliminar un pin
    """
    
    def __init__(self, pin_repository: PinRepository):
        self.pin_repository = pin_repository
    
    async def execute(self, pin_id: str, user_id: str) -> dict:
        """
        Elimina un pin
        
        Args:
            pin_id: ID del pin a eliminar
            user_id: ID del usuario autenticado
            
        Returns:
            Diccionario con mensaje de confirmación
            
        Raises:
            Exception: Si el pin no existe o el usuario no es el dueño
        """
        # 1. Obtener pin
        pin = await self.pin_repository.get_by_id(pin_id)
        if not pin:
            raise Exception(f"Pin {pin_id} not found")
        
        # 2. Verificar que el usuario sea el dueño
        if pin.user_id != user_id:
            raise Exception("You can only delete your own pins")
        
        # 3. Eliminar
        deleted = await self.pin_repository.delete(pin_id)
        
        if not deleted:
            raise Exception("Failed to delete pin")
        
        return {
            "message": "Pin deleted successfully",
            "pin_id": pin_id
        }