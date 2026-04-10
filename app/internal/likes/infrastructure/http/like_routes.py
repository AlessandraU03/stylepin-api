"""
Rutas HTTP de Likes
"""
from fastapi import APIRouter, Depends, HTTPException, status

from internal.likes.application.schemas.like_schemas import (
    LikePinRequest,
    LikeStatusResponse,
    LikesListResponse,
    UserLikesListResponse,
)
from app.internal.likes.infrastructure.http.like_controller import LikeController
from app.internal.likes.infrastructure.dependencies import get_like_controller
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id

router = APIRouter(prefix="/likes", tags=["Likes"])


# ✅ POST /likes — alias directo de /likes/toggle para la app móvil
@router.post(
    "",
    response_model=LikeStatusResponse,
    summary="Toggle like a un pin (alias de /toggle)",
)
async def toggle_like_root(
    body: LikePinRequest,
    user_id: str = Depends(get_current_user_id),
    controller: LikeController = Depends(get_like_controller),
):
    try:
        return await controller.toggle_like(body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# POST /likes/toggle
@router.post(
    "/toggle",
    response_model=LikeStatusResponse,
    summary="Toggle like a un pin",
)
async def toggle_like(
    body: LikePinRequest,
    user_id: str = Depends(get_current_user_id),
    controller: LikeController = Depends(get_like_controller),
):
    try:
        return await controller.toggle_like(body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/like",
    response_model=LikeStatusResponse,
    summary="Dar like a un pin",
)
async def like_pin(
    body: LikePinRequest,
    user_id: str = Depends(get_current_user_id),
    controller: LikeController = Depends(get_like_controller),
):
    try:
        return await controller.like_pin(body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{pin_id}",
    response_model=LikeStatusResponse,
    summary="Quitar like a un pin",
)
async def unlike_pin(
    pin_id: str,
    user_id: str = Depends(get_current_user_id),
    controller: LikeController = Depends(get_like_controller),
):
    try:
        return await controller.unlike_pin(pin_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/pins/{pin_id}",
    response_model=LikesListResponse,
    summary="Obtener likes de un pin",
)
async def get_pin_likes(
    pin_id: str,
    limit: int = 50,
    offset: int = 0,
    controller: LikeController = Depends(get_like_controller),
):
    try:
        return await controller.get_pin_likes(pin_id, limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/users/{user_id}",
    response_model=UserLikesListResponse,
    summary="Obtener likes de un usuario",
)
async def get_user_likes(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    controller: LikeController = Depends(get_like_controller),
):
    try:
        return await controller.get_user_likes(user_id, limit, offset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get(
    "/status/{pin_id}",
    response_model=LikeStatusResponse,
    summary="Verificar estado de like del usuario autenticado",
)
async def check_like_status(
    pin_id: str,
    user_id: str = Depends(get_current_user_id),
    controller: LikeController = Depends(get_like_controller),
):
    try:
        return await controller.check_like_status(user_id, pin_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))