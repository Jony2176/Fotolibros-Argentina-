"""
Reglas del Editor de Fabrica de Fotolibros (FDF)
================================================

Este archivo contiene todas las reglas de diseño y configuración del editor
de FDF que el agente de automatización debe seguir.

Basado en la documentación oficial y mejores prácticas de diseño de fotolibros.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


# =============================================================================
# ESTRUCTURA DEL EDITOR
# =============================================================================

class PanelEditor(Enum):
    """Paneles disponibles en el editor FDF"""
    HERRAMIENTAS = "izquierda_vertical"      # Añadir QR, Texto, Cuadros de Color, Contenedores
    PESTANAS_DISENO = "lateral_izquierdo"    # Plantillas, Temas, Máscaras, Cliparts, Fondos, Bordes
    LIENZO_PRINCIPAL = "centro"               # Área de trabajo (Tapa/Contratapa o Doble Página)
    PROPIEDADES = "lateral_derecho"          # Fuentes, colores, tamaños, rotación
    NAVEGADOR_PAGINAS = "inferior"           # Miniaturas para saltar entre páginas
    BARRA_ACCION = "superior_derecha"        # Guardar, Comprar, Deshacer


class HerramientaEditor(Enum):
    """Herramientas disponibles en el panel izquierdo"""
    ANADIR_QR = "qr"
    TEXTO = "texto"
    CUADRO_COLOR = "color_box"
    CONTENEDOR_FOTO = "photo_container"


class PestanaDiseno(Enum):
    """Pestañas de diseño disponibles"""
    PLANTILLAS = "plantillas"
    TEMAS = "temas"
    MASCARAS = "mascaras"
    CLIPARTS = "cliparts"
    FONDOS = "fondos"
    BORDES = "bordes"


# =============================================================================
# ANATOMÍA DE LA TAPA
# =============================================================================

@dataclass
class ZonaTapa:
    """Zonas de la vista de Tapa/Contratapa"""
    nombre: str
    descripcion: str
    posicion_relativa: str  # izquierda, centro, derecha
    
ZONAS_TAPA = {
    "contratapa": ZonaTapa(
        nombre="Contratapa",
        descripcion="Zona IZQUIERDA del lienzo - parte trasera del libro",
        posicion_relativa="izquierda"
    ),
    "lomo": ZonaTapa(
        nombre="Lomo",
        descripcion="Franja CENTRAL entre las líneas punteadas - visible en el estante",
        posicion_relativa="centro"
    ),
    "portada": ZonaTapa(
        nombre="Portada",
        descripcion="Zona DERECHA del lienzo - cara principal del libro",
        posicion_relativa="derecha"
    )
}


# =============================================================================
# REGLAS DEL LOMO (Consejo Oficial FDF #2)
# =============================================================================

@dataclass
class ReglasLomo:
    """
    Reglas para el diseño del lomo del libro.
    
    CONSEJO OFICIAL FDF #2: Textos en el lomo del fotolibro
    "Cuando quieras colocar texto en el lomo del fotolibro tené presente ajustar 
    el tamaño de la tipografía para que no quede super apretadito en el área 
    punteada que delimita el lomo."
    """
    
    # Dimensiones físicas del lomo (en mm)
    perdida_por_lado_mm: float = 10.0  # El lomo "come" ~10mm de cada lado
    perdida_total_mm: float = 20.0     # Total de pérdida en la unión
    
    # Reglas de contenido
    prohibido_en_lomo: List[str] = field(default_factory=lambda: [
        "rostros",
        "caras",
        "texto importante",
        "elementos críticos",
        "logos",
        "información clave"
    ])
    
    permitido_en_lomo: List[str] = field(default_factory=lambda: [
        "fondos neutros",
        "cielos",
        "paisajes",
        "texturas uniformes",
        "colores sólidos"
    ])
    
    # CONSEJO FDF: Texto en el lomo
    regla_texto_lomo: str = (
        "Si ponés el texto muy grande y queda 'apretado' en el área del lomo, "
        "cuando encuadernemos tu fotolibro, el texto en el lomo podría quedar "
        "DESCENTRADO o DEMASIADO GRANDE extendiéndose a la tapa y contratapa."
    )
    
    # Instrucciones para texto en el lomo
    texto_lomo_instrucciones: List[str] = field(default_factory=lambda: [
        "1. Click en herramienta 'Texto'",
        "2. Doble click en el lomo para escribir",
        "3. En Panel Derecho, usar TIRADOR CIRCULAR sobre la caja de texto",
        "4. Rotar 90 grados (el texto se lee de abajo hacia arriba)",
        "5. Centrar manualmente entre las líneas punteadas",
        "6. IMPORTANTE: Ajustar tamaño de fuente para que NO quede apretado",
        "7. Dejar margen dentro del área punteada del lomo"
    ])
    
    # Errores comunes
    errores_comunes_lomo: List[str] = field(default_factory=lambda: [
        "Texto muy grande que queda 'apretado' en el área del lomo",
        "Texto que se extiende a la tapa o contratapa",
        "Texto descentrado por falta de margen",
        "No rotar el texto 90 grados"
    ])

REGLAS_LOMO = ReglasLomo()


# =============================================================================
# REGLAS DE DOBLE PÁGINA (Consejo Oficial FDF #3)
# =============================================================================

@dataclass
class ReglasDoblePagina:
    """
    Reglas para fotos que cruzan el lomo (doble página).
    
    CONSEJO OFICIAL FDF #3: Fotos a doble página
    "Cuando quieras poner una foto ocupando dos páginas, tené presente que lo que 
    quede justo en el medio, sobre el lomo del fotolibro, va a quedar OCULTO o CORTADO, 
    por la misma encuadernación del libro (que 'come' un poquito en el centro, 
    donde se unen las hojas)."
    """
    
    # Contenido apropiado para doble página
    contenido_ideal: List[str] = field(default_factory=lambda: [
        "paisajes amplios",
        "cielos",
        "playas",
        "montañas",
        "arquitectura sin personas",
        "texturas",
        "fondos abstractos"
    ])
    
    contenido_aceptable_con_ajuste: List[str] = field(default_factory=lambda: [
        "grupos de personas (desplazando motivo hacia un lado)",
        "escenas donde las personas están en los tercios laterales"
    ])
    
    contenido_prohibido: List[str] = field(default_factory=lambda: [
        "rostros centrados",
        "personas en el centro exacto",
        "texto importante cruzando el lomo",
        "elementos críticos en la zona central"
    ])
    
    # INSTRUCCIONES OFICIALES FDF para fotos a doble página con sujetos en el centro
    instrucciones_oficiales_fdf: List[str] = field(default_factory=lambda: [
        "1. Seleccioná la foto",
        "2. En las herramientas contextuales, seleccioná la LUPA y agrandá la imagen",
        "3. Luego DESPLAZALA utilizando la MANITO (aparece cuando tenés la foto seleccionada)",
        "4. Ubicar la parte principal de la foto LEJOS del lomo (centro del libro)",
        "5. El contenido importante debe quedar en los tercios laterales"
    ])
    
    # Instrucciones simplificadas
    instrucciones_ajuste: List[str] = field(default_factory=lambda: [
        "1. Si la foto tiene personas, DESPLAZAR el motivo hacia IZQUIERDA o DERECHA",
        "2. Usar 'Herramienta Mano/Manito' (aparece al hacer click en la foto)",
        "3. Usar 'Lupa' para agrandar la imagen si es necesario",
        "4. Arrastrar la imagen dentro del marco para mover el contenido",
        "5. El centro del libro NO debe tener rostros ni elementos importantes",
        "6. Verificar que los tercios laterales contengan lo importante"
    ])
    
    # Regla crítica oficial
    regla_critica: str = (
        "Cuando la foto que quieras usar en una doble página tenga los sujetos principales "
        "ubicados en el centro, seleccioná la foto, usá la LUPA para agrandarla, y luego "
        "DESPLAZALA con la MANITO para ubicar la parte principal de la foto LEJOS del lomo "
        "(centro del libro). Lo que quede en el medio quedará OCULTO o CORTADO."
    )
    
    # Qué pasa si no se sigue esta regla
    consecuencia_ignorar: str = (
        "Lo que quede justo en el medio, sobre el lomo del fotolibro, va a quedar "
        "OCULTO o CORTADO por la misma encuadernación del libro."
    )

REGLAS_DOBLE_PAGINA = ReglasDoblePagina()


# =============================================================================
# REGLAS DE MÁRGENES Y SANGRADO (Consejos Oficiales FDF #1 y #4)
# =============================================================================

@dataclass
class ReglasMargenes:
    """
    Reglas de márgenes y sangrado.
    
    CONSEJO OFICIAL FDF #1: Fotos hasta el borde de la página
    "Si querés que tus fotos ocupen toda la página o lleguen hasta el borde del papel, 
    asegurate de colocar la foto llegando hasta el LÍMITE DEL ÁREA DE IMPRESIÓN 
    (línea llena exterior)."
    
    CONSEJO OFICIAL FDF #4: Textos cerca de los bordes
    "Cuando ubiques un texto cerca de los bordes tené presente dejar un cierto 
    MARGEN DE SEGURIDAD para evitar que tu texto quede cortado."
    """
    
    sangrado_minimo_mm: float = 5.0      # Sangrado mínimo en todos los bordes
    margen_seguridad_mm: float = 10.0    # Distancia mínima para elementos importantes
    
    # LÍNEAS DEL EDITOR FDF
    linea_exterior_llena: str = "Límite del área de IMPRESIÓN - las fotos deben llegar hasta aquí"
    linea_interior_punteada: str = "Límite del área de DISEÑO - por donde se corta/dobla el papel"
    
    # Concepto de DEMASÍA (bleed)
    concepto_demasia: str = (
        "DEMASÍA: Es un área impresa adicional en los márgenes, que finalmente "
        "NO formará parte de la impresión visible. Se utiliza como 'margen de seguridad' "
        "cuando tenemos imágenes o fondos que se imprimirán 'al corte', es decir, "
        "que llegarán hasta el borde del papel."
    )
    
    # Regla para fotos al borde (Consejo #1)
    regla_fotos_al_borde: str = (
        "Para fotos que ocupen toda la página: colocar la foto llegando hasta el "
        "LÍMITE DEL ÁREA DE IMPRESIÓN (línea llena exterior). Si ubicás la foto solo "
        "hasta el límite del área de diseño (línea punteada interior) podría quedar "
        "una LÍNEA FINITA BLANCA sobre el borde en tu fotolibro impreso."
    )
    
    # Regla para textos cerca del borde (Consejo #4)
    regla_textos_borde: str = (
        "Las líneas punteadas delimitan por donde se DOBLARÁ el papel (tapas duras) "
        "o por donde se CORTARÁ el papel (tapas blandas y páginas interiores). "
        "NUNCA dejes un texto muy cerca de esa línea punteada para evitar que quede cortado."
    )
    
    descripcion: str = (
        "Dejar márgenes generosos (espacio en blanco) en los bordes "
        "para evitar cortes en la encuadernación."
    )
    
    elementos_afectados: List[str] = field(default_factory=lambda: [
        "textos cerca del borde",
        "rostros cerca del borde",
        "logos",
        "información importante",
        "códigos QR"
    ])
    
    # Errores comunes
    errores_comunes: List[str] = field(default_factory=lambda: [
        "Foto que no llega al borde exterior -> queda línea blanca",
        "Texto pegado a la línea punteada -> puede quedar cortado",
        "No considerar la demasía al diseñar",
        "Elementos importantes muy cerca del borde"
    ])

REGLAS_MARGENES = ReglasMargenes()


# =============================================================================
# HERRAMIENTAS DE MANIPULACIÓN DE FOTOS
# =============================================================================

@dataclass
class HerramientasFoto:
    """Herramientas para manipular fotos en el editor"""
    
    herramienta_mano: Dict = field(default_factory=lambda: {
        "nombre": "Herramienta Mano",
        "activacion": "Click en una foto ya colocada en el lienzo",
        "funcion": "Mover la imagen DENTRO de su marco/contenedor",
        "uso": "Permite ajustar qué parte de la foto se ve sin cambiar el tamaño del marco"
    })
    
    control_zoom: Dict = field(default_factory=lambda: {
        "nombre": "Control de Zoom",
        "ubicacion": "Panel derecho (slider/deslizador)",
        "funcion": "Ampliar o reducir la foto dentro del marco",
        "uso": "Permite hacer zoom in/out para mostrar más o menos de la foto"
    })
    
    rotacion: Dict = field(default_factory=lambda: {
        "nombre": "Tirador de Rotación",
        "ubicacion": "Tirador circular sobre la caja de texto/imagen seleccionada",
        "funcion": "Rotar el elemento seleccionado",
        "uso_tipico": "Rotar texto 90° para el lomo del libro"
    })

HERRAMIENTAS_FOTO = HerramientasFoto()


# =============================================================================
# ESTILOS DE DISEÑO
# =============================================================================

class EstiloDiseno(Enum):
    """Estilos de diseño disponibles"""
    SIN_DISENO = "sin_diseno"
    SOLO_FOTOS = "solo_fotos"
    MINIMALISTA = "minimalista"
    CLASICO = "clasico"
    DIVERTIDO = "divertido"
    PREMIUM = "premium"


@dataclass
class ConfiguracionEstilo:
    """Configuración de cada estilo de diseño"""
    id: str
    nombre: str
    descripcion: str
    usar_stickers: bool
    tipo_stickers: List[str]
    fondos_recomendados: List[str]
    casos_uso: List[str]
    
ESTILOS_DISPONIBLES = {
    EstiloDiseno.SIN_DISENO: ConfiguracionEstilo(
        id="sin_diseno",
        nombre="Sin Diseño",
        descripcion="Libro en blanco, sin fondos temáticos - solo las fotos",
        usar_stickers=False,
        tipo_stickers=[],
        fondos_recomendados=["blanco", "negro"],
        casos_uso=["cliente trae diseño propio", "diseño minimalista extremo"]
    ),
    EstiloDiseno.MINIMALISTA: ConfiguracionEstilo(
        id="minimalista",
        nombre="Minimalista",
        descripcion="Limpio, fondos blancos, 1 foto por página",
        usar_stickers=False,
        tipo_stickers=["lineas_finas_sutiles"],
        fondos_recomendados=["blanco", "gris_claro", "crema"],
        casos_uso=["portfolios", "arte", "arquitectura", "moda"]
    ),
    EstiloDiseno.CLASICO: ConfiguracionEstilo(
        id="clasico",
        nombre="Clásico",
        descripcion="Elegante, flores, ideal bodas/aniversarios",
        usar_stickers=True,
        tipo_stickers=["marcos_dorados", "esquinas_decorativas", "lineas_sutiles", "adornos_florales"],
        fondos_recomendados=["crema", "beige", "rosa_pastel", "dorado_suave"],
        casos_uso=["bodas", "aniversarios", "compromisos", "bautismos"]
    ),
    EstiloDiseno.DIVERTIDO: ConfiguracionEstilo(
        id="divertido",
        nombre="Divertido",
        descripcion="Colorido, collages, ideal cumpleaños/infantil",
        usar_stickers=True,
        tipo_stickers=["estrellas", "corazones", "globos", "confeti", "emojis"],
        fondos_recomendados=["colores_brillantes", "patrones", "degradados"],
        casos_uso=["cumpleaños", "fiestas_infantiles", "graduaciones", "vacaciones"]
    ),
    EstiloDiseno.PREMIUM: ConfiguracionEstilo(
        id="premium",
        nombre="Premium",
        descripcion="Lujo, sofisticado, ideal regalos especiales",
        usar_stickers=True,
        tipo_stickers=["elementos_dorados", "plateados", "marcos_elegantes", "flores_estilizadas"],
        fondos_recomendados=["negro", "dorado", "burdeos", "azul_marino"],
        casos_uso=["regalos_especiales", "aniversarios_importantes", "homenajes"]
    )
}


# =============================================================================
# REGLAS DE STICKERS
# =============================================================================

@dataclass
class ReglasStickers:
    """Reglas para el uso de stickers y adornos"""
    
    regla_principal: str = "NUNCA tapar rostros con stickers"
    
    ubicaciones_recomendadas: List[str] = field(default_factory=lambda: [
        "esquinas de la página",
        "espacios vacíos",
        "junto a los bordes",
        "debajo de fotos (como decoración)"
    ])
    
    cantidad_maxima_por_pagina: Dict[str, int] = field(default_factory=lambda: {
        "sin_diseno": 0,
        "minimalista": 1,
        "clasico": 3,
        "divertido": 5,
        "premium": 3
    })
    
    advertencias: List[str] = field(default_factory=lambda: [
        "No sobrecargar la página",
        "Mantener coherencia de estilo",
        "Los textos deben tener buen contraste",
        "No tapar información importante"
    ])

REGLAS_STICKERS = ReglasStickers()


# =============================================================================
# GESTIÓN DE FONDOS Y BORDES
# =============================================================================

@dataclass
class ConfiguracionFondos:
    """Configuración de fondos"""
    
    ubicacion_panel: str = "Pestaña 'Fondos'"
    
    opciones_aplicacion: List[str] = field(default_factory=lambda: [
        "Página izquierda",
        "Página derecha", 
        "Todo el libro"
    ])
    
    herramienta_gotero: str = (
        "Usar el GOTERO para copiar un color exacto de una de las fotografías"
    )
    
    tip_profesional: str = (
        "Elegir colores que complementen las fotos del cliente. "
        "El gotero permite extraer colores de las propias imágenes."
    )


@dataclass
class ConfiguracionBordes:
    """Configuración de bordes"""
    
    ubicacion_panel: str = "Pestaña 'Bordes'"
    borde_profesional_estandar: str = "blanco"
    grosores_tipicos_px: List[int] = field(default_factory=lambda: [0, 2, 5, 10, 15, 20])

FONDOS_CONFIG = ConfiguracionFondos()
BORDES_CONFIG = ConfiguracionBordes()


# =============================================================================
# PLANTILLAS (LAYOUTS)
# =============================================================================

@dataclass
class ConfiguracionPlantillas:
    """Configuración de plantillas/layouts"""
    
    ubicacion_panel: str = "Pestaña 'Plantillas'"
    
    instrucciones: List[str] = field(default_factory=lambda: [
        "1. Ir a pestaña 'Plantillas'",
        "2. Filtrar por número de fotos (ej. '4 fotos')",
        "3. Arrastrar la plantilla elegida a la página deseada"
    ])
    
    filtros_disponibles: List[str] = field(default_factory=lambda: [
        "1 foto",
        "2 fotos", 
        "3 fotos",
        "4 fotos",
        "5+ fotos",
        "collage"
    ])

PLANTILLAS_CONFIG = ConfiguracionPlantillas()


# =============================================================================
# CÓDIGOS QR
# =============================================================================

@dataclass
class ConfiguracionQR:
    """Configuración de códigos QR"""
    
    tamano_minimo_cm: float = 2.0  # 2x2 cm mínimo para asegurar lectura
    
    instrucciones: List[str] = field(default_factory=lambda: [
        "1. Seleccionar herramienta 'Añadir QR'",
        "2. Pegar URL (YouTube, Instagram, sitio web, etc.)",
        "3. El sistema genera el código imprimible",
        "4. Ajustar tamaño (mínimo 2x2 cm)",
        "5. Colocar en una esquina (típicamente en contratapa)"
    ])
    
    ubicaciones_recomendadas: List[str] = field(default_factory=lambda: [
        "esquina inferior de contratapa",
        "junto a información de contacto",
        "página final del libro"
    ])

QR_CONFIG = ConfiguracionQR()


# =============================================================================
# CATEGORÍAS DE TEMPLATES FDF
# =============================================================================

CATEGORIAS_TEMPLATES_FDF = {
    "TODOS": "Muestra todos los templates",
    "Anuarios": "Templates para anuarios escolares",
    "Vacío": "Template en blanco sin diseño",
    "Solo Fotos": "Templates minimalistas",
    "Colecciones": "Templates especiales",
    "Viajes": "Tema viajes/vacaciones",
    "Infantil": "Bebés y niños",
    "Bodas": "Templates elegantes para bodas",
    "Quince": "Quinceañeras",
    "Cumple y Aniversario": "Cumpleaños y aniversarios",
    "San Valentín": "Románticos",
    "Egresados": "Graduaciones",
    "Comunión": "Primera comunión",
    "Día del Padre": "Especial papás",
    "Día de la Madre": "Especial mamás"
}

# Mapeo de estilos del cliente a categorías FDF
MAPEO_ESTILO_A_CATEGORIA = {
    "sin_diseno": "Vacío",
    "solo_fotos": "Solo Fotos",
    "minimalista": "Solo Fotos",
    "clasico": "Bodas",  # O "Colecciones" dependiendo del evento
    "divertido": "Cumple y Aniversario",
    "premium": "Colecciones",
    "viaje": "Viajes",
    "infantil": "Infantil",
    "boda": "Bodas",
    "graduacion": "Egresados"
}


# =============================================================================
# REGLAS DE RESOLUCION
# =============================================================================

@dataclass
class ReglasResolucion:
    """Reglas de resolución de imágenes"""
    
    dpi_ideal: int = 170  # Para impresión HP Indigo
    dpi_minimo_aceptable: int = 150
    
    reglas: List[str] = field(default_factory=lambda: [
        "Fotos de alta resolución: usar a página completa o en slots grandes",
        "Fotos de baja resolución: usar en slots pequeños únicamente",
        "Evitar estirar fotos pequeñas a tamaños grandes",
        "Preferir recortar antes que estirar"
    ])

REGLAS_RESOLUCION = ReglasResolucion()


# =============================================================================
# REGLA DE GUARDADO
# =============================================================================

REGLA_GUARDADO = {
    "frecuencia": "Cada 5 minutos o tras finalizar cada doble página",
    "ubicacion_boton": "Barra superior derecha - botón 'Guardar'",
    "importancia": "CRITICO - Evitar pérdida de trabajo ante desconexiones o errores"
}


# =============================================================================
# VERSIONES DE TEMPLATES (RESELLERS)
# =============================================================================

@dataclass
class ReglasVersionesTemplate:
    """Reglas para selección de versiones de templates (importante para resellers)"""
    
    version_recomendada: str = "para Editores"
    sufijos_editores: List[str] = field(default_factory=lambda: ["- ED", "para Editores", "Editores"])
    sufijos_clientes: List[str] = field(default_factory=lambda: ["- CL", "para Clientes", "Clientes"])
    
    razon: str = (
        "Las versiones 'para Editores' NO incluyen el logo de FDF, "
        "permitiendo agregar marca propia. Las versiones 'para Clientes' "
        "tienen el logo de FDF visible."
    )
    
    regla_reseller: str = (
        "Como RESELLER, SIEMPRE usar versión 'para Editores' o '- ED'"
    )

REGLAS_VERSIONES = ReglasVersionesTemplate()


# =============================================================================
# MODOS DE RELLENO DE FOTOS
# =============================================================================

class ModoRellenoFotos(Enum):
    """
    Modos de relleno de fotos disponibles en FDF.
    Se seleccionan en la pantalla de templates, parte inferior derecha.
    """
    MANUAL = "manual"       # Control total - el agente/usuario coloca cada foto
    RAPIDO = "rapido"       # El sistema coloca fotos automáticamente (básico)
    SMART = "smart"         # El sistema usa IA para colocar fotos inteligentemente


@dataclass
class ConfiguracionModoRelleno:
    """Configuración de cada modo de relleno"""
    id: str
    nombre: str
    nombre_boton: str  # Texto exacto del botón en FDF
    descripcion: str
    cuando_usar: List[str]
    ventajas: List[str]
    desventajas: List[str]
    recomendado_para_agente: bool


MODOS_RELLENO_DISPONIBLES = {
    ModoRellenoFotos.MANUAL: ConfiguracionModoRelleno(
        id="manual",
        nombre="Relleno Manual",
        nombre_boton="Relleno fotos manual",
        descripcion="Control total sobre la colocación de cada foto. El agente/usuario decide dónde va cada imagen.",
        cuando_usar=[
            "Cuando se necesita control preciso sobre el diseño",
            "Para aplicar reglas específicas de composición",
            "Cuando hay fotos con requisitos especiales (doble página, portada)",
            "Para diseños personalizados según instrucciones del cliente"
        ],
        ventajas=[
            "Control total sobre cada foto",
            "Permite aplicar reglas de diseño profesional",
            "Ideal para evitar problemas con el lomo",
            "Permite personalización completa"
        ],
        desventajas=[
            "Más lento",
            "Requiere más trabajo del agente"
        ],
        recomendado_para_agente=True  # RECOMENDADO para nuestro agente
    ),
    ModoRellenoFotos.RAPIDO: ConfiguracionModoRelleno(
        id="rapido",
        nombre="Relleno Rápido",
        nombre_boton="Relleno fotos rápido",
        descripcion="El sistema coloca las fotos automáticamente de forma básica, siguiendo el orden de subida.",
        cuando_usar=[
            "Cuando hay prisa y no se necesita personalización",
            "Para libros simples sin requisitos especiales",
            "Como punto de partida para luego ajustar manualmente"
        ],
        ventajas=[
            "Muy rápido",
            "No requiere intervención"
        ],
        desventajas=[
            "No respeta reglas de diseño profesional",
            "Puede colocar rostros en el lomo",
            "Sin personalización",
            "Puede desperdiciar fotos buenas en posiciones malas"
        ],
        recomendado_para_agente=False
    ),
    ModoRellenoFotos.SMART: ConfiguracionModoRelleno(
        id="smart",
        nombre="Relleno Smart (IA de FDF)",
        nombre_boton="Relleno fotos smart",
        descripcion="El sistema de FDF usa su propia IA para colocar fotos de manera inteligente.",
        cuando_usar=[
            "Cuando se confía en la IA de FDF",
            "Para libros donde no se necesita control específico",
            "Como alternativa cuando el agente no puede completar el diseño"
        ],
        ventajas=[
            "Inteligente (usa IA de FDF)",
            "Considera calidad y composición de fotos",
            "Más rápido que manual"
        ],
        desventajas=[
            "No podemos controlar sus decisiones",
            "Puede no seguir nuestras reglas específicas",
            "Resultado impredecible"
        ],
        recomendado_para_agente=False  # Preferimos control total
    )
}


def get_modo_relleno_recomendado(estilo: str = None, cantidad_fotos: int = None) -> str:
    """
    Retorna el modo de relleno recomendado según el contexto.
    
    Por defecto siempre recomendamos MANUAL para tener control total.
    """
    # Por ahora siempre recomendamos manual para control total
    # En el futuro podríamos usar smart para casos específicos
    return ModoRellenoFotos.MANUAL.value


# Selectores de botones para cada modo
SELECTORES_MODO_RELLENO = {
    "manual": [
        "text=Relleno fotos manual",
        "button:has-text('manual')",
        "[data-mode='manual']"
    ],
    "rapido": [
        "text=Relleno fotos rápido",
        "button:has-text('rápido')",
        "[data-mode='rapido']"
    ],
    "smart": [
        "text=Relleno fotos smart",
        "button:has-text('smart')",
        "[data-mode='smart']"
    ]
}


# =============================================================================
# 4 CONSEJOS OFICIALES DE FÁBRICA DE FOTOLIBROS
# =============================================================================

CONSEJOS_OFICIALES_FDF = {
    1: {
        "titulo": "Fotos hasta el borde de la página",
        "descripcion": (
            "Si querés que tus fotos ocupen toda la página o lleguen hasta el borde del papel, "
            "asegurate de colocar la foto llegando hasta el LÍMITE DEL ÁREA DE IMPRESIÓN "
            "(línea llena exterior)."
        ),
        "problema_si_ignora": (
            "Si ubicás la foto solo hasta el límite del área de diseño (línea punteada interior) "
            "podría quedar una LÍNEA FINITA BLANCA sobre el borde en tu fotolibro impreso."
        ),
        "concepto_tecnico": "DEMASÍA (bleed)",
        "definicion_tecnica": (
            "Área impresa adicional en los márgenes que no formará parte de la impresión visible. "
            "Se usa como margen de seguridad para imágenes que llegan 'al corte' (hasta el borde)."
        ),
        "accion": "Extender fotos hasta la LÍNEA LLENA EXTERIOR (límite de impresión)"
    },
    2: {
        "titulo": "Textos en el lomo del fotolibro",
        "descripcion": (
            "Cuando quieras colocar texto en el lomo del fotolibro tené presente ajustar "
            "el tamaño de la tipografía para que NO quede super apretadito en el área "
            "punteada que delimita el lomo."
        ),
        "problema_si_ignora": (
            "Si ponés el texto muy grande y queda 'apretado' en el área del lomo, "
            "cuando encuadernemos tu fotolibro, el texto podría quedar DESCENTRADO "
            "o DEMASIADO GRANDE extendiéndose a la tapa y contratapa."
        ),
        "accion": "Reducir tamaño de fuente para dejar margen dentro del área del lomo"
    },
    3: {
        "titulo": "Fotos a doble página",
        "descripcion": (
            "Cuando quieras poner una foto ocupando dos páginas, tené presente que "
            "lo que quede justo en el medio, sobre el lomo del fotolibro, va a quedar "
            "OCULTO o CORTADO, por la misma encuadernación del libro "
            "(que 'come' un poquito en el centro, donde se unen las hojas)."
        ),
        "problema_si_ignora": (
            "Los sujetos principales (personas, rostros) quedarán CORTADOS por el lomo."
        ),
        "solucion_oficial": (
            "Cuando la foto tenga los sujetos principales ubicados en el centro: "
            "1) Seleccioná la foto, "
            "2) En herramientas contextuales seleccioná la LUPA y agrandá la imagen, "
            "3) Luego desplazala usando la MANITO para ubicar la parte principal "
            "de la foto LEJOS del lomo (centro del libro)."
        ),
        "accion": "Usar LUPA + MANITO para desplazar sujetos importantes lejos del centro"
    },
    4: {
        "titulo": "Textos cerca de los bordes",
        "descripcion": (
            "Cuando ubiques un texto cerca de los bordes tené presente dejar "
            "un cierto MARGEN DE SEGURIDAD para evitar que tu texto quede cortado."
        ),
        "problema_si_ignora": (
            "El texto puede quedar cortado al encuadernar el libro."
        ),
        "explicacion_tecnica": (
            "Las líneas punteadas delimitan por donde se DOBLARÁ el papel (tapas duras) "
            "o por donde se CORTARÁ el papel (tapas blandas y páginas interiores). "
            "Nunca dejes un texto muy cerca de esa línea punteada."
        ),
        "excepcion": "Excepto que quieras que se corte por decisión de diseño.",
        "accion": "Mantener textos alejados de las líneas punteadas"
    }
}


def get_consejos_fdf_as_text() -> str:
    """Retorna los 4 consejos oficiales de FDF como texto formateado."""
    text = """
