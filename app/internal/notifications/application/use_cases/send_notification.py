from datetime import datetime
from uuid import uuid4
from sqlalchemy.orm import Session
from app.core.database.models import Notification, User, FCMToken
from app.core.firebase import send_fcm_notification
from app.internal.notifications.application.schemas.notification_schema import NotificationType

class SendNotificationUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(
        self,
        user_id: str,
        actor_id: str,
        notification_type: NotificationType,
        title: str,
        body: str,
        pin_id: str = None,
        comment_id: str = None,
        board_id: str = None
    ) -> dict:
        """Crear notificación y enviar push"""
        try:
            # Crear registro en BD
            notification = Notification(
                id=str(uuid4()),
                user_id=user_id,
                actor_id=actor_id,
                type=notification_type,
                title=title,
                body=body,
                pin_id=pin_id,
                comment_id=comment_id,
                board_id=board_id,
                is_read=False,
                created_at=datetime.utcnow()
            )
            self.db.add(notification)
            self.db.flush()

            # Obtener tokens FCM del usuario
            fcm_tokens = self.db.query(FCMToken).filter(
                FCMToken.user_id == user_id,
                FCMToken.is_active == True
            ).all()

            device_tokens = [token.device_token for token in fcm_tokens]

            # Preparar datos para FCM
            data = {
                "notification_id": notification.id,
                "type": notification_type,
                "actor_id": actor_id,
                "pin_id": pin_id or "",
                "comment_id": comment_id or "",
                "board_id": board_id or ""
            }

            # Enviar notificación push
            fcm_result = send_fcm_notification(
                device_tokens=device_tokens,
                title=title,
                body=body,
                data=data
            )

            self.db.commit()

            return {
                "success": True,
                "notification_id": notification.id,
                "fcm_result": fcm_result
            }
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": str(e)}


class RegisterFCMTokenUseCase:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, user_id: str, device_token: str, device_name: str = None) -> dict:
        """Registrar token FCM del dispositivo"""
        try:
            existing_token = self.db.query(FCMToken).filter(
                FCMToken.user_id == user_id,
                FCMToken.device_token == device_token
            ).first()

            if existing_token:
                existing_token.updated_at = datetime.utcnow()
                existing_token.is_active = True
            else:
                fcm_token = FCMToken(
                    id=str(uuid4()),
                    user_id=user_id,
                    device_token=device_token,
                    device_name=device_name,
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                self.db.add(fcm_token)

            self.db.commit()
            return {"success": True, "message": "FCM token registered"}
        except Exception as e:
            self.db.rollback()
            return {"success": False, "error": str(e)}
