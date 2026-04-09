"""
Use Case: Guardar FCM Token
"""
from typing import Optional
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session


class SaveFcmTokenUseCase:
    """Guardar o actualizar el token FCM del usuario"""
    
    def __init__(self, db: Session):
        self._db = db
    
    async def execute(
        self, 
        user_id: str, 
        device_token: str, 
        device_name: Optional[str] = None
    ) -> dict:
        """
        Guardar o actualizar token FCM en tabla separada
        
        Args:
            user_id: ID del usuario
            device_token: Token de FCM
            device_name: Nombre del dispositivo (opcional)
        
        Returns:
            dict con información del token guardado
        """
        try:
            # ✅ IMPORTAR aquí para evitar circular imports
            from core.database.models import FCMToken, User
            
            # ✅ Verificar que el usuario existe
            user = self._db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError("Usuario no encontrado")
            
            # ✅ Verificar si el token ya existe para este usuario
            existing = self._db.query(FCMToken).filter(
                FCMToken.user_id == user_id,
                FCMToken.device_token == device_token
            ).first()
            
            if existing:
                # ✅ Actualizar token existente
                existing.is_active = True
                existing.device_name = device_name or existing.device_name
                existing.updated_at = datetime.now(timezone.utc)
                self._db.commit()
                self._db.refresh(existing)
                
                return {
                    "id": existing.id,
                    "user_id": existing.user_id,
                    "device_token": existing.device_token,
                    "device_name": existing.device_name,
                    "is_active": existing.is_active,
                    "message": "Token actualizado",
                }
            else:
                # ✅ Crear nuevo token
                new_token = FCMToken(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    device_token=device_token,
                    device_name=device_name or "Unknown Device",
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                self._db.add(new_token)
                self._db.commit()
                self._db.refresh(new_token)
                
                return {
                    "id": new_token.id,
                    "user_id": new_token.user_id,
                    "device_token": new_token.device_token,
                    "device_name": new_token.device_name,
                    "is_active": new_token.is_active,
                    "message": "Token guardado",
                }
                
        except Exception as e:
            self._db.rollback()
            raise ValueError(f"Error al guardar FCM token: {str(e)}")