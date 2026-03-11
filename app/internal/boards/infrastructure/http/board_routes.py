"""
Rutas HTTP de Boards
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated

from internal.boards.domain.entities.board import (
    BoardResponse,
    BoardPin,
    BoardCollaboratorResponse,
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


# ==================== BOARDS ====================

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


# ==================== BOARD PINS ====================

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


# ==================== COLLABORATORS ====================

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