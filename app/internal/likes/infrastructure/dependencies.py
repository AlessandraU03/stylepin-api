"""
Inyección de dependencias para Likes
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from core.connection import get_db
from internal.likes.infrastructure.adapters.mysql_like_repository import MySQLLikeRepository
from internal.pines.infrastructure.adapters.mysql_pin_repository import MySQLPinRepository
from internal.users.infrastructure.adapters.mysql_user_repository import MySQLUserRepository

from internal.likes.application.use_cases.toggle_like import ToggleLikeUseCase
from internal.likes.application.use_cases.like_pin import LikePinUseCase
from internal.likes.application.use_cases.unlike_pin import UnlikePinUseCase
from internal.likes.application.use_cases.get_pin_likes import GetPinLikesUseCase
from internal.likes.application.use_cases.get_user_likes import GetUserLikesUseCase
from internal.likes.application.use_cases.check_like_status import CheckLikeStatusUseCase

from internal.likes.infrastructure.http.like_controller import LikeController


def get_like_controller(db: Session = Depends(get_db)) -> LikeController:
    like_repo = MySQLLikeRepository(db)
    pin_repo  = MySQLPinRepository(db)
    user_repo = MySQLUserRepository(db)

    return LikeController(
        like_uc=LikePinUseCase(like_repo, pin_repo),        # ← faltaba pin_repo
        unlike_uc=UnlikePinUseCase(like_repo, pin_repo),    # ← faltaba pin_repo
        toggle_like_uc=ToggleLikeUseCase(like_repo, pin_repo, user_repo),
        get_pin_likes_uc=GetPinLikesUseCase(like_repo),
        get_user_likes_uc=GetUserLikesUseCase(like_repo),
        check_status_uc=CheckLikeStatusUseCase(like_repo),
        db_session=db,
    )