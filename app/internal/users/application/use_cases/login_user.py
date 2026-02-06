from datetime import datetime, timedelta
from app.internal.users.domain.repositories.user_repository import UserRepository
from app.internal.users.application.schemas.auth_schema import LoginRequest
from app.internal.users.domain.entities.user import UserProfile
from app.core.security import verify_password, create_access_token
from app.core.exceptions import (
    InvalidCredentialsException,
    AccountLockedException,
    AccountDeactivatedException,
    UserNotFoundException
)

class LoginUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, request: LoginRequest) -> dict:
        # 1. Buscar usuario por email
        user = await self.user_repository.get_by_email(request.email.lower())
        
        if not user:
            raise InvalidCredentialsException()
        
        # 2. Verificar que esté activo
        if not user.is_active:
            raise AccountDeactivatedException()
        
        # 3. Verificar si está bloqueado
        if user.is_locked():
            raise AccountLockedException()
        
        # 4. Verificar contraseña
        if not verify_password(request.password, user.password_hash):
            # Incrementar intentos fallidos
            user.login_attempts += 1
            
            # Bloquear si llega a 5 intentos
            locked_until = None
            if user.login_attempts >= 5:
                locked_until = datetime.utcnow() + timedelta(minutes=15)
            
            await self.user_repository.update_login_attempts(
                user.id,
                user.login_attempts,
                locked_until
            )
            
            raise InvalidCredentialsException()
        
        # 5. Login exitoso: resetear intentos
        await self.user_repository.update_login_attempts(user.id, 0, None)
        
        # 6. Actualizar última fecha de login
        await self.user_repository.update_last_login(user.id)
        
        # 7. Generar token JWT
        token = create_access_token(
            data={"sub": user.id, "role": user.role}
        )
        
        # 8. Retornar respuesta (SOLO datos públicos)
        return {
            "user": UserProfile(
                id=user.id,
                username=user.username,
                full_name=user.full_name,
                bio=user.bio,
                avatar_url=user.avatar_url,
                preferred_styles=user.preferred_styles,
                is_verified=user.is_verified,
                created_at=user.created_at
            ).model_dump(),
            "token": token,
            "token_type": "bearer"
        }