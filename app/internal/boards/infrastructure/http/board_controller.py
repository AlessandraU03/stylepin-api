"""
Controlador HTTP de Boards
"""
from internal.boards.application.use_cases.create_board import CreateBoardUseCase
from internal.boards.application.use_cases.get_board import GetBoardUseCase
from internal.boards.application.use_cases.get_user_boards import GetUserBoardsUseCase
from internal.boards.application.use_cases.update_board import UpdateBoardUseCase
from internal.boards.application.use_cases.delete_board import DeleteBoardUseCase
from internal.boards.application.use_cases.add_pin_to_board import AddPinToBoardUseCase
from internal.boards.application.use_cases.remove_pin_from_board import RemovePinFromBoardUseCase
from internal.boards.application.use_cases.get_board_pins import GetBoardPinsUseCase
from internal.boards.application.use_cases.add_collaborator import AddCollaboratorUseCase
from internal.boards.application.use_cases.remove_collaborator import RemoveCollaboratorUseCase
from internal.boards.application.use_cases.update_collaborator import UpdateCollaboratorUseCase

from internal.boards.domain.entities.board import Board, BoardResponse, BoardCollaboratorResponse
from internal.boards.application.schemas.board_schemas import (
    CreateBoardRequest,
    UpdateBoardRequest,
    AddPinToBoardRequest,
    AddCollaboratorRequest,
    UpdateCollaboratorRequest,
    BoardListResponse,
    BoardPinListResponse,
    CollaboratorListResponse,
    MessageResponse,
)


