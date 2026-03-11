"""
Implementación MySQL (SQLAlchemy) del repositorio de Follows (Adapter)
"""
from typing import List
from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from internal.follows.domain.entities.follow import Follow
from internal.follows.domain.repositories.follow_repository import FollowRepository
from core.database.models import FollowModel


class MySQLFollowRepository(FollowRepository):

    def __init__(self, db: Session):
        self._db = db

    # ── Mapeo ─────────────────────────────────────────────────

    @staticmethod
    def _to_entity(model: FollowModel) -> Follow:
        return Follow(
            id=model.id,
            follower_id=model.follower_id,
            following_id=model.following_id,
            created_at=model.created_at,
        )

    # ── CRUD ──────────────────────────────────────────────────

    async def create(self, follow: Follow) -> Follow:
        model = FollowModel(
            id=str(uuid.uuid4()),
            follower_id=follow.follower_id,
            following_id=follow.following_id,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    async def delete(self, follower_id: str, following_id: str) -> bool:
        deleted = self._db.query(FollowModel).filter(
            and_(
                FollowModel.follower_id == follower_id,
                FollowModel.following_id == following_id,
            )
        ).delete()
        self._db.commit()
        return deleted > 0

    async def get_followers(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Follow]:
        models = (
            self._db.query(FollowModel)
            .filter(FollowModel.following_id == user_id)
            .order_by(FollowModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    async def get_following(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Follow]:
        models = (
            self._db.query(FollowModel)
            .filter(FollowModel.follower_id == user_id)
            .order_by(FollowModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    async def exists(self, follower_id: str, following_id: str) -> bool:
        count = (
            self._db.query(func.count(FollowModel.id))
            .filter(
                and_(
                    FollowModel.follower_id == follower_id,
                    FollowModel.following_id == following_id,
                )
            )
            .scalar()
        )
        return (count or 0) > 0

    async def count_followers(self, user_id: str) -> int:
        return (
            self._db.query(func.count(FollowModel.id))
            .filter(FollowModel.following_id == user_id)
            .scalar()
        ) or 0

    async def count_following(self, user_id: str) -> int:
        return (
            self._db.query(func.count(FollowModel.id))
            .filter(FollowModel.follower_id == user_id)
            .scalar()
        ) or 0

    async def get_follower_ids(self, user_id: str) -> List[str]:
        rows = (
            self._db.query(FollowModel.follower_id)
            .filter(FollowModel.following_id == user_id)
            .all()
        )
        return [row[0] for row in rows]

    async def get_following_ids(self, user_id: str) -> List[str]:
        rows = (
            self._db.query(FollowModel.following_id)
            .filter(FollowModel.follower_id == user_id)
            .all()
        )
        return [row[0] for row in rows]

    async def are_mutual_followers(self, user_id_1: str, user_id_2: str) -> bool:
        follows_1_to_2 = await self.exists(user_id_1, user_id_2)
        follows_2_to_1 = await self.exists(user_id_2, user_id_1)
        return follows_1_to_2 and follows_2_to_1