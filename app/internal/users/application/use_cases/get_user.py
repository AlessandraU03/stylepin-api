from app.internal.users.domain.repositories.user_repository import UserRepository
from app.internal.users.domain.entities.user import UserProfile, UserMe
from app.core.exceptions import UserNotFoundException

class GetUserByIdUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, user_id: str) -> UserProfile:
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundException()
        
        return UserProfile(
            id=user.id,
            username=user.username,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            preferred_styles=user.preferred_styles,
            is_verified=user.is_verified,
            created_at=user.created_at
        )

class GetCurrentUserUseCase:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    async def execute(self, user_id: str) -> UserMe:
        user = await self.user_repository.get_by_id(user_id)
        
        if not user:
            raise UserNotFoundException()
        
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
            last_login=user.last_login
        )