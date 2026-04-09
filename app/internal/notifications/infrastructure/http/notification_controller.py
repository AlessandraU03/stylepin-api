"""
Controlador HTTP de Notificaciones
"""
from sqlalchemy.orm import Session
from internal.notifications.application.schemas.notification_schema import RegisterFCMTokenRequest
from internal.notifications.application.use_cases.send_notification import RegisterFCMTokenUseCase


class NotificationController:
    async def register_fcm_token(self, body: RegisterFCMTokenRequest, db: Session):
        """Registrar un token FCM"""
        use_case = RegisterFCMTokenUseCase(db)
        return use_case.execute(
            user_id="current_user_id",  # TODO: Obtener del JWT
            device_token=body.device_token,
            device_name=body.device_name
        )