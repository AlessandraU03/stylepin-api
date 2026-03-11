"""
Caso de uso: Login de usuario con seguridad
"""
from datetime import datetime, timezone, timedelta
from internal.users.domain.entities.user import User
from internal.users.domain.repositories.user_repository import UserRepository

MAX_LOGIN_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 30


class LoginUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute(self, identity: str) -> User:
        """
        Busca al usuario y verifica que no esté bloqueado.
        La verificación del password se hace en el controller.
        """
        user = await self._repo.get_by_identity(identity.strip())

        if not user:
            raise ValueError("Credenciales inválidas")

        if not user.is_active:
            raise ValueError("La cuenta está desactivada")

        # Verificar si está bloqueado
        if user.is_locked():
            raise ValueError(
                f"Cuenta bloqueada temporalmente. Intenta de nuevo después de {user.locked_until}"
            )

        return user

    async def on_login_success(self, user_id: str) -> None:
        """Llamar después de verificar password exitosamente"""
        await self._repo.reset_login_attempts(user_id)
        await self._repo.update_last_login(user_id)

    async def on_login_failure(self, user_id: str, current_attempts: int) -> None:
        """Llamar cuando el password es incorrecto"""
        new_attempts = current_attempts + 1
        await self._repo.increment_login_attempts(user_id)

        # Bloquear cuenta si se exceden intentos
        if new_attempts >= MAX_LOGIN_ATTEMPTS:
            lock_until = datetime.now(timezone.utc) + timedelta(
                minutes=LOCK_DURATION_MINUTES
            )
            await self._repo.lock_account(user_id, lock_until)