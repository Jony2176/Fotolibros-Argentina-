"""
Modelos de Datos - Fotolibros Argentina
"""
from .catalogo import (
    Producto,
    TipoTapa,
    Orientacion,
    MargenGanancia,
    PaquetePredefinido,
    TiemposEntrega,
    ZonaEnvio,
    ConfiguracionProveedor,
    CATALOGO_PRODUCTOS,
    PAQUETES_PREDEFINIDOS,
    TIEMPOS_ENTREGA,
    ZONAS_ENVIO,
    PROVEEDOR,
    obtener_producto_por_id,
    obtener_paquete_por_id,
    obtener_zona_por_provincia,
)

from .pedido import (
    Pedido,
    EstadoPedido,
    MetodoPago,
    DatosCliente,
    DatosEnvio,
    DatosPago,
    DatosProduccion,
    FotoSubida,
    HistorialEstado,
    crear_pedido,
    GeneradorNumeroPedido,
)

__all__ = [
    # Catálogo
    "Producto",
    "TipoTapa",
    "Orientacion",
    "MargenGanancia",
    "PaquetePredefinido",
    "TiemposEntrega",
    "ZonaEnvio",
    "ConfiguracionProveedor",
    "CATALOGO_PRODUCTOS",
    "PAQUETES_PREDEFINIDOS",
    "TIEMPOS_ENTREGA",
    "ZONAS_ENVIO",
    "PROVEEDOR",
    "obtener_producto_por_id",
    "obtener_paquete_por_id",
    "obtener_zona_por_provincia",
    # Pedidos
    "Pedido",
    "EstadoPedido",
    "MetodoPago",
    "DatosCliente",
    "DatosEnvio",
    "DatosPago",
    "DatosProduccion",
    "FotoSubida",
    "HistorialEstado",
    "crear_pedido",
    "GeneradorNumeroPedido",
]
