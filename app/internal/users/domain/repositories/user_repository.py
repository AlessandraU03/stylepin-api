from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime
from app.internal.users.domain.entities.user import User

class UserRepository(ABC):
    """Interface del repositorio de usuarios (Port)"""
    
    @abstractmethod
    async def create(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update(self, user: User) -> User:
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: str) -> None:
        pass
    
    @abstractmethod
    async def update_login_attempts(
        self, 
        user_id: str, 
        attempts: int, 
        locked_until: Optional[datetime]
    ) -> None:
        pass
    
    @abstractmethod
    async def get_by_identity(self, identity: str) -> Optional[User]:
        """
        Busca un usuario por su email o por su username.
        Esencial para el login flexible.
        """
        pass
    