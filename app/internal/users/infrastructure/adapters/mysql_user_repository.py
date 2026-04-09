"""
Implementación MySQL (SQLAlchemy) del repositorio de Users (Adapter)
"""
from typing import Optional, List
from datetime import datetime, timezone
import uuid
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from internal.users.domain.entities.user import User
from internal.users.domain.repositories.user_repository import UserRepository
from internal.users.infrastructure.database.user_model import User


class MySQLUserRepository(UserRepository):

    def __init__(self, db: Session):
        self._db = db

    # ── Mapeo ─────────────────────────────────────────────────

    @staticmethod
    def _parse_json_list(value) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        return []

    @staticmethod
    def _to_json(value: Optional[List[str]]) -> Optional[str]:
        if value:
            return json.dumps(value)
        return None

    def _to_entity(self, model: User) -> User:
        return User(
            id=model.id,
            username=model.username,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            bio=model.bio,
            avatar_url=model.avatar_url,
            gender=model.gender or "prefer_not_to_say",
            preferred_styles=self._parse_json_list(model.preferred_styles),
            is_verified=model.is_verified or False,
            is_active=model.is_active if model.is_active is not None else True,
            role=model.role or "user",
            email_verified_at=model.email_verified_at,
            login_attempts=model.login_attempts or 0,
            locked_until=model.locked_until,
            password_reset_token=model.password_reset_token,
            password_reset_token_expiry=model.password_reset_token_expiry,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login,
        )

    # ── CRUD ──────────────────────────────────────────────────

    async def create(self, user: User) -> User:
        now = datetime.now(timezone.utc)
        model = User(
            id=str(uuid.uuid4()),
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            gender=user.gender,
            preferred_styles=self._to_json(user.preferred_styles),
            is_verified=False,
            is_active=True,
            role="user",
            email_verified_at=None,
            login_attempts=0,
            locked_until=None,
            password_reset_token=None,
            password_reset_token_expiry=None,
            created_at=now,
            updated_at=now,
            last_login=None,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: str) -> Optional[User]:
        model = self._db.query(User).filter(
            User.id == user_id,
        ).first()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        model = self._db.query(User).filter(
            User.email == email,
        ).first()
        return self._to_entity(model) if model else None

    async def get_by_username(self, username: str) -> Optional[User]:
        model = self._db.query(User).filter(
            User.username == username,
        ).first()
        return self._to_entity(model) if model else None

    async def get_by_identity(self, identity: str) -> Optional[User]:
        """Busca por email o username"""
        identity_lower = identity.lower().strip()
        model = self._db.query(User).filter(
            or_(
                User.email == identity_lower,
                User.username == identity_lower,
            )
        ).first()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        model = self._db.query(User).filter(
            User.id == user.id
        ).first()
        if model:
            model.full_name = user.full_name
            model.bio = user.bio
            model.avatar_url = user.avatar_url
            model.gender = user.gender
            model.preferred_styles = self._to_json(user.preferred_styles)
            model.password_hash = user.password_hash
            model.is_active = user.is_active
            model.updated_at = datetime.now(timezone.utc)
            self._db.commit()
            self._db.refresh(model)
            return self._to_entity(model)
        return user

    async def delete(self, user_id: str) -> bool:
        """Soft delete - desactiva la cuenta"""
        model = self._db.query(User).filter(
            User.id == user_id
        ).first()
        if model:
            model.is_active = False
            model.updated_at = datetime.now(timezone.utc)
            self._db.commit()
            return True
        return False

    # ── Validaciones ──────────────────────────────────────────

    async def exists_by_email(self, email: str) -> bool:
        count = (
            self._db.query(func.count(User.id))
            .filter(User.email == email)
            .scalar()
        )
        return (count or 0) > 0

    async def exists_by_username(self, username: str) -> bool:
        count = (
            self._db.query(func.count(User.id))
            .filter(User.username == username)
            .scalar()
        )
        return (count or 0) > 0

    # ── Seguridad / Login ─────────────────────────────────────

    async def update_last_login(self, user_id: str) -> None:
        self._db.query(User).filter(
            User.id == user_id
        ).update({
            User.last_login: datetime.now(timezone.utc),
        })
        self._db.commit()

    async def update_login_attempts(
        self,
        user_id: str,
        attempts: int,
        locked_until: Optional[datetime],
    ) -> None:
        self._db.query(User).filter(
            User.id == user_id
        ).update({
            User.login_attempts: attempts,
            User.locked_until: locked_until,
        })
        self._db.commit()

    async def increment_login_attempts(self, user_id: str) -> None:
        self._db.query(User).filter(
            User.id == user_id
        ).update({
            User.login_attempts: User.login_attempts + 1,
        })
        self._db.commit()

    async def reset_login_attempts(self, user_id: str) -> None:
        self._db.query(User).filter(
            User.id == user_id
        ).update({
            User.login_attempts: 0,
            User.locked_until: None,
        })
        self._db.commit()

    async def lock_account(self, user_id: str, until: datetime) -> None:
        self._db.query(User).filter(
            User.id == user_id
        ).update({
            User.locked_until: until,
        })
        self._db.commit()

    # ── Búsqueda ──────────────────────────────────────────────

    async def search_users(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[User]:
        search_term = f"%{query}%"
        models = (
            self._db.query(User)
            .filter(
                User.is_active == True,
                or_(
                    User.username.ilike(search_term),
                    User.full_name.ilike(search_term),
                )
            )
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    # ── Estadísticas ──────────────────────────────────────────

    async def get_user_stats(self, user_id: str) -> dict:
        """
        Obtener estadísticas del usuario.
        TODO: Integrar con tablas reales de pins, follows, boards.
        Por ahora retorna conteos básicos.
        """
        # Importar modelos si existen
        stats = {
            "total_pins": 0,
            "total_followers": 0,
            "total_following": 0,
            "total_boards": 0,
        }

        try:
            from core.database.models import Pin
            stats["total_pins"] = (
                self._db.query(func.count(Pin.id))
                .filter(Pin.user_id == user_id)
                .scalar() or 0
            )
        except ImportError:
            pass

        try:
            from core.database.models import Follow
            stats["total_followers"] = (
                self._db.query(func.count(Follow.id))
                .filter(Follow.following_id == user_id)
                .scalar() or 0
            )
            stats["total_following"] = (
                self._db.query(func.count(Follow.id))
                .filter(Follow.follower_id == user_id)
                .scalar() or 0
            )
        except ImportError:
            pass

        try:
            from core.database.models import Board
            stats["total_boards"] = (
                self._db.query(func.count(Board.id))
                .filter(Board.user_id == user_id)
                .scalar() or 0
            )
        except ImportError:
            pass

        return stats
