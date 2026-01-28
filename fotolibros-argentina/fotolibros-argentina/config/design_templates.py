"""
Templates de Diseño para el Editor de Fábrica de Fotolibros
============================================================
Estos templates definen cómo el agente debe configurar cada estilo
de diseño en el editor online de la gráfica.

Cada template incluye:
- Configuración de tapa (portada)
- Configuración de interior (páginas)
- Selectores CSS del editor para automatización
"""

from typing import Optional, List
from dataclasses import dataclass, field
from enum import Enum


class EstiloFondo(Enum):
    NINGUNO = "ninguno"
    SOLIDO = "solido"
    GRADIENTE = "gradiente"
    IMAGEN = "imagen"


class LayoutPagina(Enum):
    UNA_FOTO = "1_foto"
    DOS_FOTOS_HORIZONTAL = "2_fotos_h"
    DOS_FOTOS_VERTICAL = "2_fotos_v"
    TRES_FOTOS = "3_fotos"
    CUATRO_FOTOS = "4_fotos"
    COLLAGE = "collage"


@dataclass
class ConfigTapa:
    """Configuración de la tapa/portada del fotolibro"""
    con_titulo: bool = True
    titulo_default: str = ""
    posicion_titulo: str = "centro"  # centro, arriba, abajo
    fuente_titulo: str = "Montserrat"
    tamanio_titulo: int = 48
    color_titulo: str = "#FFFFFF"
    
    con_texto_lomo: bool = False
    texto_lomo_default: str = ""
    
    con_fondo: bool = True
    estilo_fondo: EstiloFondo = EstiloFondo.SOLIDO
    color_fondo_primario: str = "#1a365d"
    color_fondo_secundario: str = "#d69e2e"  # Para gradientes
    
    con_foto_portada: bool = True
    foto_portada_opacidad: float = 1.0
    foto_portada_blur: int = 0


@dataclass
class ConfigInterior:
    """Configuración del interior del fotolibro"""
    fotos_por_pagina: int = 2
    layout_default: LayoutPagina = LayoutPagina.DOS_FOTOS_HORIZONTAL
    layouts_permitidos: List[LayoutPagina] = field(default_factory=list)
    
    con_fondo: bool = False
    color_fondo: str = "#FFFFFF"
    
    con_margenes: bool = True
    margen_px: int = 20
    
    con_bordes_foto: bool = False
    color_borde_foto: str = "#000000"
    grosor_borde_foto: int = 1
    
    con_sombras: bool = True
    
    con_etiquetas: bool = False
    fuente_etiqueta: str = "Open Sans"
    tamanio_etiqueta: int = 12
    
    con_adornos: bool = False
    tipo_adornos: str = "ninguno"  # ninguno, estrellas, corazones, flores
    
    con_qr: bool = False
    qr_posicion: str = "ultima_pagina"  # ultima_pagina, cada_10_paginas


@dataclass
class SelectoresEditor:
    """Selectores CSS del editor de Fábrica de Fotolibros para automatización"""
    # Selectores de navegación
    btn_nueva_pagina: str = ".btn-new-page"
    btn_agregar_foto: str = ".btn-add-photo"
    btn_agregar_texto: str = ".btn-add-text"
    btn_fondo: str = ".btn-background"
    btn_guardar: str = ".btn-save"
    btn_enviar: str = ".btn-send"
    
    # Selectores de herramientas
    input_titulo: str = "#cover-title"
    input_lomo: str = "#spine-text"
    selector_fuente: str = ".font-selector"
    selector_color: str = ".color-picker"
    selector_layout: str = ".layout-selector"
    
    # Selectores de contenido
    area_pagina: str = ".page-area"
    contenedor_fotos: str = ".photo-container"
    upload_input: str = "input[type='file']"


@dataclass
class DesignTemplate:
    """Template completo de diseño"""
    id: str
    nombre: str
    descripcion: str
    
    tapa: ConfigTapa
    interior: ConfigInterior
    selectores: SelectoresEditor = field(default_factory=SelectoresEditor)
    
    # Metadatos
    ideal_para: List[str] = field(default_factory=list)
    tiempo_estimado_minutos: int = 5


# ============================================================
# TEMPLATES PREDEFINIDOS
# ============================================================

