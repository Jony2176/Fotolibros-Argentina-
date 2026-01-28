"""
Modelos SQLAlchemy para la base de datos
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class EstadoPedido(str, enum.Enum):
    """Estados posibles de un pedido"""
    PENDIENTE = "pendiente"
    EN_COLA = "en_cola"
    ANALIZANDO = "analizando"
    EJECUTANDO = "ejecutando"
    ESPERANDO_CONFIRMACION = "esperando_confirmacion"
    COMPLETADO = "completado"
    ERROR = "error"
    CANCELADO = "cancelado"


class Pedido(Base):
    """Tabla de pedidos"""
    __tablename__ = "pedidos"
    
    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Cliente
    cliente_nombre = Column(String(200), nullable=False)
    cliente_email = Column(String(200), nullable=False)
    cliente_telefono = Column(String(50))
    
    # Libro
    codigo_producto = Column(String(50), nullable=False)
    tamano = Column(String(20))
    tapa = Column(String(20))
    estilo = Column(String(50))
    ocasion = Column(String(100))
    titulo_personalizado = Column(String(200))
    
    # Fotos
    directorio_fotos = Column(String(500))
    cantidad_fotos = Column(Integer)
    
    # Configuración
    modo_confirmacion = Column(Boolean, default=True)
    
    # Estado
    estado = Column(Enum(EstadoPedido), default=EstadoPedido.PENDIENTE)
    
    # AGNO
    agno_config = Column(JSON)  # Config generado por AGNO
    
    # Clawdbot
    clawdbot_session_key = Column(String(200))
    
    # Metadatos
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    fecha_pago = Column(DateTime)
    fecha_completado = Column(DateTime)
    
    # Errores
    intentos = Column(Integer, default=0)
    ultimo_error = Column(Text)
    
    # Extra
    notas_cliente = Column(Text)
    notas_internas = Column(Text)
