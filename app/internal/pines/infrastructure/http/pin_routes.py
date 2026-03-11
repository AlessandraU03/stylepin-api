"""
Rutas HTTP de Pins
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from typing import Annotated, Optional, List
import json
import logging

from internal.pines.domain.entities.pin import PinResponse
from internal.pines.application.schemas.pin_schemas import (
    CreatePinRequest,
    UpdatePinRequest,
    PinListResponse,
    PinSummaryListResponse,
    PinFeedResponse,
    PinTrendingResponse,
    MessageResponse,
)
from internal.pines.infrastructure.http.pin_controller import PinController
from internal.pines.infrastructure.dependencies import get_pin_controller
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id
from core.image_upload import image_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pins", tags=["Pins"])


# ==================== FEED & DISCOVER ====================

@router.get(
    "/feed",
    response_model=PinFeedResponse,
    summary="Feed personalizado del usuario",
)
async def get_feed(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: PinController = Depends(get_pin_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.get_feed(user_id=user_id, limit=limit, offset=offset)


@router.get(
    "/trending",
    response_model=PinTrendingResponse,
    summary="Pins trending",
)
async def get_trending(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    hours: Annotated[int, Query(ge=1, le=168)] = 24,
    controller: PinController = Depends(get_pin_controller),
):
    return await controller.get_trending(limit=limit, hours=hours)


@router.get(
    "/search",
    response_model=PinSummaryListResponse,
    summary="Buscar pins",
)
async def search_pins(
    q: Annotated[str, Query(min_length=1, max_length=100)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: PinController = Depends(get_pin_controller),
):
    try:
        return await controller.search_pins(query=q, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ==================== EXPLORE (con filtros) ====================

@router.get(
    "",
    response_model=PinListResponse,
    summary="Explorar pins con filtros",
)
async def get_pins(
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    category: Optional[str] = Query(None, example="casual"),
    season: Optional[str] = Query(None, example="primavera"),
    price_range: Optional[str] = Query(None, example="500_1000"),
    controller: PinController = Depends(get_pin_controller),
):
    return await controller.get_pins(
        limit=limit,
        offset=offset,
        category=category,
        season=season,
        price_range=price_range,
    )


# ==================== USER PINS ====================

@router.get(
    "/user/{user_id}",
    response_model=PinListResponse,
    summary="Pins de un usuario",
)
async def get_user_pins(
    user_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: PinController = Depends(get_pin_controller),
    current_user_id: str = Depends(get_current_user_id),
):
    return await controller.get_user_pins(
        user_id, current_user_id=current_user_id, limit=limit, offset=offset
    )


# ==================== CRUD ====================

@router.post(
    "",
    response_model=PinResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un pin con imagen",
    description="📱 Sube imagen + datos en una sola llamada (multipart/form-data)",
)
async def create_pin(
    image: UploadFile = File(..., description="Imagen del pin (JPEG, PNG, WebP, GIF, máx 10MB)"),
    title: str = Form(..., min_length=1, max_length=200, description="Título del pin"),
    description: Optional[str] = Form(None, max_length=2000, description="Descripción"),
    category: str = Form(..., description="outfit_completo | prenda_individual | accesorio | calzado"),
    styles: Optional[str] = Form(None, description='JSON array: ["casual", "streetwear"]'),
    occasions: Optional[str] = Form(None, description='JSON array: ["playa", "fiesta"]'),
    season: Optional[str] = Form("todo_el_ano", description="primavera | verano | otono | invierno | todo_el_ano"),
    brands: Optional[str] = Form(None, description='JSON array: ["Zara", "H&M"]'),
    price_range: Optional[str] = Form("bajo_500", description="bajo_500 | 500_1000 | 1000_2000 | mas_2000"),
    where_to_buy: Optional[str] = Form(None, max_length=200),
    purchase_link: Optional[str] = Form(None, max_length=500),
    colors: Optional[str] = Form(None, description='JSON array: ["azul", "blanco"]'),
    tags: Optional[str] = Form(None, description='JSON array: ["verano2026", "playa"]'),
    is_private: Optional[bool] = Form(False),
    user_id: str = Depends(get_current_user_id),
    controller: PinController = Depends(get_pin_controller),
):
    # LOGS DETALLADOS
    logger.warning(f"POST /pins - image: {image.filename if image else None}")
    logger.warning(f"title: {title}, category: {category}, season: {season}, price_range: {price_range}, is_private: {is_private}")
    logger.warning(f"description: {description}, styles: {styles}, occasions: {occasions}, brands: {brands}, where_to_buy: {where_to_buy}, purchase_link: {purchase_link}, colors: {colors}, tags: {tags}")
    logger.warning(f"user_id: {user_id}")

    # ...existing code...
    """
    📱 **Endpoint principal para la app móvil.**

    Sube la imagen a Cloudinary y crea el pin en una sola llamada.

    Los campos `styles`, `occasions`, `brands`, `colors`, `tags`
    se envían como strings JSON: `["valor1", "valor2"]`
    """

    # ── Helper para parsear JSON arrays ───────────────────────
    def parse_json_list(value: Optional[str]) -> List[str]:
        if not value:
            return []
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []

    # 1️⃣ Subir imagen a Cloudinary
    try:
        upload_result = await image_service.upload_image(image, folder="pins")
        image_url = upload_result["url"]
        logger.info(f"✅ Imagen subida: {image_url}")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al subir imagen: {str(e)}",
        )

    # 2️⃣ Crear el pin
    try:
        pin_data = CreatePinRequest(
            title=title,
            description=description,
            image_url=image_url,
            category=category,
            styles=parse_json_list(styles),
            occasions=parse_json_list(occasions),
            season=season or "todo_el_ano",
            brands=parse_json_list(brands),
            price_range=price_range or "bajo_500",
            where_to_buy=where_to_buy,
            purchase_link=purchase_link,
            colors=parse_json_list(colors),
            tags=parse_json_list(tags),
            is_private=is_private or False,
        )

        return await controller.create_pin(pin_data, user_id)

    except Exception as e:
        # Si falla crear el pin, eliminar la imagen subida
        await image_service.delete_image(upload_result["public_id"])
        logger.error(f"❌ Error creando pin, imagen eliminada: {e}", exc_info=True)  # <-- AGREGA ESTA LÍNEA
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/{pin_id}",
    response_model=PinResponse,
    summary="Obtener un pin por ID",
)
async def get_pin(
    pin_id: str,
    controller: PinController = Depends(get_pin_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.get_pin(pin_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.put(
    "/{pin_id}",
    response_model=PinResponse,
    summary="Actualizar un pin",
)
async def update_pin(
    pin_id: str,
    body: UpdatePinRequest,
    controller: PinController = Depends(get_pin_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.update_pin(pin_id, body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{pin_id}",
    response_model=MessageResponse,
    summary="Eliminar un pin",
)
async def delete_pin(
    pin_id: str,
    controller: PinController = Depends(get_pin_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.delete_pin(pin_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))