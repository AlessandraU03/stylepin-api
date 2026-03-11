"""
Controlador HTTP de Pins
"""
from internal.pines.application.use_cases.create_pin import CreatePinUseCase
from internal.pines.application.use_cases.get_pin import GetPinUseCase
from internal.pines.application.use_cases.get_pins import GetPinsUseCase
from internal.pines.application.use_cases.get_user_pins import GetUserPinsUseCase
from internal.pines.application.use_cases.update_pin import UpdatePinUseCase
from internal.pines.application.use_cases.delete_pin import DeletePinUseCase
from internal.pines.application.use_cases.search_pins import SearchPinsUseCase
from internal.pines.application.use_cases.get_feed import GetFeedUseCase
from internal.pines.application.use_cases.get_trending import GetTrendingUseCase

from internal.pines.domain.entities.pin import Pin, PinResponse, PinSummary
from internal.pines.application.schemas.pin_schemas import (
    CreatePinRequest,
    UpdatePinRequest,
    PinListResponse,
    PinSummaryListResponse,
    PinFeedResponse,
    PinTrendingResponse,
    MessageResponse,
)


class PinController:
    def __init__(
        self,
        create_uc: CreatePinUseCase,
        get_uc: GetPinUseCase,
        get_pins_uc: GetPinsUseCase,
        get_user_pins_uc: GetUserPinsUseCase,
        update_uc: UpdatePinUseCase,
        delete_uc: DeletePinUseCase,
        search_uc: SearchPinsUseCase,
        get_feed_uc: GetFeedUseCase,
        get_trending_uc: GetTrendingUseCase,
    ):
        self._create_uc = create_uc
        self._get_uc = get_uc
        self._get_pins_uc = get_pins_uc
        self._get_user_pins_uc = get_user_pins_uc
        self._update_uc = update_uc
        self._delete_uc = delete_uc
        self._search_uc = search_uc
        self._get_feed_uc = get_feed_uc
        self._get_trending_uc = get_trending_uc

    # ── Mapeo ─────────────────────────────────────────────────

    @staticmethod
    def _to_response(pin: Pin) -> PinResponse:
        """Convierte entidad Pin a PinResponse"""
        return PinResponse(
            id=pin.id,
            user_id=pin.user_id,
            user_username="",               # TODO: obtener del usuario real
            user_full_name="",              # TODO: obtener del usuario real
            user_avatar_url=None,           # TODO: obtener del usuario real
            user_is_verified=False,         # TODO: obtener del usuario real
            image_url=pin.image_url,
            title=pin.title,
            description=pin.description,
            category=pin.category,
            styles=pin.styles,
            occasions=pin.occasions,
            season=pin.season,
            brands=pin.brands,
            price_range=pin.price_range,
            where_to_buy=pin.where_to_buy,
            purchase_link=pin.purchase_link,
            likes_count=pin.likes_count,
            saves_count=pin.saves_count,
            comments_count=pin.comments_count,
            views_count=pin.views_count,
            colors=pin.colors,
            tags=pin.tags,
            is_private=pin.is_private,
            created_at=pin.created_at,
            updated_at=pin.updated_at,
            is_liked_by_me=False,           # TODO: verificar con like repo
            is_saved_by_me=False,           # TODO: verificar con board repo
        )

    @staticmethod
    def _to_summary(pin: Pin) -> PinSummary:
        """Convierte entidad Pin a PinSummary"""
        return PinSummary(
            id=pin.id,
            user_id=pin.user_id,
            user_username="",               # TODO: obtener del usuario real
            user_avatar_url=None,           # TODO: obtener del usuario real
            image_url=pin.image_url,
            title=pin.title,
            category=pin.category,
            likes_count=pin.likes_count,
            saves_count=pin.saves_count,
            created_at=pin.created_at,
        )

    # ── CRUD ──────────────────────────────────────────────────

    async def create_pin(self, body: CreatePinRequest, user_id: str) -> PinResponse:
        pin = await self._create_uc.execute(
            user_id=user_id,
            title=body.title,
            description=body.description,
            image_url=body.image_url,
            category=body.category,
            styles=body.styles,
            occasions=body.occasions,
            season=body.season,
            brands=body.brands,
            price_range=body.price_range,
            where_to_buy=body.where_to_buy,
            purchase_link=body.purchase_link,
            colors=body.colors,
            tags=body.tags,
            is_private=body.is_private,
        )
        return self._to_response(pin)

    async def get_pin(self, pin_id: str, user_id: str = None) -> PinResponse:
        pin = await self._get_uc.execute(pin_id, requesting_user_id=user_id)
        return self._to_response(pin)

    async def get_pins(
        self,
        limit: int = 20,
        offset: int = 0,
        category: str = None,
        season: str = None,
        price_range: str = None,
    ) -> PinListResponse:
        result = await self._get_pins_uc.execute(
            limit=limit,
            offset=offset,
            category=category,
            season=season,
            price_range=price_range,
        )
        return PinListResponse(
            pins=[self._to_response(p) for p in result["pins"]],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    async def get_user_pins(
        self,
        user_id: str,
        current_user_id: str = None,
        limit: int = 20,
        offset: int = 0,
    ) -> PinListResponse:
        result = await self._get_user_pins_uc.execute(
            user_id=user_id,
            requesting_user_id=current_user_id,
            limit=limit,
            offset=offset,
        )
        return PinListResponse(
            pins=[self._to_response(p) for p in result["pins"]],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    async def update_pin(
        self, pin_id: str, body: UpdatePinRequest, user_id: str
    ) -> PinResponse:
        pin = await self._update_uc.execute(
            pin_id=pin_id,
            user_id=user_id,
            title=body.title,
            description=body.description,
            category=body.category,
            styles=body.styles,
            occasions=body.occasions,
            season=body.season,
            brands=body.brands,
            price_range=body.price_range,
            where_to_buy=body.where_to_buy,
            purchase_link=body.purchase_link,
            colors=body.colors,
            tags=body.tags,
            is_private=body.is_private,
        )
        return self._to_response(pin)

    async def delete_pin(self, pin_id: str, user_id: str) -> MessageResponse:
        await self._delete_uc.execute(pin_id=pin_id, user_id=user_id)
        return MessageResponse(message="Pin eliminado correctamente")

    # ── Búsqueda ──────────────────────────────────────────────

    async def search_pins(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> PinSummaryListResponse:
        result = await self._search_uc.execute(
            query=query, limit=limit, offset=offset
        )
        return PinSummaryListResponse(
            pins=[self._to_summary(p) for p in result["pins"]],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    # ── Feed ──────────────────────────────────────────────────

    async def get_feed(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> PinFeedResponse:
        result = await self._get_feed_uc.execute(
            user_id=user_id, limit=limit, offset=offset
        )
        return PinFeedResponse(
            pins=[self._to_response(p) for p in result["pins"]],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    # ── Trending ──────────────────────────────────────────────

    async def get_trending(
        self, limit: int = 20, hours: int = 24
    ) -> PinTrendingResponse:
        result = await self._get_trending_uc.execute(
            limit=limit, hours=hours
        )
        return PinTrendingResponse(
            pins=[self._to_summary(p) for p in result["pins"]],
            hours=result["hours"],
        )