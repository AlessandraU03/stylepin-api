from datetime import datetime, timedelta
import uuid
from app.internal.users.domain.entities.user import User, UserProfile
from app.internal.users.domain.repositories.user_repository import UserRepository
from app.internal.users.application.schemas.auth_schema import RegisterRequest
from app.core.security import get_password_hash, create_access_token
from app.core.exceptions import UserAlreadyExistsException

class CreateUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, request: RegisterRequest) -> dict:
        # 1. Verificar que email no exista
        if await self.user_repository.exists_by_email(request.email):
            raise UserAlreadyExistsException("Email already in use")
        
        # 2. Verificar que username no exista
        if await self.user_repository.exists_by_username(request.username):
            raise UserAlreadyExistsException("Username already in use")
        
        # 3. Crear entidad User
        user = User(
            id=str(uuid.uuid4()),
            username=request.username,
            email=request.email.lower(),
            password_hash=get_password_hash(request.password),
            full_name=request.full_name,
            gender=request.gender or "prefer_not_to_say",
            preferred_styles=request.preferred_styles or [],
            is_verified=False,
            is_active=True,
            role="user",
            login_attempts=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 4. Guardar en DB
        created_user = await self.user_repository.create(user)
        
        # 5. Generar token JWT
        token = create_access_token(
            data={"sub": created_user.id, "role": created_user.role}
        )
        
        # 6. Retornar respuesta (SOLO datos públicos)
        return {
            "user": UserProfile(
                id=created_user.id,
                username=created_user.username,
                full_name=created_user.full_name,
                bio=created_user.bio,
                avatar_url=created_user.avatar_url,
                preferred_styles=created_user.preferred_styles,
                is_verified=created_user.is_verified,
                created_at=created_user.created_at
            ).model_dump(),
            "token": token,
            "token_type": "bearer"
        }