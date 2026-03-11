"""
Rutas HTTP de Autenticación
"""
from fastapi import APIRouter, Depends, HTTPException, status

from internal.users.application.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
)
from internal.users.infrastructure.http.auth_controller import AuthController
from internal.users.infrastructure.dependencies import get_auth_controller


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
async def register(
    body: RegisterRequest,
    controller: AuthController = Depends(get_auth_controller),
):
    try:
        return await controller.register(body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Iniciar sesión",
)
async def login(
    body: LoginRequest,
    controller: AuthController = Depends(get_auth_controller),
):
    try:
        return await controller.login(body)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )