"""
Modelos SQLAlchemy para todas las tablas
"""
from sqlalchemy import Column, String, Boolean, Integer, Text, TIMESTAMP, Enum, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from core.connection import Base
import enum

# ==================== ENUMS ====================

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    non_binary = "non_binary"
    prefer_not_to_say = "prefer_not_to_say"

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"

class PinCategoryEnum(str, enum.Enum):
    outfit_completo = "outfit_completo"
    prenda_individual = "prenda_individual"
    accesorio = "accesorio"
    calzado = "calzado"

class SeasonEnum(str, enum.Enum):
    primavera = "primavera"
    verano = "verano"
    otono = "otono"
    invierno = "invierno"
    todo_el_ano = "todo_el_ano"

class PriceRangeEnum(str, enum.Enum):
    bajo_500 = "bajo_500"
    rango_500_1000 = "500_1000"
    rango_1000_2000 = "1000_2000"
    mas_2000 = "mas_2000"

# ==================== USERS ====================

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    gender = Column(Enum(GenderEnum), default=GenderEnum.prefer_not_to_say)
    preferred_styles = Column(JSON, default=list)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    email_verified_at = Column(TIMESTAMP, nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(TIMESTAMP, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expiry = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP, nullable=True)

# ==================== PINS ====================

class PinModel(Base):
    __tablename__ = "pins"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(Enum(PinCategoryEnum), nullable=False, index=True)
    styles = Column(JSON, default=list)
    occasions = Column(JSON, default=list)
    season = Column(Enum(SeasonEnum), default=SeasonEnum.todo_el_ano, index=True)
    brands = Column(JSON, default=list)
    price_range = Column(Enum(PriceRangeEnum), default=PriceRangeEnum.bajo_500)
    where_to_buy = Column(String(200), nullable=True)
    purchase_link = Column(String(500), nullable=True)
    likes_count = Column(Integer, default=0, index=True)
    saves_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    colors = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    is_private = Column(Boolean, default=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# ==================== BOARDS ====================

class BoardModel(Base):
    __tablename__ = "boards"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    cover_image_url = Column(String(500), nullable=True)
    is_private = Column(Boolean, default=False, index=True)
    is_collaborative = Column(Boolean, default=False)
    pins_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

# ==================== BOARD_PINS ====================

class BoardPinModel(Base):
    __tablename__ = "board_pins"
    
    id = Column(String(36), primary_key=True)
    board_id = Column(String(36), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True)
    pin_id = Column(String(36), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('board_id', 'pin_id', name='unique_board_pin'),
    )

# ==================== BOARD_COLLABORATORS ====================

class BoardCollaboratorModel(Base):
    __tablename__ = "board_collaborators"
    
    id = Column(String(36), primary_key=True)
    board_id = Column(String(36), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    can_edit = Column(Boolean, default=False)
    can_add_pins = Column(Boolean, default=True)
    can_remove_pins = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('board_id', 'user_id', name='unique_board_collaborator'),
    )

# ==================== LIKES ====================

class LikeModel(Base):
    __tablename__ = "likes"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    pin_id = Column(String(36), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('user_id', 'pin_id', name='unique_user_pin_like'),
    )

# ==================== FOLLOWS ====================

class FollowModel(Base):
    __tablename__ = "follows"
    
    id = Column(String(36), primary_key=True)
    follower_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    following_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_follower_following'),
    )

# ==================== COMMENTS ====================

class CommentModel(Base):
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True)
    pin_id = Column(String(36), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    parent_comment_id = Column(String(36), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    likes_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())