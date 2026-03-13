"""
Inyección de dependencias para Boards
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.internal.boards.application.use_cases.get_all_boards import GetAllBoardsUseCase
from core.connection import get_db
from internal.boards.infrastructure.adapters.mysql_board_repository import MySQLBoardRepository
from internal.users.infrastructure.adapters.mysql_user_repository import MySQLUserRepository  # ✅ AGREGAR
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
    board_repo = MySQLBoardRepository(db)
    user_repo = MySQLUserRepository(db)  # ✅ CREAR INSTANCIA DE USER REPO

    return BoardController(
        create_uc=CreateBoardUseCase(board_repo),
        get_all_boards_uc=GetAllBoardsUseCase(board_repo, user_repo),  # ✅ PASAR 2 PARÁMETROS
        get_uc=GetBoardUseCase(board_repo),
        get_user_boards_uc=GetUserBoardsUseCase(board_repo),
        update_uc=UpdateBoardUseCase(board_repo),
        delete_uc=DeleteBoardUseCase(board_repo),
        add_pin_uc=AddPinToBoardUseCase(board_repo),
        remove_pin_uc=RemovePinFromBoardUseCase(board_repo),
        get_pins_uc=GetBoardPinsUseCase(board_repo),
        add_collab_uc=AddCollaboratorUseCase(board_repo),
        remove_collab_uc=RemoveCollaboratorUseCase(board_repo),
        update_collab_uc=UpdateCollaboratorUseCase(board_repo),
    )
