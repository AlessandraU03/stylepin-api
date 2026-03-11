"""
Controlador HTTP de Autenticación
"""
from core.security import hash_password, verify_password

from internal.users.application.use_cases.create_user import CreateUserUseCase
from internal.users.application.use_cases.login_user import LoginUserUseCase

from internal.users.domain.entities.user import User, UserMe
from internal.users.application.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
)
from internal.users.infrastructure.middlewares.auth_middleware import create_access_token


class AuthController:
    def __init__(
        self,
        create_user_uc: CreateUserUseCase,
        login_user_uc: LoginUserUseCase,
    ):
        self._create_user_uc = create_user_uc
        self._login_user_uc = login_user_uc

    # ── Helpers ───────────────────────────────────────────────

    @staticmethod
    def _to_user_me(user: User) -> UserMe:
        return UserMe(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            gender=user.gender,
            preferred_styles=user.preferred_styles,
            is_verified=user.is_verified,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login,
        )

    # ── Register ──────────────────────────────────────────────

    async def register(self, body: RegisterRequest) -> AuthResponse:
        password_hash = hash_password(body.password)

        user = await self._create_user_uc.execute(
            username=body.username,
            email=body.email,
            password_hash=password_hash,
            full_name=body.full_name,
            gender=body.gender,
            preferred_styles=body.preferred_styles or [],
        )

        token = create_access_token(data={"sub": user.id})

        return AuthResponse(
            user=self._to_user_me(user),
            token=token,
            token_type="bearer",
        )

    # ── Login ─────────────────────────────────────────────────

    async def login(self, body: LoginRequest) -> AuthResponse:
        user = await self._login_user_uc.execute(identity=body.identity)

        if not verify_password(body.password, user.password_hash):
            await self._login_user_uc.on_login_failure(
                user_id=user.id,
                current_attempts=user.login_attempts,
            )
            raise ValueError("Credenciales inválidas")

        await self._login_user_uc.on_login_success(user_id=user.id)

        token = create_access_token(data={"sub": user.id})

        return AuthResponse(
            user=self._to_user_me(user),
            token=token,
            token_type="bearer",
        )