# SIN DISEÑO - Libro completamente en blanco, solo fotos
TEMPLATE_SIN_DISENO = DesignTemplate(
    id="sin_diseno",
    nombre="Sin Diseño",
    descripcion="Libro en blanco. Solo tus fotos, sin fondos ni decoraciones.",
    tapa=ConfigTapa(
        con_titulo=False,
        con_texto_lomo=False,
        con_fondo=False,
        estilo_fondo=EstiloFondo.NINGUNO,
        color_fondo_primario="#FFFFFF",
        con_foto_portada=True,
        foto_portada_opacidad=1.0,
    ),
    interior=ConfigInterior(
        fotos_por_pagina=1,
        layout_default=LayoutPagina.UNA_FOTO,
        layouts_permitidos=[LayoutPagina.UNA_FOTO, LayoutPagina.DOS_FOTOS_HORIZONTAL],
        con_fondo=False,
        color_fondo="#FFFFFF",
        con_margenes=True,
        margen_px=30,
        con_bordes_foto=False,
        con_sombras=False,
        con_etiquetas=False,
        con_adornos=False,
        con_qr=False,
    ),
    ideal_para=["Solo Fotos", "Diseño Manual", "Portfolios", "Arte"],
    tiempo_estimado_minutos=2,
)

TEMPLATE_MINIMALISTA = DesignTemplate(
    id="minimalista",
    nombre="Minimalista",
    descripcion="Limpio y moderno. Deja que tus fotos hablen por sí solas.",
    tapa=ConfigTapa(
        con_titulo=False,
        con_texto_lomo=False,
        con_fondo=False,
        estilo_fondo=EstiloFondo.NINGUNO,
        con_foto_portada=True,
        foto_portada_opacidad=1.0,
    ),
    interior=ConfigInterior(
        fotos_por_pagina=1,
        layout_default=LayoutPagina.UNA_FOTO,
        layouts_permitidos=[LayoutPagina.UNA_FOTO, LayoutPagina.DOS_FOTOS_HORIZONTAL],
        con_fondo=False,
        color_fondo="#FFFFFF",
        con_margenes=True,
        margen_px=40,
        con_bordes_foto=False,
        con_sombras=False,
        con_etiquetas=False,
        con_adornos=False,
        con_qr=False,
    ),
    ideal_para=["Viajes", "Paisajes", "Arquitectura", "Portfolios"],
    tiempo_estimado_minutos=3,
)

TEMPLATE_CLASICO = DesignTemplate(
    id="clasico",
    nombre="Clásico",
    descripcion="Elegante y atemporal. Perfecto para momentos especiales.",
    tapa=ConfigTapa(
        con_titulo=True,
        titulo_default="Nuestros Recuerdos",
        posicion_titulo="centro",
        fuente_titulo="Playfair Display",
        tamanio_titulo=52,
        color_titulo="#FFFFFF",
        con_texto_lomo=True,
        texto_lomo_default="",
        con_fondo=True,
        estilo_fondo=EstiloFondo.SOLIDO,
        color_fondo_primario="#1a365d",
        con_foto_portada=True,
        foto_portada_opacidad=0.3,
    ),
    interior=ConfigInterior(
        fotos_por_pagina=2,
        layout_default=LayoutPagina.DOS_FOTOS_HORIZONTAL,
        layouts_permitidos=[
            LayoutPagina.UNA_FOTO,
            LayoutPagina.DOS_FOTOS_HORIZONTAL,
            LayoutPagina.DOS_FOTOS_VERTICAL,
        ],
        con_fondo=True,
        color_fondo="#FAF9F6",  # Crema suave
        con_margenes=True,
        margen_px=25,
        con_bordes_foto=False,
        con_sombras=True,
        con_etiquetas=True,
        fuente_etiqueta="Lora",
        tamanio_etiqueta=11,
        con_adornos=False,
        con_qr=False,
    ),
    ideal_para=["Bodas", "Graduaciones", "Aniversarios", "Familia"],
    tiempo_estimado_minutos=5,
)

