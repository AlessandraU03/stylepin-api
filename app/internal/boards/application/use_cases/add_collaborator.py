"""
Caso de uso: Agregar colaborador a un tablero
"""
import logging
from datetime import datetime, timezone
from app.core.notifications import notify_new_collaborator
from internal.boards.domain.entities.board import BoardCollaborator
from internal.boards.domain.repositories.board_repository import BoardRepository
from internal.users.domain.repositories.user_repository import UserRepository

logger = logging.getLogger(__name__)

class AddCollaboratorUseCase:
    def __init__(
        self,
        board_repository: BoardRepository,
        user_repository: UserRepository
    ):
        self._repo = board_repository
        self._user_repo = user_repository

    async def execute(
        self,
        board_id: str,
        owner_id: str,
        collaborator_user_id: str,
        can_edit: bool = False,
        can_add_pins: bool = True,
        can_remove_pins: bool = False,
    ) -> BoardCollaborator:
        """
        Agregar colaborador a un tablero y enviar notificación
        """
        board = await self._repo.get_by_id(board_id)
        if not board:
            raise ValueError("El tablero no existe")

        if board.user_id != owner_id:
            raise PermissionError("Solo el dueño puede agregar colaboradores")

        if not board.is_collaborative:
            raise ValueError("Este tablero no permite colaboradores")

        if owner_id == collaborator_user_id:
            raise ValueError("No puedes agregarte como colaborador de tu propio tablero")

        already = await self._repo.is_collaborator(board_id, collaborator_user_id)
        if already:
            raise ValueError("El usuario ya es colaborador de este tablero")

        now = datetime.now(timezone.utc)
        collaborator = BoardCollaborator(
            id="",
            board_id=board_id,
            user_id=collaborator_user_id,
            can_edit=can_edit,
            can_add_pins=can_add_pins,
            can_remove_pins=can_remove_pins,
            created_at=now,
        )

        created = await self._repo.add_collaborator(collaborator)

        # 🔔 Notificar al colaborador que fue añadido al tablero
        collaborator_user = await self._user_repo.get_by_id(collaborator_user_id)
        owner = await self._user_repo.get_by_id(owner_id)

        if collaborator_user and owner:
            # ✅ OBTENER TOKEN FCM usando el repositorio
            fcm_token = await self._user_repo.get_fcm_token(collaborator_user_id)
            
            if fcm_token:
                try:
                    await notify_new_collaborator(
                        token=fcm_token,
                        username=owner.username,
                        board_name=board.name
                    )
                    logger.info(f"✅ Notificación de colaborador enviada a {collaborator_user.username}")
                except Exception as e:
                    logger.error(f"❌ Error enviando notificación de colaborador: {e}")
            else:
                logger.warning(f"⚠️ No FCM token found for user {collaborator_user_id}")

        return created