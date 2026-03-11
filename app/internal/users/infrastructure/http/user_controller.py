"""
Controlador HTTP de Users
"""
from passlib.context import CryptContext

from internal.users.application.use_cases.get_user import GetUserUseCase
from internal.users.application.use_cases.update_user import UpdateUserUseCase
from internal.users.application.use_cases.delete_user import DeleteUserUseCase
from internal.users.application.use_cases.search_users import SearchUsersUseCase

from internal.users.domain.entities.user import User, UserProfile, UserMe
from internal.users.application.schemas.user_schema import (
    UpdateProfileRequest,
    ChangePasswordRequest,
    UserProfileResponse,
    UserListResponse,
    UserSearchResult,
    UserStatsResponse,
    MessageResponse,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserController:
    def __init__(
        self,
        get_user_uc: GetUserUseCase,
        update_user_uc: UpdateUserUseCase,
        delete_user_uc: DeleteUserUseCase,
        search_users_uc: SearchUsersUseCase,
    ):
        self._get_user_uc = get_user_uc
        self._update_user_uc = update_user_uc
        self._delete_user_uc = delete_user_uc
        self._search_users_uc = search_users_uc

    # ── Mapeo ─────────────────────────────────────────────────

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

    @staticmethod
    def _to_profile(user: User, stats: dict) -> UserProfile:
        return UserProfile(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            preferred_styles=user.preferred_styles,
            is_verified=user.is_verified,
            created_at=user.created_at,
            total_pins=stats.get("total_pins", 0),
            total_followers=stats.get("total_followers", 0),
            total_following=stats.get("total_following", 0),
        )

    @staticmethod
    def _to_search_result(user: User) -> UserSearchResult:
        return UserSearchResult(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            avatar_url=user.avatar_url,
            is_verified=user.is_verified,
        )

    # ── Mi Perfil ─────────────────────────────────────────────

    async def get_me(self, user_id: str) -> UserMe:
        user = await self._get_user_uc.execute_by_id(user_id)
        return self._to_user_me(user)

    async def update_profile(
        self, user_id: str, body: UpdateProfileRequest
    ) -> UserMe:
        user = await self._update_user_uc.execute(
            user_id=user_id,
            requesting_user_id=user_id,
            full_name=body.full_name,
            bio=body.bio,
            avatar_url=body.avatar_url,
            gender=body.gender,
            preferred_styles=body.preferred_styles,
        )
        return self._to_user_me(user)

    async def change_password(
        self, user_id: str, body: ChangePasswordRequest
    ) -> MessageResponse:
        user = await self._get_user_uc.execute_by_id(user_id)

        # Verificar password actual
        if not pwd_context.verify(body.current_password, user.password_hash):
            raise ValueError("La contraseña actual es incorrecta")

        # Hashear nueva contraseña
        new_hash = pwd_context.hash(body.new_password)
        await self._update_user_uc.change_password(user_id, new_hash)

        return MessageResponse(message="Contraseña actualizada correctamente")

    async def delete_account(self, user_id: str) -> MessageResponse:
        await self._delete_user_uc.execute(
            user_id=user_id,
            requesting_user_id=user_id,
        )
        return MessageResponse(message="Cuenta eliminada correctamente")

    # ── Perfil Público ────────────────────────────────────────

    async def get_profile(self, username: str) -> UserProfileResponse:
        user = await self._get_user_uc.execute_by_username(username)
        stats = await self._get_user_uc.get_stats(user.id)

        return UserProfileResponse(
            user=self._to_profile(user, stats),
            is_following=False,     # TODO: verificar con follow repo
            is_followed_by=False,   # TODO: verificar con follow repo
        )

    async def get_user_by_id(self, user_id: str) -> UserProfileResponse:
        user = await self._get_user_uc.execute_by_id(user_id)
        stats = await self._get_user_uc.get_stats(user_id)

        return UserProfileResponse(
            user=self._to_profile(user, stats),
            is_following=False,
            is_followed_by=False,
        )

    async def get_stats(self, user_id: str) -> UserStatsResponse:
        stats = await self._get_user_uc.get_stats(user_id)
        return UserStatsResponse(**stats)

    # ── Búsqueda ──────────────────────────────────────────────

    async def search_users(
        self, query: str, limit: int = 20, offset: int = 0
    ) -> UserListResponse:
        result = await self._search_users_uc.execute(
            query=query, limit=limit, offset=offset
        )
        return UserListResponse(
            users=[self._to_search_result(u) for u in result["users"]],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )