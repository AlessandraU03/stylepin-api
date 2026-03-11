from abc import ABC, abstractmethod
from typing import Optional, List
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

    @abstractmethod
    async def increment_login_attempts(self, user_id: str) -> None:
        """Incrementar intentos de login fallidos"""
        pass
    
    @abstractmethod
    async def reset_login_attempts(self, user_id: str) -> None:
        """Resetear intentos de login"""
        pass
    
    @abstractmethod
    async def lock_account(self, user_id: str, until: any) -> None:
        """Bloquear cuenta temporalmente"""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: str) -> None:
        """Actualizar timestamp de último login"""
        pass

    @abstractmethod
    async def search_users(
        self, 
        query: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[User]:
        """Buscar usuarios por username o full_name"""
        pass
    
    @abstractmethod
    async def get_user_stats(self, user_id: str) -> dict:
        """
        Obtener estadísticas del usuario
        Returns: {
            'total_pins': int,
            'total_followers': int,
            'total_following': int,
            'total_boards': int
        }
        """
        pass
    