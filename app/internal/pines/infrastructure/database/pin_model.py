"""
Modelo SQLAlchemy para la tabla pins
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, TIMESTAMP, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from app.core.connection import Base
import enum

class PinCategoryEnum(str, enum.Enum):
    """Enum para categorías de pins"""
    outfit_completo = "outfit_completo"
    prenda_individual = "prenda_individual"
    accesorio = "accesorio"
    calzado = "calzado"

class SeasonEnum(str, enum.Enum):
    """Enum para temporadas"""
    primavera = "primavera"
    verano = "verano"
    otono = "otono"
    invierno = "invierno"
    todo_el_ano = "todo_el_ano"

class PriceRangeEnum(str, enum.Enum):
    """Enum para rangos de precio"""
    bajo_500 = "bajo_500"
    rango_500_1000 = "500_1000"
    rango_1000_2000 = "1000_2000"
    mas_2000 = "mas_2000"

class PinModel(Base):
    """
    Modelo de base de datos para pins
    Mapea a la tabla 'pins' en MySQL
    """
    __tablename__ = "pins"
    
    # Identificación
    id = Column(String(36), primary_key=True)
    user_id = Column(
        String(36), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Contenido
    image_url = Column(String(500), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Categorización
    category = Column(Enum(PinCategoryEnum), nullable=False, index=True)
    styles = Column(JSON, default=list)
    occasions = Column(JSON, default=list)
    season = Column(Enum(SeasonEnum), default=SeasonEnum.todo_el_ano, index=True)
    
    # Shopping
    brands = Column(JSON, default=list)
    price_range = Column(Enum(PriceRangeEnum), default=PriceRangeEnum.bajo_500)
    where_to_buy = Column(String(200), nullable=True)
    purchase_link = Column(String(500), nullable=True)
    
    # Engagement
    likes_count = Column(Integer, default=0, index=True)
    saves_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    views_count = Column(Integer, default=0)
    
    # Metadata
    colors = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    is_private = Column(Boolean, default=False, index=True)
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())