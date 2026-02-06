from sqlalchemy.orm import Session
from fastapi import Depends

# Importaciones de infraestructura base
from app.core.connection import get_db 
from app.internal.users.infrastructure.repositories.user_repository_impl import UserRepositoryImpl
from app.core.security import get_current_user_id

# Importaciones del módulo Pines
from app.internal.pines.infrastructure.repositories.pin_repository_impl import PinRepositoryImpl
from app.internal.pines.application.use_cases.create_pin import CreatePinUseCase
from app.internal.pines.application.use_cases.get_pins import GetPinsUseCase, GetPinByIdUseCase
from app.internal.pines.application.use_cases.update_pin import UpdatePinUseCase
from app.internal.pines.application.use_cases.delete_pin import DeletePinUseCase

# --- Inyección de Repositorios ---
def get_pin_repository(db: Session = Depends(get_db)) -> PinRepositoryImpl:
    return PinRepositoryImpl(db)

def get_user_repository(db: Session = Depends(get_db)) -> UserRepositoryImpl:
    return UserRepositoryImpl(db)

# --- Inyección de Casos de Uso ---
def get_create_pin_use_case(
    pin_repo: PinRepositoryImpl = Depends(get_pin_repository),
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> CreatePinUseCase:
    return CreatePinUseCase(pin_repo, user_repo)

def get_get_pins_use_case(
    pin_repo: PinRepositoryImpl = Depends(get_pin_repository),
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> GetPinsUseCase:
    return GetPinsUseCase(pin_repo, user_repo)

def get_get_pin_by_id_use_case(
    pin_repo: PinRepositoryImpl = Depends(get_pin_repository),
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> GetPinByIdUseCase:
    return GetPinByIdUseCase(pin_repo, user_repo)

def get_update_pin_use_case(
    pin_repo: PinRepositoryImpl = Depends(get_pin_repository),
    user_repo: UserRepositoryImpl = Depends(get_user_repository)
) -> UpdatePinUseCase:
    return UpdatePinUseCase(pin_repo, user_repo)

def get_delete_pin_use_case(
    pin_repo: PinRepositoryImpl = Depends(get_pin_repository)
) -> DeletePinUseCase:
    return DeletePinUseCase(pin_repo)