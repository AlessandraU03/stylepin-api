from app.internal.users.domain.repositories.user_repository import UserRepository

class SaveFcmTokenUseCase:

    def __init__(self, user_repository: UserRepository):
        self._repo = user_repository

    async def execute(self, user_id: str, token: str):
        user = await self._repo.get_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        user.fcm_token = token
        return await self._repo.update(user)