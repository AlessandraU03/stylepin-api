"""
Caso de uso: Dar/quitar like a un comentario
"""
from internal.comments.domain.repositories.comment_repository import CommentRepository


class LikeCommentUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self._repo = comment_repository

    async def like(self, comment_id: str) -> None:
        comment = await self._repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("El comentario no existe")
        await self._repo.increment_likes(comment_id)

    async def unlike(self, comment_id: str) -> None:
        comment = await self._repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("El comentario no existe")
        if comment.likes_count <= 0:
            raise ValueError("El comentario no tiene likes")
        await self._repo.decrement_likes(comment_id)