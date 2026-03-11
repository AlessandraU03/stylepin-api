"""
Servicio de notificaciones en tiempo real
"""
import logging
from core.websocket import manager

logger = logging.getLogger(__name__)


async def notify_new_like(pin_owner_id: str, liker_username: str, pin_id: str, pin_title: str):
    """Notifica al dueño del pin que alguien le dio like"""
    await manager.send_personal(pin_owner_id, {
        "type": "new_like",
        "pin_id": pin_id,
        "pin_title": pin_title,
        "liker_username": liker_username,
        "message": f"❤️ {liker_username} le dio like a tu pin '{pin_title}'",
    })


async def notify_new_follow(followed_user_id: str, follower_username: str, follower_id: str):
    """Notifica al usuario que alguien lo empezó a seguir"""
    await manager.send_personal(followed_user_id, {
        "type": "new_follow",
        "follower_id": follower_id,
        "follower_username": follower_username,
        "message": f"👤 {follower_username} te empezó a seguir",
    })


async def notify_new_comment(pin_owner_id: str, commenter_username: str, pin_id: str, pin_title: str, comment_text: str):
    """Notifica al dueño del pin que alguien comentó"""
    await manager.send_personal(pin_owner_id, {
        "type": "new_comment",
        "pin_id": pin_id,
        "pin_title": pin_title,
        "commenter_username": commenter_username,
        "comment_preview": comment_text[:100],
        "message": f"💬 {commenter_username} comentó en tu pin '{pin_title}'",
    })


async def notify_new_pin(user_id: str, username: str, pin_id: str, pin_title: str):
    """Notifica a todos que alguien publicó un nuevo pin"""
    await manager.broadcast(
        {
            "type": "new_pin",
            "user_id": user_id,
            "username": username,
            "pin_id": pin_id,
            "pin_title": pin_title,
            "message": f"📌 {username} publicó un nuevo pin: '{pin_title}'",
        },
        exclude_user=user_id,
    )