class BoardController:
    def __init__(
        self,
        create_uc: CreateBoardUseCase,
        get_uc: GetBoardUseCase,
        get_user_boards_uc: GetUserBoardsUseCase,
        update_uc: UpdateBoardUseCase,
        delete_uc: DeleteBoardUseCase,
        add_pin_uc: AddPinToBoardUseCase,
        remove_pin_uc: RemovePinFromBoardUseCase,
        get_pins_uc: GetBoardPinsUseCase,
        add_collab_uc: AddCollaboratorUseCase,
        remove_collab_uc: RemoveCollaboratorUseCase,
        update_collab_uc: UpdateCollaboratorUseCase,
    ):
        self._create_uc = create_uc
        self._get_uc = get_uc
        self._get_user_boards_uc = get_user_boards_uc
        self._update_uc = update_uc
        self._delete_uc = delete_uc
        self._add_pin_uc = add_pin_uc
        self._remove_pin_uc = remove_pin_uc
        self._get_pins_uc = get_pins_uc
        self._add_collab_uc = add_collab_uc
        self._remove_collab_uc = remove_collab_uc
        self._update_collab_uc = update_collab_uc

    @staticmethod
    def _to_response(
        board: Board,
        current_user_id: str = None,
        is_collaborator: bool = False,
    ) -> BoardResponse:
        """Convierte entidad Board a BoardResponse"""
        return BoardResponse(
            id=board.id,
            user_id=board.user_id,
            user_username="",       # TODO: obtener del usuario real
            user_full_name="",      # TODO: obtener del usuario real
            user_avatar_url=None,   # TODO: obtener del usuario real
            name=board.name,
            description=board.description,
            cover_image_url=board.cover_image_url,
            is_private=board.is_private,
            is_collaborative=board.is_collaborative,
            pins_count=board.pins_count,
            created_at=board.created_at,
            updated_at=board.updated_at,
            is_owner=(current_user_id == board.user_id) if current_user_id else False,
            is_collaborator=is_collaborator,
        )

    # ── Boards ────────────────────────────────────────────────

    async def create_board(self, body: CreateBoardRequest, user_id: str) -> BoardResponse:
        board = await self._create_uc.execute(
            user_id=user_id,
            name=body.name,
            description=body.description,
            is_private=body.is_private,
            is_collaborative=body.is_collaborative,
        )
        return self._to_response(board, current_user_id=user_id)

    async def get_board(self, board_id: str, user_id: str = None) -> BoardResponse:
        board = await self._get_uc.execute(board_id, requesting_user_id=user_id)
        return self._to_response(board, current_user_id=user_id)

    async def get_user_boards(
        self, user_id: str, current_user_id: str = None, limit: int = 20, offset: int = 0
    ) -> BoardListResponse:
        result = await self._get_user_boards_uc.execute(
            user_id=user_id,
            requesting_user_id=current_user_id,
            limit=limit,
            offset=offset,
        )
        return BoardListResponse(
            boards=[
                self._to_response(b, current_user_id=current_user_id)
                for b in result["boards"]
            ],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    async def update_board(
        self, board_id: str, body: UpdateBoardRequest, user_id: str
    ) -> BoardResponse:
        board = await self._update_uc.execute(
            board_id=board_id,
            user_id=user_id,
            name=body.name,
            description=body.description,
            is_private=body.is_private,
            is_collaborative=body.is_collaborative,
            cover_image_url=body.cover_image_url,
        )
        return self._to_response(board, current_user_id=user_id)

    async def delete_board(self, board_id: str, user_id: str) -> MessageResponse:
        await self._delete_uc.execute(board_id=board_id, user_id=user_id)
        return MessageResponse(message="Tablero eliminado correctamente")

    # ── Pins ──────────────────────────────────────────────────

    async def add_pin(self, board_id: str, body: AddPinToBoardRequest, user_id: str):
        return await self._add_pin_uc.execute(
            board_id=board_id,
            pin_id=body.pin_id,
            user_id=user_id,
            notes=body.notes,
        )

    async def remove_pin(self, board_id: str, pin_id: str, user_id: str) -> MessageResponse:
        await self._remove_pin_uc.execute(board_id=board_id, pin_id=pin_id, user_id=user_id)
        return MessageResponse(message="Pin removido del tablero")

    async def get_board_pins(
        self, board_id: str, user_id: str = None, limit: int = 20, offset: int = 0
    ) -> BoardPinListResponse:
        result = await self._get_pins_uc.execute(
            board_id=board_id,
            requesting_user_id=user_id,
            limit=limit,
            offset=offset,
        )
        return BoardPinListResponse(
            pins=result["pins"],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    # ── Collaborators ─────────────────────────────────────────

    async def add_collaborator(
        self, board_id: str, body: AddCollaboratorRequest, owner_id: str
    ) -> BoardCollaboratorResponse:
        collab = await self._add_collab_uc.execute(
            board_id=board_id,
            owner_id=owner_id,
            collaborator_user_id=body.user_id,
            can_edit=body.can_edit,
            can_add_pins=body.can_add_pins,
            can_remove_pins=body.can_remove_pins,
        )
        return BoardCollaboratorResponse(
            id=collab.id,
            board_id=collab.board_id,
            user_id=collab.user_id,
            user_username="",       # TODO: obtener del usuario real
            user_full_name="",      # TODO: obtener del usuario real
            user_avatar_url=None,   # TODO: obtener del usuario real
            can_edit=collab.can_edit,
            can_add_pins=collab.can_add_pins,
            can_remove_pins=collab.can_remove_pins,
            created_at=collab.created_at,
        )

    async def remove_collaborator(
        self, board_id: str, collaborator_user_id: str, owner_id: str
    ) -> MessageResponse:
        await self._remove_collab_uc.execute(
            board_id=board_id,
            owner_id=owner_id,
            collaborator_user_id=collaborator_user_id,
        )
        return MessageResponse(message="Colaborador removido")

    async def update_collaborator(
        self, board_id: str, collaborator_user_id: str, body: UpdateCollaboratorRequest, owner_id: str
    ) -> BoardCollaboratorResponse:
        collab = await self._update_collab_uc.execute(
            board_id=board_id,
            owner_id=owner_id,
            collaborator_user_id=collaborator_user_id,
            can_edit=body.can_edit,
            can_add_pins=body.can_add_pins,
            can_remove_pins=body.can_remove_pins,
        )
        return BoardCollaboratorResponse(
            id=collab.id,
            board_id=collab.board_id,
            user_id=collab.user_id,
            user_username="",       # TODO: obtener del usuario real
            user_full_name="",      # TODO: obtener del usuario real
            user_avatar_url=None,   # TODO: obtener del usuario real
            can_edit=collab.can_edit,
            can_add_pins=collab.can_add_pins,
            can_remove_pins=collab.can_remove_pins,
            created_at=collab.created_at,
        )

    async def get_collaborators(self, board_id: str) -> CollaboratorListResponse:
        # Verificar que el board existe
        await self._get_uc.execute(board_id)

        # Obtener colaboradores del repo directamente
        collabs = await self._add_collab_uc._repo.get_collaborators(board_id)
        responses = [
            BoardCollaboratorResponse(
                id=c.id,
                board_id=c.board_id,
                user_id=c.user_id,
                user_username="",       # TODO: obtener del usuario real
                user_full_name="",      # TODO: obtener del usuario real
                user_avatar_url=None,   # TODO: obtener del usuario real
                can_edit=c.can_edit,
                can_add_pins=c.can_add_pins,
                can_remove_pins=c.can_remove_pins,
                created_at=c.created_at,
            )
            for c in collabs
        ]
        return CollaboratorListResponse(collaborators=responses)