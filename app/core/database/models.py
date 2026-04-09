from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Enum, ForeignKey, Float, Table, Index, UniqueConstraint, func
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import enum
import uuid

Base = declarative_base()

# =====================================================
# ENUMS
# =====================================================

class NotificationType(str, enum.Enum):
    LIKE = "like"
    FOLLOW = "follow"
    COMMENT = "comment"
    BOARD_COLLABORATION = "board_collaboration"

# =====================================================
# USERS
# =====================================================

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(30), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # ✅ NO hashed_password
    full_name = Column(String(100), nullable=False)  # ✅ AGREGAR
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)  # ✅ NO profile_picture
    gender = Column(String(50), default="prefer_not_to_say")  # ✅ AGREGAR
    preferred_styles = Column(Text, nullable=True)  # ✅ AGREGAR (JSON como TEXT)
    is_verified = Column(Boolean, default=False)  # ✅ AGREGAR
    is_active = Column(Boolean, default=True)
    role = Column(String(20), default="user")  # ✅ AGREGAR
    email_verified_at = Column(DateTime, nullable=True)  # ✅ AGREGAR
    login_attempts = Column(Integer, default=0)  # ✅ AGREGAR
    locked_until = Column(DateTime, nullable=True)  # ✅ AGREGAR
    password_reset_token = Column(String(255), nullable=True)  # ✅ AGREGAR
    password_reset_token_expiry = Column(DateTime, nullable=True)  # ✅ AGREGAR
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)  # ✅ AGREGAR
    
    # Relaciones
    pins = relationship("Pin", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    follows = relationship("Follow", foreign_keys="Follow.follower_id", cascade="all, delete-orphan")
    followers = relationship("Follow", foreign_keys="Follow.following_id", cascade="all, delete-orphan")
    boards = relationship("Board", back_populates="user", cascade="all, delete-orphan")
    notifications_received = relationship("Notification", foreign_keys="Notification.user_id", cascade="all, delete-orphan")
    notifications_sent = relationship("Notification", foreign_keys="Notification.actor_id", cascade="all, delete-orphan")
    fcm_tokens = relationship("FCMToken", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_is_active', 'is_active'),
        Index('idx_username', 'username'),
    )

# =====================================================
# PINS
# =====================================================

class Pin(Base):
    __tablename__ = "pins"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=False)  # ✅ REQUIRED
    category = Column(String(100), nullable=True)
    styles = Column(Text, nullable=True)  # ✅ AGREGAR (JSON como TEXT)
    occasions = Column(Text, nullable=True)  # ✅ AGREGAR
    season = Column(String(50), nullable=True)
    brands = Column(Text, nullable=True)  # ✅ AGREGAR
    price_range = Column(String(50), nullable=True)
    where_to_buy = Column(String(200), nullable=True)  # ✅ AGREGAR
    purchase_link = Column(String(500), nullable=True)  # ✅ AGREGAR
    likes_count = Column(Integer, default=0)
    saves_count = Column(Integer, default=0)  # ✅ AGREGAR
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)  # ✅ AGREGAR
    colors = Column(Text, nullable=True)  # ✅ AGREGAR
    tags = Column(Text, nullable=True)  # ✅ AGREGAR
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="pins")
    likes = relationship("Like", back_populates="pin", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="pin", cascade="all, delete-orphan")
    notifications = relationship("Notification", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_is_private', 'is_private'),
        Index('idx_user_id', 'user_id'),
    )
# =====================================================
# LIKES
# =====================================================

class Like(Base):
    __tablename__ = "likes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pin_id = Column(String(36), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="likes")
    pin = relationship("Pin", back_populates="likes")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'pin_id', name='unique_user_pin_like'),
        Index('idx_user_id', 'user_id'),
        Index('idx_pin_id', 'pin_id'),
    )

# =====================================================
# FOLLOWS
# =====================================================

class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    follower_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    following_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        UniqueConstraint('follower_id', 'following_id', name='unique_follow'),
        Index('idx_follower_id', 'follower_id'),
        Index('idx_following_id', 'following_id'),
    )

# =====================================================
# COMMENTS
# =====================================================

class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pin_id = Column(String(36), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False)
    text = Column(Text, nullable=False)
    parent_comment_id = Column(String(36), ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    likes_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="comments")
    pin = relationship("Pin", back_populates="comments")
    notifications = relationship("Notification", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_pin_id', 'pin_id'),
        Index('idx_user_id', 'user_id'),
    )

# =====================================================
# BOARDS
# =====================================================

class Board(Base):
    __tablename__ = "boards"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="boards")
    board_pins = relationship("BoardPin", back_populates="board", cascade="all, delete-orphan")
    collaborators = relationship("BoardCollaborator", back_populates="board", cascade="all, delete-orphan")
    notifications = relationship("Notification", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_created_at', 'created_at'),
    )

# =====================================================
# BOARD PINS
# =====================================================

class BoardPin(Base):
    __tablename__ = "board_pins"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    board_id = Column(String(36), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    pin_id = Column(String(36), ForeignKey("pins.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    board = relationship("Board", back_populates="board_pins")
    
    __table_args__ = (
        UniqueConstraint('board_id', 'pin_id', name='unique_board_pin'),
        Index('idx_board_id', 'board_id'),
        Index('idx_pin_id', 'pin_id'),
    )

# =====================================================
# BOARD COLLABORATORS
# =====================================================

class BoardCollaborator(Base):
    __tablename__ = "board_collaborators"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    board_id = Column(String(36), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    can_edit = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    board = relationship("Board", back_populates="collaborators")
    
    __table_args__ = (
        UniqueConstraint('board_id', 'user_id', name='unique_board_collaborator'),
        Index('idx_board_id', 'board_id'),
        Index('idx_user_id', 'user_id'),
    )

# =====================================================
# NOTIFICATIONS
# =====================================================

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    actor_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    pin_id = Column(String(36), ForeignKey("pins.id", ondelete="SET NULL"), nullable=True)
    comment_id = Column(String(36), ForeignKey("comments.id", ondelete="SET NULL"), nullable=True)
    board_id = Column(String(36), ForeignKey("boards.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    
    # Relaciones
    user = relationship("User", foreign_keys=[user_id], back_populates="notifications_received")
    actor = relationship("User", foreign_keys=[actor_id], back_populates="notifications_sent")
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_actor_id', 'actor_id'),
        Index('idx_is_read', 'is_read'),
        Index('idx_created_at', 'created_at'),
        Index('idx_type', 'type'),
    )

# =====================================================
# FCM TOKENS
# =====================================================

class FCMToken(Base):
    __tablename__ = "fcm_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    device_token = Column(String(500), nullable=False)
    device_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    user = relationship("User", back_populates="fcm_tokens")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'device_token', name='unique_user_device_token'),
        Index('idx_user_id', 'user_id'),
        Index('idx_is_active', 'is_active'),
    )