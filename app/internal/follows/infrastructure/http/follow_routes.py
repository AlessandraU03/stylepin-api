"""
Rutas HTTP de Follows
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated

from internal.follows.application.schemas.follow_schemas import (
    FollowUserRequest,
    FollowersListResponse,
    FollowingListResponse,
    FollowStatusResponse,
    FollowCountsResponse,
    MessageResponse,
)
from internal.follows.infrastructure.http.follow_controller import FollowController
from internal.follows.infrastructure.dependencies import get_follow_controller
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id

router = APIRouter(prefix="/follows", tags=["Follows"])


@router.post(
    "",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Seguir a un usuario",
)
async def follow_user(
    body: FollowUserRequest,
    controller: FollowController = Depends(get_follow_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.follow_user(body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{target_user_id}",
    response_model=MessageResponse,
    summary="Dejar de seguir a un usuario",
)
async def unfollow_user(
    target_user_id: str,
    controller: FollowController = Depends(get_follow_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.unfollow_user(target_user_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/{user_id}/followers",
    response_model=FollowersListResponse,
    summary="Obtener seguidores de un usuario",
)
async def get_followers(
    user_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: FollowController = Depends(get_follow_controller),
    current_user_id: str = Depends(get_current_user_id),
):
    return await controller.get_followers(
        user_id, current_user_id=current_user_id, limit=limit, offset=offset
    )


@router.get(
    "/{user_id}/following",
    response_model=FollowingListResponse,
    summary="Obtener usuarios que sigue un usuario",
)
async def get_following(
    user_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: FollowController = Depends(get_follow_controller),
    current_user_id: str = Depends(get_current_user_id),
):
    return await controller.get_following(
        user_id, current_user_id=current_user_id, limit=limit, offset=offset
    )


@router.get(
    "/status/{target_user_id}",
    response_model=FollowStatusResponse,
    summary="Verificar estado de follow con otro usuario",
)
async def check_follow_status(
    target_user_id: str,
    controller: FollowController = Depends(get_follow_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.check_follow_status(user_id, target_user_id)


@router.get(
    "/{user_id}/counts",
    response_model=FollowCountsResponse,
    summary="Obtener contadores de seguidores y seguidos",
)
async def get_follow_counts(
    user_id: str,
    controller: FollowController = Depends(get_follow_controller),
):
    return await controller.get_follow_counts(user_id)