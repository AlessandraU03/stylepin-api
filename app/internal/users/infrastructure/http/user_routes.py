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


# ====================== MI PERFIL (protegido) ======================

@router.get(
    "/me",
    response_model=UserMe,
    summary="Obtener mi perfil",
)
async def get_me(
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.get_me(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.put(
    "/me",
    response_model=UserMe,
    summary="Actualizar mi perfil",
)
async def update_me(
    body: UpdateProfileRequest,
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.update_profile(user_id, body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(e)
        )


@router.put(
    "/me/password",
    response_model=MessageResponse,
    summary="Cambiar mi contraseña",
)
async def change_password(
    body: ChangePasswordRequest,
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.change_password(user_id, body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.delete(
    "/me",
    response_model=MessageResponse,
    summary="Eliminar mi cuenta",
)
async def delete_me(
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.delete_account(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


@router.get(
    "/me/stats",
    response_model=UserStatsResponse,
    summary="Mis estadísticas",
)
async def get_my_stats(
    controller: UserController = Depends(get_user_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.get_stats(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


# ====================== BÚSQUEDA ======================

@router.get(
    "/search",
    response_model=UserListResponse,
    summary="Buscar usuarios",
)
async def search_users(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: UserController = Depends(get_user_controller),
):
    try:
        return await controller.search_users(query=q, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


# ====================== PERFIL PÚBLICO ======================

@router.get(
    "/profile/{username}",
    response_model=UserProfileResponse,
    summary="Ver perfil de un usuario por username",
)
async def get_profile(
    username: str,
    controller: UserController = Depends(get_user_controller),
):
    try:
        return await controller.get_profile(username)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "/{user_id}",
    response_model=UserProfileResponse,
    summary="Ver perfil de un usuario por ID",
)
async def get_user(
    user_id: str,
    controller: UserController = Depends(get_user_controller),
):
    try:
        return await controller.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )


@router.get(
    "/{user_id}/stats",
    response_model=UserStatsResponse,
    summary="Estadísticas de un usuario",
)
async def get_user_stats(
    user_id: str,
    controller: UserController = Depends(get_user_controller),
):
    try:
        return await controller.get_stats(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(e)
        )