================================================================================
4 CONSEJOS OFICIALES DE FÁBRICA DE FOTOLIBROS
================================================================================
"""
    for num, consejo in CONSEJOS_OFICIALES_FDF.items():
        text += f"""
CONSEJO #{num}: {consejo['titulo']}
{'-' * 60}
{consejo['descripcion']}

PROBLEMA SI SE IGNORA: {consejo.get('problema_si_ignora', 'N/A')}

ACCIÓN: {consejo['accion']}
"""
    return text


# =============================================================================
# FUNCIÓN DE UTILIDAD: Obtener reglas como texto
# =============================================================================

def get_all_rules_as_text() -> str:
    """
    Retorna todas las reglas como un texto formateado.
    Útil para incluir en prompts de LLM.
    """
    return f"""
================================================================================
REGLAS DEL EDITOR FDF - GUÍA COMPLETA
================================================================================

ESTRUCTURA DE LA TAPA:
- CONTRATAPA: Zona IZQUIERDA (parte trasera del libro)
- LOMO: Franja CENTRAL entre líneas punteadas
- PORTADA: Zona DERECHA (cara principal)

--------------------------------------------------------------------------------
REGLAS DEL LOMO:
--------------------------------------------------------------------------------
- El lomo "come" ~{REGLAS_LOMO.perdida_total_mm}mm total de la unión
- NUNCA colocar: {', '.join(REGLAS_LOMO.prohibido_en_lomo)}
- Permitido: {', '.join(REGLAS_LOMO.permitido_en_lomo)}

