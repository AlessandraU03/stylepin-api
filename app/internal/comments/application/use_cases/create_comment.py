"""
Caso de uso: Crear un comentario
"""
from internal.comments.domain.entities.comment import Comment
from internal.comments.domain.repositories.comment_repository import CommentRepository


class CreateCommentUseCase:
    def __init__(self, comment_repository: CommentRepository):
        self._repo = comment_repository

    async def execute(
        self,
        pin_id: str,
        user_id: str,
        text: str,
        parent_comment_id: str = None
    ) -> Comment:
        # Si es respuesta, verificar que el padre existe
        if parent_comment_id:
            parent = await self._repo.get_by_id(parent_comment_id)
            if not parent:
                raise ValueError("El comentario padre no existe")
            # Solo un nivel de anidamiento
            if parent.parent_comment_id is not None:
                raise ValueError("No se puede responder a una respuesta")

        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)

        comment = Comment(
            id="",  # se asignará en el repo
            pin_id=pin_id,
            user_id=user_id,
            text=text,
            parent_comment_id=parent_comment_id,
            likes_count=0,
            created_at=now,
            updated_at=now,
        )

        created = await self._repo.create(comment)
        return created