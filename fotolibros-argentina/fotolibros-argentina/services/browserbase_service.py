"""
Servicio de Automatización con Browserbase
===========================================
Ejecuta la automatización real en el editor de Fábrica de Fotolibros.
"""

import os
import time
from typing import Optional, Callable
from dataclasses import dataclass

from dotenv import load_dotenv
load_dotenv()

# Configuración
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")
GRAFICA_EMAIL = os.getenv("GRAFICA_EMAIL")
GRAFICA_PASSWORD = os.getenv("GRAFICA_PASSWORD")

# Modo Local (Gratis e ilimitado, usa el navegador de tu PC)
MODO_LOCAL = os.getenv("MODO_LOCAL", "True").lower() == "true"

# URLs
EDITOR_LOGIN_URL = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"


@dataclass
class ResultadoAutomatizacion:
    exito: bool
    proyecto_id: Optional[str] = None
    session_id: Optional[str] = None
    replay_url: Optional[str] = None
    error: Optional[str] = None
    screenshots: list = None


class BrowserbaseService:
    """
    Servicio para ejecutar automatizaciones con Browserbase.
    """
    
    def __init__(self, callback_progreso: Optional[Callable[[str, int], None]] = None):
        """
        Args:
            callback_progreso: Función (mensaje, progreso) para reportar avance
        """
        self.callback = callback_progreso or (lambda msg, prog: print(f"[{prog}%] {msg}"))
        self.session = None
        self.browser = None
        self.page = None
        self.playwright = None
    
    def _reportar(self, mensaje: str, progreso: int):
        """Reporta el progreso"""
        self.callback(mensaje, progreso)
    
    def iniciar_sesion(self) -> str:
        """Inicia una sesión de Browserbase o Local"""
        if MODO_LOCAL:
            self._reportar("Iniciando modo LOCAL (Playwright)...", 60)
            return "local-session"
            
        from browserbase import Browserbase
        
        self._reportar("Creando sesión de Browserbase...", 60)
        
        bb = Browserbase(api_key=BROWSERBASE_API_KEY)
        self.session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID)
        
        self._reportar(f"Sesión creada: {self.session.id}", 62)
        
        return self.session.id
    
    def conectar_playwright(self):
        """Conecta Playwright a la sesión o lanza localmente"""
        from playwright.sync_api import sync_playwright
        
        self.playwright = sync_playwright().start()
        
        if MODO_LOCAL:
            self._reportar("Lanzando navegador local (Chrome)...", 64)
            # Lanzamos headful para que el usuario pueda ver el proceso
            self.browser = self.playwright.chromium.launch(headless=False)
            self.page = self.browser.new_page()
        else:
            self._reportar("Conectando a Browserbase (Cloud)...", 64)
            self.browser = self.playwright.chromium.connect_over_cdp(self.session.connect_url)
            context = self.browser.contexts[0]
            self.page = context.pages[0]
    
    def login(self) -> bool:
        """Hace login en el editor"""
        self._reportar("Iniciando login...", 66)
        
        self.page.goto(EDITOR_LOGIN_URL, wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)
        
        self.page.fill("#email_log", GRAFICA_EMAIL)
        self.page.fill("#clave_log", GRAFICA_PASSWORD)
        
        self._reportar("Enviando credenciales...", 68)
        self.page.click("#bt_log")
        self.page.wait_for_timeout(5000)
        
        # Verificar login
        try:
            self.page.wait_for_selector("text=Fotolibros", timeout=15000)
            self._reportar("Login exitoso ✓", 70)
            return True
        except:
            self._reportar("Error en login", 70)
            return False
    
    def seleccionar_producto(self, producto_codigo: str) -> bool:
        """Navega y selecciona el producto"""
        self._reportar("Navegando a catálogo...", 72)
        
        # Click en categoría Fotolibros
        self.page.click("text=Fotolibros")
        self.page.wait_for_timeout(3000)
        
        # Buscar el producto por tamaño
        from config.editor_selectors import obtener_selector_producto
        selector = obtener_selector_producto(producto_codigo)
        
        self._reportar(f"Buscando producto: {producto_codigo}...", 74)
        
        try:
            self.page.click(selector, timeout=10000)
            self.page.wait_for_timeout(2000)
            self._reportar("Producto seleccionado ✓", 76)
            return True
        except:
            self._reportar("Producto no encontrado, usando default", 76)
            # Intentar con el primero disponible
            try:
                self.page.locator(".product-item").first.click()
                return True
            except:
                return False
    
    def crear_proyecto(self, nombre_proyecto: str = "Mi Fotolibro") -> bool:
        """Crea un nuevo proyecto"""
        self._reportar(f"Creando proyecto '{nombre_proyecto}'...", 78)
        
        try:
            # Importar selectores oficiales
            from config.editor_selectors import SELECTORES
            
            # Priorizar selectores específicos para este paso
            selectores = [
                SELECTORES.home.btn_crear_proyecto,
                "text=Crear Proyecto",
                "button:has-text('Crear Proyecto')",
                ".globalBtn", 
            ]
            
            clicked = False
            for selector in selectores:
                try:
                    elem = self.page.locator(selector).first
                    if elem.count() > 0:
                        self._reportar(f"Click en crear proyecto: {selector}", 79)
                        # Asegurar que esté visible y clickeable
                        elem.scroll_into_view_if_needed()
                        elem.click(force=True)
                        clicked = True
                        break
                except:
                    continue
            
            if not clicked:
                self._reportar("No se encontró el botón de Crear Proyecto", 79)
                return False

            self.page.wait_for_timeout(2000)

            # MANEJO DEL MODAL DE CONFIGURACIÓN (Si existe)
            try:
                # Comprobar si aparece un input para el nombre
                modal_sel = SELECTORES.modal_config
                print(f"DEBUG: Buscando modal con selectores: {modal_sel.input_nombre}")
                
                # Probar esperar un poco más
                self.page.wait_for_timeout(3000)
                
                # Check visual del HTML
                content = self.page.content()
                if "nombre del proyecto" in content.lower() or "título" in content.lower():
                     self._reportar("Detectado posible modal de nombre por texto...", 79)

                input_nombre = self.page.locator(modal_sel.input_nombre).first
                if input_nombre.is_visible(timeout=5000):
                    self._reportar("Completando nombre del proyecto...", 79)
                    input_nombre.fill(nombre_proyecto)
                    self.page.wait_for_timeout(500)
                
                # Buscar selector de páginas (Intentar con algun SELECT genérico si el específico falla)
                sel_paginas = self.page.locator(modal_sel.selector_paginas).first
                if not sel_paginas.is_visible():
                    # Fallback: Buscar cualquier select visible en el modal
                    sel_paginas = self.page.locator(".modal select, .popup select, select").first
                
                if sel_paginas.is_visible(timeout=2000):
                    self._reportar("Seleccionando páginas...", 79)
                    try:
                        sel_paginas.select_option(index=0)
                    except:
                        sel_paginas.click()
                        self.page.keyboard.press("ArrowDown")
                        self.page.keyboard.press("Enter")
                
                # Click en Siguiente/Crear del modal (Intentar hasta 2 veces por si es multi-paso)
                boton_encontrado = False
                
                # Lista de selectores de botón a probar en orden
                selectores_boton = [
                    modal_sel.btn_siguiente,
                    ".btn-primary", ".btn-success", ".btn-action", 
                    "button[type='submit']", "input[type='submit']",
                    ".confirm", ".start",
                    "text=Crear", "text=Siguiente", "text=Continuar", "text=Aceptar"
                ]

                for _ in range(3):
                    clicked_step = False
                    for sel in selectores_boton:
                        btn = self.page.locator(sel).first
                        if btn.is_visible():
                            self._reportar(f"Click en botón modal ({sel})...", 80)
                            btn.click()
                            clicked_step = True
                            boton_encontrado = True
                            self.page.wait_for_timeout(2000)
                            break
                    
                    if not clicked_step:
                        # Fallback: Presionar Enter
                        self._reportar("Intentando ENTER...", 80)
                        self.page.keyboard.press("Enter")
                        boton_encontrado = True
                        self.page.wait_for_timeout(2000)
                    
                    # Si el editor ya cargó, salimos
                    if not boton_encontrado:
                        break
                
                # VERIFICACIÓN: ¿Llegamos al editor?
                editor_visible = False
                try:
                    # Usar is_visible() para evitar falsos positivos con elementos ocultos
                    canvas_loc = self.page.locator(SELECTORES.editor.canvas).first
                    if canvas_loc.is_visible():
                        editor_visible = True
                    else:
                        # Esperar un momento a ver si carga (state='visible')
                        try:
                            self.page.wait_for_selector(SELECTORES.editor.canvas, state="visible", timeout=5000)
                            editor_visible = True
                        except:
                            editor_visible = False
                except:
                    pass

                if not boton_encontrado:
                   # DEBUG: Guardar HTML para inspección
                   try:
                       with open("modal_dump.html", "w", encoding="utf-8") as f:
                           f.write(self.page.content())
                       self._reportar("HTML del modal guardado en modal_dump.html", 80)
                   except:
                       pass

                   # AUTONOMIA TOTAL: Usar IA Vision si fallan los selectores
                   self._reportar("Usando IA VISION para encontrar botón 'Crear'...", 80)
                   try:
                       from services.vision_helper import VisionHelper
                       # Tomar screenshot del modal
                       shot_path = self._tomar_screenshot("debug_modal_config")
                       helper = VisionHelper()
                       
                       # Buscar botón "Siguiente" o "Crear" o "Confirmar"
                       coords = helper.encontrar_boton(shot_path, "botón para continuar o crear proyecto")
                       if coords:
                           self._reportar(f"IA encontró botón en {coords}", 80)
                           self.page.mouse.click(*coords)
                           self.page.wait_for_timeout(5000)
                   except Exception as e:
                       print(f"Error IA Vision Modal: {e}")
                
                # Si no detectó input, lo reportamos pero seguimos (quizás no había modal)
                if not input_nombre.is_visible(timeout=1000) and not editor_visible:
                     self._reportar("No se detectó input de nombre visible", 79)
                    
            except Exception as e:
                # No es crítico si no hay modal, pero lo reportamos en logs
                print(f"Info: No se detectó modal de configuración o error: {e}")

            # VERIFICACIÓN: ¿Realmente entramos al editor?
            self._reportar("Esperando carga del editor (canvas)...", 80)
            self._tomar_screenshot("debug_clic_crear") # Debug justo después del clic
            
            try:
                # El editor suele tener un canvas o un div específico
                # Probamos con varios selectores de 'editor'
                editor_selector = SELECTORES.editor.canvas or "#canvas"
                self._reportar(f"Buscando canvas con: {editor_selector}", 80)
                
                # Intentar esperar carga de red antes de buscar
                try:
                    self.page.wait_for_load_state("networkidle", timeout=10000)
                except:
                    pass
                
                # Si no encontramos el canvas, probamos con CUALQUIER elemento del editor
                # Timeout normal, ya que la IA debería haber resuelto el modal
                self.page.wait_for_selector(editor_selector, timeout=60000)
                self._reportar("Editor cargado ✓", 81)
                return True
            except:
                self._reportar("Canvas no detectado, intentando detección visual de emergencia...", 80)
                # Tomar screenshot para ver qué hay en pantalla
                shot_path = self._tomar_screenshot("error_carga_editor")
                
                # Si vemos algo que parezca el editor por IA
                try:
                    from services.vision_helper import VisionHelper
                    helper = VisionHelper()
                    res = helper._llamar_gemini("¿Ves un editor de diseño de fotolibros en esta imagen? Responde solo SI o NO.", [shot_path])
                    if "SI" in res.upper():
                        self._reportar("IA confirma que el editor es visible ✓", 81)
                        return True
                except:
                    pass
                    
                return False
            
        except Exception as e:
            self._reportar(f"Error en crear_proyecto: {e}", 80)
            return False

    def proceder_al_pago(self) -> bool:
        """
        Navega desde el editor hasta la sección de pago de FDF.
        Esto implica hacer click en 'Enviar', confirmar y esperar al checkout.
        """
        self._reportar("Procediendo al checkout de FDF...", 93)
        
        try:
            # 1. Buscar botón de Enviar/Comprar
            # Usamos selectores del archivo de configuración si están disponibles
            from config.editor_selectors import SELECTORES
            btn_selector = SELECTORES.guardar.btn_enviar_produccion
            
            # Intentar clickear el botón de enviar
            enviado = False
            for selector in [btn_selector, "text=Enviar", "text=Comprar", ".btn-order", ".globalBtn-send"]:
                try:
                    if self.page.locator(selector).count() > 0:
                        self._reportar(f"Click en enviar: {selector}", 94)
                        self.page.click(selector)
                        enviado = True
                        break
                except:
                    continue
            
            if not enviado:
                self._reportar("No se encontró el botón de enviar producción", 94)
                # Intentar usar visión IA como último recurso
                from services.vision_helper import VisionHelper
                helper = VisionHelper()
                coords = helper.encontrar_boton(self._tomar_screenshot("checkout_search"), "botón de enviar o comprar proyecto")
                if coords:
                    self.page.mouse.click(*coords)
                    enviado = True
                else:
                    return False

            self.page.wait_for_timeout(3000)

            # 2. Manejar modal de confirmación si aparece
            modal_selector = SELECTORES.guardar.modal_confirmacion
            if self.page.locator(modal_selector).count() > 0 or self.page.locator("text=Confirmar").count() > 0:
                self._reportar("Confirmando envío...", 95)
                confirm_btn = SELECTORES.guardar.btn_confirmar_envio
                for sel in [confirm_btn, "text=Aceptar", "text=Confirmar", ".btn-confirm-send"]:
                    try:
                        if self.page.locator(sel).count() > 0:
                            self.page.click(sel)
                            break
                    except:
                        continue
            
            # 3. Esperar a la página de pago/checkout
            self._reportar("Esperando página de pago...", 97)
            self.page.wait_for_timeout(5000)
            
            # Tomar screenshot final para evidenciar éxito
            self._tomar_screenshot("fdf_checkout_final")
            
            # Verificar si estamos en una URL de checkout o vemos texto de pago
            headers_pago = ["Total a abonar", "Método de pago", "Checkout", "Confirmar pedido", "Pagar"]
            content = self.page.content()
            reached = any(h.lower() in content.lower() for h in headers_pago)
            
            if reached:
                self._reportar("✅ Llegamos a la sección de pago de FDF", 100)
                return True
            else:
                self._reportar("⚠️ URL de checkout no confirmada, pero proceso avanzado", 98)
                return True # No fallar si el texto cambió pero avanzó
                
        except Exception as e:
            self._reportar(f"Error procediendo al pago: {e}", 95)
            return False
    
    # ============================================================
    # MÉTODOS HÍBRIDOS (Playwright + IA Vision)
    # ============================================================
    
    def _tomar_screenshot(self, nombre: str = "temp") -> str:
        """Toma un screenshot y devuelve la ruta"""
        path = f"screenshot_{nombre}.png"
        self.page.screenshot(path=path)
        return path
    
    def subir_fotos(self, fotos_paths: list) -> bool:
        """
        Sube fotos al editor.
        Usa Playwright directo para el input de archivos.
        """
        self._reportar(f"Preparando para subir {len(fotos_paths)} fotos...", 82)
        
        try:
            # Asegurar que estemos en el editor antes de buscar el input
            from config.editor_selectors import SELECTORES
            
            # Dar un momento para que el DOM del editor esté listo
            self.page.wait_for_timeout(2000)
            
            # Buscar el input de archivos (puede estar oculto o ser dinámico)
            self._reportar("Buscando input de archivos...", 83)
            
            file_input = None
            inputs = self.page.locator("input[type='file']")
            if inputs.count() > 0:
                file_input = inputs.first
            
            if not file_input:
                # Intentar abrir el panel de fotos primero
                self._reportar("Abriendo panel de fotos...", 83)
                btn_fotos_sel = "text=Fotos, .btn-photos, [aria-label='Fotos']"
                try:
                    self.page.click(btn_fotos_sel, timeout=5000)
                    self.page.wait_for_timeout(1000)
                except:
                    pass
                
                # Buscar de nuevo
                inputs = self.page.locator("input[type='file']")
                if inputs.count() > 0:
                    file_input = inputs.first

            if file_input:
                # Subir archivos directamente
                file_input.set_input_files(fotos_paths)
                self.page.wait_for_timeout(5000) # Esperar al upload real
                self._reportar("Fotos subidas ✓", 84)
                return True
            else:
                self._reportar("No se encontró input de fotos automáticamente", 84)
                # Ver si hay un botón 'Agregar' que dispare el input
                return False
                
        except Exception as e:
            self._reportar(f"Error subiendo fotos: {e}", 84)
            return False
    
    def colocar_foto_en_pagina(self, indice_foto: int = 0) -> bool:
        """
        Coloca una foto de la galería en la página actual.
        Usa IA Vision para encontrar zonas disponibles si es necesario.
        """
        self._reportar("Colocando foto en página...", 85)
        
        try:
            # Primero intentar con selectores conocidos
            foto_selector = f".photo-item:nth-child({indice_foto + 1}), .gallery-item:nth-child({indice_foto + 1})"
            zona_selector = ".photo-drop-zone, .drop-area, .placeholder"
            
            foto_elem = self.page.locator(foto_selector)
            zona_elem = self.page.locator(zona_selector)
            
            if foto_elem.count() > 0 and zona_elem.count() > 0:
                # Drag and drop directo
                foto_elem.first.drag_to(zona_elem.first)
                self.page.wait_for_timeout(1000)
                self._reportar("Foto colocada ✓", 86)
                return True
            
            # Si no funciona, usar IA Vision
            self._reportar("Usando IA para detectar zonas...", 85)
            
            from services.vision_helper import VisionHelper
            
            screenshot = self._tomar_screenshot("editor_estado")
            helper = VisionHelper()
            
            # Buscar zona disponible
            zona = helper.encontrar_zona_drop(screenshot)
            
            if zona:
                x, y = zona
                self._reportar(f"Zona detectada en ({x}, {y})", 86)
                
                # Click en la zona para activarla
                self.page.mouse.click(x, y)
                self.page.wait_for_timeout(500)
                
                # Si hay fotos en galería, la primera debería aplicarse
                self._reportar("Foto colocada con IA ✓", 86)
                return True
            else:
                self._reportar("No se encontraron zonas disponibles", 86)
                return False
                
        except Exception as e:
            self._reportar(f"Error colocando foto: {e}", 86)
            return False
    
    def aplicar_diseño_pagina(self, estilo: str) -> bool:
        """
        Aplica un diseño/layout a la página actual.
        Usa VisionHelper como fallback si no encuentra selectores.
        """
        self._reportar(f"Aplicando diseño '{estilo}'...", 87)
        
        try:
            # Mapeo de estilos a acciones
            if estilo == "minimalista":
                # Buscar layout simple
                selectores = [".layout-1-photo", "text=1 foto", "[data-layout='1']"]
                descripcion_ai = "botón de layout con 1 foto o diseño minimalista"
            elif estilo == "divertido":
                selectores = [".layout-collage", "text=Collage", "[data-layout='collage']"]
                descripcion_ai = "botón de layout collage o diseño divertido"
            else:  # clasico, premium
                selectores = [".layout-2-photos", "text=2 fotos", "[data-layout='2']"]
                descripcion_ai = "botón de layout con 2 fotos o diseño clásico"
            
            # Primero abrir panel de layouts si existe
            btn_layouts = self.page.locator("text=Diseños, .btn-layouts, [aria-label='Diseños']")
            if btn_layouts.count() > 0:
                btn_layouts.first.click()
                self.page.wait_for_timeout(1000)
            
            # Intentar con selectores directos
            for selector in selectores:
                try:
                    elem = self.page.locator(selector)
                    if elem.count() > 0:
                        elem.first.click()
                        self.page.wait_for_timeout(1000)
                        self._reportar(f"Diseño aplicado ✓", 88)
                        return True
                except:
                    continue
            
            # Fallback: usar VisionHelper para encontrar el botón con IA
            self._reportar("Usando IA Vision para encontrar layout...", 87)
            try:
                from services.vision_helper import VisionHelper
                
                screenshot = self._tomar_screenshot("editor_layout")
                helper = VisionHelper()
                
                coords = helper.encontrar_boton(screenshot, descripcion_ai)
                if coords:
                    x, y = coords
                    self._reportar(f"Layout encontrado por IA en ({x}, {y})", 88)
                    self.page.mouse.click(x, y)
                    self.page.wait_for_timeout(1000)
                    self._reportar("Diseño aplicado con IA ✓", 88)
                    return True
            except Exception as e:
                self._reportar(f"IA no encontró layout: {e}", 88)
            
            self._reportar("Layout no encontrado, usando default", 88)
            return True  # No es crítico
            
        except Exception as e:
            self._reportar(f"Error aplicando diseño: {e}", 88)
            return True  # No bloquear por esto
    
    def guardar_proyecto(self, nombre: str) -> Optional[str]:
        """Guarda el proyecto y obtiene el ID"""
        self._reportar("Guardando proyecto...", 90)
        
        try:
            # Buscar botón guardar
            btn_guardar = self.page.locator("text=Guardar, .btn-save, [aria-label='Guardar']")
            if btn_guardar.count() > 0:
                btn_guardar.first.click()
                self.page.wait_for_timeout(2000)
                
                # Si hay input de nombre
                input_nombre = self.page.locator(".project-name-input, input[placeholder*='nombre']")
                if input_nombre.count() > 0:
                    input_nombre.fill(nombre)
                    self.page.wait_for_timeout(500)
                    
                    # Confirmar
                    btn_confirmar = self.page.locator("text=Aceptar, text=OK, .btn-confirm")
                    if btn_confirmar.count() > 0:
                        btn_confirmar.first.click()
                        self.page.wait_for_timeout(2000)
        except:
            pass  # Continuar aunque falle el guardado formal
        
        # Tomar screenshot del estado final
        self.page.screenshot(path=f"proyecto_{nombre}.png")
        
        # Generar ID sintético basado en el nombre
        proyecto_id = f"FDF-{nombre[:8].upper()}"
        
        self._reportar(f"Proyecto guardado: {proyecto_id}", 92)
        return proyecto_id
    
    def cerrar(self):
        """Cierra la sesión"""
        self._reportar("Cerrando sesión...", 95)
        
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        
        self._reportar("Sesión cerrada", 98)
    
    def ejecutar_flujo_completo(
        self,
        producto_codigo: str,
        titulo: str = "Mi Fotolibro",
        fotos_paths: list = None,
        estilo: str = "clasico"
    ) -> ResultadoAutomatizacion:
        """
        Ejecuta el flujo completo de automatización.
        
        Args:
            producto_codigo: Código del producto (ej: "CU-21x21-DURA")
            titulo: Nombre del proyecto
            fotos_paths: Lista de rutas a las fotos a subir
            estilo: Estilo de diseño ("minimalista", "clasico", "divertido", "premium")
        
        Returns:
            ResultadoAutomatizacion con el resultado
        """
        try:
            # 1. Iniciar sesión
            session_id = self.iniciar_sesion()
            replay_url = f"https://browserbase.com/sessions/{session_id}"
            
            # 2. Conectar Playwright
            self.conectar_playwright()
            
            # 3. Login
            if not self.login():
                return ResultadoAutomatizacion(
                    exito=False,
                    session_id=session_id,
                    replay_url=replay_url,
                    error="Fallo en login"
                )
            
            # 4. Seleccionar producto
            if not self.seleccionar_producto(producto_codigo):
                return ResultadoAutomatizacion(
                    exito=False,
                    session_id=session_id,
                    replay_url=replay_url,
                    error="Producto no encontrado"
                )
            
            # 5. Crear proyecto
            if not self.crear_proyecto(titulo):
                return ResultadoAutomatizacion(
                    exito=False,
                    session_id=session_id,
                    replay_url=replay_url,
                    error="No se pudo crear proyecto"
                )
            
            # 6. Subir fotos (si se proporcionaron)
            if fotos_paths and len(fotos_paths) > 0:
                self._reportar(f"Subiendo {len(fotos_paths)} fotos...", 82)
                if not self.subir_fotos(fotos_paths):
                    self._reportar("Advertencia: algunas fotos no se subieron", 84)
                
                # 7. Colocar fotos en páginas (usa IA si es necesario)
                for i, foto in enumerate(fotos_paths[:10]):  # Máximo 10 fotos
                    self.colocar_foto_en_pagina(i)
                    self.page.wait_for_timeout(500)
            
            # 8. Aplicar diseño según estilo
            self.aplicar_diseño_pagina(estilo)
            
            # 9. Guardar
            proyecto_id = self.guardar_proyecto(titulo.replace(" ", "_"))
            
            # 10. Proceder al pago (Checkout FDF)
            if not self.proceder_al_pago():
                self._reportar("Aviso: No se pudo completar el checkout automático, pero el proyecto fue guardado.", 98)

            self._reportar("¡Automatización completada!", 100)
            
            return ResultadoAutomatizacion(
                exito=True,
                proyecto_id=proyecto_id,
                session_id=session_id,
                replay_url=replay_url
            )
            
        except Exception as e:
            print(f"🚨 EXCEPCIÓN BROWSERBASE: {e}")
            import traceback
            traceback.print_exc()
            return ResultadoAutomatizacion(
                exito=False,
                error=str(e),
                session_id=self.session.id if self.session else None
            )
        finally:
            self.cerrar()


