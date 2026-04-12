"""
Rutas HTTP de Boards - CORREGIDO
Problema: GET /api/v1/boards devolvía List[BoardSummary] (array directo)
pero el cliente Android espera BoardListResponse {boards, total, limit, offset, has_more}
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, Optional, List

from internal.boards.domain.entities.board import (
    BoardResponse,
    BoardPin,
    BoardCollaboratorResponse,
    BoardSummary,
)
from internal.boards.application.schemas.board_schemas import (
    CreateBoardRequest,
    UpdateBoardRequest,
    AddPinToBoardRequest,
    AddCollaboratorRequest,
    UpdateCollaboratorRequest,
    BoardListResponse,
    BoardPinListResponse,
    CollaboratorListResponse,
    MessageResponse,
)
from internal.boards.infrastructure.http.board_controller import BoardController
from internal.boards.infrastructure.dependencies import get_board_controller
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id

router = APIRouter(prefix="/boards", tags=["Boards"])


# ── GET /boards ───────────────────────────────────────────────
# CORRECCIÓN: devuelve BoardListResponse en vez de List[BoardSummary]
# El cliente Android llama a .body()?.boards para extraer la lista

@router.get(
    "",
    response_model=BoardListResponse,   # ← CAMBIADO de List[BoardSummary]
    status_code=status.HTTP_200_OK,
    summary="Get all public boards",
    description="Get list of public boards with optional filters"
)
async def get_all_boards(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    controller: BoardController = Depends(get_board_controller),
):
    summaries = await controller.get_all_boards(
        user_id=user_id,
        limit=limit,
        offset=offset
    )
    # Convertir List[BoardSummary] a BoardListResponse para que el Android
    # pueda extraerlo con .body()?.boards
    return BoardListResponse(
        boards=summaries,      # BoardSummary es compatible con BoardDto en el cliente
        total=len(summaries),
        limit=limit,
        offset=offset,
        has_more=len(summaries) >= limit,
    )


# ── POST /boards ──────────────────────────────────────────────

@router.post(
    "",
    response_model=BoardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un tablero",
)
async def create_board(
    body: CreateBoardRequest,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.create_board(body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# ── GET /boards/{board_id} ────────────────────────────────────

@router.get(
    "/{board_id}",
    response_model=BoardResponse,
    summary="Obtener un tablero por ID",
)
async def get_board(
    board_id: str,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.get_board(board_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── GET /boards/user/{user_id} ────────────────────────────────

@router.get(
    "/user/{user_id}",
    response_model=BoardListResponse,
    summary="Obtener tableros de un usuario",
)
async def get_user_boards(
    user_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: BoardController = Depends(get_board_controller),
    current_user_id: str = Depends(get_current_user_id),
):
    return await controller.get_user_boards(
        user_id, current_user_id=current_user_id, limit=limit, offset=offset
    )


# ── PUT /boards/{board_id} ────────────────────────────────────

@router.put(
    "/{board_id}",
    response_model=BoardResponse,
    summary="Actualizar un tablero",
)
async def update_board(
    board_id: str,
    body: UpdateBoardRequest,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.update_board(board_id, body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── DELETE /boards/{board_id} ─────────────────────────────────

@router.delete(
    "/{board_id}",
    response_model=MessageResponse,
    summary="Eliminar un tablero",
)
async def delete_board(
    board_id: str,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.delete_board(board_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── POST /boards/{board_id}/pins ──────────────────────────────

@router.post(
    "/{board_id}/pins",
    response_model=BoardPin,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar pin a un tablero",
)
async def add_pin_to_board(
    board_id: str,
    body: AddPinToBoardRequest,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.add_pin(board_id, body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── DELETE /boards/{board_id}/pins/{pin_id} ───────────────────

@router.delete(
    "/{board_id}/pins/{pin_id}",
    response_model=MessageResponse,
    summary="Quitar pin de un tablero",
)
async def remove_pin_from_board(
    board_id: str,
    pin_id: str,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.remove_pin(board_id, pin_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── GET /boards/{board_id}/pins ───────────────────────────────

@router.get(
    "/{board_id}/pins",
    response_model=BoardPinListResponse,
    summary="Obtener pins de un tablero",
)
async def get_board_pins(
    board_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.get_board_pins(board_id, user_id=user_id, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── POST /boards/{board_id}/collaborators ─────────────────────

@router.post(
    "/{board_id}/collaborators",
    response_model=BoardCollaboratorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Agregar colaborador",
)
async def add_collaborator(
    board_id: str,
    body: AddCollaboratorRequest,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.add_collaborator(board_id, body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── DELETE /boards/{board_id}/collaborators/{id} ──────────────

@router.delete(
    "/{board_id}/collaborators/{collaborator_user_id}",
    response_model=MessageResponse,
    summary="Quitar colaborador",
)
async def remove_collaborator(
    board_id: str,
    collaborator_user_id: str,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.remove_collaborator(board_id, collaborator_user_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── PUT /boards/{board_id}/collaborators/{id} ─────────────────

@router.put(
    "/{board_id}/collaborators/{collaborator_user_id}",
    response_model=BoardCollaboratorResponse,
    summary="Actualizar permisos de colaborador",
)
async def update_collaborator(
    board_id: str,
    collaborator_user_id: str,
    body: UpdateCollaboratorRequest,
    controller: BoardController = Depends(get_board_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.update_collaborator(board_id, collaborator_user_id, body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


# ── GET /boards/{board_id}/collaborators ──────────────────────

@router.get(
    "/{board_id}/collaborators",
    response_model=CollaboratorListResponse,
    summary="Obtener colaboradores de un tablero",
)
async def get_collaborators(
    board_id: str,
    controller: BoardController = Depends(get_board_controller),
):
    try:
        return await controller.get_collaborators(board_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))