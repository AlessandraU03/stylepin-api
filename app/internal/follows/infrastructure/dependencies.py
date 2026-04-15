"""
Inyección de dependencias para Follows - CORREGIDO
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from core.connection import get_db
from internal.follows.infrastructure.adapters.mysql_follow_repository import MySQLFollowRepository
from internal.follows.infrastructure.http.follow_controller import FollowController
from internal.follows.application.use_cases.follow_user import FollowUserUseCase
from internal.follows.application.use_cases.unfollow_user import UnfollowUserUseCase
from internal.follows.application.use_cases.get_followers import GetFollowersUseCase
from internal.follows.application.use_cases.get_following import GetFollowingUseCase
from internal.follows.application.use_cases.check_follow_status import CheckFollowStatusUseCase
from internal.follows.application.use_cases.get_follow_counts import GetFollowCountsUseCase
from internal.users.infrastructure.adapters.mysql_user_repository import MySQLUserRepository
from internal.notifications.infrastructure.http.mysql_notificarion_repository import MySQLNotificationRepository


def get_follow_controller(db: Session = Depends(get_db)) -> FollowController:
    repo              = MySQLFollowRepository(db)
    user_repo         = MySQLUserRepository(db)
    notification_repo = MySQLNotificationRepository(db)  # ← NUEVO

    return FollowController(
        follow_uc=FollowUserUseCase(
            follow_repository=repo,
            user_repository=user_repo,
            notification_repository=notification_repo,   # ← NUEVO
        ),
        unfollow_uc=UnfollowUserUseCase(repo),
        get_followers_uc=GetFollowersUseCase(repo),
        get_following_uc=GetFollowingUseCase(repo),
        check_status_uc=CheckFollowStatusUseCase(repo),
        get_counts_uc=GetFollowCountsUseCase(repo),
        db_session=db,
    )