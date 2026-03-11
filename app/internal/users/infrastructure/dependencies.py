"""
Inyección de dependencias para Users
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from core.connection import get_db
from internal.users.infrastructure.adapters.mysql_user_repository import MySQLUserRepository

# Auth
from internal.users.infrastructure.http.auth_controller import AuthController
from internal.users.application.use_cases.create_user import CreateUserUseCase
from internal.users.application.use_cases.login_user import LoginUserUseCase

# Users
from internal.users.infrastructure.http.user_controller import UserController
from internal.users.application.use_cases.get_user import GetUserUseCase
from internal.users.application.use_cases.update_user import UpdateUserUseCase
from internal.users.application.use_cases.delete_user import DeleteUserUseCase
from internal.users.application.use_cases.search_users import SearchUsersUseCase


def get_auth_controller(db: Session = Depends(get_db)) -> AuthController:
    repo = MySQLUserRepository(db)

    return AuthController(
        create_user_uc=CreateUserUseCase(repo),
        login_user_uc=LoginUserUseCase(repo),
    )


def get_user_controller(db: Session = Depends(get_db)) -> UserController:
    repo = MySQLUserRepository(db)

    return UserController(
        get_user_uc=GetUserUseCase(repo),
        update_user_uc=UpdateUserUseCase(repo),
        delete_user_uc=DeleteUserUseCase(repo),
        search_users_uc=SearchUsersUseCase(repo),
    )