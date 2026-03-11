"""
Caso de uso: Obtener respuestas de un comentario
"""
from typing import List
from internal.comments.domain.entities.comment import Comment
from internal.comments.domain.repositories.comment_repository import CommentRepository


class GetRepliesUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self._repo = comment_repository

    async def execute(
        self,
        comment_id: str,
        limit: int = 20,
        offset: int = 0
    ) -> dict:
        parent = await self._repo.get_by_id(comment_id)
        if not parent:
            raise ValueError("El comentario no existe")

        replies: List[Comment] = await self._repo.get_replies(
            comment_id=comment_id,
            limit=limit,
            offset=offset
        )
        total = await self._repo.count_replies(comment_id)

        return {
            "replies": replies,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": (offset + limit) < total
        }