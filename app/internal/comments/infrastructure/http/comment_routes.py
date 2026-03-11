"""
Rutas HTTP de Comments
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated

from internal.comments.domain.entities.comment import CommentResponse
from internal.comments.application.schemas.comment_schemas import (
    CreateCommentRequest,
    UpdateCommentRequest,
    CommentListResponse,
    RepliesListResponse,
    MessageResponse,
)
from internal.comments.infrastructure.http.comment_controller import CommentController
from internal.comments.infrastructure.dependencies import get_comment_controller
from internal.users.infrastructure.middlewares.auth_middleware import get_current_user_id

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.post(
    "",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear comentario o respuesta",
)
async def create_comment(
    body: CreateCommentRequest,
    controller: CommentController = Depends(get_comment_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.create_comment(body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/pin/{pin_id}",
    response_model=CommentListResponse,
    summary="Obtener comentarios de un pin",
)
async def get_comments_by_pin(
    pin_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: CommentController = Depends(get_comment_controller),
    user_id: str = Depends(get_current_user_id),
):
    return await controller.get_comments_by_pin(pin_id, current_user_id=user_id, limit=limit, offset=offset)


@router.get(
    "/{comment_id}/replies",
    response_model=RepliesListResponse,
    summary="Obtener respuestas de un comentario",
)
async def get_replies(
    comment_id: str,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    controller: CommentController = Depends(get_comment_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.get_replies(comment_id, current_user_id=user_id, limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.put(
    "/{comment_id}",
    response_model=CommentResponse,
    summary="Editar un comentario",
)
async def update_comment(
    comment_id: str,
    body: UpdateCommentRequest,
    controller: CommentController = Depends(get_comment_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.update_comment(comment_id, body, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.delete(
    "/{comment_id}",
    response_model=MessageResponse,
    summary="Eliminar un comentario",
)
async def delete_comment(
    comment_id: str,
    controller: CommentController = Depends(get_comment_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.delete_comment(comment_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/{comment_id}/like",
    response_model=MessageResponse,
    summary="Dar like",
)
async def like_comment(
    comment_id: str,
    controller: CommentController = Depends(get_comment_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.like_comment(comment_id, user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{comment_id}/like",
    response_model=MessageResponse,
    summary="Quitar like",
)
async def unlike_comment(
    comment_id: str,
    controller: CommentController = Depends(get_comment_controller),
    user_id: str = Depends(get_current_user_id),
):
    try:
        return await controller.unlike_comment(comment_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))