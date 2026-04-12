"""
Rutas HTTP de Notificaciones - CORREGIDO

PROBLEMA: GET /api/v1/notifications devolvía un dict:
  {"notifications": [...], "total": N, "limit": 50, ...}

El cliente Android usa Response<List<NotificationResponse>> y llama:
  response.body()?.map { it.toDomain() }

Gson no puede convertir un dict a List → body() devuelve null →
el repositorio lanza la excepción y la pantalla muestra el error.

CORRECCIÓN: el endpoint devuelve directamente el array de notificaciones.
Se usa result.get("notifications", []) sin construir objetos Pydantic
manualmente (lo que causaba AttributeError en versiones anteriores).
FastAPI serializa el array directamente como JSON.
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "",
    # SIN response_model: FastAPI serializa el resultado tal cual,
    # evitando la conversión de modelos que causaba AttributeError.
    # El Android recibe un array JSON en la raíz: [{...}, {...}, ...]
    summary="Obtener notificaciones del usuario",
)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    controller: NotificationController = Depends(get_notification_controller),
):
    """
    Devuelve directamente un array JSON.

    Estructura de cada elemento que el Android espera:
    {
        "id":         "...",
        "title":      "...",
        "body":       "...",
        "type":       "like | follow | comment | board_collaboration",
        "is_read":    false,
        "created_at": "2026-04-12T...",
        "read_at":    null
    }
    """
    try:
        result = await controller.get_notifications(user_id, limit, offset)

        # El controller devuelve {"notifications": [...], "total": N, ...}
        # Extraemos solo la lista para que el Android pueda leerla directamente
        if isinstance(result, dict):
            return result.get("notifications", [])
        if isinstance(result, list):
            return result
        return []

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener notificaciones: {str(e)}"
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))