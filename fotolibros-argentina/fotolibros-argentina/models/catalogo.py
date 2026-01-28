"""
Catálogo de Productos - Fotolibros Argentina
=============================================
Datos extraídos de Fábrica de Fotolibros (Enero 2026)
Incluye precios mayoristas, márgenes y tiempos de entrega.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List
from decimal import Decimal


class TipoTapa(Enum):
    BLANDA = "blanda"
    DURA = "dura"
    SIMIL_CUERO = "simil_cuero"


class Orientacion(Enum):
    APAISADO = "apaisado"      # Horizontal
    CUADRADO = "cuadrado"
    VERTICAL = "vertical"


class MargenGanancia(Enum):
    """Márgenes de ganancia sobre precio mayorista"""
    PENETRACION = 0.50    # 50% - Cliente trae diseño listo
    ESTANDAR = 0.70       # 70% - Clientes particulares
    PREMIUM = 1.00        # 100% - Incluye diseño y armado


@dataclass
class Producto:
    """Producto del catálogo"""
    id: str
    nombre: str
    ancho_cm: float
    alto_cm: float
    orientacion: Orientacion
    tipo_tapa: TipoTapa
    paginas_base: int
    paginas_max: int
    precio_mayorista: Decimal          # Lo que pago a la gráfica
    precio_pagina_adicional: Decimal   # Costo por página extra
    activo: bool = True
    descripcion: str = ""
    
    def calcular_precio_venta(self, margen: MargenGanancia) -> Decimal:
        """Calcula precio de venta con margen"""
        return self.precio_mayorista * Decimal(1 + margen.value)
    
    def calcular_costo_paginas_extra(self, paginas_totales: int) -> Decimal:
        """Calcula costo de páginas adicionales"""
        if paginas_totales <= self.paginas_base:
            return Decimal(0)
        extras = paginas_totales - self.paginas_base
        return extras * self.precio_pagina_adicional
    
    def calcular_precio_total(self, paginas_totales: int, margen: MargenGanancia) -> Decimal:
        """Precio total incluyendo páginas extra y margen"""
        base = self.calcular_precio_venta(margen)
        extras = self.calcular_costo_paginas_extra(paginas_totales) * Decimal(1 + margen.value)
        return base + extras


# ============================================
# CATÁLOGO COMPLETO - FÁBRICA DE FOTOLIBROS
# ============================================
# Datos extraídos del informe de Gemini (Enero 2026)

CATALOGO_PRODUCTOS: List[Producto] = [
    # ═══════════════════════════════════════
    # FORMATO APAISADO (Horizontal)
    # ═══════════════════════════════════════
    Producto(
        id="AP-21x15-BLANDA",
        nombre="Fotolibro 21x14,8 Tapa Blanda",
        ancho_cm=21.0,
        alto_cm=14.8,
        orientacion=Orientacion.APAISADO,
        tipo_tapa=TipoTapa.BLANDA,
        paginas_base=22,
        paginas_max=80,
        precio_mayorista=Decimal("11500"),
        precio_pagina_adicional=Decimal("250"),
        descripcion="Económico, ideal para souvenirs y regalos"
    ),
    Producto(
        id="AP-21x15-DURA",
        nombre="Fotolibro 21x14,8 Tapa Dura",
        ancho_cm=21.0,
        alto_cm=14.8,
        orientacion=Orientacion.APAISADO,
        tipo_tapa=TipoTapa.DURA,
        paginas_base=22,
        paginas_max=80,
        precio_mayorista=Decimal("16900"),
        precio_pagina_adicional=Decimal("250"),
        descripcion="Más resistente, acabado profesional"
    ),
    Producto(
        id="AP-28x22-DURA",
        nombre="Fotolibro 27,9x21,6 Tapa Dura",
        ancho_cm=27.9,
        alto_cm=21.6,
        orientacion=Orientacion.APAISADO,
        tipo_tapa=TipoTapa.DURA,
        paginas_base=22,
        paginas_max=80,
        precio_mayorista=Decimal("24000"),
        precio_pagina_adicional=Decimal("500"),
        descripcion="Tamaño estándar, muy popular"
    ),
    Producto(
        id="AP-41x29-DURA",
        nombre="Fotolibro 41x29 Tapa Dura",
        ancho_cm=41.0,
        alto_cm=29.0,
        orientacion=Orientacion.APAISADO,
        tipo_tapa=TipoTapa.DURA,
        paginas_base=20,
        paginas_max=80,
        precio_mayorista=Decimal("47000"),
        precio_pagina_adicional=Decimal("1000"),
        descripcion="Gran formato, ideal para bodas y XV"
    ),
    Producto(
        id="AP-41x29-CUERO",
        nombre="Fotolibro 41x29 Premium Simil Cuero",
        ancho_cm=41.0,
        alto_cm=29.0,
        orientacion=Orientacion.APAISADO,
        tipo_tapa=TipoTapa.SIMIL_CUERO,
        paginas_base=20,
        paginas_max=80,
        precio_mayorista=Decimal("49000"),
        precio_pagina_adicional=Decimal("1000"),
        descripcion="Premium, acabado de lujo en simil cuero negro"
    ),
    
    # ═══════════════════════════════════════
    # FORMATO CUADRADO
    # ═══════════════════════════════════════
    Producto(
        id="CU-10x10-PACK12",
        nombre="Souvenir Pack x12 (10x10)",
        ancho_cm=10.0,
        alto_cm=10.0,
        orientacion=Orientacion.CUADRADO,
        tipo_tapa=TipoTapa.BLANDA,  # Puede variar
        paginas_base=22,
        paginas_max=80,
        precio_mayorista=Decimal("24000"),  # PACK de 12 unidades
        precio_pagina_adicional=Decimal("1000"),
        descripcion="Pack de 12 mini fotolibros, ideal para eventos"
    ),
    Producto(
        id="CU-21x21-BLANDA",
        nombre="Fotolibro 21x21 Tapa Blanda",
        ancho_cm=21.0,
        alto_cm=21.0,
        orientacion=Orientacion.CUADRADO,
        tipo_tapa=TipoTapa.BLANDA,
        paginas_base=22,
        paginas_max=80,
        precio_mayorista=Decimal("17500"),
        precio_pagina_adicional=Decimal("500"),
        descripcion="Cuadrado versátil, muy popular para viajes"
    ),
    Producto(
        id="CU-21x21-DURA",
        nombre="Fotolibro 21x21 Tapa Dura",
        ancho_cm=21.0,
        alto_cm=21.0,
        orientacion=Orientacion.CUADRADO,
        tipo_tapa=TipoTapa.DURA,
        paginas_base=22,
        paginas_max=80,
        precio_mayorista=Decimal("24000"),
        precio_pagina_adicional=Decimal("500"),
        descripcion="⭐ RECOMENDADO - Mejor relación calidad/precio"
    ),
    Producto(
        id="CU-29x29-DURA",
        nombre="Fotolibro 29x29 Tapa Dura",
        ancho_cm=29.0,
        alto_cm=29.0,
        orientacion=Orientacion.CUADRADO,
        tipo_tapa=TipoTapa.DURA,
        paginas_base=20,
        paginas_max=80,
        precio_mayorista=Decimal("45000"),
        precio_pagina_adicional=Decimal("1000"),
        descripcion="Premium cuadrado grande"
    ),
    Producto(
        id="CU-29x29-CUERO",
        nombre="Fotolibro 29x29 Premium Simil Cuero",
        ancho_cm=29.0,
        alto_cm=29.0,
        orientacion=Orientacion.CUADRADO,
        tipo_tapa=TipoTapa.SIMIL_CUERO,
        paginas_base=20,
        paginas_max=80,
        precio_mayorista=Decimal("47000"),
        precio_pagina_adicional=Decimal("1000"),
        descripcion="Lujo, acabado simil cuero negro"
    ),
    
    # ═══════════════════════════════════════
    # FORMATO VERTICAL (Portrait)
    # ═══════════════════════════════════════
    Producto(
        id="VE-22x28-BLANDA",
        nombre="Fotolibro 21,6x27,9 Tapa Blanda",
        ancho_cm=21.6,
        alto_cm=27.9,
        orientacion=Orientacion.VERTICAL,
        tipo_tapa=TipoTapa.BLANDA,
        paginas_base=22,
        paginas_max=80,
        precio_mayorista=Decimal("17500"),
        precio_pagina_adicional=Decimal("500"),
        descripcion="Estilo revista, ideal para portfolios"
    ),
    Producto(
        id="VE-22x28-DURA",
        nombre="Fotolibro 21,6x27,9 Tapa Dura",
        ancho_cm=21.6,
        alto_cm=27.9,
        orientacion=Orientacion.VERTICAL,
        tipo_tapa=TipoTapa.DURA,
        paginas_base=22,
        paginas_max=80,
        precio_mayorista=Decimal("24000"),
        precio_pagina_adicional=Decimal("500"),
        descripcion="Profesional vertical, muy elegante"
    ),
]


# ============================================
# PAQUETES PREDEFINIDOS
# ============================================

@dataclass
class PaquetePredefinido:
    """Paquetes listos para vender"""
    id: str
    nombre: str
    descripcion: str
    producto_id: str              # ID del producto base
    paginas_incluidas: int
    precio_sugerido: Decimal      # Precio final al cliente
    incluye_diseno: bool          # Si incluye armado por nosotros
    activo: bool = True


PAQUETES_PREDEFINIDOS: List[PaquetePredefinido] = [
    PaquetePredefinido(
        id="PKG-RECUERDOS-EXPRESS",
        nombre="Recuerdos Express",
        descripcion="Ideal para escapadas de fin de semana. Hasta 50 fotos.",
        producto_id="AP-21x15-DURA",
        paginas_incluidas=22,  # Base
        precio_sugerido=Decimal("23500"),
        incluye_diseno=False
    ),
    PaquetePredefinido(
        id="PKG-GRAN-VIAJE",
        nombre="Gran Viaje",
        descripcion="Diseño asistido + revisión de calidad + packaging regalo.",
        producto_id="CU-21x21-DURA",
        paginas_incluidas=30,
        precio_sugerido=Decimal("42000"),
        incluye_diseno=True
    ),
    PaquetePredefinido(
        id="PKG-BODA-PREMIUM",
        nombre="Boda/XV Premium",
        descripcion="Armado profesional de layout + papel premium 170g + tapa simil cuero.",
        producto_id="CU-29x29-CUERO",  # o "AP-41x29-CUERO"
        paginas_incluidas=40,
        precio_sugerido=Decimal("95000"),
        incluye_diseno=True
    ),
]


# ============================================
# TIEMPOS DE ENTREGA (Con buffer de seguridad)
# ============================================

@dataclass
class TiemposEntrega:
    """
    Tiempos de entrega al cliente.
    
    FLUJO:
    1. Cliente paga → Jonatan hace pedido a gráfica
    2. Gráfica produce (4-5 días hábiles)
    3. Gráfica envía a Jonatan (2-3 días hábiles)
    4. Jonatan envía al cliente (3-5 días hábiles)
    
    TOTAL REAL: ~10-13 días hábiles
    BUFFER DE SEGURIDAD: +2-5 días
    PROMESA AL CLIENTE: 12-18 días hábiles
    """
    produccion_grafica_min: int = 4      # Días hábiles
    produccion_grafica_max: int = 5
    envio_grafica_a_jonatan_min: int = 2
    envio_grafica_a_jonatan_max: int = 3
    envio_jonatan_a_cliente_min: int = 3
    envio_jonatan_a_cliente_max: int = 5
    buffer_seguridad: int = 3            # Días extra por imprevistos
    
    @property
    def total_min_dias(self) -> int:
        """Mínimo de días hábiles"""
        return (
            self.produccion_grafica_min +
            self.envio_grafica_a_jonatan_min +
            self.envio_jonatan_a_cliente_min +
            self.buffer_seguridad
        )
    
    @property
    def total_max_dias(self) -> int:
        """Máximo de días hábiles"""
        return (
            self.produccion_grafica_max +
            self.envio_grafica_a_jonatan_max +
            self.envio_jonatan_a_cliente_max +
            self.buffer_seguridad
        )
    
    def mensaje_cliente(self) -> str:
        """Mensaje para mostrar al cliente"""
        return f"{self.total_min_dias}-{self.total_max_dias} días hábiles"


TIEMPOS_ENTREGA = TiemposEntrega()


# ============================================
# ZONAS DE ENVÍO Y COSTOS
# ============================================

@dataclass
class ZonaEnvio:
    """Zona de envío con costos"""
    id: str
    nombre: str
    provincias: List[str]
    costo_base: Decimal           # Costo base del envío
    dias_estimados_min: int
    dias_estimados_max: int
    activo: bool = True


ZONAS_ENVIO: List[ZonaEnvio] = [
    ZonaEnvio(
        id="ZONA-AMBA",
        nombre="AMBA (Buenos Aires + GBA)",
        provincias=["CABA", "Buenos Aires"],
        costo_base=Decimal("3500"),
        dias_estimados_min=2,
        dias_estimados_max=4,
    ),
    ZonaEnvio(
        id="ZONA-CENTRO",
        nombre="Centro (Córdoba, Santa Fe, Entre Ríos)",
        provincias=["Córdoba", "Santa Fe", "Entre Ríos"],
        costo_base=Decimal("5000"),
        dias_estimados_min=3,
        dias_estimados_max=5,
    ),
    ZonaEnvio(
        id="ZONA-CUYO",
        nombre="Cuyo (Mendoza, San Juan, San Luis)",
        provincias=["Mendoza", "San Juan", "San Luis"],
        costo_base=Decimal("6000"),
        dias_estimados_min=4,
        dias_estimados_max=6,
    ),
    ZonaEnvio(
        id="ZONA-NOA",
        nombre="NOA (Tucumán, Salta, Jujuy, Catamarca, La Rioja, Sgo. del Estero)",
        provincias=["Tucumán", "Salta", "Jujuy", "Catamarca", "La Rioja", "Santiago del Estero"],
        costo_base=Decimal("7000"),
        dias_estimados_min=5,
        dias_estimados_max=7,
    ),
    ZonaEnvio(
        id="ZONA-NEA",
        nombre="NEA (Chaco, Formosa, Misiones, Corrientes)",
        provincias=["Chaco", "Formosa", "Misiones", "Corrientes"],
        costo_base=Decimal("7000"),
        dias_estimados_min=5,
        dias_estimados_max=7,
    ),
    ZonaEnvio(
        id="ZONA-PATAGONIA",
        nombre="Patagonia (Neuquén, Río Negro, Chubut, Santa Cruz, T. del Fuego)",
        provincias=["Neuquén", "Río Negro", "La Pampa", "Chubut", "Santa Cruz", "Tierra del Fuego"],
        costo_base=Decimal("9000"),
        dias_estimados_min=6,
        dias_estimados_max=10,
    ),
]


def obtener_zona_por_provincia(provincia: str) -> Optional[ZonaEnvio]:
    """Obtiene la zona de envío según la provincia"""
    for zona in ZONAS_ENVIO:
        if provincia in zona.provincias:
            return zona
    return None


def obtener_producto_por_id(producto_id: str) -> Optional[Producto]:
    """Obtiene un producto por su ID"""
    for producto in CATALOGO_PRODUCTOS:
        if producto.id == producto_id:
            return producto
    return None


def obtener_paquete_por_id(paquete_id: str) -> Optional[PaquetePredefinido]:
    """Obtiene un paquete por su ID"""
    for paquete in PAQUETES_PREDEFINIDOS:
        if paquete.id == paquete_id:
            return paquete
    return None


# ============================================
# CONFIGURACIÓN DEL PROVEEDOR
# ============================================

@dataclass
class ConfiguracionProveedor:
    """Datos del proveedor mayorista"""
    nombre: str = "Fábrica de Fotolibros"
    direccion: str = "Concepción Arenal 4501, Chacarita, CABA"
    telefono: str = "011.5217.8188"
    email: str = "info@fabricadefotolibros.com"
    web: str = "https://www.fabricadefotolibros.com"
    horario: str = "Lunes a viernes de 10 a 18 hs"
    # Especificaciones técnicas
    papel_gramaje: int = 170  # gramos
    acabado_tapa: str = "Laminado polipropileno mate"
    encuadernacion: str = "Tradicional (libro)"


PROVEEDOR = ConfiguracionProveedor()


# ============================================
# EJEMPLO DE USO
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("CATÁLOGO FOTOLIBROS ARGENTINA")
    print("=" * 60)
    
    # Mostrar productos
    print("\n📦 PRODUCTOS DISPONIBLES:\n")
    for p in CATALOGO_PRODUCTOS:
        precio_50 = p.calcular_precio_venta(MargenGanancia.PENETRACION)
        precio_70 = p.calcular_precio_venta(MargenGanancia.ESTANDAR)
        precio_100 = p.calcular_precio_venta(MargenGanancia.PREMIUM)
        print(f"  {p.nombre}")
        print(f"    Costo: ${p.precio_mayorista:,.0f} | "
              f"50%: ${precio_50:,.0f} | "
              f"70%: ${precio_70:,.0f} | "
              f"100%: ${precio_100:,.0f}")
    
    # Mostrar paquetes
    print("\n🎁 PAQUETES PREDEFINIDOS:\n")
    for pkg in PAQUETES_PREDEFINIDOS:
        print(f"  {pkg.nombre}: ${pkg.precio_sugerido:,.0f}")
        print(f"    {pkg.descripcion}")
    
    # Mostrar tiempos
    print(f"\n⏱️ TIEMPO DE ENTREGA: {TIEMPOS_ENTREGA.mensaje_cliente()}")
    
    # Mostrar zonas de envío
    print("\n🚚 ZONAS DE ENVÍO:\n")
    for zona in ZONAS_ENVIO:
        print(f"  {zona.nombre}: ${zona.costo_base:,.0f}")
