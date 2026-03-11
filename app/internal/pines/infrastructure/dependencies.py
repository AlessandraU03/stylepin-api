"""
Inyección de dependencias para Pins
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from core.connection import get_db
from internal.pines.infrastructure.adapters.mysql_pin_repository import MySQLPinRepository
from internal.pines.infrastructure.http.pin_controller import PinController
from internal.pines.application.use_cases.create_pin import CreatePinUseCase
from internal.pines.application.use_cases.get_pin import GetPinUseCase
from internal.pines.application.use_cases.get_pins import GetPinsUseCase
from internal.pines.application.use_cases.get_user_pins import GetUserPinsUseCase
from internal.pines.application.use_cases.update_pin import UpdatePinUseCase
from internal.pines.application.use_cases.delete_pin import DeletePinUseCase
from internal.pines.application.use_cases.search_pins import SearchPinsUseCase
from internal.pines.application.use_cases.get_feed import GetFeedUseCase
from internal.pines.application.use_cases.get_trending import GetTrendingUseCase


def get_pin_controller(db: Session = Depends(get_db)) -> PinController:
    repo = MySQLPinRepository(db)

    return PinController(
        create_uc=CreatePinUseCase(repo),
        get_uc=GetPinUseCase(repo),
        get_pins_uc=GetPinsUseCase(repo),
        get_user_pins_uc=GetUserPinsUseCase(repo),
        update_uc=UpdatePinUseCase(repo),
        delete_uc=DeletePinUseCase(repo),
        search_uc=SearchPinsUseCase(repo),
        get_feed_uc=GetFeedUseCase(repo),
        get_trending_uc=GetTrendingUseCase(repo),
    )