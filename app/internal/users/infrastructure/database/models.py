from sqlalchemy import Column, String, Boolean, Integer, Text, TIMESTAMP, Enum, JSON
from sqlalchemy.sql import func
from app.core.connection import Base
import enum

class GenderEnum(str, enum.Enum):
    male = "male"
    female = "female"
    non_binary = "non_binary"
    prefer_not_to_say = "prefer_not_to_say"

class RoleEnum(str, enum.Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    username = Column(String(30), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Información personal
    full_name = Column(String(100), nullable=False)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Preferencias
    gender = Column(Enum(GenderEnum), default=GenderEnum.prefer_not_to_say)
    preferred_styles = Column(JSON, default=list)
    
    # Estado
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    email_verified_at = Column(TIMESTAMP, nullable=True)
    
    # Seguridad
    login_attempts = Column(Integer, default=0)
    locked_until = Column(TIMESTAMP, nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_expiry = Column(TIMESTAMP, nullable=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP, nullable=True)