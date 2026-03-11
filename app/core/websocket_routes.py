"""
Rutas WebSocket
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
import logging

from core.websocket import manager
from internal.users.infrastructure.middlewares.auth_middleware import decode_access_token

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    Conexión WebSocket principal.

    Conectar desde el cliente:
        ws://localhost:8000/ws?token=<JWT_TOKEN>

    Mensajes que el cliente puede enviar:
        {"type": "subscribe", "channel": "pin:123"}
        {"type": "unsubscribe", "channel": "pin:123"}
        {"type": "ping"}

    Eventos que el servidor envía:
        {"type": "notification", "event": "new_like", "data": {...}}
        {"type": "notification", "event": "new_follow", "data": {...}}
        {"type": "notification", "event": "new_comment", "data": {...}}
        {"type": "pong"}
        {"type": "connected", "user_id": "..."}
    """
    # ── Autenticación ─────────────────────────────────────────
    if not token:
        await websocket.close(code=4001, reason="Token required")
        return

    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=4001, reason="Invalid token")
            return
    except Exception:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    # ── Conectar ──────────────────────────────────────────────
    await manager.connect(websocket, user_id)

    try:
        # Confirmar conexión
        await websocket.send_json({
            "type": "connected",
            "user_id": user_id,
            "online_users": len(manager.get_online_users()),
        })

        # ── Loop de mensajes ──────────────────────────────────
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                msg_type = message.get("type", "")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

                elif msg_type == "subscribe":
                    channel = message.get("channel", "")
                    if channel:
                        manager.subscribe(user_id, channel)
                        await websocket.send_json({
                            "type": "subscribed",
                            "channel": channel,
                        })

                elif msg_type == "unsubscribe":
                    channel = message.get("channel", "")
                    if channel:
                        manager.unsubscribe(user_id, channel)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "channel": channel,
                        })

                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {msg_type}",
                    })

            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"👋 WebSocket disconnected: user={user_id}")
    except Exception as e:
        manager.disconnect(websocket, user_id)
        logger.error(f"❌ WebSocket error for user={user_id}: {e}")