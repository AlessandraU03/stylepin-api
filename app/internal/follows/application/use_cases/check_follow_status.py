"""
Caso de uso: Verificar estado de follow entre dos usuarios
"""
from internal.follows.domain.repositories.follow_repository import FollowRepository


class CheckFollowStatusUseCase:
    def __init__(self, follow_repository: FollowRepository):
        self._repo = follow_repository

    async def execute(self, current_user_id: str, target_user_id: str) -> dict:
        is_following = await self._repo.exists(current_user_id, target_user_id)
        is_followed_by = await self._repo.exists(target_user_id, current_user_id)
        are_mutual = is_following and is_followed_by

        return {
            "is_following": is_following,
            "is_followed_by": is_followed_by,
            "are_mutual": are_mutual,
        }