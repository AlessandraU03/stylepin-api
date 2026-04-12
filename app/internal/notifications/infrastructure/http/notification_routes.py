"""
Rutas HTTP de Notificaciones - CORREGIDO

Problema: GET /api/v1/notifications devolvía un dict:
  {"notifications": [...], "total": 0, "limit": 50, ...}

Pero el cliente Android espera directamente una List:
  Response<List<NotificationResponse>>
  y llama a response.body()?.map { it.toDomain() }

Si recibe un dict en vez de una lista, Gson falla y lanza excepción
→ el Android muestra "No se pudieron cargar las notificaciones".

CORRECCIÓN: el endpoint ahora devuelve directamente la lista de notificaciones.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List

from internal.notifications.infrastructure.http.notification_controller import (
    NotificationController
)
from internal.notifications.infrastructure.http.dependencies import (
    get_notification_controller
)
from internal.notifications.application.schemas.notification_schema import NotificationResponse
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "",
    response_model=List[NotificationResponse],  # ← CAMBIADO: lista directa, no dict
    summary="Obtener notificaciones del usuario",
)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    controller: NotificationController = Depends(get_notification_controller),
):
    """
    Obtener notificaciones del usuario autenticado.
    Devuelve directamente un array JSON para que el cliente Android
    pueda hacer response.body()?.map { it.toDomain() } sin problemas.
    """
    try:
        result = await controller.get_notifications(user_id, limit, offset)
        # result es {"notifications": [...], "total": N, ...}
        # Extraemos solo la lista para devolverla directamente
        notifications = result.get("notifications", [])

        # Convertimos cada entidad de dominio a NotificationResponse (schema Pydantic)
        return [
            NotificationResponse(
                id=n.id,
                title=n.title,
                body=n.body,
                type=n.type,
                is_read=n.is_read,
                created_at=n.created_at,
                read_at=n.read_at,
            )
            for n in notifications
        ]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))