TEMPLATE_DIVERTIDO = DesignTemplate(
    id="divertido",
    nombre="Divertido",
    descripcion="Colorido y alegre. Ideal para celebraciones.",
    tapa=ConfigTapa(
        con_titulo=True,
        titulo_default="¡Momentos Felices!",
        posicion_titulo="arriba",
        fuente_titulo="Fredoka One",
        tamanio_titulo=48,
        color_titulo="#FFFFFF",
        con_texto_lomo=False,
        con_fondo=True,
        estilo_fondo=EstiloFondo.GRADIENTE,
        color_fondo_primario="#ed8936",
        color_fondo_secundario="#38a169",
        con_foto_portada=True,
        foto_portada_opacidad=0.7,
    ),
    interior=ConfigInterior(
        fotos_por_pagina=3,
        layout_default=LayoutPagina.TRES_FOTOS,
        layouts_permitidos=[
            LayoutPagina.DOS_FOTOS_HORIZONTAL,
            LayoutPagina.TRES_FOTOS,
            LayoutPagina.CUATRO_FOTOS,
            LayoutPagina.COLLAGE,
        ],
        con_fondo=True,
        color_fondo="#FFF9E6",  # Amarillo muy suave
        con_margenes=True,
        margen_px=15,
        con_bordes_foto=True,
        color_borde_foto="#FFFFFF",
        grosor_borde_foto=3,
        con_sombras=True,
        con_etiquetas=True,
        fuente_etiqueta="Comic Neue",
        tamanio_etiqueta=14,
        con_adornos=True,
        tipo_adornos="estrellas",
        con_qr=True,
        qr_posicion="ultima_pagina",
    ),
    ideal_para=["Cumpleaños", "Bebés", "Mascotas", "Fiestas"],
    tiempo_estimado_minutos=7,
)

TEMPLATE_PREMIUM = DesignTemplate(
    id="premium",
    nombre="Premium",
    descripcion="Lujo y sofisticación. Para regalos inolvidables.",
    tapa=ConfigTapa(
        con_titulo=True,
        titulo_default="",
        posicion_titulo="abajo",
        fuente_titulo="Cormorant Garamond",
        tamanio_titulo=56,
        color_titulo="#C9A227",  # Dorado
        con_texto_lomo=True,
        texto_lomo_default="",
        con_fondo=True,
        estilo_fondo=EstiloFondo.GRADIENTE,
        color_fondo_primario="#2d3748",
        color_fondo_secundario="#1a202c",
        con_foto_portada=True,
        foto_portada_opacidad=0.5,
        foto_portada_blur=2,
    ),
    interior=ConfigInterior(
        fotos_por_pagina=1,
        layout_default=LayoutPagina.UNA_FOTO,
        layouts_permitidos=[
            LayoutPagina.UNA_FOTO,
            LayoutPagina.DOS_FOTOS_HORIZONTAL,
        ],
        con_fondo=True,
        color_fondo="#F5F5F0",  # Marfil
        con_margenes=True,
        margen_px=50,
        con_bordes_foto=True,
        color_borde_foto="#C9A227",  # Dorado
        grosor_borde_foto=1,
        con_sombras=True,
        con_etiquetas=True,
        fuente_etiqueta="Cormorant",
        tamanio_etiqueta=12,
        con_adornos=True,
        tipo_adornos="elegantes",
        con_qr=False,
    ),
    ideal_para=["Regalos", "Aniversarios", "Quinceañeras", "Empresas"],
    tiempo_estimado_minutos=6,
)


# Diccionario de acceso rápido
DESIGN_TEMPLATES = {
    "sin_diseno": TEMPLATE_SIN_DISENO,
    "solo_fotos": TEMPLATE_SIN_DISENO,  # Alias
    "minimalista": TEMPLATE_MINIMALISTA,
    "clasico": TEMPLATE_CLASICO,
    "divertido": TEMPLATE_DIVERTIDO,
    "premium": TEMPLATE_PREMIUM,
}


def get_template(estilo_id: str) -> Optional[DesignTemplate]:
    """Obtiene un template por su ID"""
    return DESIGN_TEMPLATES.get(estilo_id)


def calcular_paginas_necesarias(num_fotos: int, estilo_id: str) -> int:
    """Calcula cuántas páginas se necesitan según el estilo y cantidad de fotos"""
    template = get_template(estilo_id)
    if not template:
        return num_fotos  # Default: 1 foto por página
    
    fotos_por_pagina = template.interior.fotos_por_pagina
    paginas = (num_fotos + fotos_por_pagina - 1) // fotos_por_pagina
    
    # Mínimo 22 páginas, máximo 80
    return max(22, min(80, paginas * 2))  # *2 porque son hojas (2 páginas por hoja)
