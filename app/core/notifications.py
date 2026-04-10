from firebase_admin import messaging
import logging

logger = logging.getLogger(__name__)

# ================================
# 🔹 FUNCIÓN BASE
# ================================
async def send_push(token: str, title: str, body: str, data: dict = None):
    """
    Enviar notificación push genérica
    
    Args:
        token: Device token FCM
        title: Título de la notificación
        body: Cuerpo de la notificación
        data: Datos adicionales (dict)
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )

        response = messaging.send(message)
        logger.info(f"✅ Push enviado: {response}")
        return response

    except Exception as e:
        logger.error(f"❌ Error Firebase: {e}")
        return None


# ================================
# ❤️ LIKE
# ================================
async def notify_new_like(token: str, username: str):
    """Notificación cuando alguien da like"""
    return await send_push(
        token=token,
        title="Nuevo Like ❤️",
        body=f"{username} le dio like a tu publicación",
        data={
            "type": "new_like",
            "username": username
        }
    )


# ================================
# 👥 FOLLOW
# ================================
async def notify_new_follow(token: str, username: str):
    """Notificación cuando alguien sigue al usuario"""
    return await send_push(
        token=token,
        title="Nuevo seguidor 👥",
        body=f"{username} empezó a seguirte",
        data={
            "type": "new_follow",
            "username": username
        }
    )


# ================================
# 💬 COMMENT
# ================================
async def notify_new_comment(token: str, username: str, comment: str):
    """Notificación cuando alguien comenta en un pin"""
    return await send_push(
        token=token,
        title="Nuevo comentario 💬",
        body=f"{username} comentó: {comment}",
        data={
            "type": "new_comment",
            "username": username,
            "comment": comment[:100]  # Primeros 100 caracteres
        }
    )


# ================================
# 📌 COLLABORATOR
# ================================
async def notify_new_collaborator(token: str, username: str, board_name: str):
    """Notificación cuando agregan usuario como colaborador en un tablero"""
    return await send_push(
        token=token,
        title="Nuevo Colaborador 📌",
        body=f"{username} te añadió a '{board_name}'",
        data={
            "type": "new_collaborator",
            "username": username,
            "board_name": board_name
        }
    )