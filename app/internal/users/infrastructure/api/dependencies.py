from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.connection import get_db
from app.internal.users.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.internal.users.application.use_cases.create_user import CreateUserUseCase
from app.internal.users.application.use_cases.login_user import LoginUserUseCase
from app.internal.users.application.use_cases.get_user import GetUserByIdUseCase, GetCurrentUserUseCase
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException

security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")
# ==================== REPOSITORIES ====================

def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryImpl:
    """Dependency para obtener UserRepository"""
    return UserRepositoryImpl(db)

# ==================== USE CASES ====================

def get_create_user_use_case(
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> CreateUserUseCase:
    """Dependency para CreateUserUseCase"""
    return CreateUserUseCase(user_repo)

def get_login_user_use_case(
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> LoginUserUseCase:
    """Dependency para LoginUserUseCase"""
    return LoginUserUseCase(user_repo)

def get_user_by_id_use_case(
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> GetUserByIdUseCase:
    """Dependency para GetUserByIdUseCase"""
    return GetUserByIdUseCase(user_repo)

def get_current_user_use_case(
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> GetCurrentUserUseCase:
    """Dependency para GetCurrentUserUseCase"""
    return GetCurrentUserUseCase(user_repo)

# ==================== AUTHENTICATION ====================

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """Obtiene el ID del usuario desde un token Bearer JSON"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise UnauthorizedException("Invalid or expired token")
    
    return payload.get("sub")

async def get_current_user(
    user_id: str = Depends(get_current_user_id),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case)
):
    """
    Dependency para obtener el usuario autenticado completo
    """
    return await use_case.execute(user_id)

# ==================== ADMIN ONLY ====================

async def get_current_admin_user(
    current_user = Depends(get_current_user)
):
    """
    Dependency para verificar que el usuario sea admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user