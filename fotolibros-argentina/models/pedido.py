"""
Modelo de Pedidos - Fotolibros Argentina
========================================
Gestión completa del ciclo de vida de un pedido.

FLUJO DE ESTADOS:
1. PENDIENTE_PAGO    → Cliente cargó pedido, esperando comprobante
2. VERIFICANDO_PAGO  → Comprobante subido, verificando con IA
3. PAGO_APROBADO     → Pago verificado, listo para producir
4. EN_PRODUCCION     → Pedido enviado a la gráfica
5. PRODUCIDO         → Gráfica terminó, en camino a Jonatan
6. EN_MI_DOMICILIO   → Recibido por Jonatan, listo para enviar
7. ENVIADO_CLIENTE   → Despachado al cliente final
8. ENTREGADO         → Cliente confirmó recepción
9. CANCELADO         → Pedido cancelado
10. RECHAZADO        → Pago rechazado
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from decimal import Decimal
import uuid


class EstadoPedido(Enum):
    """Estados del pedido en el flujo"""
    PENDIENTE_PAGO = "pendiente_pago"
    VERIFICANDO_PAGO = "verificando_pago"
    PAGO_APROBADO = "pago_aprobado"
    EN_PRODUCCION = "en_produccion"         # Enviado a la gráfica
    PRODUCIDO = "producido"                  # Gráfica terminó
    EN_MI_DOMICILIO = "en_mi_domicilio"     # Jonatan lo recibió
    ENVIADO_CLIENTE = "enviado_cliente"      # Despachado al cliente
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"
    RECHAZADO = "rechazado"                  # Pago no válido


class MetodoPago(Enum):
    """Métodos de pago aceptados"""
    TRANSFERENCIA = "transferencia"
    MERCADOPAGO = "mercadopago"
    EFECTIVO = "efectivo"  # Solo para retiro en persona (futuro)


@dataclass
class DatosCliente:
    """Información del cliente"""
    nombre: str
    apellido: str
    email: str
    telefono: str
    # Dirección de envío
    calle: str
    numero: str
    piso: Optional[str] = None
    departamento: Optional[str] = None
    codigo_postal: str = ""
    ciudad: str = ""
    provincia: str = ""
    pais: str = "Argentina"
    # Extras
    notas_entrega: Optional[str] = None  # "Tocar timbre 2B", etc.
    
    @property
    def direccion_completa(self) -> str:
        """Dirección formateada para etiqueta de envío"""
        direccion = f"{self.calle} {self.numero}"
        if self.piso:
            direccion += f", Piso {self.piso}"
        if self.departamento:
            direccion += f", Depto {self.departamento}"
        direccion += f"\n{self.codigo_postal} - {self.ciudad}, {self.provincia}"
        return direccion
    
    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


@dataclass
class DatosEnvio:
    """Información del envío al cliente"""
    zona_id: str
    costo_envio: Decimal
    dias_estimados_min: int
    dias_estimados_max: int
    # Tracking
    codigo_seguimiento: Optional[str] = None
    empresa_envio: Optional[str] = None  # "Correo Argentino", "Andreani", etc.
    fecha_despacho: Optional[datetime] = None
    fecha_entrega_estimada: Optional[datetime] = None
    fecha_entrega_real: Optional[datetime] = None


@dataclass
class DatosPago:
    """Información del pago"""
    metodo: MetodoPago
    monto_total: Decimal
    monto_producto: Decimal
    monto_paginas_extra: Decimal
    monto_envio: Decimal
    # Verificación
    comprobante_path: Optional[str] = None
    verificado: bool = False
    fecha_verificacion: Optional[datetime] = None
    resultado_verificacion: Optional[Dict[str, Any]] = None
    # Errores
    motivo_rechazo: Optional[str] = None


@dataclass
class DatosProduccion:
    """Información de la producción en la gráfica"""
    fecha_pedido_grafica: Optional[datetime] = None
    numero_pedido_grafica: Optional[str] = None  # Número de orden de FDF
    fecha_produccion_estimada: Optional[datetime] = None
    fecha_produccion_real: Optional[datetime] = None
    # Envío gráfica → Jonatan
    fecha_envio_grafica: Optional[datetime] = None
    fecha_recepcion_jonatan: Optional[datetime] = None
    tracking_grafica: Optional[str] = None
    notas_produccion: Optional[str] = None


@dataclass
class FotoSubida:
    """Información de una foto subida por el cliente"""
    id: str
    nombre_original: str
    ruta_almacenamiento: str
    tamaño_bytes: int
    ancho_px: int
    alto_px: int
    orientacion: str  # "horizontal", "vertical", "cuadrada"
    fecha_subida: datetime
    orden: int  # Posición en el fotolibro
    # Metadata EXIF
    fecha_toma: Optional[datetime] = None
    camara: Optional[str] = None
    # Calidad
    dpi: Optional[int] = None
    calidad_score: Optional[float] = None  # 0-100
    advertencias: List[str] = field(default_factory=list)


@dataclass
class HistorialEstado:
    """Registro de cambio de estado"""
    estado: EstadoPedido
    fecha: datetime
    nota: Optional[str] = None
    actor: str = "sistema"  # "sistema", "admin", "cliente"


@dataclass
class Pedido:
    """Pedido completo de un fotolibro"""
    # Identificación
    id: str
    numero_pedido: str  # Formato: FA-2026-0001
    fecha_creacion: datetime
    
    # Producto
    producto_id: str
    producto_nombre: str
    paquete_id: Optional[str] = None  # Si eligió un paquete predefinido
    paginas_totales: int = 22
    margen_aplicado: str = "estandar"  # "penetracion", "estandar", "premium"
    
    # Fotos
    fotos: List[FotoSubida] = field(default_factory=list)
    cantidad_fotos: int = 0
    
    # Cliente
    cliente: Optional[DatosCliente] = None
    
    # Envío
    envio: Optional[DatosEnvio] = None
    
    # Pago
    pago: Optional[DatosPago] = None
    
    # Producción
    produccion: Optional[DatosProduccion] = None
    
    # Estado
    estado: EstadoPedido = EstadoPedido.PENDIENTE_PAGO
    historial_estados: List[HistorialEstado] = field(default_factory=list)
    
    # Timestamps
    fecha_actualizacion: Optional[datetime] = None
    fecha_finalizacion: Optional[datetime] = None
    
    # Notas internas
    notas_admin: Optional[str] = None
    
    def cambiar_estado(self, nuevo_estado: EstadoPedido, nota: str = None, actor: str = "sistema"):
        """Cambia el estado y registra en historial"""
        self.estado = nuevo_estado
        self.fecha_actualizacion = datetime.now()
        self.historial_estados.append(HistorialEstado(
            estado=nuevo_estado,
            fecha=datetime.now(),
            nota=nota,
            actor=actor
        ))
        
        # Marcar como finalizado si corresponde
        if nuevo_estado in [EstadoPedido.ENTREGADO, EstadoPedido.CANCELADO, EstadoPedido.RECHAZADO]:
            self.fecha_finalizacion = datetime.now()
    
    def calcular_fecha_entrega_estimada(self) -> datetime:
        """Calcula fecha estimada de entrega al cliente"""
        # Importar aquí para evitar circular
        from models.catalogo import TIEMPOS_ENTREGA
        
        base = self.fecha_creacion
        if self.pago and self.pago.fecha_verificacion:
            base = self.pago.fecha_verificacion
        
        # Agregar días hábiles (simplificado, sin contar feriados)
        dias_habiles = TIEMPOS_ENTREGA.total_max_dias
        dias_agregados = 0
        fecha = base
        
        while dias_agregados < dias_habiles:
            fecha += timedelta(days=1)
            # Saltar fines de semana
            if fecha.weekday() < 5:  # Lunes=0, Viernes=4
                dias_agregados += 1
        
        return fecha
    
    @property
    def precio_total(self) -> Decimal:
        """Precio total del pedido"""
        if self.pago:
            return self.pago.monto_total
        return Decimal(0)
    
    @property
    def dias_desde_creacion(self) -> int:
        """Días transcurridos desde la creación"""
        return (datetime.now() - self.fecha_creacion).days
    
    @property
    def esta_activo(self) -> bool:
        """Si el pedido está activo (no finalizado)"""
        return self.estado not in [
            EstadoPedido.ENTREGADO,
            EstadoPedido.CANCELADO,
            EstadoPedido.RECHAZADO
        ]


# ============================================
# GENERADOR DE NÚMEROS DE PEDIDO
# ============================================

class GeneradorNumeroPedido:
    """Genera números de pedido únicos"""
    _contador: int = 0
    _año_actual: int = 0
    
    @classmethod
    def generar(cls) -> str:
        """Genera número de pedido: FA-2026-0001"""
        año = datetime.now().year
        
        # Resetear contador si cambió el año
        if año != cls._año_actual:
            cls._año_actual = año
            cls._contador = 0
        
        cls._contador += 1
        return f"FA-{año}-{cls._contador:04d}"


def crear_pedido(
    producto_id: str,
    producto_nombre: str,
    paginas_totales: int = 22,
    paquete_id: Optional[str] = None,
    margen: str = "estandar"
) -> Pedido:
    """Factory para crear un nuevo pedido"""
    return Pedido(
        id=str(uuid.uuid4()),
        numero_pedido=GeneradorNumeroPedido.generar(),
        fecha_creacion=datetime.now(),
        producto_id=producto_id,
        producto_nombre=producto_nombre,
        paquete_id=paquete_id,
        paginas_totales=paginas_totales,
        margen_aplicado=margen,
        historial_estados=[
            HistorialEstado(
                estado=EstadoPedido.PENDIENTE_PAGO,
                fecha=datetime.now(),
                nota="Pedido creado",
                actor="sistema"
            )
        ]
    )


# ============================================
# EJEMPLO DE USO
# ============================================

if __name__ == "__main__":
    from models.catalogo import (
        obtener_producto_por_id,
        obtener_zona_por_provincia,
        MargenGanancia,
        TIEMPOS_ENTREGA
    )
    
    # Crear pedido
    pedido = crear_pedido(
        producto_id="CU-21x21-DURA",
        producto_nombre="Fotolibro 21x21 Tapa Dura",
        paginas_totales=30,
        margen="estandar"
    )
    
    print(f"📦 Pedido creado: {pedido.numero_pedido}")
    print(f"   Estado: {pedido.estado.value}")
    print(f"   Producto: {pedido.producto_nombre}")
    print(f"   Páginas: {pedido.paginas_totales}")
    
    # Calcular precio
    producto = obtener_producto_por_id("CU-21x21-DURA")
    if producto:
        precio = producto.calcular_precio_total(30, MargenGanancia.ESTANDAR)
        print(f"   Precio (70%): ${precio:,.0f}")
    
    # Fecha estimada
    fecha_entrega = pedido.calcular_fecha_entrega_estimada()
    print(f"   Entrega estimada: {fecha_entrega.strftime('%d/%m/%Y')}")
    print(f"   Tiempo: {TIEMPOS_ENTREGA.mensaje_cliente()}")
