"""
Caso de uso: Eliminar un comentario
"""
from internal.comments.domain.repositories.comment_repository import CommentRepository


class DeleteCommentUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self._repo = comment_repository

    async def execute(self, comment_id: str, user_id: str) -> bool:
        comment = await self._repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("El comentario no existe")

        if comment.user_id != user_id:
            raise PermissionError("No tienes permiso para eliminar este comentario")

        return await self._repo.delete(comment_id)