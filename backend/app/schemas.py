"""
Esquemas Pydantic para validación de requests/responses
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import EstadoPedido


class ClienteCreate(BaseModel):
    """Schema para datos del cliente"""
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None


class LibroCreate(BaseModel):
    """Schema para datos del libro"""
    codigo_producto: str
    tamano: str
    tapa: str
    estilo: str
    ocasion: Optional[str] = None
    titulo_personalizado: Optional[str] = None


class PedidoCreate(BaseModel):
    """Schema para crear un pedido"""
    cliente: ClienteCreate
    libro: LibroCreate
    notas_cliente: Optional[str] = None
    modo_confirmacion: bool = True


class PedidoResponse(BaseModel):
    """Schema para respuesta de pedido"""
    id: int
    pedido_id: str
    cliente_nombre: str
    cliente_email: str
    codigo_producto: str
    estado: EstadoPedido
    cantidad_fotos: Optional[int]
    fecha_creacion: datetime
    fecha_actualizacion: datetime
    
    class Config:
        from_attributes = True


class PedidoEstado(BaseModel):
    """Schema para actualizar estado"""
    estado: EstadoPedido
    notas_internas: Optional[str] = None


class FotoUploadResponse(BaseModel):
    """Schema para respuesta de upload de fotos"""
    success: bool
    cantidad_subidas: int
    directorio: str
    mensaje: Optional[str] = None
