"""
Rutas HTTP de Notificaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.connection import get_db
from internal.notifications.application.schemas.notification_schema import RegisterFCMTokenRequest
from internal.notifications.infrastructure.http.notification_controller import NotificationController
from internal.notifications.infrastructure.http.dependencies import get_notification_controller
from internal.notifications.application.use_cases.send_notification import SendNotificationUseCase
from internal.notifications.application.schemas.notification_schema import NotificationType


router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post(
    "/register-fcm-token",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar token FCM del dispositivo",
)
async def register_fcm_token(
    body: RegisterFCMTokenRequest,
    db: Session = Depends(get_db),
    controller: NotificationController = Depends(get_notification_controller),
):
    try:
        return await controller.register_fcm_token(body, db)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# ✅ NUEVO: Endpoint de PRUEBA para enviar notificación
@router.post(
    "/test-send",
    summary="PRUEBA: Enviar notificación de prueba",
    tags=["Testing"],
)
async def test_send_notification(
    user_id: str,
    actor_id: str = "admin",
    db: Session = Depends(get_db),
):
    """
    ⚠️ SOLO PARA DESARROLLO - Envía una notificación de prueba
    
    Parámetros:
    - user_id: ID del usuario que recibe la notificación
    - actor_id: ID del usuario que realiza la acción (por defecto "admin")
    """
    try:
        use_case = SendNotificationUseCase(db)
        result = use_case.execute(
            user_id=user_id,
            actor_id=actor_id,
            notification_type=NotificationType.LIKE,
            title="🧪 Notificación de Prueba",
            body="Esta es una notificación de prueba del sistema FCM",
            pin_id="test_pin_123"
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/",
    summary="Obtener todas las notificaciones del usuario",
)
async def get_notifications(
    db: Session = Depends(get_db),
):
    try:
        # TODO: Implementar obtención de notificaciones
        return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/{notification_id}/read",
    summary="Marcar notificación como leída",
)
async def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db),
):
    try:
        # TODO: Implementar marcar como leído
        return {"message": "Notification marked as read"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )