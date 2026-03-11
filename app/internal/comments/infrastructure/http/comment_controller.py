"""
Controlador HTTP de Comments
"""
import logging

from internal.comments.application.use_cases.create_comment import CreateCommentUseCase
from internal.comments.application.use_cases.get_comments_by_pin import GetCommentsByPinUseCase
from internal.comments.application.use_cases.get_replies import GetRepliesUseCase
from internal.comments.application.use_cases.update_comment import UpdateCommentUseCase
from internal.comments.application.use_cases.delete_comment import DeleteCommentUseCase
from internal.comments.application.use_cases.like_comment import LikeCommentUseCase

from internal.comments.domain.entities.comment import Comment, CommentResponse
from internal.comments.application.schemas.comment_schemas import (
    CreateCommentRequest,
    UpdateCommentRequest,
    CommentListResponse,
    RepliesListResponse,
    MessageResponse,
)
from core.notifications import notify_new_comment

logger = logging.getLogger(__name__)


class CommentController:
    def __init__(
        self,
        create_uc: CreateCommentUseCase,
        get_by_pin_uc: GetCommentsByPinUseCase,
        get_replies_uc: GetRepliesUseCase,
        update_uc: UpdateCommentUseCase,
        delete_uc: DeleteCommentUseCase,
        like_uc: LikeCommentUseCase,
        db_session=None,
    ):
        self._create_uc = create_uc
        self._get_by_pin_uc = get_by_pin_uc
        self._get_replies_uc = get_replies_uc
        self._update_uc = update_uc
        self._delete_uc = delete_uc
        self._like_uc = like_uc
        self._db = db_session

    @staticmethod
    def _to_response(
        comment: Comment,
        current_user_id: str = None,
        replies_count: int = 0,
    ) -> CommentResponse:
        is_owner = (current_user_id == comment.user_id) if current_user_id else False
        return CommentResponse(
            id=comment.id,
            pin_id=comment.pin_id,
            user_id=comment.user_id,
            user_username="",
            user_full_name="",
            user_avatar_url=None,
            user_is_verified=False,
            text=comment.text,
            parent_comment_id=comment.parent_comment_id,
            likes_count=comment.likes_count,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            is_edited=comment.created_at != comment.updated_at,
            can_edit=is_owner,
            can_delete=is_owner,
            replies_count=replies_count,
        )

    async def create_comment(
        self, body: CreateCommentRequest, user_id: str
    ) -> CommentResponse:
        comment = await self._create_uc.execute(
            pin_id=body.pin_id,
            user_id=user_id,
            text=body.text,
            parent_comment_id=body.parent_comment_id,
        )

        try:
            await self._send_comment_notification(user_id, body.pin_id, body.text)
        except Exception as e:
            logger.warning(f"No se pudo enviar notificacion de comment: {e}")

        return self._to_response(comment, current_user_id=user_id)

    async def _send_comment_notification(self, commenter_id: str, pin_id: str, text: str):
        if not self._db:
            return

        from core.database.models import PinModel, UserModel

        pin = self._db.query(PinModel).filter(PinModel.id == pin_id).first()
        if not pin or pin.user_id == commenter_id:
            return

        commenter = self._db.query(UserModel).filter(UserModel.id == commenter_id).first()
        commenter_username = commenter.username if commenter else "alguien"

        await notify_new_comment(
            pin_owner_id=pin.user_id,
            commenter_username=commenter_username,
            pin_id=pin_id,
            pin_title=pin.title or "tu pin",
            comment_text=text,
        )
        logger.info(f"Comment: {commenter_username} -> pin '{pin.title}' de {pin.user_id}")

    async def get_comments_by_pin(
        self, pin_id: str, current_user_id: str = None, limit: int = 50, offset: int = 0
    ) -> CommentListResponse:
        result = await self._get_by_pin_uc.execute(
            pin_id=pin_id, limit=limit, offset=offset
        )
        return CommentListResponse(
            comments=[
                self._to_response(c, current_user_id=current_user_id)
                for c in result["comments"]
            ],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    async def get_replies(
        self, comment_id: str, current_user_id: str = None, limit: int = 20, offset: int = 0
    ) -> RepliesListResponse:
        result = await self._get_replies_uc.execute(
            comment_id=comment_id, limit=limit, offset=offset
        )
        return RepliesListResponse(
            replies=[
                self._to_response(c, current_user_id=current_user_id)
                for c in result["replies"]
            ],
            total=result["total"],
            limit=result["limit"],
            offset=result["offset"],
            has_more=result["has_more"],
        )

    async def update_comment(
        self, comment_id: str, body: UpdateCommentRequest, user_id: str
    ) -> CommentResponse:
        comment = await self._update_uc.execute(
            comment_id=comment_id, user_id=user_id, new_text=body.text
        )
        return self._to_response(comment, current_user_id=user_id)

    async def delete_comment(self, comment_id: str, user_id: str) -> MessageResponse:
        await self._delete_uc.execute(comment_id=comment_id, user_id=user_id)
        return MessageResponse(message="Comentario eliminado correctamente")

    async def like_comment(self, comment_id: str) -> MessageResponse:
        await self._like_uc.like(comment_id)
        return MessageResponse(message="Like agregado")

    async def unlike_comment(self, comment_id: str) -> MessageResponse:
        await self._like_uc.unlike(comment_id)
        return MessageResponse(message="Like removido")