"""
Implementación MySQL (SQLAlchemy) del repositorio de Boards (Adapter)
"""
from typing import Optional, List
from datetime import datetime, timezone
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import func

from internal.boards.domain.entities.board import Board, BoardPin, BoardCollaborator
from internal.boards.domain.repositories.board_repository import BoardRepository
from core.database.models import BoardModel, BoardPinModel, BoardCollaboratorModel


class MySQLBoardRepository(BoardRepository):

    def __init__(self, db: Session):
        self._db = db

    # ── Mapeo ─────────────────────────────────────────────────

    @staticmethod
    def _to_board_entity(model: BoardModel) -> Board:
        return Board(
            id=model.id,
            user_id=model.user_id,
            name=model.name,
            description=model.description,
            cover_image_url=model.cover_image_url,
            is_private=model.is_private,
            is_collaborative=model.is_collaborative,
            pins_count=model.pins_count or 0,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def _to_board_pin_entity(model: BoardPinModel) -> BoardPin:
        return BoardPin(
            id=model.id,
            board_id=model.board_id,
            pin_id=model.pin_id,
            user_id=model.user_id,
            notes=model.notes,
            created_at=model.created_at,
        )

    @staticmethod
    def _to_collaborator_entity(model: BoardCollaboratorModel) -> BoardCollaborator:
        return BoardCollaborator(
            id=model.id,
            board_id=model.board_id,
            user_id=model.user_id,
            can_edit=model.can_edit,
            can_add_pins=model.can_add_pins,
            can_remove_pins=model.can_remove_pins,
            created_at=model.created_at,
        )

    # ── BOARDS CRUD ───────────────────────────────────────────

    async def create(self, board: Board) -> Board:
        now = datetime.now(timezone.utc)
        model = BoardModel(
            id=str(uuid.uuid4()),
            user_id=board.user_id,
            name=board.name,
            description=board.description,
            cover_image_url=board.cover_image_url,
            is_private=board.is_private,
            is_collaborative=board.is_collaborative,
            pins_count=0,
            created_at=now,
            updated_at=now,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_board_entity(model)

    async def get_by_id(self, board_id: str) -> Optional[Board]:
        model = self._db.query(BoardModel).filter(
            BoardModel.id == board_id
        ).first()
        return self._to_board_entity(model) if model else None

    async def get_by_user(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[Board]:
        models = (
            self._db.query(BoardModel)
            .filter(BoardModel.user_id == user_id)
            .order_by(BoardModel.updated_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_board_entity(m) for m in models]

    async def update(self, board: Board) -> Board:
        model = self._db.query(BoardModel).filter(
            BoardModel.id == board.id
        ).first()
        if model:
            model.name = board.name
            model.description = board.description
            model.cover_image_url = board.cover_image_url
            model.is_private = board.is_private
            model.is_collaborative = board.is_collaborative
            model.updated_at = datetime.now(timezone.utc)
            self._db.commit()
            self._db.refresh(model)
            return self._to_board_entity(model)
        return board

    async def delete(self, board_id: str) -> bool:
        # Eliminar colaboradores
        self._db.query(BoardCollaboratorModel).filter(
            BoardCollaboratorModel.board_id == board_id
        ).delete()
        # Eliminar board_pins
        self._db.query(BoardPinModel).filter(
            BoardPinModel.board_id == board_id
        ).delete()
        # Eliminar board
        deleted = self._db.query(BoardModel).filter(
            BoardModel.id == board_id
        ).delete()
        self._db.commit()
        return deleted > 0

    async def increment_pins_count(self, board_id: str) -> None:
        self._db.query(BoardModel).filter(
            BoardModel.id == board_id
        ).update({BoardModel.pins_count: BoardModel.pins_count + 1})
        self._db.commit()

    async def decrement_pins_count(self, board_id: str) -> None:
        self._db.query(BoardModel).filter(
            BoardModel.id == board_id,
            BoardModel.pins_count > 0
        ).update({BoardModel.pins_count: BoardModel.pins_count - 1})
        self._db.commit()

    async def update_cover_image(self, board_id: str, image_url: str) -> None:
        self._db.query(BoardModel).filter(
            BoardModel.id == board_id
        ).update({BoardModel.cover_image_url: image_url})
        self._db.commit()

    # ── BOARD PINS ────────────────────────────────────────────

    async def add_pin(self, board_pin: BoardPin) -> BoardPin:
        model = BoardPinModel(
            id=str(uuid.uuid4()),
            board_id=board_pin.board_id,
            pin_id=board_pin.pin_id,
            user_id=board_pin.user_id,
            notes=board_pin.notes,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_board_pin_entity(model)

    async def remove_pin(self, board_id: str, pin_id: str) -> bool:
        deleted = self._db.query(BoardPinModel).filter(
            BoardPinModel.board_id == board_id,
            BoardPinModel.pin_id == pin_id,
        ).delete()
        self._db.commit()
        return deleted > 0

    async def get_board_pins(
        self, board_id: str, limit: int = 20, offset: int = 0
    ) -> List[BoardPin]:
        models = (
            self._db.query(BoardPinModel)
            .filter(BoardPinModel.board_id == board_id)
            .order_by(BoardPinModel.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return [self._to_board_pin_entity(m) for m in models]

    async def is_pin_in_board(self, board_id: str, pin_id: str) -> bool:
        count = (
            self._db.query(func.count(BoardPinModel.id))
            .filter(
                BoardPinModel.board_id == board_id,
                BoardPinModel.pin_id == pin_id,
            )
            .scalar()
        )
        return (count or 0) > 0

    async def get_boards_with_pin(self, pin_id: str, user_id: str) -> List[Board]:
        board_ids = (
            self._db.query(BoardPinModel.board_id)
            .filter(BoardPinModel.pin_id == pin_id)
            .all()
        )
        ids = [row[0] for row in board_ids]
        if not ids:
            return []

        models = (
            self._db.query(BoardModel)
            .filter(
                BoardModel.id.in_(ids),
                BoardModel.user_id == user_id,
            )
            .all()
        )
        return [self._to_board_entity(m) for m in models]

    # ── COLLABORATORS ─────────────────────────────────────────

    async def add_collaborator(self, collaborator: BoardCollaborator) -> BoardCollaborator:
        model = BoardCollaboratorModel(
            id=str(uuid.uuid4()),
            board_id=collaborator.board_id,
            user_id=collaborator.user_id,
            can_edit=collaborator.can_edit,
            can_add_pins=collaborator.can_add_pins,
            can_remove_pins=collaborator.can_remove_pins,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_collaborator_entity(model)

    async def remove_collaborator(self, board_id: str, user_id: str) -> bool:
        deleted = self._db.query(BoardCollaboratorModel).filter(
            BoardCollaboratorModel.board_id == board_id,
            BoardCollaboratorModel.user_id == user_id,
        ).delete()
        self._db.commit()
        return deleted > 0

    async def get_collaborators(self, board_id: str) -> List[BoardCollaborator]:
        models = (
            self._db.query(BoardCollaboratorModel)
            .filter(BoardCollaboratorModel.board_id == board_id)
            .all()
        )
        return [self._to_collaborator_entity(m) for m in models]

    async def is_collaborator(self, board_id: str, user_id: str) -> bool:
        count = (
            self._db.query(func.count(BoardCollaboratorModel.id))
            .filter(
                BoardCollaboratorModel.board_id == board_id,
                BoardCollaboratorModel.user_id == user_id,
            )
            .scalar()
        )
        return (count or 0) > 0

    async def update_collaborator_permissions(
        self,
        board_id: str,
        user_id: str,
        can_edit: bool,
        can_add_pins: bool,
        can_remove_pins: bool,
    ) -> BoardCollaborator:
        model = self._db.query(BoardCollaboratorModel).filter(
            BoardCollaboratorModel.board_id == board_id,
            BoardCollaboratorModel.user_id == user_id,
        ).first()

        if not model:
            raise ValueError("Colaborador no encontrado")

        model.can_edit = can_edit
        model.can_add_pins = can_add_pins
        model.can_remove_pins = can_remove_pins
        self._db.commit()
        self._db.refresh(model)
        return self._to_collaborator_entity(model)

    async def get_collaborative_boards(
        self, user_id: str, limit: int = 20, offset: int = 0
    ) -> List[Board]:
        board_ids = (
            self._db.query(BoardCollaboratorModel.board_id)
            .filter(BoardCollaboratorModel.user_id == user_id)
            .offset(offset)
            .limit(limit)
            .all()
        )
        ids = [row[0] for row in board_ids]
        if not ids:
            return []

        models = (
            self._db.query(BoardModel)
            .filter(BoardModel.id.in_(ids))
            .order_by(BoardModel.updated_at.desc())
            .all()
        )
        return [self._to_board_entity(m) for m in models]