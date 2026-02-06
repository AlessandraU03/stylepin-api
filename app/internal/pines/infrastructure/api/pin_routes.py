"""
Rutas de API para Pins
Endpoints REST para gestionar pins
"""
from fastapi import APIRouter, Depends, status, Query, HTTPException
from typing import List, Optional

from app.internal.pines.domain.entities.pin import PinResponse, PinSummary
from app.internal.pines.application.schemas.pin_schemas import (
    CreatePinRequest,
    UpdatePinRequest,
    PinFilters
)
from app.internal.pines.application.use_cases.create_pin import CreatePinUseCase
from app.internal.pines.application.use_cases.get_pins import (
    GetPinsUseCase,
    GetPinByIdUseCase
)
from app.internal.pines.application.use_cases.update_pin import UpdatePinUseCase
from app.internal.pines.application.use_cases.delete_pin import DeletePinUseCase
from fastapi import APIRouter, Depends, status, Query, HTTPException
from app.core.security import get_current_user_id 
from app.internal.pines.infrastructure.api.pin_dependencies import (
    get_create_pin_use_case,
    get_get_pins_use_case,
    get_get_pin_by_id_use_case,
    get_update_pin_use_case,
    get_delete_pin_use_case
)
# ... el resto de tus imports y decoradores de rutas se mantienen igual

router = APIRouter(prefix="/pins", tags=["Pins"])

# ==================== CREATE PIN ====================

@router.post(
    "",
    response_model=PinResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new pin",
    description="Upload a new fashion pin to StylePin"
)
async def create_pin(
    request: CreatePinRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: CreatePinUseCase = Depends(get_create_pin_use_case)
):
    """
    **Create a new pin**
    
    Required fields:
    - **image_url**: URL of the outfit/item image
    - **title**: Pin title (max 200 chars)
    - **category**: outfit_completo, prenda_individual, accesorio, calzado
    
    **Requires authentication** (Bearer token)
    """
    try:
        return await use_case.execute(current_user_id, request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# ==================== GET PINS (FEED) ====================

@router.get(
    "",
    response_model=List[PinSummary],
    status_code=status.HTTP_200_OK,
    summary="Get pins feed",
    description="Get list of pins with optional filters (public feed)"
)
async def get_pins_feed(
    category: Optional[str] = Query(None, description="Filter by category"),
    season: Optional[str] = Query(None, description="Filter by season"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    use_case: GetPinsUseCase = Depends(get_get_pins_use_case)
):
    """
    **Get public pins feed**
    
    Returns a list of pins with summary information
    
    **No authentication required**
    """
    filters = PinFilters(
        category=category,
        season=season,
        user_id=user_id,
        limit=limit,
        offset=offset
    )
    return await use_case.execute(filters)

# ==================== GET PIN BY ID ====================

@router.get(
    "/{pin_id}",
    response_model=PinResponse,
    status_code=status.HTTP_200_OK,
    summary="Get pin by ID",
    description="Get detailed information of a specific pin"
)
async def get_pin_by_id(
    pin_id: str,
    use_case: GetPinByIdUseCase = Depends(get_get_pin_by_id_use_case)
):
    """
    **Get pin details**
    
    Returns complete information about a pin
    
    **Note:** This endpoint increments the view counter
    
    **No authentication required**
    """
    try:
        return await use_case.execute(pin_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

# ==================== GET MY PINS ====================

@router.get(
    "/me/pins",
    response_model=List[PinSummary],
    status_code=status.HTTP_200_OK,
    summary="Get my pins",
    description="Get all pins created by authenticated user"
)
async def get_my_pins(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: str = Depends(get_current_user_id),
    use_case: GetPinsUseCase = Depends(get_get_pins_use_case)
):
    """
    **Get my pins**
    
    Returns all pins created by the authenticated user (including private pins)
    
    **Requires authentication** (Bearer token)
    """
    filters = PinFilters(
        user_id=current_user_id,
        limit=limit,
        offset=offset
    )
    return await use_case.execute(filters)

# ==================== UPDATE PIN ====================

@router.patch(
    "/{pin_id}",
    response_model=PinResponse,
    status_code=status.HTTP_200_OK,
    summary="Update pin",
    description="Update an existing pin (only owner can edit)"
)
async def update_pin(
    pin_id: str,
    request: UpdatePinRequest,
    current_user_id: str = Depends(get_current_user_id),
    use_case: UpdatePinUseCase = Depends(get_update_pin_use_case)
):
    """
    **Update pin**
    
    Update one or more fields of your pin. All fields are optional.
    
    **Note:** Only the owner can update the pin
    
    **Requires authentication** (Bearer token)
    """
    try:
        return await use_case.execute(pin_id, current_user_id, request)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "only edit your own" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

# ==================== DELETE PIN ====================

@router.delete(
    "/{pin_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete pin",
    description="Delete a pin (only owner can delete)"
)
async def delete_pin(
    pin_id: str,
    current_user_id: str = Depends(get_current_user_id),
    use_case: DeletePinUseCase = Depends(get_delete_pin_use_case)
):
    """
    **Delete pin**
    
    Permanently delete a pin from the database.
    
    **Important:** Only the owner can delete the pin
    
    **Requires authentication** (Bearer token)
    """
    try:
        return await use_case.execute(pin_id, current_user_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        elif "only delete your own" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )