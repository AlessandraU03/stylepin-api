"""
Implementación MySQL (SQLAlchemy) del repositorio de Comments (Adapter)
"""
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import func

from internal.comments.domain.entities.comment import Comment
from internal.comments.domain.repositories.comment_repository import CommentRepository
from core.database.models import CommentModel


class MySQLCommentRepository(CommentRepository):

    def __init__(self, db: Session):
        self._db = db

    # ── Mapeo ─────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: CommentModel) -> Comment:
        return Comment(
            id=model.id,
            pin_id=model.pin_id,
            user_id=model.user_id,
            text=model.text,
            parent_comment_id=model.parent_comment_id,
            likes_count=model.likes_count or 0,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # ── CRUD ──────────────────────────────────────────────────

    async def create(self, comment: Comment) -> Comment:
        now = datetime.now(timezone.utc)
        model = CommentModel(
            id=str(uuid.uuid4()),
            pin_id=comment.pin_id,
            user_id=comment.user_id,
            text=comment.text,
            parent_comment_id=comment.parent_comment_id,
            likes_count=0,
            created_at=now,
            updated_at=now,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, comment_id: str) -> Optional[Comment]:
        model = self._db.query(CommentModel).filter(
            CommentModel.id == comment_id
        ).first()
        return self._to_entity(model) if model else None

    async def get_by_pin(
        self,
        pin_id: str,
        limit: int = 50,
        offset: int = 0,
        parent_only: bool = True,
    ) -> List[Comment]:
        query = self._db.query(CommentModel).filter(
            CommentModel.pin_id == pin_id
        )
        if parent_only:
            query = query.filter(CommentModel.parent_comment_id.is_(None))

        models = (
            query
            .order_by(CommentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    async def get_replies(
        self, comment_id: str, limit: int = 20, offset: int = 0
    ) -> List[Comment]:
        models = (
            self._db.query(CommentModel)
            .filter(CommentModel.parent_comment_id == comment_id)
            .order_by(CommentModel.created_at.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    async def update(self, comment: Comment) -> Comment:
        model = self._db.query(CommentModel).filter(
            CommentModel.id == comment.id
        ).first()
        if model:
            model.text = comment.text
            model.likes_count = comment.likes_count
            model.updated_at = datetime.now(timezone.utc)
            self._db.commit()
            self._db.refresh(model)
            return self._to_entity(model)
        return comment

    async def delete(self, comment_id: str) -> bool:
        # Eliminar respuestas hijas primero
        self._db.query(CommentModel).filter(
            CommentModel.parent_comment_id == comment_id
        ).delete()

        # Eliminar el comentario
        deleted = self._db.query(CommentModel).filter(
            CommentModel.id == comment_id
        ).delete()

        self._db.commit()
        return deleted > 0

    async def count_by_pin(self, pin_id: str) -> int:
        return (
            self._db.query(func.count(CommentModel.id))
            .filter(
                CommentModel.pin_id == pin_id,
                CommentModel.parent_comment_id.is_(None)
            )
            .scalar()
        ) or 0

    async def count_replies(self, comment_id: str) -> int:
        return (
            self._db.query(func.count(CommentModel.id))
            .filter(CommentModel.parent_comment_id == comment_id)
            .scalar()
        ) or 0

    async def increment_likes(self, comment_id: str) -> None:
        self._db.query(CommentModel).filter(
            CommentModel.id == comment_id
        ).update({CommentModel.likes_count: CommentModel.likes_count + 1})
        self._db.commit()

    async def decrement_likes(self, comment_id: str) -> None:
        self._db.query(CommentModel).filter(
            CommentModel.id == comment_id,
            CommentModel.likes_count > 0
        ).update({CommentModel.likes_count: CommentModel.likes_count - 1})
        self._db.commit()

    async def get_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Comment]:
        models = (
            self._db.query(CommentModel)
            .filter(CommentModel.user_id == user_id)
            .order_by(CommentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]