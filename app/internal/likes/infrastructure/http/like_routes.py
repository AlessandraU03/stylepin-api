"""
Rutas HTTP de Likes
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated

from internal.likes.application.schemas.like_schemas import (
    LikePinRequest,
    LikeStatusResponse,
    LikesListResponse,
    UserLikesListResponse,
    MessageResponse,
)
from internal.likes.infrastructure.http.like_controller import LikeController
from internal.likes.infrastructure.dependencies import get_like_controller
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id


router = APIRouter(prefix="/likes", tags=["Likes"])



# ==================== LIKE / UNLIKE ====================

@router.post(
    "",
    response_model=LikeStatusResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dar like a un pin",
)
async def like_pin(
    body: LikePinRequest,
    controller: LikeController = Depends(get_like_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.like_pin(body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{pin_id}",
    response_model=LikeStatusResponse,
    summary="Quitar like de un pin",
)
async def unlike_pin(
    pin_id: str,
    controller: LikeController = Depends(get_like_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.unlike_pin(pin_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== LISTAS ====================

@router.get(
    "/pin/{pin_id}",
    response_model=LikesListResponse,
    summary="Obtener usuarios que dieron like a un pin",
)
async def get_pin_likes(
    pin_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: LikeController = Depends(get_like_controller),
):
    return await controller.get_pin_likes(pin_id, limit=limit, offset=offset)


@router.get(
    "/user/{user_id}",
    response_model=UserLikesListResponse,
    summary="Obtener pins que un usuario ha dado like",
)
async def get_user_likes(
    user_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: LikeController = Depends(get_like_controller),
):
    return await controller.get_user_likes(user_id, limit=limit, offset=offset)


# ==================== STATUS ====================

@router.get(
    "/status/{pin_id}",
    response_model=LikeStatusResponse,
    summary="Verificar si ya diste like a un pin",
)
async def check_like_status(
    pin_id: str,
    controller: LikeController = Depends(get_like_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.check_like_status(user_id, pin_id)