"""
Caso de uso: Actualizar un comentario
"""
from datetime import datetime, timezone
from internal.comments.domain.entities.comment import Comment
from internal.comments.domain.repositories.comment_repository import CommentRepository


class UpdateCommentUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self._repo = comment_repository

    async def execute(
        self,
        comment_id: str,
        user_id: str,
        new_text: str
    ) -> Comment:
        comment = await self._repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("El comentario no existe")

        if comment.user_id != user_id:
            raise PermissionError("No tienes permiso para editar este comentario")

        # Crear copia actualizada (Pydantic es inmutable por defecto)
        updated_comment = comment.model_copy(update={
            "text": new_text.strip(),
            "updated_at": datetime.now(timezone.utc),
        })

        result = await self._repo.update(updated_comment)
        return result