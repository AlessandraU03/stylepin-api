"""
Caso de uso: Guardar token FCM del usuario
"""
from datetime import datetime, timezone
from uuid import uuid4
from internal.users.domain.repositories.user_repository import UserRepository
from core.database.models import FCMToken
import logging

logger = logging.getLogger(__name__)

class SaveFcmTokenUseCase:
    def __init__(self, user_repository: UserRepository, db_session):
        self._user_repo = user_repository
        self._db = db_session

    async def execute(
        self,
        user_id: str,
        token: str,
        device_name: str = None
    ) -> dict:
        """
        Guardar o actualizar token FCM del usuario
        
        Args:
            user_id: ID del usuario
            token: Device token de Firebase
            device_name: Nombre del dispositivo (opcional)
            
        Returns:
            {"success": True, "message": "..."}
        """
        
        # 1. Verificar que el usuario existe
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"Usuario {user_id} no encontrado")
        
        try:
            # 2. Buscar si ya existe un token para este usuario y dispositivo
            existing_token = self._db.query(FCMToken).filter(
                FCMToken.user_id == user_id,
                FCMToken.device_token == token
            ).first()
            
            now = datetime.now(timezone.utc)
            
            if existing_token:
                # ✅ ACTUALIZAR token existente
                existing_token.is_active = True
                existing_token.device_name = device_name or existing_token.device_name
                existing_token.updated_at = now
                
                logger.info(f"✅ FCM token updated for user {user_id}")
            else:
                # ✅ CREAR nuevo token
                new_token = FCMToken(
                    id=str(uuid4()),
                    user_id=user_id,
                    device_token=token,
                    device_name=device_name or "Unknown Device",
                    is_active=True,
                    created_at=now,
                    updated_at=now
                )
                self._db.add(new_token)
                
                logger.info(f"✅ New FCM token created for user {user_id}")
            
            # 3. Desactivar otros tokens si lo deseas (opcional)
            # Esto permite un solo dispositivo activo a la vez
            # other_tokens = self._db.query(FCMToken).filter(
            #     FCMToken.user_id == user_id,
            #     FCMToken.device_token != token
            # ).all()
            # for other_token in other_tokens:
            #     other_token.is_active = False
            
            self._db.commit()
            
            return {
                "success": True,
                "message": "FCM token saved successfully",
                "user_id": user_id,
                "device_name": device_name or "Unknown Device"
            }
        
        except Exception as e:
            self._db.rollback()
            logger.error(f"❌ Error saving FCM token: {e}")
            raise ValueError(f"Error al guardar FCM token: {str(e)}")