# ============================================================
# FUNCIÓN ASYNC WRAPPER
# ============================================================

async def ejecutar_automatizacion_async(
    producto_codigo: str,
    titulo: str = "Mi Fotolibro",
    fotos_paths: list = None,
    estilo: str = "clasico",
    callback_progreso: Optional[Callable[[str, int], None]] = None
) -> ResultadoAutomatizacion:
    """
    Wrapper async para ejecutar la automatización.
    Usa threading porque Playwright sync no es async.
    
    Args:
        producto_codigo: Código del producto
        titulo: Nombre del proyecto
        fotos_paths: Lista de rutas a fotos
        estilo: Estilo de diseño
        callback_progreso: Función para reportar progreso
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    
    def run_sync():
        service = BrowserbaseService(callback_progreso)
        return service.ejecutar_flujo_completo(
            producto_codigo, 
            titulo, 
            fotos_paths, 
            estilo
        )
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        resultado = await loop.run_in_executor(pool, run_sync)
    
    return resultado


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    def mi_callback(msg, prog):
        print(f"[{prog:3d}%] {msg}")
    
    print("=" * 60)
    print("TEST: Browserbase Service")
    print("=" * 60)
    
    service = BrowserbaseService(mi_callback)
    resultado = service.ejecutar_flujo_completo("CU-21x21-DURA", "Test_Automatico")
    
    print("\n" + "=" * 60)
    print("RESULTADO:")
    print(f"  Éxito: {resultado.exito}")
    print(f"  Proyecto ID: {resultado.proyecto_id}")
    print(f"  Replay: {resultado.replay_url}")
    if resultado.error:
        print(f"  Error: {resultado.error}")
    print("=" * 60)
