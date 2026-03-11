"""
Rutas de subida de imágenes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import Optional
from pydantic import BaseModel

from core.image_upload import image_service
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id


router = APIRouter(prefix="/upload", tags=["Upload"])


class ImageUploadResponse(BaseModel):
    url: str
    public_id: str
    width: int
    height: int
    format: str
    size_bytes: int
    thumbnail_url: str


class DeleteImageResponse(BaseModel):
    message: str
    deleted: bool


@router.post(
    "/pin-image",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen para un pin",
)
async def upload_pin_image(
    file: UploadFile = File(..., description="Imagen del pin (JPEG, PNG, WebP, GIF, máx 10MB)"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Sube una imagen a Cloudinary para usarla en un pin.

    **Flujo recomendado:**
    1. Subir imagen con este endpoint → obtener `url`
    2. Crear pin con `POST /api/v1/pins` usando la `url` obtenida
    """
    try:
        result = await image_service.upload_image(file, folder="pins")
        return ImageUploadResponse(
            url=result["url"],
            public_id=result["public_id"],
            width=result["width"],
            height=result["height"],
            format=result["format"],
            size_bytes=result["size_bytes"],
            thumbnail_url=image_service.get_thumbnail_url(result["url"]),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/avatar",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir avatar de usuario",
)
async def upload_avatar(
    file: UploadFile = File(..., description="Foto de perfil (JPEG, PNG, WebP, máx 10MB)"),
    user_id: str = Depends(get_current_user_id),
):
    """Sube una imagen de avatar para el perfil del usuario."""
    try:
        result = await image_service.upload_image(file, folder="avatars")
        return ImageUploadResponse(
            url=result["url"],
            public_id=result["public_id"],
            width=result["width"],
            height=result["height"],
            format=result["format"],
            size_bytes=result["size_bytes"],
            thumbnail_url=image_service.get_thumbnail_url(result["url"], 150, 150),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post(
    "/board-cover",
    response_model=ImageUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Subir imagen de portada de tablero",
)
async def upload_board_cover(
    file: UploadFile = File(..., description="Portada del tablero (JPEG, PNG, WebP, máx 10MB)"),
    user_id: str = Depends(get_current_user_id),
):
    """Sube una imagen de portada para un tablero."""
    try:
        result = await image_service.upload_image(file, folder="boards")
        return ImageUploadResponse(
            url=result["url"],
            public_id=result["public_id"],
            width=result["width"],
            height=result["height"],
            format=result["format"],
            size_bytes=result["size_bytes"],
            thumbnail_url=image_service.get_thumbnail_url(result["url"], 400, 300),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{public_id:path}",
    response_model=DeleteImageResponse,
    summary="Eliminar una imagen",
)
async def delete_image(
    public_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Elimina una imagen de Cloudinary por su public_id."""
    deleted = await image_service.delete_image(public_id)
    return DeleteImageResponse(
        message="Imagen eliminada exitosamente" if deleted else "No se pudo eliminar la imagen",
        deleted=deleted,
    )