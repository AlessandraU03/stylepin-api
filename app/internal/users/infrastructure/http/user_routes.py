"""
Rutas HTTP de Users
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated

from internal.users.domain.entities.user import UserMe
from internal.users.application.schemas.user_schema import (
    UpdateProfileRequest,
    ChangePasswordRequest,
    UserProfileResponse,
    UserListResponse,
    UserStatsResponse,
    MessageResponse,
)
from internal.users.infrastructure.http.user_controller import UserController
from internal.users.infrastructure.dependencies import get_user_controller
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id


router = APIRouter(prefix="/users", tags=["Users"])


# ====================== FCM TOKEN ======================

@router.post("/fcm-token")
async def save_fcm_token(
    token: str,
    user_id: str = Depends(get_current_user_id),
    controller: UserController = Depends(get_user_controller),
):
    return await controller.save_fcm_token(user_id, token)


# ====================== TEST NOTIFICATION ======================

@router.get("/test-notification")
async def test_notification(
    user_id: str = Depends(get_current_user_id),
    controller: UserController = Depends(get_user_controller),
):
    print("USER_ID DEL TOKEN:", user_id)

    user = await controller._get_user_uc.execute_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado en DB")

    if not user.fcm_token:
        return {"error": "El usuario no tiene FCM token"}

    from core.notifications import send_push

    result = await send_push(
        token=user.fcm_token,
        title="PRUEBA 🔥",
        body="Si ves esto, Firebase funciona correctamente"
    )

    print("RESULTADO FIREBASE:", result)

    return {
        "message": "Notificación enviada",
        "firebase_response": result
    }


# ====================== MI PERFIL ======================

@router.get("/me", response_model=UserMe)
async def get_me(
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.get_me(user_id)


@router.put("/me", response_model=UserMe)
async def update_me(
    body: UpdateProfileRequest,
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.update_profile(user_id, body)


@router.put("/me/password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.change_password(user_id, body)


@router.delete("/me", response_model=MessageResponse)
async def delete_me(
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.delete_account(user_id)


@router.get("/me/stats", response_model=UserStatsResponse)
async def get_my_stats(
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.get_stats(user_id)


# ====================== BÚSQUEDA ======================

@router.get("/search", response_model=UserListResponse)
async def search_users(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.search_users(query=q, limit=limit, offset=offset)


# ====================== PERFIL PÚBLICO ======================

@router.get("/profile/{username}", response_model=UserProfileResponse)
async def get_profile(
    username: str,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.get_profile(username)


# ⚠️ IMPORTANTE: rutas dinámicas SIEMPRE al final

@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user(
    user_id: str,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.get_user_by_id(user_id)


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: str,
    controller: UserController = Depends(get_user_controller),
):
    return await controller.get_stats(user_id)