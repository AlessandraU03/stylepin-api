"""
Caso de uso: Crear un pin
"""
from datetime import datetime, timezone
from typing import Optional, List
from internal.pines.domain.entities.pin import Pin
from internal.pines.domain.repositories.pin_repository import PinRepository


class CreatePinUseCase:
    def __init__(self, pin_repository: PinRepository):
        self._repo = pin_repository

    async def execute(
        self,
        user_id: str,
        title: str,
        image_url: str,
        category: str,
        description: Optional[str] = None,
        styles: List[str] = None,
        occasions: List[str] = None,
        season: str = "todo_el_ano",
        brands: List[str] = None,
        price_range: str = "bajo_500",
        where_to_buy: Optional[str] = None,
        purchase_link: Optional[str] = None,
        colors: List[str] = None,
        tags: List[str] = None,
        is_private: bool = False,
    ) -> Pin:
        now = datetime.now(timezone.utc)

        pin = Pin(
            id="",
            user_id=user_id,
            image_url=image_url,
            title=title,
            description=description,
            category=category,
            styles=styles or [],
            occasions=occasions or [],
            season=season,
            brands=brands or [],
            price_range=price_range,
            where_to_buy=where_to_buy,
            purchase_link=purchase_link,
            likes_count=0,
            saves_count=0,
            comments_count=0,
            views_count=0,
            colors=colors or [],
            tags=tags or [],
            is_private=is_private,
            created_at=now,
            updated_at=now,
        )

        return await self._repo.create(pin)