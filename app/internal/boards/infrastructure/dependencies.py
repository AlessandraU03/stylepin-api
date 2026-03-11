"""
Inyección de dependencias para Boards
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from core.connection import get_db
from internal.boards.infrastructure.adapters.mysql_board_repository import MySQLBoardRepository
from internal.boards.infrastructure.http.board_controller import BoardController
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


def get_board_controller(db: Session = Depends(get_db)) -> BoardController:
    repo = MySQLBoardRepository(db)

    return BoardController(
        create_uc=CreateBoardUseCase(repo),
        get_uc=GetBoardUseCase(repo),
        get_user_boards_uc=GetUserBoardsUseCase(repo),
        update_uc=UpdateBoardUseCase(repo),
        delete_uc=DeleteBoardUseCase(repo),
        add_pin_uc=AddPinToBoardUseCase(repo),
        remove_pin_uc=RemovePinFromBoardUseCase(repo),
        get_pins_uc=GetBoardPinsUseCase(repo),
        add_collab_uc=AddCollaboratorUseCase(repo),
        remove_collab_uc=RemoveCollaboratorUseCase(repo),
        update_collab_uc=UpdateCollaboratorUseCase(repo),
    )