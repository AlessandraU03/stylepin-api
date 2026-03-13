"""
Inyección de dependencias para Likes
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.internal.pines.infrastructure.adapters.mysql_pin_repository import MySQLPinRepository
from core.connection import get_db
from internal.likes.infrastructure.adapters.mysql_like_repository import MySQLLikeRepository
from internal.likes.infrastructure.http.like_controller import LikeController
from internal.likes.application.use_cases.like_pin import LikePinUseCase
from internal.likes.application.use_cases.unlike_pin import UnlikePinUseCase
from internal.likes.application.use_cases.get_pin_likes import GetPinLikesUseCase
from internal.likes.application.use_cases.get_user_likes import GetUserLikesUseCase
from internal.likes.application.use_cases.check_like_status import CheckLikeStatusUseCase
from internal.likes.application.use_cases.toggle_like import ToggleLikeUseCase


def get_like_controller(db: Session = Depends(get_db)) -> LikeController:
    repo = MySQLLikeRepository(db)
    pin_repo = MySQLPinRepository(db)  # ✅ NECESITAS ESTE REPOSITORIO PARA ACTUALIZAR CONTADOR DE LIKES

    return LikeController(
        like_uc=LikePinUseCase(repo, pin_repo),  # ✅ PASAR PIN REPO
        unlike_uc=UnlikePinUseCase(repo, pin_repo),  # ✅ PASAR PIN REPO
        get_pin_likes_uc=GetPinLikesUseCase(repo),
        toggle_like_uc=ToggleLikeUseCase(repo, pin_repo),
        get_user_likes_uc=GetUserLikesUseCase(repo),
        check_status_uc=CheckLikeStatusUseCase(repo),
        db_session=db,
    )