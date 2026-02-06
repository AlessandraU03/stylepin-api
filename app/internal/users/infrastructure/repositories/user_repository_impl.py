from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.internal.users.domain.entities.user import User
from app.internal.users.domain.repositories.user_repository import UserRepository
from app.internal.users.infrastructure.database.models import UserModel

class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, user: User) -> User:
        db_user = UserModel(
            id=user.id,
            username=user.username,
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            gender=user.gender,
            preferred_styles=user.preferred_styles,
            is_verified=user.is_verified,
            is_active=user.is_active,
            role=user.role,
            login_attempts=user.login_attempts
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return self._to_entity(db_user)
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(
            UserModel.id == user_id,
            UserModel.is_active == True
        ).first()
        
        return self._to_entity(db_user) if db_user else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(
            UserModel.email == email.lower()
        ).first()
        
        return self._to_entity(db_user) if db_user else None
    
    async def get_by_username(self, username: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(
            UserModel.username == username,
            UserModel.is_active == True
        ).first()
        
        return self._to_entity(db_user) if db_user else None
    
    async def update(self, user: User) -> User:
        db_user = self.db.query(UserModel).filter(UserModel.id == user.id).first()
        
        if db_user:
            db_user.username = user.username
            db_user.email = user.email
            db_user.full_name = user.full_name
            db_user.bio = user.bio
            db_user.avatar_url = user.avatar_url
            db_user.gender = user.gender
            db_user.preferred_styles = user.preferred_styles
            db_user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_user)
        
        return self._to_entity(db_user)
    
    async def delete(self, user_id: str) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if db_user:
            db_user.is_active = False
            db_user.updated_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    async def exists_by_email(self, email: str) -> bool:
        return self.db.query(UserModel).filter(
            UserModel.email == email.lower()
        ).first() is not None
    
    async def exists_by_username(self, username: str) -> bool:
        return self.db.query(UserModel).filter(
            UserModel.username == username
        ).first() is not None
    
    async def update_last_login(self, user_id: str) -> None:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if db_user:
            db_user.last_login = datetime.utcnow()
            self.db.commit()
    
    async def update_login_attempts(
        self,
        user_id: str,
        attempts: int,
        locked_until: Optional[datetime]
    ) -> None:
        db_user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        
        if db_user:
            db_user.login_attempts = attempts
            db_user.locked_until = locked_until
            db_user.updated_at = datetime.utcnow()
            self.db.commit()
    
    def _to_entity(self, db_user: UserModel) -> User:
        """Convierte modelo de DB a entidad de dominio"""
        return User(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            password_hash=db_user.password_hash,
            full_name=db_user.full_name,
            bio=db_user.bio,
            avatar_url=db_user.avatar_url,
            gender=db_user.gender.value if db_user.gender else "prefer_not_to_say",
            preferred_styles=db_user.preferred_styles or [],
            is_verified=db_user.is_verified,
            is_active=db_user.is_active,
            role=db_user.role.value if db_user.role else "user",
            email_verified_at=db_user.email_verified_at,
            login_attempts=db_user.login_attempts,
            locked_until=db_user.locked_until,
            password_reset_token=db_user.password_reset_token,
            password_reset_token_expiry=db_user.password_reset_token_expiry,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
            last_login=db_user.last_login
        )