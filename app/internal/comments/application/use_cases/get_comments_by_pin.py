"""
Caso de uso: Obtener comentarios de un pin
"""
from typing import List
from internal.comments.domain.entities.comment import Comment
from internal.comments.domain.repositories.comment_repository import CommentRepository


class GetCommentsByPinUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self._repo = comment_repository

    async def execute(
        self,
        pin_id: str,
        limit: int = 50,
        offset: int = 0,
        parent_only: bool = True
    ) -> dict:
        comments: List[Comment] = await self._repo.get_by_pin(
            pin_id=pin_id,
            limit=limit,
            offset=offset,
            parent_only=parent_only
        )
        total = await self._repo.count_by_pin(pin_id)

        return {
            "comments": comments,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }