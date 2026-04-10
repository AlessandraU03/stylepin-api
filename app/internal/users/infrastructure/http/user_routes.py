"""
Rutas HTTP de Users
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from typing import Annotated, Optional

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


# ✅ AGREGAR MODELO PARA FCM TOKEN
class SaveFCMTokenRequest(BaseModel):
    token: str
    device_name: Optional[str] = None


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


# ====================== FCM TOKEN ======================

# ✅ CORREGIR: Usar modelo Pydantic en Body
@router.post(
    "/fcm-token",
    summary="Guardar token FCM para notificaciones push",
)
async def save_fcm_token(
    body: SaveFCMTokenRequest,  # ✅ CAMBIAR: Recibir como JSON Body
    user_id: str = Depends(get_current_user_id),
    controller: UserController = Depends(get_user_controller),
):
    """Guardar token FCM del dispositivo"""
    try:
        if not body.token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token es requerido"
            )
        
        result = await controller.save_fcm_token(
            user_id, 
            body.token, 
            body.device_name
        )
        
        return {
            "status": "success",
            "message": "✅ Token FCM guardado correctamente",
            "data": result
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )


# ====================== TEST NOTIFICATION ======================

@router.get(
    "/test-notification",
    summary="Enviar notificación de prueba",
)
async def test_notification(
    user_id: str = Depends(get_current_user_id),
    controller: UserController = Depends(get_user_controller),
):
    """Enviar notificación de prueba al usuario autenticado"""
    print(f"📱 TEST NOTIFICATION para user_id: {user_id}")

    try:
        # 🔍 Obtener usuario real desde DB
        user = await controller._get_user_uc.execute_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado en DB"
            )

        # 🔔 Obtener FCM token desde repository
        fcm_token = await controller._get_user_uc._user_repo.get_fcm_token(user_id)
        
        if not fcm_token:
            return {
                "error": "El usuario no tiene FCM token registrado",
                "user_id": user_id,
                "help": "Primero guardar FCM token en POST /api/v1/users/fcm-token"
            }

        # 🔔 Enviar notificación a Firebase
        try:
            from app.core.notifications import send_push

            result = await send_push(
                token=fcm_token,
                title="🔥 PRUEBA StylePin",
                body="Si ves esto, ¡Firebase funciona correctamente!"
            )

            print(f"✅ RESULTADO FIREBASE: {result}")

            return {
                "status": "success",
                "message": "✅ Notificación enviada correctamente",
                "firebase_response": result,
                "user_id": user_id
            }
        except Exception as firebase_error:
            print(f"❌ Error Firebase: {firebase_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al enviar notificación: {str(firebase_error)}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error general: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
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