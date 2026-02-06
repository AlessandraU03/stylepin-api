"""
Implementación del repositorio de Pins usando SQLAlchemy
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc

from app.internal.pines.domain.entities.pin import Pin
from app.internal.pines.domain.repositories.pin_repository import PinRepository
from app.internal.pines.infrastructure.database.pin_model import PinModel

class PinRepositoryImpl(PinRepository):
    """
    Implementación concreta del repositorio de Pins
    Usa SQLAlchemy para interactuar con MySQL
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, pin: Pin) -> Pin:
        """Crea un nuevo pin en la base de datos"""
        db_pin = PinModel(
            id=pin.id,
            user_id=pin.user_id,
            image_url=pin.image_url,
            title=pin.title,
            description=pin.description,
            category=pin.category,
            styles=pin.styles,
            occasions=pin.occasions,
            season=pin.season,
            brands=pin.brands,
            price_range=pin.price_range,
            where_to_buy=pin.where_to_buy,
            purchase_link=pin.purchase_link,
            colors=pin.colors,
            tags=pin.tags,
            is_private=pin.is_private,
            likes_count=0,
            saves_count=0,
            comments_count=0,
            views_count=0
        )
        
        self.db.add(db_pin)
        self.db.commit()
        self.db.refresh(db_pin)
        
        return self._to_entity(db_pin)
    
    async def get_by_id(self, pin_id: str) -> Optional[Pin]:
        """Obtiene un pin por su ID"""
        db_pin = self.db.query(PinModel).filter(
            PinModel.id == pin_id
        ).first()
        
        return self._to_entity(db_pin) if db_pin else None
    
    async def get_all(
        self,
        limit: int = 20,
        offset: int = 0,
        user_id: Optional[str] = None,
        category: Optional[str] = None,
        season: Optional[str] = None
    ) -> List[Pin]:
        """Obtiene lista de pins públicos con filtros opcionales"""
        query = self.db.query(PinModel).filter(
            PinModel.is_private == False
        )
        
        # Aplicar filtros opcionales
        if user_id:
            query = query.filter(PinModel.user_id == user_id)
        if category:
            query = query.filter(PinModel.category == category)
        if season:
            query = query.filter(PinModel.season == season)
        
        # Ordenar por más recientes
        query = query.order_by(desc(PinModel.created_at))
        
        # Paginación
        db_pins = query.limit(limit).offset(offset).all()
        
        return [self._to_entity(pin) for pin in db_pins]
    
    async def get_by_user(
        self, 
        user_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Pin]:
        """Obtiene pins de un usuario específico (incluye privados)"""
        db_pins = self.db.query(PinModel).filter(
            PinModel.user_id == user_id
        ).order_by(
            desc(PinModel.created_at)
        ).limit(limit).offset(offset).all()
        
        return [self._to_entity(pin) for pin in db_pins]
    
    async def update(self, pin: Pin) -> Pin:
        """Actualiza un pin existente"""
        db_pin = self.db.query(PinModel).filter(
            PinModel.id == pin.id
        ).first()
        
        if db_pin:
            db_pin.title = pin.title
            db_pin.description = pin.description
            db_pin.category = pin.category
            db_pin.styles = pin.styles
            db_pin.occasions = pin.occasions
            db_pin.season = pin.season
            db_pin.brands = pin.brands
            db_pin.price_range = pin.price_range
            db_pin.where_to_buy = pin.where_to_buy
            db_pin.purchase_link = pin.purchase_link
            db_pin.colors = pin.colors
            db_pin.tags = pin.tags
            db_pin.is_private = pin.is_private
            db_pin.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_pin)
        
        return self._to_entity(db_pin)
    
    async def delete(self, pin_id: str) -> bool:
        """Elimina un pin de la base de datos"""
        db_pin = self.db.query(PinModel).filter(
            PinModel.id == pin_id
        ).first()
        
        if db_pin:
            self.db.delete(db_pin)
            self.db.commit()
            return True
        
        return False
    
    async def increment_views(self, pin_id: str) -> None:
        """Incrementa el contador de vistas de un pin"""
        db_pin = self.db.query(PinModel).filter(
            PinModel.id == pin_id
        ).first()
        
        if db_pin:
            db_pin.views_count += 1
            self.db.commit()
    
    async def search(
        self, 
        query: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Pin]:
        """Busca pins por título o descripción"""
        search_pattern = f"%{query}%"
        
        db_pins = self.db.query(PinModel).filter(
            and_(
                PinModel.is_private == False,
                or_(
                    PinModel.title.like(search_pattern),
                    PinModel.description.like(search_pattern)
                )
            )
        ).order_by(
            desc(PinModel.created_at)
        ).limit(limit).offset(offset).all()
        
        return [self._to_entity(pin) for pin in db_pins]
    
    def _to_entity(self, db_pin: PinModel) -> Pin:
        """Convierte modelo de DB a entidad de dominio"""
        return Pin(
            id=db_pin.id,
            user_id=db_pin.user_id,
            image_url=db_pin.image_url,
            title=db_pin.title,
            description=db_pin.description,
            category=db_pin.category.value if hasattr(db_pin.category, 'value') else db_pin.category,
            styles=db_pin.styles or [],
            occasions=db_pin.occasions or [],
            season=db_pin.season.value if hasattr(db_pin.season, 'value') else db_pin.season,
            brands=db_pin.brands or [],
            price_range=db_pin.price_range.value if hasattr(db_pin.price_range, 'value') else db_pin.price_range,
            where_to_buy=db_pin.where_to_buy,
            purchase_link=db_pin.purchase_link,
            likes_count=db_pin.likes_count,
            saves_count=db_pin.saves_count,
            comments_count=db_pin.comments_count,
            views_count=db_pin.views_count,
            colors=db_pin.colors or [],
            tags=db_pin.tags or [],
            is_private=db_pin.is_private,
            created_at=db_pin.created_at,
            updated_at=db_pin.updated_at
        )