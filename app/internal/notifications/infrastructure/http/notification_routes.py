"""
Rutas HTTP de Notificaciones - CORREGIDO v3

PROBLEMA: GetNotificationsUseCase devuelve entidades de dominio Python (no Pydantic).
FastAPI no sabe cómo serializarlas a JSON → el Android recibe objetos vacíos {} o falla.

SOLUCIÓN: Convertir cada entidad de dominio a dict manualmente antes de devolverla.
Así FastAPI serializa dicts simples sin problema y el Android recibe el JSON correcto.

Estructura que espera el Android (NotificationResponse):
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
from fastapi import APIRouter, Depends, HTTPException, Query, status

from internal.notifications.infrastructure.http.notification_controller import (
    NotificationController
)
from internal.notifications.infrastructure.http.dependencies import (
    get_notification_controller
)
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _notification_to_dict(n) -> dict:
    """
    Convierte una entidad de dominio Notification a dict serializable.
    Funciona tanto si n es un objeto Python como si ya es un dict.
    """
    if isinstance(n, dict):
        return {
            "id":         n.get("id", ""),
            "title":      n.get("title", ""),
            "body":       n.get("body", ""),
            "type":       str(n.get("type", "")),
            "is_read":    bool(n.get("is_read", False)),
            "created_at": str(n.get("created_at", "")),
            "read_at":    str(n.get("read_at")) if n.get("read_at") else None,
        }
    # Es un objeto de dominio — acceder por atributos
    return {
        "id":         getattr(n, "id", ""),
        "title":      getattr(n, "title", ""),
        "body":       getattr(n, "body", ""),
        "type":       str(getattr(n, "type", "")),
        "is_read":    bool(getattr(n, "is_read", False)),
        "created_at": str(getattr(n, "created_at", "")),
        "read_at":    str(getattr(n, "read_at")) if getattr(n, "read_at", None) else None,
    }


@router.get(
    "/test",
    summary="Enviar notificación de prueba",
)
async def test_notification(
    user_id: str = Depends(get_current_user_id),
    controller: NotificationController = Depends(get_notification_controller),
):
    try:
        return await controller.send_test_notification(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get(
    "",
    summary="Obtener notificaciones del usuario — devuelve array JSON directamente",
)
async def get_notifications(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_user_id),
    controller: NotificationController = Depends(get_notification_controller),
):
    try:
        result = await controller.get_notifications(user_id, limit, offset)

        # Extraer la lista del dict que devuelve el use case
        if isinstance(result, dict):
            raw_list = result.get("notifications", [])
        elif isinstance(result, list):
            raw_list = result
        else:
            raw_list = []

        # Convertir cada entidad de dominio a dict serializable
        return [_notification_to_dict(n) for n in raw_list]

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
    try:
        result = await controller.mark_as_read(notification_id, user_id)
        return {"status": "success", "data": result}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))