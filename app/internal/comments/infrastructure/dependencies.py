"""
Inyección de dependencias para Comments
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from core.connection import get_db
from internal.comments.infrastructure.adapters.mysql_comment_repository import MySQLCommentRepository
from internal.comments.infrastructure.http.comment_controller import CommentController
from internal.comments.application.use_cases.create_comment import CreateCommentUseCase
from internal.comments.application.use_cases.get_comments_by_pin import GetCommentsByPinUseCase
from internal.comments.application.use_cases.get_replies import GetRepliesUseCase
from internal.comments.application.use_cases.update_comment import UpdateCommentUseCase
from internal.comments.application.use_cases.delete_comment import DeleteCommentUseCase
from internal.comments.application.use_cases.like_comment import LikeCommentUseCase


def get_comment_controller(db: Session = Depends(get_db)) -> CommentController:
    repo = MySQLCommentRepository(db)

    return CommentController(
        create_uc=CreateCommentUseCase(repo),
        get_by_pin_uc=GetCommentsByPinUseCase(repo),
        get_replies_uc=GetRepliesUseCase(repo),
        update_uc=UpdateCommentUseCase(repo),
        delete_uc=DeleteCommentUseCase(repo),
        like_uc=LikeCommentUseCase(repo),
        db_session=db,
    )