Para texto en el lomo:
{chr(10).join(REGLAS_LOMO.texto_lomo_instrucciones)}

--------------------------------------------------------------------------------
REGLAS DE DOBLE PÁGINA:
--------------------------------------------------------------------------------
{REGLAS_DOBLE_PAGINA.regla_critica}

Contenido ideal: {', '.join(REGLAS_DOBLE_PAGINA.contenido_ideal)}
PROHIBIDO: {', '.join(REGLAS_DOBLE_PAGINA.contenido_prohibido)}

Instrucciones de ajuste:
{chr(10).join(REGLAS_DOBLE_PAGINA.instrucciones_ajuste)}

--------------------------------------------------------------------------------
MÁRGENES DE SEGURIDAD:
--------------------------------------------------------------------------------
- Sangrado mínimo: {REGLAS_MARGENES.sangrado_minimo_mm}mm
- Margen de seguridad: {REGLAS_MARGENES.margen_seguridad_mm}mm
{REGLAS_MARGENES.descripcion}

--------------------------------------------------------------------------------
HERRAMIENTAS DE FOTO:
--------------------------------------------------------------------------------
- {HERRAMIENTAS_FOTO.herramienta_mano['nombre']}: {HERRAMIENTAS_FOTO.herramienta_mano['funcion']}
- {HERRAMIENTAS_FOTO.control_zoom['nombre']}: {HERRAMIENTAS_FOTO.control_zoom['funcion']}
- {HERRAMIENTAS_FOTO.rotacion['nombre']}: {HERRAMIENTAS_FOTO.rotacion['funcion']}

--------------------------------------------------------------------------------
STICKERS:
--------------------------------------------------------------------------------
Regla principal: {REGLAS_STICKERS.regla_principal}
Ubicaciones recomendadas: {', '.join(REGLAS_STICKERS.ubicaciones_recomendadas)}

--------------------------------------------------------------------------------
CÓDIGOS QR:
--------------------------------------------------------------------------------
Tamaño mínimo: {QR_CONFIG.tamano_minimo_cm}x{QR_CONFIG.tamano_minimo_cm} cm
{chr(10).join(QR_CONFIG.instrucciones)}

--------------------------------------------------------------------------------
GUARDADO:
--------------------------------------------------------------------------------
{REGLA_GUARDADO['frecuencia']}
{REGLA_GUARDADO['importancia']}

--------------------------------------------------------------------------------
VERSIONES DE TEMPLATES (RESELLERS):
--------------------------------------------------------------------------------
{REGLAS_VERSIONES.regla_reseller}
{REGLAS_VERSIONES.razon}
================================================================================
"""


# =============================================================================
# FUNCIÓN DE UTILIDAD: Validar diseño
# =============================================================================

def validar_diseno(
    tiene_rostros_en_lomo: bool = False,
    tiene_elementos_en_margen: bool = False,
    usa_version_editores: bool = True,
    stickers_tapan_rostros: bool = False
) -> Dict:
    """
    Valida un diseño contra las reglas.
    
    Returns:
        Dict con resultado de validación y problemas encontrados
    """
    problemas = []
    advertencias = []
    
    if tiene_rostros_en_lomo:
        problemas.append({
            "tipo": "critico",
            "mensaje": "Hay rostros en la zona del lomo - serán cortados al encuadernar",
            "solucion": "Usar Herramienta Mano para desplazar el motivo hacia un lado"
        })
    
    if tiene_elementos_en_margen:
        advertencias.append({
            "tipo": "advertencia", 
            "mensaje": "Hay elementos muy cerca del borde - podrían cortarse",
            "solucion": "Alejar elementos al menos 10mm del borde"
        })
    
    if not usa_version_editores:
        advertencias.append({
            "tipo": "advertencia",
            "mensaje": "No se está usando versión para Editores - tendrá logo de FDF",
            "solucion": "Seleccionar template con sufijo '- ED' o 'para Editores'"
        })
    
    if stickers_tapan_rostros:
        problemas.append({
            "tipo": "critico",
            "mensaje": "Hay stickers tapando rostros",
            "solucion": "Mover stickers a esquinas o espacios vacíos"
        })
    
    return {
        "valido": len(problemas) == 0,
        "problemas_criticos": problemas,
        "advertencias": advertencias,
        "puntuacion": 100 - (len(problemas) * 30) - (len(advertencias) * 10)
    }
