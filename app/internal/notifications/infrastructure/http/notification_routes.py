"""
Rutas HTTP de Notificaciones
"""
from fastapi import APIRouter, Depends, HTTPException, status

from internal.notifications.infrastructure.http.dependencies import (
    get_notification_controller
)
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "/",
    summary="Obtener notificaciones del usuario",
)
async def get_notifications(
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user_id),
    controller = Depends(get_notification_controller),
):
    """Obtener notificaciones del usuario autenticado"""
    try:
        result = await controller.get_notifications(user_id, limit, offset)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/{notification_id}/read",
    summary="Marcar notificación como leída",
)
async def mark_as_read(
    notification_id: str,
    user_id: str = Depends(get_current_user_id),
    controller = Depends(get_notification_controller),
):
    """Marcar una notificación como leída"""
    try:
        result = await controller.mark_as_read(notification_id, user_id)
        return {
            "status": "success",
            "message": "Notificación marcada como leída",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )