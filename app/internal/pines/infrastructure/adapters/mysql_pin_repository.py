"""
Implementación MySQL (SQLAlchemy) del repositorio de Pins (Adapter)
"""
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_

from internal.pines.domain.entities.pin import Pin, PinResponse
from internal.pines.domain.repositories.pin_repository import PinRepository
from core.database.models import PinModel, UserModel


class MySQLPinRepository(PinRepository):

    def __init__(self, db: Session):
        self._db = db

    # ── Mapeo ─────────────────────────────────────────────────

    @staticmethod
    def _parse_json_list(value) -> List[str]:
        """Parsea un campo que puede ser JSON string o lista"""
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
        """Convierte lista a JSON string para almacenar"""
        if value:
            return json.dumps(value)
        return None

    def _to_entity(self, model: PinModel) -> Pin:
        return Pin(
            id=model.id,
            user_id=model.user_id,
            image_url=model.image_url,
            title=model.title,
            description=model.description,
            category=model.category,
            styles=self._parse_json_list(model.styles),
            occasions=self._parse_json_list(model.occasions),
            season=model.season or "todo_el_ano",
            brands=self._parse_json_list(model.brands),
            price_range=model.price_range or "bajo_500",
            where_to_buy=model.where_to_buy,
            purchase_link=model.purchase_link,
            likes_count=model.likes_count or 0,
            saves_count=model.saves_count or 0,
            comments_count=model.comments_count or 0,
            views_count=model.views_count or 0,
            colors=self._parse_json_list(model.colors),
            tags=self._parse_json_list(model.tags),
            is_private=model.is_private or False,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    # ── CRUD ──────────────────────────────────────────────────

    async def create(self, pin: Pin) -> Pin:
        now = datetime.now(timezone.utc)
        model = PinModel(
            id=str(uuid.uuid4()),
            user_id=pin.user_id,
            image_url=pin.image_url,
            title=pin.title,
            description=pin.description,
            category=pin.category,
            styles=self._to_json(pin.styles),
            occasions=self._to_json(pin.occasions),
            season=pin.season,
            brands=self._to_json(pin.brands),
            price_range=pin.price_range,
            where_to_buy=pin.where_to_buy,
            purchase_link=pin.purchase_link,
            likes_count=0,
            saves_count=0,
            comments_count=0,
            views_count=0,
            colors=self._to_json(pin.colors),
            tags=self._to_json(pin.tags),
            is_private=pin.is_private,
            created_at=now,
            updated_at=now,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, pin_id: str) -> Optional[Pin]:
        model = self._db.query(PinModel).filter(
            PinModel.id == pin_id
        ).first()
        return self._to_entity(model) if model else None



    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        season: Optional[str] = None,
        price_range: Optional[str] = None,
    ) -> List[Pin]:
        query = (
            self._db.query(PinModel, UserModel)
            .join(UserModel, PinModel.user_id == UserModel.id)
            .filter(PinModel.is_private == False)
        )

        if user_id:
            query = query.filter(PinModel.user_id == user_id)
        if category:
            query = query.filter(PinModel.category == category)
        if season:
            query = query.filter(PinModel.season == season)
        if price_range:
            query = query.filter(PinModel.price_range == price_range)

        models = (
            query
            .order_by(PinModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity_with_user(pin, user) for pin, user in models]

    def _to_entity_with_user(self, pin: PinModel, user: UserModel) -> Pin:
           return PinResponse(
        id=pin.id,
        user_id=pin.user_id,
        user_username=user.username,
        user_full_name=user.full_name,
        user_avatar_url=user.avatar_url,
        user_is_verified=user.is_verified,
        image_url=pin.image_url,
        title=pin.title,
        description=pin.description,
        category=pin.category,
        styles=self._parse_json_list(pin.styles),
        occasions=self._parse_json_list(pin.occasions),
        season=pin.season or "todo_el_ano",
        brands=self._parse_json_list(pin.brands),
        price_range=pin.price_range or "bajo_500",
        where_to_buy=pin.where_to_buy,
        purchase_link=pin.purchase_link,
        likes_count=pin.likes_count or 0,
        saves_count=pin.saves_count or 0,
        comments_count=pin.comments_count or 0,
        views_count=pin.views_count or 0,
        colors=self._parse_json_list(pin.colors),
        tags=self._parse_json_list(pin.tags),
        is_private=pin.is_private or False,
        created_at=pin.created_at,
        updated_at=pin.updated_at,
        is_liked_by_me=False,   # Ajusta según tu lógica
        is_saved_by_me=False,   # Ajusta según tu lógica
    )
    
    async def get_by_user(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
        include_private: bool = False,
    ) -> List[Pin]:
        query = self._db.query(PinModel).filter(PinModel.user_id == user_id)

        if not include_private:
            query = query.filter(PinModel.is_private == False)

        models = (
            query
            .order_by(PinModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    async def update(self, pin: Pin) -> Pin:
        model = self._db.query(PinModel).filter(
            PinModel.id == pin.id
        ).first()
        if model:
            model.title = pin.title
            model.description = pin.description
            model.category = pin.category
            model.styles = self._to_json(pin.styles)
            model.occasions = self._to_json(pin.occasions)
            model.season = pin.season
            model.brands = self._to_json(pin.brands)
            model.price_range = pin.price_range
            model.where_to_buy = pin.where_to_buy
            model.purchase_link = pin.purchase_link
            model.colors = self._to_json(pin.colors)
            model.tags = self._to_json(pin.tags)
            model.is_private = pin.is_private
            model.updated_at = datetime.now(timezone.utc)
            self._db.commit()
            self._db.refresh(model)
            return self._to_entity(model)
        return pin

    async def delete(self, pin_id: str) -> bool:
        deleted = self._db.query(PinModel).filter(
            PinModel.id == pin_id
        ).delete()
        self._db.commit()
        return deleted > 0

    # ── Contadores ────────────────────────────────────────────

    async def increment_views(self, pin_id: str) -> None:
        self._db.query(PinModel).filter(
            PinModel.id == pin_id
        ).update({PinModel.views_count: PinModel.views_count + 1})
        self._db.commit()

    async def increment_likes(self, pin_id: str) -> None:
        """Incrementar contador de likes en la tabla pins"""
        self._db.query(PinModel).filter(
        PinModel.id == pin_id
    ).update({
        PinModel.likes_count: PinModel.likes_count + 1
    })
        self._db.commit()

    async def decrement_likes(self, pin_id: str) -> None:
        """Decrementar contador de likes en la tabla pins"""
        self._db.query(PinModel).filter(
        PinModel.id == pin_id,
        PinModel.likes_count > 0  # ✅ Evitar números negativos
    ).update({
        PinModel.likes_count: PinModel.likes_count - 1
    })
        self._db.commit()

    async def increment_saves(self, pin_id: str) -> None:
        self._db.query(PinModel).filter(
            PinModel.id == pin_id
        ).update({PinModel.saves_count: PinModel.saves_count + 1})
        self._db.commit()

    async def decrement_saves(self, pin_id: str) -> None:
        self._db.query(PinModel).filter(
            PinModel.id == pin_id,
            PinModel.saves_count > 0,
        ).update({PinModel.saves_count: PinModel.saves_count - 1})
        self._db.commit()

    async def increment_comments(self, pin_id: str) -> None:
        self._db.query(PinModel).filter(
            PinModel.id == pin_id
        ).update({PinModel.comments_count: PinModel.comments_count + 1})
        self._db.commit()

    async def decrement_comments(self, pin_id: str) -> None:
        self._db.query(PinModel).filter(
            PinModel.id == pin_id,
            PinModel.comments_count > 0,
        ).update({PinModel.comments_count: PinModel.comments_count - 1})
        self._db.commit()

    # ── Búsqueda ──────────────────────────────────────────────

    async def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Pin]:
        search_term = f"%{query}%"
        models = (
            self._db.query(PinModel)
            .filter(
                PinModel.is_private == False,
                or_(
                    PinModel.title.ilike(search_term),
                    PinModel.description.ilike(search_term),
                    PinModel.tags.ilike(search_term),
                    PinModel.category.ilike(search_term),
                    PinModel.brands.ilike(search_term),
                    PinModel.colors.ilike(search_term),
                )
            )
            .order_by(PinModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    # ── Feed ──────────────────────────────────────────────────

    async def get_feed(
        self,
        user_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Pin]:
        """
        Feed personalizado: pins públicos recientes.
        TODO: Integrar con follows para mostrar solo pins de usuarios seguidos.
        Por ahora retorna pins públicos excluyendo los del propio usuario.
        """
        models = (
            self._db.query(PinModel)
            .filter(
                PinModel.is_private == False,
                PinModel.user_id != user_id,
            )
            .order_by(PinModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]

    # ── Trending ──────────────────────────────────────────────

    async def get_trending(
        self,
        limit: int = 20,
        hours: int = 24,
    ) -> List[Pin]:
        """Pins trending: más likes + views en las últimas X horas"""
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        models = (
            self._db.query(PinModel)
            .filter(
                PinModel.is_private == False,
                PinModel.created_at >= cutoff,
            )
            .order_by(
                (PinModel.likes_count + PinModel.views_count).desc()
            )
            .limit(limit)
            .all()
        )
        return [self._to_entity(m) for m in models]