"""
Caso de uso: Registrar un nuevo usuario
"""
from datetime import datetime, timezone
from typing import Optional, List
from internal.users.domain.entities.user import User
from internal.users.domain.repositories.user_repository import UserRepository


class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute(
        self,
        username: str,
        email: str,
        password_hash: str,
        full_name: str,
        gender: Optional[str] = None,
        preferred_styles: List[str] = None,
    ) -> User:
        # Verificar unicidad de email
        if await self._repo.exists_by_email(email.lower().strip()):
            raise ValueError("El email ya está registrado")

        # Verificar unicidad de username
        if await self._repo.exists_by_username(username.lower().strip()):
            raise ValueError("El username ya está en uso")

        now = datetime.now(timezone.utc)

        user = User(
            id="",
            username=username.lower().strip(),
            email=email.lower().strip(),
            password_hash=password_hash,
            full_name=full_name,
            bio=None,
            avatar_url=None,
            gender=gender or "prefer_not_to_say",
            preferred_styles=preferred_styles or [],
            is_verified=False,
            is_active=True,
            role="user",
            email_verified_at=None,
            login_attempts=0,
            locked_until=None,
            password_reset_token=None,
            password_reset_token_expiry=None,
            created_at=now,
            updated_at=now,
            last_login=None,
        )

        return await self._repo.create(user)