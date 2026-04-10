"""
Rutas HTTP de Notificaciones
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from internal.notifications.infrastructure.http.notification_controller import (
    NotificationController
)
from internal.notifications.infrastructure.http.dependencies import (
    get_notification_controller
)
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "/test",
    summary="Enviar notificación de prueba",
)
async def test_notification(
    user_id: str = Depends(get_current_user_id),
    controller: NotificationController = Depends(get_notification_controller),
):
    """Enviar notificación de prueba al usuario autenticado"""
    try:
        result = await controller.send_test_notification(user_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


@router.get(
    "",
    summary="Obtener notificaciones del usuario",
)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    controller: NotificationController = Depends(get_notification_controller),
):
    """Obtener notificaciones del usuario autenticado"""
    try:
        result = await controller.get_notifications(user_id, limit, offset)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put(
    "/{notification_id}/read",
    summary="Marcar notificación como leída",
)
async def mark_as_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    controller: NotificationController = Depends(get_notification_controller),
):
    """Marcar una notificación como leída"""
    try:
        result = await controller.mark_as_read(notification_id, user_id)
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )