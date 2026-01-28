"""
Selectores CSS del Editor de Fábrica de Fotolibros
===================================================
Mapeados a partir de la exploración automatizada del editor.
Estos selectores se usan para la automatización con Browserbase.

NOTA: Estos selectores deben actualizarse si la gráfica modifica su editor.
Última actualización: 2026-01-18
"""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class SelectoresLogin:
    """Selectores de la página de login"""
    url: str = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
    
    input_email: str = "#email_log"
    input_password: str = "#clave_log"
    btn_login: str = "#bt_log"
    
    # Indicadores de login exitoso
    texto_exito: str = "text=Fotolibros"
    home_url: str = "https://online.fabricadefotolibros.com"


@dataclass
class SelectoresHome:
    """Selectores de la página principal del editor"""
    # Navegación por categorías
    categoria_fotolibros: str = "text=Fotolibros"
    categoria_calendarios: str = "text=Calendarios"
    categoria_otros: str = "text=Otros"
    
    # Lista de productos
    producto_item: str = ".product-item"
    producto_nombre: str = ".product-name"
    producto_precio: str = ".product-price"
    
    # Productos específicos por texto
    producto_21x21: str = "text=21 x 21"
    producto_29x29: str = "text=29 x 29"
    producto_41x29: str = "text=41 x 29"
    producto_21x15: str = "text=21 x 15"
    
    # Crear proyecto
    btn_crear_proyecto: str = "text=Crear Proyecto"
    btn_abrir_proyecto: str = "text=Abrir"


@dataclass
class SelectoresModalConfiguracion:
    """Selectores del modal de configuración inicial (antes del editor)"""
    # Intentamos ser muy genéricos para atrapar cualquier input de nombre
    input_nombre: str = "input[type='text'], input.form-control, .modal input, .popup input, input"
    btn_siguiente: str = "text=Siguiente, text=Continuar, text=Aceptar, .btn-next, .btn-continue, button:has-text('Crear'), button[type='submit']"
    selector_paginas: str = ".pages-selector, select[name='pages']"


@dataclass
class SelectoresEditor:
    """Selectores del editor de diseño"""
    # Canvas/Área de trabajo
    canvas: str = "#canvas, .canvas, .editor-canvas, #editor-container, .main-editor, .design-area, iframe, .working-area"
    pagina_actual: str = ".page-current, .current-page"
    paginas_lista: str = ".pages-list, .page-thumbnails"
    
    # Navegación de páginas
    btn_pagina_anterior: str = ".btn-prev-page, [aria-label='Anterior']"
    btn_pagina_siguiente: str = ".btn-next-page, [aria-label='Siguiente']"
    btn_agregar_pagina: str = ".btn-add-page, [aria-label='Agregar página']"
    
    # Herramientas de foto
    btn_agregar_foto: str = ".btn-add-photo, [aria-label='Agregar foto']"
    input_upload_foto: str = "input[type='file']"
    zona_drop_foto: str = ".photo-drop-zone, .drop-area"
    
    # Galería de fotos subidas
    galeria_fotos: str = ".photo-gallery, .uploaded-photos"
    foto_galeria_item: str = ".photo-item, .gallery-item"
    
    # Herramientas de texto
    btn_agregar_texto: str = ".btn-add-text, [aria-label='Agregar texto']"
    input_texto: str = ".text-input, [contenteditable='true']"
    
    # Herramientas de fondo
    btn_fondo: str = ".btn-background, [aria-label='Fondo']"
    selector_color_fondo: str = ".background-color-picker"
    fondos_predefinidos: str = ".background-presets"
    
    # Layouts predefinidos
    btn_layouts: str = ".btn-layouts, [aria-label='Diseños']"
    layout_1_foto: str = ".layout-1-photo"
    layout_2_fotos: str = ".layout-2-photos"
    layout_3_fotos: str = ".layout-3-photos"
    layout_4_fotos: str = ".layout-4-photos"
    layout_collage: str = ".layout-collage"
    
    # Elementos decorativos
    btn_stickers: str = ".btn-stickers, [aria-label='Stickers']"
    btn_marcos: str = ".btn-frames, [aria-label='Marcos']"
    btn_adornos: str = ".btn-decorations"
    
    # Texto en tapa
    input_titulo_tapa: str = "#cover-title, .cover-title-input"
    input_texto_lomo: str = "#spine-text, .spine-text-input"


@dataclass
class SelectoresConfiguracion:
    """Selectores de configuración del proyecto"""
    # Selector de páginas
    input_num_paginas: str = ".page-count-input"
    btn_paginas_mas: str = ".btn-pages-plus"
    btn_paginas_menos: str = ".btn-pages-minus"
    
    # Selector de formato/tamaño
    selector_formato: str = ".format-selector"
    selector_tapa: str = ".cover-type-selector"
    
    # Opciones de calidad
    selector_papel: str = ".paper-selector"


@dataclass
class SelectoresGuardar:
    """Selectores para guardar y enviar el proyecto"""
    btn_guardar: str = ".btn-save, [aria-label='Guardar']"
    btn_guardar_como: str = ".btn-save-as"
    
    input_nombre_proyecto: str = ".project-name-input"
    
    btn_vista_previa: str = ".btn-preview, [aria-label='Vista previa']"
    btn_enviar_produccion: str = ".btn-send, .btn-order, text=Enviar"
    
    # Confirmación de envío
    modal_confirmacion: str = ".modal-confirm, .confirmation-modal"
    btn_confirmar_envio: str = ".btn-confirm-send"
    btn_cancelar: str = ".btn-cancel"


@dataclass
class SelectoresCompletos:
    """Contenedor de todos los selectores"""
    login: SelectoresLogin
    home: SelectoresHome
    editor: SelectoresEditor
    configuracion: SelectoresConfiguracion
    guardar: SelectoresGuardar
    modal_config: SelectoresModalConfiguracion = None
    
    # Timeouts recomendados (en ms)
    timeout_carga_pagina: int = 30000
    timeout_accion: int = 5000
    timeout_upload: int = 60000
    
    # Delays recomendados (en ms)
    delay_entre_acciones: int = 500
    delay_despues_click: int = 1000
    delay_despues_upload: int = 2000


# Instancia por defecto
SELECTORES = SelectoresCompletos(
    login=SelectoresLogin(),
    home=SelectoresHome(),
    editor=SelectoresEditor(),
    configuracion=SelectoresConfiguracion(),
    guardar=SelectoresGuardar(),
    modal_config=SelectoresModalConfiguracion()  # New field
)


# ============================================================
# FUNCIONES HELPER
# ============================================================

def obtener_selector_producto(codigo_producto: str) -> str:
    """
    Dado un código de producto, devuelve el selector más apropiado.
    """
    mapeo = {
        # Cuadrados
        "CU-21x21-BLANDA": "text=21 x 21",
        "CU-21x21-DURA": "text=21 x 21",
        "CU-29x29-DURA": "text=29 x 29",
        "CU-29x29-CUERO": "text=29 x 29",
        
        # Apaisados
        "AP-21x15-BLANDA": "text=21 x 15",
        "AP-21x15-DURA": "text=21 x 15",
        "AP-28x22-DURA": "text=28 x 22",
        "AP-41x29-DURA": "text=41 x 29",
        "AP-41x29-CUERO": "text=41 x 29",
        
        # Verticales
        "VE-22x28-BLANDA": "text=22 x 28",
        "VE-22x28-DURA": "text=22 x 28",
        
        # Souvenir
        "SV-10x10-PACK12": "text=10 x 10",
    }
    
    return mapeo.get(codigo_producto, "text=21 x 21")


def obtener_selector_layout(fotos_por_pagina: int) -> str:
    """
    Devuelve el selector de layout según cantidad de fotos.
    """
    layouts = {
        1: SELECTORES.editor.layout_1_foto,
        2: SELECTORES.editor.layout_2_fotos,
        3: SELECTORES.editor.layout_3_fotos,
        4: SELECTORES.editor.layout_4_fotos,
    }
    
    return layouts.get(fotos_por_pagina, SELECTORES.editor.layout_2_fotos)


def obtener_selectores_texto(estilo: str) -> dict:
    """
    Devuelve configuración de texto según el estilo.
    """
    configuraciones = {
        "minimalista": {
            "mostrar_titulo": False,
            "mostrar_lomo": False,
        },
        "clasico": {
            "mostrar_titulo": True,
            "mostrar_lomo": True,
            "fuente": "Playfair Display",
            "tamaño": 52,
        },
        "divertido": {
            "mostrar_titulo": True,
            "mostrar_lomo": False,
            "fuente": "Fredoka One",
            "tamaño": 48,
        },
        "premium": {
            "mostrar_titulo": True,
            "mostrar_lomo": True,
            "fuente": "Cormorant Garamond",
            "tamaño": 56,
        },
    }
    
    return configuraciones.get(estilo, configuraciones["clasico"])
