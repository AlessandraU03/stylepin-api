from firebase_admin import messaging

# ================================
# 🔹 FUNCIÓN BASE
# ================================
async def send_push(token: str, title: str, body: str):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=token,
        )

        return messaging.send(message)

    except Exception as e:
        print("Error Firebase:", e)
        return None


# ================================
# ❤️ LIKE
# ================================
async def notify_new_like(token: str, username: str):
    return await send_push(
        token=token,
        title="Nuevo Like ❤️",
        body=f"{username} le dio like a tu publicación"
    )


# ================================
# 👥 FOLLOW
# ================================
async def notify_new_follow(token: str, username: str):
    return await send_push(
        token=token,
        title="Nuevo seguidor 👥",
        body=f"{username} empezó a seguirte"
    )


# ================================
# 💬 COMMENT
# ================================
async def notify_new_comment(token: str, username: str, comment: str):
    return await send_push(
        token=token,
        title="Nuevo comentario 💬",
        body=f"{username} comentó: {comment}"
    )