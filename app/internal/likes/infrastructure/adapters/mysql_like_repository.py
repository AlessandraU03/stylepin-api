"""
Implementación MySQL (SQLAlchemy) del repositorio de Likes (Adapter)
"""
from typing import List
from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from internal.likes.domain.entities.like import Like
from internal.likes.domain.repositories.like_repository import LikeRepository
from core.database.models import LikeModel


class MySQLLikeRepository(LikeRepository):

    def __init__(self, db: Session):
        self._db = db

    # ── Mapeo ─────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: LikeModel) -> Like:
        return Like(
            id=model.id,
            user_id=model.user_id,
            pin_id=model.pin_id,
            created_at=model.created_at,
        )

    # ── CRUD ──────────────────────────────────────────────────

    async def create(self, like: Like) -> Like:
        model = LikeModel(
            id=str(uuid.uuid4()),
            user_id=like.user_id,
            pin_id=like.pin_id,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: str, pin_id: str) -> bool:
        deleted = self._db.query(LikeModel).filter(
            and_(
                LikeModel.user_id == user_id,
                LikeModel.pin_id == pin_id,
            )
        ).delete()
        self._db.commit()
        return deleted > 0

    async def get_by_pin(self, pin_id: str, limit: int = 50) -> List[Like]:
        models = (
            self._db.query(LikeModel)
            .filter(LikeModel.pin_id == pin_id)
            .order_by(LikeModel.created_at.desc())
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    async def get_by_user(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Like]:
        models = (
            self._db.query(LikeModel)
            .filter(LikeModel.user_id == user_id)
            .order_by(LikeModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    async def exists(self, user_id: str, pin_id: str) -> bool:
        count = (
            self._db.query(func.count(LikeModel.id))
            .filter(
                and_(
                    LikeModel.user_id == user_id,
                    LikeModel.pin_id == pin_id,
                )
            )
            .scalar()
        )
        return (count or 0) > 0

    async def count_by_pin(self, pin_id: str) -> int:
        return (
            self._db.query(func.count(LikeModel.id))
            .filter(LikeModel.pin_id == pin_id)
            .scalar()
        ) or 0

    async def count_by_user(self, user_id: str) -> int:
        return (
            self._db.query(func.count(LikeModel.id))
            .filter(LikeModel.user_id == user_id)
            .scalar()
        ) or 0