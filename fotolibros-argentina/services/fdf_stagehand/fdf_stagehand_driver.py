"""
FDF Stagehand Driver
====================
Implementacion HIBRIDA v2:
- Playwright directo para DOM (login, menus, uploads) - RAPIDO
- Gemini Vision para diseno inteligente del canvas - INTELIGENTE
- Pattern Cache para reducir llamadas a Vision (SQLite) - EFICIENTE
- Stagehand v3 wrapper para acciones self-healing - RESILIENTE

Con manejo robusto de errores y reintentos.

Arquitectura:
    ┌─────────────────────────────────────────────────────┐
    │              FDFStagehandToolkit                     │
    ├─────────────────────────────────────────────────────┤
    │  Playwright    │  Pattern Cache  │  Stagehand v3    │
    │  (DOM rapido)  │  (reduce 80%    │  (self-healing)  │
    │                │   Vision calls) │                  │
    └─────────────────────────────────────────────────────┘
"""

import asyncio
import os
from typing import Optional, List, Dict, Any
from playwright.async_api import async_playwright, Page, Browser

from .vision_designer import VisionDesigner
from .pattern_cache import FDFPatternCache, get_pattern_cache
from .stagehand_wrapper import FDFStagehandWrapper, FDFStagehandActions, STAGEHAND_AVAILABLE
from .error_handling import (
    logger, 
    retry_async, 
    with_retry,
    VisionFallback,
    RecoveryStrategy,
    LoginError,
    NavigationError,
    UploadError,
    EditorError,
    DragDropError,
    health_check
)

# URLs
EDITOR_LOGIN_URL = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"

# Configuración de reintentos
DEFAULT_RETRIES = 3
DEFAULT_DELAY = 1.0
DEFAULT_BACKOFF = 2.0


class FDFStagehandToolkit:
    """
    Toolkit hibrido v2: Playwright + Pattern Cache + Stagehand para FDF.
    
    Componentes:
    - Playwright: Login, navegacion, uploads (DOM estable, rapido)
    - Pattern Cache: Almacena coordenadas aprendidas (reduce 80% Vision calls)
    - Stagehand v3: Acciones self-healing para UI cambiante (opcional)
    - Vision Designer: Analisis visual inteligente (cuando no hay cache)
    
    Flujo de decision:
    1. Accion simple (login, menu) → Playwright directo
    2. Accion con coordenadas conocidas → Pattern Cache → Playwright
    3. Accion con coordenadas desconocidas → Vision → guardar en Cache → Playwright
    4. Accion fragil/cambiante → Stagehand self-healing
    """
    
    def __init__(
        self,
        model_api_key: str,
        fdf_email: str,
        fdf_password: str,
        model_name: str = "google/gemini-2.0-flash-001",
        headless: bool = False,
        cache_db_path: str = "data/fdf_patterns.db",
        use_stagehand: bool = True
    ):
        self.model_api_key = model_api_key
        self.fdf_email = fdf_email
        self.fdf_password = fdf_password
        self.model_name = model_name
        self.headless = headless
        self.use_stagehand = use_stagehand and STAGEHAND_AVAILABLE
        
        # Playwright directo
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        
        # Pattern Cache (NUEVO)
        self.cache = FDFPatternCache(cache_db_path)
        logger.info(f"[Toolkit] Pattern Cache inicializado en {cache_db_path}")
        
        # Stagehand Wrapper (NUEVO - lazy init)
        self._stagehand: Optional[FDFStagehandWrapper] = None
        self._stagehand_actions: Optional[FDFStagehandActions] = None
        
        # Estado
        self.logged_in = False
        self.current_product = None
        self.current_layout = None
        
        # Stats
        self._stats = {
            "cache_hits": 0,
            "cache_misses": 0,
            "vision_calls": 0,
            "stagehand_calls": 0,
            "playwright_calls": 0
        }
    
    async def _ensure_stagehand(self):
        """Inicializa Stagehand de forma lazy (solo cuando se necesita)"""
        if not self.use_stagehand:
            logger.warning("[Toolkit] Stagehand deshabilitado")
            return False
        
        if self._stagehand is None:
            try:
                self._stagehand = FDFStagehandWrapper(
                    model_name=self.model_name,
                    model_api_key=self.model_api_key,
                    headless=self.headless
                )
                await self._stagehand.start()
                self._stagehand_actions = FDFStagehandActions(self._stagehand)
                logger.info("[Toolkit] Stagehand inicializado (lazy)")
                return True
            except Exception as e:
                logger.error(f"[Toolkit] Error iniciando Stagehand: {e}")
                self._stagehand = None
                return False
        
        return True
    
    def get_stats(self) -> Dict:
        """Obtiene estadisticas de uso del toolkit"""
        cache_stats = self.cache.get_cache_stats()
        return {
            **self._stats,
            "cache": cache_stats,
            "stagehand_available": STAGEHAND_AVAILABLE,
            "stagehand_active": self._stagehand is not None
        }
    
    async def _ensure_browser(self):
        """Inicializa Playwright browser"""
        if self.browser:
            return
            
        print("[Stagehand] Iniciando browser...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--force-device-scale-factor=1"
            ]
        )
        
        # Viewport estándar, el zoom se aplica via CSS
        context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=1,
            no_viewport=False
        )
        self.page = await context.new_page()
        
        print("[Stagehand] Browser listo (1920x1080)")
    
    async def apply_zoom(self, zoom_level: float = 0.5):
        """
        Aplica zoom a la página para ver todo el contenido.
        zoom_level: 0.5 = 50%, 0.75 = 75%, etc.
        """
        await self._ensure_browser()
        
        try:
            width_percent = int(100 / zoom_level)
            # Usar transform scale para hacer zoom out y centrar
            await self.page.evaluate(f"""
                () => {{
                    document.body.style.transform = 'scale({zoom_level})';
                    document.body.style.transformOrigin = 'top left';
                    document.body.style.width = '{width_percent}%';
                    document.body.style.overflow = 'visible';
                }}
            """)
            print(f"[DOM] Zoom aplicado: {int(zoom_level * 100)}%")
            await asyncio.sleep(0.3)
            return {"success": True, "zoom": zoom_level}
        except Exception as e:
            print(f"[DOM] Error aplicando zoom: {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Cierra el browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
    
    # =========================================
    # HEALTH CHECK
    # =========================================
    
    async def health_check(self) -> Dict:
        """Verifica el estado del toolkit"""
        return await health_check(self)
    
    # =========================================
    # ACCIONES DOM (Playwright directo - rápido)
    # =========================================
    
    async def login(self, max_retries: int = DEFAULT_RETRIES) -> dict:
        """
        Login usando Playwright directo (DOM estable).
        Incluye reintentos automáticos.
        """
        await self._ensure_browser()
        
        async def _do_login():
            await self.page.goto(EDITOR_LOGIN_URL, timeout=30000)
            await asyncio.sleep(1)
            
            # Login form - selectores estables
            print("[DOM] Llenando formulario de login...")
            await self.page.fill('#email_log', self.fdf_email)
            await self.page.fill('#clave_log', self.fdf_password)
            await self.page.click('#bt_log')
            
            # Esperar que cargue el catálogo
            await self.page.wait_for_selector("text=Fotolibros", timeout=15000)
            
            self.logged_in = True
            logger.info("Login exitoso")
            return {"success": True, "message": "Login exitoso"}
        
        # Ejecutar con retry
        result = await with_retry(
            _do_login,
            max_attempts=max_retries,
            delay=DEFAULT_DELAY,
            backoff=DEFAULT_BACKOFF,
            error_message="Login a FDF"
        )
        
        if isinstance(result, dict) and not result.get("success"):
            logger.error(f"Login falló después de {max_retries} intentos")
        
        return result
    
    async def navigate_to_fotolibros(self, for_professionals: bool = True) -> dict:
        """
        Navega a la categoría de Fotolibros.
        
        IMPORTANTE: Como RESELLERS debemos usar la opción "Para Profesionales (sin logo de FDF)"
        para que los fotolibros no tengan el logo de FDF.
        
        Args:
            for_professionals: Si True, clickea "Para Profesionales" en lugar de "Fotolibros"
        """
        await self._ensure_browser()
        
        try:
            if for_professionals:
                # Para RESELLERS: Usar la opción "Para Profesionales (sin logo de FDF)"
                # Esta opción aparece después del login en la pantalla principal
                print("[DOM] Buscando opción 'Para Profesionales (sin logo de FDF)'...")
                
                # Selectores en orden de prioridad para la opción de profesionales
                professional_selectors = [
                    "text=Para Profesionales (sin logo de FDF)",
                    "text=Para Profesionales",
                    "text=sin logo de FDF",
                    "text=/Para\\s+Profesionales/i",
                    "text=/sin\\s+logo/i",
                    # Cards/divs que contengan el texto
                    "*:has-text('Para Profesionales (sin logo de FDF)')",
                    "*:has-text('sin logo de FDF')",
                ]
                
                clicked = False
                for selector in professional_selectors:
                    try:
                        locator = self.page.locator(selector).first
                        if await locator.count() > 0 and await locator.is_visible(timeout=2000):
                            await locator.click(force=True, timeout=5000)
                            print(f"[DOM] Clickeado: {selector}")
                            clicked = True
                            break
                    except:
                        continue
                
                if not clicked:
                    # Fallback: Intentar con JavaScript para encontrar la card correcta
                    print("[DOM] Intentando click con JavaScript...")
                    result = await self.page.evaluate("""
                        () => {
                            const elements = document.querySelectorAll('*');
                            for (const el of elements) {
                                const text = el.textContent || '';
                                if (text.includes('Para Profesionales') && text.includes('sin logo')) {
                                    const rect = el.getBoundingClientRect();
                                    if (rect.width > 100 && rect.width < 500 && rect.height > 50) {
                                        return {
                                            found: true,
                                            x: rect.x + rect.width / 2,
                                            y: rect.y + rect.height / 2
                                        };
                                    }
                                }
                            }
                            return { found: false };
                        }
                    """)
                    
                    if result and result.get("found"):
                        await self.page.mouse.click(result["x"], result["y"])
                        print(f"[DOM] Clickeado via JS en ({result['x']:.0f}, {result['y']:.0f})")
                        clicked = True
                
                if not clicked:
                    print("[DOM] ADVERTENCIA: No se encontró 'Para Profesionales', usando fallback 'Fotolibros'")
                    await self.page.click("text=Fotolibros")
            else:
                # Opción normal (con logo de FDF)
                print("[DOM] Clickeando categoría Fotolibros...")
                await self.page.click("text=Fotolibros")
            
            await asyncio.sleep(2)
            
            # Verificar que cargaron los productos
            content = await self.page.content()
            if "21x21" in content or "21 x 21" in content or "Tapa" in content:
                print("[DOM] Productos de fotolibros cargados")
                return {"success": True, "message": "En categoría Fotolibros (Profesionales)"}
            
            return {"success": True, "message": "Navegación completada"}
            
        except Exception as e:
            print(f"[DOM] Error navegando: {e}")
            return {"success": False, "error": str(e)}
    
    async def explore_product_catalog(self) -> dict:
        """
        Explora el catálogo de productos haciendo scroll para ver todos los formatos.
        Retorna información sobre los productos encontrados.
        """
        await self._ensure_browser()
        
        try:
            print("[DOM] Explorando catálogo de productos...")
            
            # Scroll al inicio
            await self.scroll_page("top")
            await asyncio.sleep(0.5)
            
            products_found = []
            
            # Hacer scroll y buscar productos
            for i in range(5):  # Máximo 5 scrolls
                # Buscar productos visibles
                product_elements = await self.page.query_selector_all("[class*='product'], [class*='item'], h4, h5")
                
                for el in product_elements:
                    try:
                        text = await el.text_content()
                        if text and ("Fotolibro" in text or "x" in text) and text not in products_found:
                            products_found.append(text.strip())
                    except:
                        continue
                
                # Verificar si hay más contenido abajo
                scroll_info = await self.get_scroll_info()
                if not scroll_info.get("info", {}).get("canScrollDown"):
                    break
                
                await self.scroll_page("down", 400)
                await asyncio.sleep(0.5)
            
            # Volver al inicio
            await self.scroll_page("top")
            
            print(f"[DOM] Productos encontrados: {len(products_found)}")
            for p in products_found[:10]:
                print(f"    - {p[:50]}")
            
            return {"success": True, "products": products_found, "count": len(products_found)}
            
        except Exception as e:
            print(f"[DOM] Error explorando catálogo: {e}")
            return {"success": False, "error": str(e)}
    
    async def select_product_by_text(self, product_text: str) -> dict:
        """Selecciona un producto buscando por texto"""
        await self._ensure_browser()
        
        try:
            # Buscar producto por texto parcial
            selectors = [
                f"text=/{product_text}/i",
                f"img[alt*='{product_text}']",
                f".product-item:has-text('{product_text}')",
                f"[data-product*='{product_text}']"
            ]
            
            for selector in selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        print(f"[DOM] Encontrado producto con: {selector}")
                        await self.page.click(selector, timeout=5000)
                        await asyncio.sleep(2)
                        self.current_product = product_text
                        return {"success": True, "product": product_text}
                except:
                    continue
            
            # Fallback: buscar cualquier elemento que contenga el texto
            elements = await self.page.query_selector_all(f"*:has-text('{product_text}')")
            for el in elements[:3]:  # Intentar los primeros 3
                try:
                    await el.click()
                    await asyncio.sleep(2)
                    return {"success": True, "product": product_text, "method": "fallback"}
                except:
                    continue
            
            return {"success": False, "error": f"Producto '{product_text}' no encontrado"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def click_create_project(self, project_title: str = "Mi Fotolibro", pages: int = 24) -> dict:
        """
        Maneja el modal de configuración del producto:
        1. Espera que aparezca el modal de config
        2. Llena el título (obligatorio)
        3. Selecciona la cantidad de páginas (dropdown)
        4. Clickea Crear Proyecto
        
        Args:
            project_title: Título del proyecto
            pages: Cantidad de páginas del libro (por defecto 24, opciones típicas: 24, 30, 40, 50, etc.)
        """
        await self._ensure_browser()
        
        try:
            # Esperar a que cargue el modal de configuración
            await asyncio.sleep(2)
            
            # Verificar si hay un campo de título visible (indica que estamos en el modal)
            # El campo tiene un label "Título" y muestra "Este campo es obligatorio"
            
            # Buscar el input de título - en FDF está después del label "Título"
            print("[DOM] Buscando campo de título...")
            
            # Método 1: Buscar input directamente debajo del texto "Título"
            title_filled = False
            
            try:
                # El input está justo después del label "Título"
                # Usar JavaScript para encontrarlo
                title_input = await self.page.evaluate("""
                    () => {
                        // Buscar el label que contiene "Título"
                        const labels = document.querySelectorAll('label, span, div');
                        for (let label of labels) {
                            if (label.textContent.trim() === 'Título') {
                                // Buscar el siguiente input
                                let parent = label.parentElement;
                                let input = parent.querySelector('input');
                                if (input) return true;
                                
                                // O buscar el siguiente hermano
                                let sibling = label.nextElementSibling;
                                while (sibling) {
                                    if (sibling.tagName === 'INPUT') return true;
                                    input = sibling.querySelector('input');
                                    if (input) return true;
                                    sibling = sibling.nextElementSibling;
                                }
                            }
                        }
                        return false;
                    }
                """)
            except:
                pass
            
            # Método 2: Buscar cualquier input de texto visible en el área del formulario
            try:
                # Buscar todos los inputs visibles
                inputs = await self.page.query_selector_all("input[type='text'], input:not([type])")
                for inp in inputs:
                    if await inp.is_visible():
                        # Verificar que no sea un campo de búsqueda
                        placeholder = await inp.get_attribute("placeholder") or ""
                        name = await inp.get_attribute("name") or ""
                        if "buscar" not in placeholder.lower() and "search" not in name.lower():
                            await inp.fill(project_title)
                            title_filled = True
                            print(f"[DOM] Título '{project_title}' escrito en input visible")
                            break
            except Exception as e:
                print(f"[DOM] Error buscando input: {e}")
            
            if not title_filled:
                print("[DOM] ADVERTENCIA: No se pudo llenar el título")
            
            await asyncio.sleep(0.5)
            
            # =============================================
            # SELECCIONAR CANTIDAD DE PÁGINAS (dropdown)
            # =============================================
            pages_selected = False
            if pages != 24:  # Solo cambiar si no es el valor por defecto
                print(f"[DOM] Seleccionando cantidad de páginas: {pages}")
                
                # Selectores para el dropdown de páginas
                pages_selectors = [
                    "select[name*='pagina']",
                    "select[name*='page']",
                    "select[id*='pagina']",
                    "select[id*='page']",
                    "select:near(:text('páginas'))",
                    "select:near(:text('paginas'))",
                    ".pages-select",
                    "[data-field='pages'] select",
                ]
                
                for selector in pages_selectors:
                    try:
                        locator = self.page.locator(selector).first
                        if await locator.count() > 0 and await locator.is_visible():
                            # Seleccionar la opción por valor o texto
                            await locator.select_option(str(pages))
                            pages_selected = True
                            print(f"[DOM] Páginas seleccionadas: {pages}")
                            break
                    except Exception as e:
                        continue
                
                # Método alternativo: buscar dropdown via JavaScript
                if not pages_selected:
                    try:
                        result = await self.page.evaluate(f"""
                            () => {{
                                // Buscar cualquier select que contenga opciones de páginas
                                const selects = document.querySelectorAll('select');
                                for (let select of selects) {{
                                    const options = select.querySelectorAll('option');
                                    for (let opt of options) {{
                                        if (opt.value === '{pages}' || opt.textContent.includes('{pages}')) {{
                                            select.value = opt.value;
                                            select.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                            return true;
                                        }}
                                    }}
                                }}
                                return false;
                            }}
                        """)
                        if result:
                            pages_selected = True
                            print(f"[DOM] Páginas seleccionadas via JS: {pages}")
                    except:
                        pass
                
                if not pages_selected:
                    print(f"[DOM] ADVERTENCIA: No se pudo cambiar a {pages} páginas, usando valor por defecto")
            else:
                print(f"[DOM] Usando páginas por defecto: {pages}")
                pages_selected = True
            
            await asyncio.sleep(0.5)
            
            # =============================================
            # CLICKEAR CREAR PROYECTO
            # =============================================
            # El botón está en la parte inferior del modal
            selectors = [
                "button:has-text('Crear Proyecto')",
                "text=Crear Proyecto",
                "button:has-text('Crear')",
                ".globalBtn:has-text('Crear')",
                "[data-action='create']"
            ]
            
            for selector in selectors:
                try:
                    locator = self.page.locator(selector)
                    if await locator.count() > 0:
                        # Si hay múltiples, tomar el último (el del modal)
                        if await locator.count() > 1:
                            await locator.last.click(timeout=5000)
                        else:
                            await locator.click(timeout=5000)
                        print(f"[DOM] Clickeando: {selector}")
                        await asyncio.sleep(3)  # El editor tarda en cargar
                        return {
                            "success": True, 
                            "message": "Crear Proyecto clickeado", 
                            "title": project_title, 
                            "title_filled": title_filled,
                            "pages": pages,
                            "pages_selected": pages_selected
                        }
                except Exception as e:
                    print(f"[DOM] Error con selector {selector}: {e}")
                    continue
            
            return {"success": False, "error": "Botón Crear Proyecto no encontrado"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def fill_project_title(self, title: str) -> dict:
        """Llena el campo de título del proyecto"""
        await self._ensure_browser()
        
        try:
            # Buscar campo de título
            selectors = [
                "input[name='title']",
                "input[name='titulo']",
                "#title",
                "#titulo",
                "input[placeholder*='título']",
                "input[placeholder*='nombre']"
            ]
            
            for selector in selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.fill(selector, title)
                        print(f"[DOM] Título escrito en: {selector}")
                        return {"success": True, "title": title}
                except:
                    continue
            
            # Fallback: buscar cualquier input visible
            inputs = await self.page.query_selector_all("input[type='text']:visible")
            if inputs:
                await inputs[0].fill(title)
                return {"success": True, "title": title, "method": "fallback"}
            
            return {"success": False, "error": "Campo de título no encontrado"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def select_photo_source(self, source: str = "computadora") -> dict:
        """
        Selecciona la fuente de fotos en la pantalla de selección.
        Opciones: computadora, celular, proyectos, facebook, instagram, google, dropbox
        """
        await self._ensure_browser()
        
        try:
            print(f"[DOM] Seleccionando fuente de fotos: {source}")
            await asyncio.sleep(1)  # Esperar que cargue la UI
            
            source_map = {
                "computadora": ["text=Desde computador", "text=computador"],
                "celular": ["text=Desde otro celular", "text=celular"],
                "proyectos": ["text=Mis proyectos"],
                "facebook": ["text=Facebook"],
                "instagram": ["text=Instagram"],
                "google": ["text=Google Photos"],
                "dropbox": ["text=Dropbox"]
            }
            
            selectors = source_map.get(source, source_map["computadora"])
            
            for selector in selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0:
                        # Usar force=True para evitar problemas de overlay
                        await locator.click(force=True, timeout=5000)
                        print(f"[DOM] Fuente '{source}' seleccionada con: {selector}")
                        await asyncio.sleep(1)
                        return {"success": True, "source": source}
                except Exception as e:
                    print(f"[DOM] Selector {selector} falló: {e}")
                    continue
            
            # Fallback: buscar por icono de computadora
            try:
                await self.page.click("svg >> nth=0", force=True, timeout=3000)
                print(f"[DOM] Fuente seleccionada via icono")
                return {"success": True, "source": source, "method": "icon"}
            except:
                pass
            
            return {"success": False, "error": "No se pudo seleccionar fuente"}
            
        except Exception as e:
            print(f"[DOM] Error seleccionando fuente: {e}")
            return {"success": False, "error": str(e)}
    
    async def upload_photos(self, photo_paths: List[str]) -> dict:
        """
        Sube fotos al editor.
        Si estamos en la pantalla de selección de fuente, primero selecciona "Desde computadora".
        """
        await self._ensure_browser()
        
        try:
            print(f"[DOM] Intentando subir {len(photo_paths)} fotos...")
            
            # Verificar si estamos en la pantalla de selección de fuente
            content = await self.page.content()
            if "dónde tomar las fotos" in content or "Desde computador" in content:
                print("[DOM] Detectada pantalla de selección de fuente")
                await self.select_photo_source("computadora")
                await asyncio.sleep(2)
            
            # Buscar input file (puede estar oculto)
            file_inputs = await self.page.query_selector_all("input[type='file']")
            
            if not file_inputs:
                # Intentar clickear botón de agregar fotos primero
                upload_selectors = [
                    "text=Agregar fotos",
                    "text=Subir fotos", 
                    "text=Añadir fotos",
                    "text=Seleccionar archivos",
                    "text=Elegir archivos",
                    ".upload-btn",
                    "[data-action='upload']"
                ]
                
                for selector in upload_selectors:
                    try:
                        if await self.page.locator(selector).count() > 0:
                            await self.page.click(selector, force=True, timeout=3000)
                            print(f"[DOM] Clickeado: {selector}")
                            await asyncio.sleep(1)
                            break
                    except:
                        continue
                
                # Buscar de nuevo el input file
                file_inputs = await self.page.query_selector_all("input[type='file']")
            
            if file_inputs:
                # Verificar si el input acepta múltiples archivos
                file_input = file_inputs[0]
                is_multiple = await file_input.get_attribute("multiple")
                
                if is_multiple:
                    # Subir todos los archivos de una vez
                    await file_input.set_input_files(photo_paths)
                    print(f"[DOM] {len(photo_paths)} archivos subidos de una vez")
                else:
                    # Subir uno por uno
                    print(f"[DOM] Input no acepta múltiples - subiendo de a uno...")
                    uploaded = 0
                    for photo_path in photo_paths:
                        try:
                            # Buscar input fresco cada vez
                            file_input = await self.page.query_selector("input[type='file']")
                            if file_input:
                                await file_input.set_input_files(photo_path)
                                uploaded += 1
                                print(f"[DOM] Foto {uploaded}/{len(photo_paths)} subida")
                                await asyncio.sleep(2)  # Esperar procesamiento
                        except Exception as e:
                            print(f"[DOM] Error subiendo foto: {e}")
                            break
                    
                    print(f"[DOM] Total subidas: {uploaded}")
                
                # Esperar procesamiento
                wait_time = min(3 + len(photo_paths) * 2, 20)
                print(f"[DOM] Esperando {wait_time}s para procesamiento...")
                await asyncio.sleep(wait_time)
                
                # Verificar si hay miniaturas cargadas
                thumbnails = await self.page.query_selector_all(".photo-thumb, .thumbnail, .uploaded-photo, .foto-item, img[src*='thumb'], img[src*='upload'], img[src*='blob']")
                print(f"[DOM] Miniaturas encontradas: {len(thumbnails)}")
                
                return {
                    "success": True, 
                    "photos_uploaded": len(photo_paths),
                    "thumbnails_found": len(thumbnails)
                }
            
            return {"success": False, "error": "Input de archivos no encontrado"}
            
        except Exception as e:
            print(f"[DOM] Error subiendo fotos: {e}")
            return {"success": False, "error": str(e)}
    
    async def click_continue(self) -> dict:
        """Clickea el botón Continuar"""
        await self._ensure_browser()
        
        try:
            selectors = [
                "text=Continuar",
                "button:has-text('Continuar')",
                "text=Siguiente",
                "button:has-text('Siguiente')"
            ]
            
            for selector in selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector, timeout=5000)
                        print(f"[DOM] Clickeado: {selector}")
                        await asyncio.sleep(2)
                        return {"success": True}
                except:
                    continue
            
            return {"success": False, "error": "Botón Continuar no encontrado"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def select_template_category(self, category: str) -> dict:
        """
        Selecciona una CATEGORÍA del menú lateral izquierdo en la pantalla de templates.
        
        CATEGORÍAS DISPONIBLES en FDF (menú lateral):
        - TODOS: Muestra todos los templates
        - Anuarios: Templates para anuarios escolares
        - Vacío: Template en blanco sin diseño
        - Solo Fotos: Templates minimalistas
        - Colecciones: Templates especiales
        - Viajes: Tema viajes/vacaciones
        - Infantil: Bebés y niños
        - Bodas: Templates elegantes
        - Quince: Quinceañeras
        - Cumple y Aniversario: Cumpleaños
        - San Valentín: Románticos
        - Egresados: Graduaciones
        - Comunión: Primera comunión
        - Día del Padre: Especial papás
        - Día de la Madre: Especial mamás
        
        Args:
            category: Nombre exacto de la categoría (ej: "Bodas", "Viajes", "Infantil")
        """
        await self._ensure_browser()
        
        try:
            print(f"[DOM] Seleccionando categoría del menú lateral: {category}")
            
            # El menú lateral está a la izquierda, buscar los links de categoría
            # Primero scroll al top del menú
            await self.page.evaluate("""
                () => {
                    const sidebar = document.querySelector('.sidebar, .menu-lateral, .categories-menu, nav');
                    if (sidebar) sidebar.scrollTop = 0;
                }
            """)
            await asyncio.sleep(0.3)
            
            # Selectores para categorías del menú lateral
            category_selectors = [
                f"nav >> text={category}",
                f".sidebar >> text={category}",
                f"aside >> text={category}",
                f"text={category}",  # Fallback general
            ]
            
            # Caso especial: "TODOS" puede estar como link activo o resaltado
            if category.upper() == "TODOS":
                category_selectors.insert(0, "text=/^TODOS$/i")
                category_selectors.insert(0, "a:has-text('TODOS')")
            
            for selector in category_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(force=True, timeout=5000)
                        print(f"[DOM] Categoría '{category}' seleccionada")
                        await asyncio.sleep(1)  # Esperar que filtren los templates
                        return {"success": True, "category": category}
                except Exception as e:
                    continue
            
            # Si no encontramos la categoría exacta, buscar por texto parcial
            try:
                # Buscar todos los elementos del menú lateral
                menu_items = await self.page.query_selector_all("nav a, .sidebar a, aside a, .menu-item, .category-item")
                for item in menu_items:
                    text = await item.text_content()
                    if text and category.lower() in text.lower():
                        await item.click()
                        print(f"[DOM] Categoría encontrada por texto parcial: {text.strip()}")
                        await asyncio.sleep(1)
                        return {"success": True, "category": category, "matched": text.strip()}
            except:
                pass
            
            print(f"[DOM] ADVERTENCIA: Categoría '{category}' no encontrada, usando TODOS")
            return {"success": False, "error": f"Categoría '{category}' no encontrada", "fallback": "TODOS"}
            
        except Exception as e:
            print(f"[DOM] Error seleccionando categoría: {e}")
            return {"success": False, "error": str(e)}
    
    async def select_template(self, template_name: str = "Vacío", for_editors: bool = True, category: str = None) -> dict:
        """
        Selecciona una plantilla/template en la pantalla de selección.
        
        IMPORTANTE: Siempre buscar versiones "para Editores" porque:
        - No incluyen el logo de FDF
        - Permiten agregar logo propio
        
        Args:
            template_name: Nombre del template (ej: "Vacío", "Flores Marga", "Acuarela Travel")
            for_editors: Si True, busca la versión "para Editores" (recomendado)
            category: Si se especifica, primero filtra por esta categoría del menú lateral
        """
        await self._ensure_browser()
        
        try:
            # Si se especificó categoría, filtrar primero
            if category:
                print(f"[DOM] Filtrando por categoría: {category}")
                cat_result = await self.select_template_category(category)
                if cat_result.get("success"):
                    await asyncio.sleep(1)  # Esperar que se actualice la lista
                else:
                    print(f"[DOM] Categoría no encontrada, buscando en TODOS")
            
            # IMPORTANTE: Siempre buscar versión "para Editores"
            if for_editors:
                print(f"[DOM] Buscando template '{template_name}' versión EDITORES (sin logo FDF)")
            else:
                print(f"[DOM] Buscando template: {template_name}")
            
            # Primero scroll al inicio para buscar desde arriba
            await self.scroll_page("top")
            await asyncio.sleep(0.5)
            
            # Buscar el template por nombre
            found = False
            max_scrolls = 8  # Más scrolls para encontrar templates
            
            for scroll_attempt in range(max_scrolls):
                # Construir selectores - buscar el nombre directo en versión "para Profesionales"
                if for_editors:
                    selectors = [
                        # En versión "para Profesionales" los templates no tienen sufijos
                        f"text={template_name}",
                        f"h4:has-text('{template_name}')",
                        f"div:has-text('{template_name}')",
                        f"img[alt*='{template_name}']",
                    ]
                else:
                    selectors = [
                        f"text={template_name}",
                        f"h4:has-text('{template_name}')",
                        f"div:has-text('{template_name}')",
                    ]
                
                for selector in selectors:
                    try:
                        locator = self.page.locator(selector).first
                        if await locator.count() > 0:
                            # Verificar si es visible
                            if await locator.is_visible():
                                # Verificar que sea versión editores si se requiere
                                text_content = await locator.text_content()
                                is_editor_version = "Editor" in (text_content or "") or "ED" in (text_content or "")
                                
                                await locator.click(force=True, timeout=5000)
                                
                                version_type = "EDITORES" if is_editor_version else "CLIENTE"
                                print(f"[DOM] Template '{template_name}' seleccionado (versión {version_type})")
                                found = True
                                break
                    except:
                        continue
                
                if found:
                    break
                
                # Si no se encontró, hacer scroll down
                print(f"[DOM] Template no visible, scrolleando... ({scroll_attempt + 1}/{max_scrolls})")
                await self.scroll_page("down", 400)
                await asyncio.sleep(0.5)
            
            if not found:
                # Fallback: seleccionar "Vacío" versión editores
                print("[DOM] Template no encontrado, buscando 'Vacío' para Editores...")
                fallback_selectors = [
                    "text=/Vacío.*Editor/i",
                    "text=Vacío - ED",
                    "text=Vacío",
                ]
                for selector in fallback_selectors:
                    try:
                        if await self.page.locator(selector).count() > 0:
                            await self.page.click(selector, force=True, timeout=5000)
                            found = True
                            print("[DOM] Fallback: 'Vacío' seleccionado")
                            break
                    except:
                        continue
            
            if found:
                await asyncio.sleep(1)
                return {"success": True, "template": template_name, "for_editors": for_editors}
            
            return {"success": False, "error": f"Template '{template_name}' no encontrado"}
            
        except Exception as e:
            print(f"[DOM] Error seleccionando template: {e}")
            return {"success": False, "error": str(e)}
    
    async def select_template_intelligent(
        self,
        estilo_cliente: str,
        categoria: str = None,
        fotos_paths: List[str] = None,
        designer: "DesignIntelligence" = None
    ) -> dict:
        """
        SELECCION HIBRIDA DE TEMPLATE:
        1. Filtra por categoria (hardcodeado, rapido)
        2. Toma screenshot de templates disponibles
        3. LLM Vision elige el mejor template
        4. Clickea ese template
        
        Args:
            estilo_cliente: Estilo elegido (minimalista, clasico, divertido, premium, sin_diseno)
            categoria: Categoria FDF a filtrar (opcional, se calcula si no se pasa)
            fotos_paths: Lista de fotos del cliente para analizar (opcional)
            designer: Instancia de DesignIntelligence (se crea si no se pasa)
            
        Returns:
            dict con resultado de la seleccion
        """
        await self._ensure_browser()
        
        # Importar aqui para evitar circular import
        from .design_intelligence import DesignIntelligence
        
        # Crear designer si no se paso
        if designer is None:
            designer = DesignIntelligence(api_key=self.model_api_key)
        
        try:
            print(f"\n[SMART] Seleccion inteligente de template para estilo: {estilo_cliente}")
            
            # PASO 1: Obtener categoria si no se especifico
            if categoria is None:
                cat_info = designer.obtener_categoria_fdf(estilo_cliente)
                categoria = cat_info["categoria_fdf"]
                print(f"[SMART] Categoria calculada: {categoria}")
            
            # PASO 2: Filtrar por categoria
            print(f"[SMART] Filtrando por categoria: {categoria}")
            await self.select_template_category(categoria)
            await asyncio.sleep(1.5)  # Esperar que se actualice la lista
            
            # PASO 3: Scroll al top y aplicar zoom para ver todos los templates
            await self.scroll_page("top")
            await self.apply_zoom(0.5)
            await asyncio.sleep(0.5)
            
            # PASO 4: Tomar screenshot de templates disponibles
            screenshot_path = "temp_templates_screenshot.png"
            await self.take_screenshot(screenshot_path)
            
            # Leer screenshot como base64
            import base64
            with open(screenshot_path, "rb") as f:
                screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
            
            # PASO 5: Analizar fotos del cliente si se proporcionaron
            descripcion_fotos = None
            fotos_b64 = None
            if fotos_paths and len(fotos_paths) > 0:
                print(f"[SMART] Analizando {len(fotos_paths)} fotos del cliente...")
                analisis = await designer.analizar_fotos_para_template(fotos_paths)
                if analisis.get("success"):
                    descripcion_fotos = analisis.get("descripcion")
                    print(f"[SMART] Fotos analizadas: {descripcion_fotos}")
            
            # PASO 6: LLM Vision elige el mejor template
            print("[SMART] Gemini Vision analizando templates disponibles...")
            resultado_vision = await designer.seleccionar_template_con_vision(
                screenshot_b64=screenshot_b64,
                estilo_cliente=estilo_cliente,
                descripcion_fotos=descripcion_fotos
            )
            
            template_elegido = resultado_vision.get("template_elegido", "Vacío - CL")
            razonamiento = resultado_vision.get("razonamiento", "")
            confianza = resultado_vision.get("confianza", 0.5)
            alternativa = resultado_vision.get("alternativa", "Vacío - CL")
            
            # Verificar si es version para Editores
            es_version_editores = resultado_vision.get("es_version_editores", False)
            necesita_scroll = resultado_vision.get("necesita_scroll", False)
            
            print(f"[SMART] Template elegido: {template_elegido}")
            print(f"[SMART] Es version Editores: {es_version_editores}")
            print(f"[SMART] Razonamiento: {razonamiento}")
            print(f"[SMART] Confianza: {confianza}")
            
            # Si no encontro version Editores, hacer scroll y buscar
            if necesita_scroll or not es_version_editores:
                print("[SMART] Buscando versiones para Editores (scrolleando)...")
                
                # Hacer scroll para buscar versiones ED
                for scroll_attempt in range(5):
                    await self.scroll_page("down", 500)
                    await asyncio.sleep(1)
                    
                    # Buscar templates con "ED" o "Editor" en el nombre
                    editor_templates = await self.page.locator("text=/- ED|para Editor|Editores/i").all()
                    if editor_templates:
                        print(f"[SMART] Encontradas {len(editor_templates)} versiones para Editores")
                        break
                
                # Tomar nuevo screenshot y re-analizar
                await self.take_screenshot(screenshot_path)
                with open(screenshot_path, "rb") as f:
                    screenshot_b64 = base64.b64encode(f.read()).decode("utf-8")
                
                print("[SMART] Re-analizando con Vision...")
                resultado_vision = await designer.seleccionar_template_con_vision(
                    screenshot_b64=screenshot_b64,
                    estilo_cliente=estilo_cliente,
                    descripcion_fotos=descripcion_fotos
                )
                
                template_elegido = resultado_vision.get("template_elegido", "Vacío - ED")
                alternativa = resultado_vision.get("alternativa", "Vacío")
                es_version_editores = resultado_vision.get("es_version_editores", False)
                print(f"[SMART] Nuevo template elegido: {template_elegido}")
            
            # PASO 7: Clickear el template elegido para SELECCIONARLO
            # IMPORTANTE: En FDF hay que hacer click en la CARD/IMAGEN del template
            # para que quede seleccionado (resaltado). Solo después se puede clickear
            # el modo de relleno.
            print(f"[SMART] Clickeando template: {template_elegido}")
            
            # Scroll al inicio para ver los templates
            await self.scroll_page("top")
            await asyncio.sleep(0.5)
            
            # Buscar y clickear el template
            template_found = False
            
            # Extraer nombre base del template (sin sufijos CL/ED)
            nombre_base = template_elegido.replace(' - CL', '').replace(' - ED', '').replace(' para Editores', '').strip()
            
            print(f"[SMART] Buscando template: '{nombre_base}'")
            
            # ESTRATEGIA ROBUSTA: Buscar la CARD del template usando múltiples métodos
            
            async def find_and_click_template_card(search_name: str) -> bool:
                """
                Busca la card del template y hace click en ella.
                En FDF, los templates son cards con:
                - Una imagen/preview arriba
                - El nombre del template abajo (ej: "Crafti - CL")
                
                La card completa es clickeable para seleccionar el template.
                """
                try:
                    # Método 1: Buscar por estructura típica de cards en FDF
                    # Las cards suelen estar en divs con clase que contiene 'template', 'card', 'item'
                    card_result = await self.page.evaluate(f"""
                        () => {{
                            const searchName = '{search_name}';
                            const searchNameLower = searchName.toLowerCase();
                            
                            // Buscar elementos de texto que contengan el nombre del template
                            const textElements = [];
                            const walker = document.createTreeWalker(
                                document.body,
                                NodeFilter.SHOW_TEXT,
                                null,
                                false
                            );
                            
                            let node;
                            while (node = walker.nextNode()) {{
                                const text = node.textContent.trim();
                                // Buscar coincidencia con el nombre (con o sin sufijos)
                                if (text.toLowerCase().includes(searchNameLower) && 
                                    (text.includes(' - CL') || text.includes(' - ED') || text === searchName)) {{
                                    textElements.push({{
                                        node: node.parentElement,
                                        text: text
                                    }});
                                }}
                            }}
                            
                            // Para cada elemento de texto encontrado, buscar la card contenedora
                            for (const item of textElements) {{
                                let el = item.node;
                                
                                // Subir por el DOM buscando un contenedor clickeable (la card)
                                for (let i = 0; i < 5 && el; i++) {{
                                    const rect = el.getBoundingClientRect();
                                    const style = window.getComputedStyle(el);
                                    
                                    // Una card típica tiene un tamaño razonable (100-300px)
                                    // y usualmente tiene cursor pointer o eventos de click
                                    const isClickable = style.cursor === 'pointer' || 
                                                       el.onclick !== null ||
                                                       el.tagName === 'BUTTON' ||
                                                       el.tagName === 'A' ||
                                                       el.getAttribute('role') === 'button';
                                    
                                    const hasReasonableSize = rect.width > 80 && rect.width < 350 &&
                                                             rect.height > 80 && rect.height < 400;
                                    
                                    // Si encontramos un elemento con tamaño de card, hacer click en su centro
                                    if (hasReasonableSize && rect.top > 0 && rect.left > 0) {{
                                        // Verificar que está visible en viewport
                                        if (rect.top < window.innerHeight && rect.bottom > 0) {{
                                            return {{
                                                found: true,
                                                x: rect.left + rect.width / 2,
                                                y: rect.top + rect.height / 2,
                                                width: rect.width,
                                                height: rect.height,
                                                text: item.text,
                                                tagName: el.tagName,
                                                isClickable: isClickable
                                            }};
                                        }}
                                    }}
                                    
                                    el = el.parentElement;
                                }}
                            }}
                            
                            return {{ found: false }};
                        }}
                    """)
                    
                    if card_result and card_result.get("found"):
                        click_x = card_result["x"]
                        click_y = card_result["y"]
                        print(f"[SMART] Card encontrada: '{card_result.get('text')}' ({card_result.get('width'):.0f}x{card_result.get('height'):.0f})")
                        print(f"[SMART] Haciendo click en centro de card: ({click_x:.0f}, {click_y:.0f})")
                        
                        await self.page.mouse.click(click_x, click_y)
                        await asyncio.sleep(1.5)
                        return True
                    
                    return False
                    
                except Exception as e:
                    print(f"[SMART] Error buscando card: {e}")
                    return False
            
            async def click_template_by_text_then_parent(search_text: str) -> bool:
                """Busca el texto del template y hace click en el contenedor padre"""
                try:
                    # Variaciones del nombre a buscar
                    search_variations = [
                        f"{search_text} - CL",
                        f"{search_text} - ED", 
                        search_text,
                    ]
                    
                    for variation in search_variations:
                        # Buscar elementos que contengan el texto exacto
                        locators = self.page.locator(f"text='{variation}'")
                        count = await locators.count()
                        
                        if count > 0:
                            for i in range(count):
                                locator = locators.nth(i)
                                try:
                                    if await locator.is_visible(timeout=1000):
                                        # Obtener el elemento padre (la card)
                                        # En lugar de hacer click en el texto, 
                                        # buscamos el contenedor padre y hacemos click ahí
                                        box = await locator.bounding_box()
                                        if box:
                                            # Hacer click un poco arriba del texto (en la imagen de la card)
                                            # o directamente en el texto que debería propagar el click
                                            click_x = box["x"] + box["width"] / 2
                                            click_y = box["y"] + box["height"] / 2
                                            
                                            # Si hay espacio arriba, clickear en la imagen
                                            if box["y"] > 100:
                                                click_y = box["y"] - 50  # Arriba del texto
                                            
                                            print(f"[SMART] Encontrado '{variation}', click en ({click_x:.0f}, {click_y:.0f})")
                                            await self.page.mouse.click(click_x, click_y)
                                            await asyncio.sleep(1)
                                            return True
                                except:
                                    continue
                    
                    return False
                except Exception as e:
                    print(f"[SMART] Error en click_template_by_text_then_parent: {e}")
                    return False
            
            async def click_template_directly(search_text: str) -> bool:
                """Último recurso: hacer click directo en el locator del texto"""
                try:
                    variations = [
                        f"text='{search_text} - CL'",
                        f"text='{search_text} - ED'",
                        f"text='{search_text}'",
                        f"*:has-text('{search_text} - CL')",
                        f"*:has-text('{search_text}')",
                    ]
                    
                    for selector in variations:
                        try:
                            locator = self.page.locator(selector).first
                            if await locator.count() > 0 and await locator.is_visible(timeout=2000):
                                await locator.click(force=True, timeout=5000)
                                print(f"[SMART] Click directo exitoso con selector: {selector}")
                                await asyncio.sleep(1)
                                return True
                        except:
                            continue
                    
                    return False
                except Exception as e:
                    print(f"[SMART] Error en click directo: {e}")
                    return False
            
            # Intentar método 1: Buscar y clickear la card del template
            print(f"[SMART] Método 1: Buscando card del template '{nombre_base}'...")
            template_found = await find_and_click_template_card(nombre_base)
            
            # Método 2: Buscar texto y clickear arriba (en la imagen)
            if not template_found:
                print(f"[SMART] Método 2: Buscando texto y clickeando en card padre...")
                template_found = await click_template_by_text_then_parent(nombre_base)
            
            # Método 3: Click directo en el elemento
            if not template_found:
                print(f"[SMART] Método 3: Click directo en elemento...")
                template_found = await click_template_directly(nombre_base)
            
            # Si no encontramos el específico, buscar con scroll
            if not template_found:
                print("[SMART] Buscando con scroll...")
                for scroll_attempt in range(3):
                    await self.scroll_page("down", 300)
                    await asyncio.sleep(0.5)
                    
                    template_found = await find_and_click_template_card(nombre_base)
                    if template_found:
                        break
                    
                    template_found = await click_template_directly(nombre_base)
                    if template_found:
                        break
            
            # ULTIMO FALLBACK: Si no encontramos el template específico, usar select_template directo
            if not template_found:
                print(f"[SMART] Usando método fallback select_template para '{nombre_base}'...")
                await self.scroll_page("top")
                await asyncio.sleep(0.5)
                
                # Usar la función select_template que ya existe
                direct_result = await self.select_template(nombre_base)
                template_found = direct_result.get("success", False)
                
                if template_found:
                    print(f"[SMART] Template seleccionado via select_template()")
            
            # Solo usar Vacío si realmente no encontramos NADA
            if not template_found:
                print("[SMART] ADVERTENCIA: No se encontró el template, usando Vacío como fallback")
                await self.select_template("Vacío")
                template_found = True
            
            # Esperar un momento para que se seleccione el template
            await asyncio.sleep(2)
            
            # Verificar si el template quedó seleccionado
            if template_found:
                print("[SMART] Template clickeado, verificando seleccion...")
                # Tomar screenshot para debug
                await self.take_screenshot("debug_template_selected.png")
                
                # NOTA: La selección de versión "para Profesionales" se hace UNA VEZ 
                # después del login (select_editor_version), no por cada template.
                # Los templates tienen sufijos -CL (cliente) o -ED (editores) que
                # determinan si tienen logo FDF o no.
            
            # Limpiar archivo temporal
            try:
                os.remove(screenshot_path)
            except:
                pass
            
            return {
                "success": template_found,
                "template_elegido": template_elegido,
                "categoria": categoria,
                "razonamiento": razonamiento,
                "confianza": confianza,
                "alternativa": alternativa,
                "templates_visibles": resultado_vision.get("templates_visibles", [])
            }
            
        except Exception as e:
            print(f"[SMART] Error en seleccion inteligente: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "template_elegido": "Vacío - CL",
                "razonamiento": "Error en seleccion inteligente"
            }
    
    async def select_editor_version(self, prefer_profesionales: bool = False) -> dict:
        """
        JUSTO DESPUES DEL LOGIN: 
        Selecciona la version (CLIENTE con logo FDF, o PROFESIONALES sin logo).
        
        Args:
            prefer_profesionales: True = "para Profesionales" (sin logo FDF, menos templates)
                                 False = "Cliente" (con logo FDF, TODOS los templates)
        """
        await self._ensure_browser()
        
        try:
            if prefer_profesionales:
                print("[DOM] Buscando opción 'para Profesionales' (sin logo FDF, templates limitados)...")
                target_selector = "text=para profesionales (sin logo de FDF)"
            else:
                print("[DOM] Buscando opción 'Cliente' (con logo FDF, templates COMPLETOS)...")
                target_selector = "text=Cliente"
            
            # Tomar screenshot para debug
            try:
                await self.take_screenshot("debug_select_version.png")
                print("[DOM] Screenshot guardado: debug_select_version.png")
            except:
                pass
            
            # Selectores para ambas versiones
            selectors = [
                # Versión PROFESIONALES (sin logo FDF)
                "text=para profesionales (sin logo de FDF)",
                "text=Para Profesionales (sin logo de FDF)",
                "text=Profesionales",
                "text=Profesional",
                "text=Para Diseñadores",
                "text=Para Editores",
                # Versión CLIENTE (con logo FDF)
                "text=Cliente",
                "text=CLIENTE",
                "text=Cliente (con logo)",
                "text=Cliente:",
                "text=/cliente/i",
            ]
            
            # Si preferimos profesionales, poner esos selectores primero
            if prefer_profesionales:
                professional_selectors = [
                    "text=para profesionales (sin logo de FDF)",
                    "text=Para Profesionales (sin logo de FDF)",
                    "text=Profesionales",
                    "text=Profesional",
                ]
                other_selectors = [s for s in selectors if s not in professional_selectors]
                selectors = professional_selectors + other_selectors
            else:
                # Poner cliente primero
                client_selectors = [
                    "text=Cliente",
                    "text=CLIENTE",
                    "text=Cliente (con logo)",
                    "text=Cliente:",
                    "text=/cliente/i",
                ]
                other_selectors = [s for s in selectors if s not in client_selectors]
                selectors = client_selectors + other_selectors
            
            for selector in selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0:
                        # Verificar que sea visible
                        if await locator.is_visible():
                            await locator.click(force=True, timeout=5000)
                            
                            if prefer_profesionales and ("profesionales" in selector.lower() or "editores" in selector.lower()):
                                print(f"[DOM] Versión 'Profesionales' seleccionada con: {selector}")
                                await asyncio.sleep(2)
                                return {"success": True, "version": "profesionales", "selector": selector}
                            elif "cliente" in selector.lower():
                                print(f"[DOM] Versión 'Cliente' seleccionada con: {selector}")
                                await asyncio.sleep(2)
                                return {"success": True, "version": "cliente", "selector": selector}
                            else:
                                print(f"[DOM] Versión seleccionada con: {selector}")
                                await asyncio.sleep(2)
                                return {"success": True, "version": "detected", "selector": selector}
                except Exception as e:
                    continue
            
            # Si no encontramos el botón específico, buscar con JavaScript
            try:
                content = await self.page.content()
                
                # Verificar si estamos en pantalla de selección
                if "cliente" in content.lower() or "profesionales" in content.lower():
                    print("[DOM] Detectada pantalla de selección de versión")
                    
                    # Intentar con JavaScript
                    clicked = await self.page.evaluate("""
                        () => {
                            const elements = document.querySelectorAll('button, a, div[onclick], span[onclick], .clickable, [role="button"], label, div');
                            for (let el of elements) {
                                const text = el.textContent.toLowerCase();
                                // Si preferimos clientes: buscar "cliente"
                                const buscar = arguments[0] === "cliente" ? "cliente" : "profesionales";
                                if (text.includes(buscar)) {
                                    el.click();
                                    return true;
                                }
                            }
                            return false;
                        }
                    """, "cliente" if not prefer_profesionales else "profesionales")
                    
                    if clicked:
                        version = "cliente" if not prefer_profesionales else "profesionales"
                        print(f"[DOM] Versión '{version}' seleccionada via JavaScript")
                        await asyncio.sleep(2)
                        return {"success": True, "version": version, "method": "javascript"}
            except:
                pass
            
            print("[DOM] ADVERTENCIA: No se encontró pantalla de selección de versión")
            print("[DOM] Continuando... (puede que ya esté seleccionada o no exista)")
            return {"success": True, "version": "unknown", "note": "No se encontró selector"}
            
        except Exception as e:
            print(f"[DOM] Error seleccionando versión: {e}")
            return {"success": False, "error": str(e)}
    
    async def click_fill_mode(self, mode: str = "manual") -> dict:
        """Selecciona el modo de relleno (manual, auto, etc.)"""
        await self._ensure_browser()
        
        try:
            print(f"[DOM] Seleccionando modo de relleno: {mode}")
            
            mode_map = {
                "manual": ["text=Manual", "text=manualmente"],
                "auto": ["text=Automático", "text=Auto", "text=relleno automático"],
                "smart": ["text=Inteligente", "text=Smart", "text=relleno inteligente"]
            }
            
            selectors = mode_map.get(mode, mode_map["manual"])
            
            for selector in selectors:
                try:
                    locator = self.page.locator(selector)
                    if await locator.count() > 0:
                        await locator.click(timeout=5000)
                        print(f"[DOM] Modo '{mode}' seleccionado con: {selector}")
                        await asyncio.sleep(2)  # Esperar que cambie la UI
                        return {"success": True, "mode": mode}
                except Exception as e:
                    print(f"[DOM] Error con selector {selector}: {e}")
                    continue
            
            return {"success": False, "error": f"Modo {mode} no encontrado"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def usar_relleno_smart(self, is_template_vacio: bool = False) -> dict:
        """
        Usa el modo de relleno inteligente según el tipo de template.
        
        Args:
            is_template_vacio: True si el template es "Vacío" (sin slots prediseñados)
        """
        await self._ensure_browser()
        
        try:
            if is_template_vacio:
                print("[SMART] Template 'Vacío' detectado - usando estrategia especial")
                return await self._relleno_para_template_vacio()
            
            print("[SMART] Intentando usar relleno smart/inteligente...")
            
            # Primero intentar modo automático (más confiable para templates con slots)
            auto_result = await self.click_fill_mode("auto")
            if auto_result.get("success"):
                print("[SMART] ✅ Modo automático aplicado")
                await asyncio.sleep(5)
                return {"success": True, "fotos_colocadas": 1, "modo": "auto"}
            
            # Segundo intento: modo smart/inteligente
            smart_result = await self.click_fill_mode("smart")
            if smart_result.get("success"):
                print("[SMART] ✅ Modo smart aplicado")
                await asyncio.sleep(5)
                return {"success": True, "fotos_colocadas": 1, "modo": "smart"}
            
            # Si no hay modos automáticos, usar slot simple
            print("[SMART] ⚠️ No hay modos automáticos, usando slot simple")
            
            # Buscar el primer slot disponible
            slot_selectors = [
                "[class*='slot']",
                "[class*='photo']",
                ".photo-slot",
                ".slot-photo",
                "[data-type='slot']"
            ]
            
            for selector in slot_selectors:
                try:
                    slots = await self.page.locator(selector).all()
                    if slots:
                        await slots[0].click(timeout=3000)
                        print(f"[SMART] Slot seleccionado: {selector}")
                        
                        # Buscar botón de rellenar o usar primera foto
                        fill_selectors = [
                            "button:has-text('Rellenar')",
                            "text=Rellenar",
                            "button:has-text('Usar')",
                            "text=Usar"
                        ]
                        
                        for fill_selector in fill_selectors:
                            try:
                                await self.page.click(fill_selector, timeout=3000)
                                print(f"[SMART] Botón rellenar clickeado: {fill_selector}")
                                await asyncio.sleep(2)
                                return {"success": True, "fotos_colocadas": 1, "modo": "manual-simple"}
                            except:
                                continue
                        
                        # Si no hay botón, usar la primera miniatura de foto
                        await self.page.click("[class*='thumbnail'] >> nth=0", timeout=3000)
                        print("[SMART] Primera foto colocada")
                        await asyncio.sleep(2)
                        return {"success": True, "fotos_colocadas": 1, "modo": "thumbnail"}
                        
                except Exception as e:
                    print(f"[SMART] Error con selector {selector}: {e}")
                    continue
            
            return {"success": False, "error": "No se pudo usar relleno smart"}
            
        except Exception as e:
            print(f"[SMART] Error en relleno smart: {e}")
            return {"success": False, "error": str(e)}
    
    async def _relleno_para_template_vacio(self) -> dict:
        """
        Estrategia especial para template 'Vacío' (libro en blanco sin slots).
        """
        print("[VACIO] Usando estrategia especial para libro en blanco...")
        
        # Paso 1: Verificar si estamos en el editor (página en blanco)
        try:
            # Tomar screenshot para debug
            await self.page.screenshot(path="template_vacio_debug.png")
            print("[VACIO] Screenshot guardado: template_vacio_debug.png")
        except:
            pass
        
        # Paso 2: Buscar panel de fotos/recursos
        panel_selectors = [
            "[class*='photos']",
            "[class*='resources']",
            "[class*='sidebar']",
            "[class*='panel']:has-text('Fotos')",
            "text=Fotos subidas"
        ]
        
        for selector in panel_selectors:
            try:
                await self.page.locator(selector).first.wait_for(state="visible", timeout=2000)
                print(f"[VACIO] Panel fotos encontrado: {selector}")
                break
            except:
                continue
        
        # Paso 3: Usar modo INSERTAR en página
        insert_selectors = [
            "text=Insertar",
            "button:has-text('Insertar')",
            "[role='button']:has-text('Insertar')",
            ".insert-photo",
            "[data-action='insert']"
        ]
        
        fotos_colocadas = 0
        
        for selector in insert_selectors:
            try:
                await self.page.click(selector, timeout=3000)
                print(f"[VACIO] Click en Insertar: {selector}")
                await asyncio.sleep(2)
                
                # Buscar modal o panel de selección de fotos
                photo_selectors = [
                    "[class*='thumbnail']:visible",
                    "[class*='photo']:visible",
                    "img[alt*='photo']:visible",
                    "[data-type='photo']:visible"
                ]
                
                for photo_selector in photo_selectors:
                    try:
                        photos = await self.page.locator(photo_selector).all()
                        if photos:
                            # Clickear la primera foto disponible
                            await photos[0].click(timeout=2000)
                            print("[VACIO] Primera foto insertada")
                            fotos_colocadas += 1
                            
                            # Buscar botón de aplicar/aceptar
                            apply_selectors = [
                                "button:has-text('Aplicar')",
                                "text=Aplicar",
                                "button:has-text('OK')",
                                "text=OK",
                                "button:has-text('Hecho')",
                                "text=Hecho"
                            ]
                            
                            for apply_selector in apply_selectors:
                                try:
                                    await self.page.click(apply_selector, timeout=2000)
                                    print(f"[VACIO] Aplicando foto con: {apply_selector}")
                                    await asyncio.sleep(2)
                                    return {"success": True, "fotos_colocadas": fotos_colocadas, "modo": "insertar_vacio"}
                                except:
                                    continue
                            
                            # Si no hay botón de aplicar, solo esperar
                            await asyncio.sleep(2)
                            return {"success": True, "fotos_colocadas": fotos_colocadas, "modo": "insertar_simple"}
                    except:
                        continue
                
            except Exception as e:
                print(f"[VACIO] Error con insertar selector {selector}: {e}")
                continue
        
        return {"success": fotos_colocadas > 0, "fotos_colocadas": fotos_colocadas, "modo": "fallback_vacio", "warning": "Problemas detectando interfaz Vacío"}
    
    async def wait_for_editor_ready(self, timeout: int = 60, check_interval: int = 3) -> dict:
        """
        Espera a que el editor este completamente cargado usando Vision.
        Detecta mensajes de carga como "Preparando el Tema X%".
        
        IMPORTANTE: Distingue entre pantalla de templates y editor real.
        Si detecta que aun estamos en pantalla de templates, NO reporta "listo".
        """
        await self._ensure_browser()
        
        from .vision_designer import VisionDesigner
        vision = VisionDesigner(api_key=self.model_api_key)
        
        print(f"[WAIT] Esperando que el editor este listo (max {timeout}s)...")
        
        template_screen_count = 0
        max_template_warnings = 3
        
        for i in range(0, timeout, check_interval):
            try:
                result = await vision.is_editor_ready(self.page)
                
                # Si aun estamos en pantalla de templates
                if result.get("is_template_screen"):
                    template_screen_count += 1
                    print(f"[WAIT] Aun en pantalla de templates ({i}s)")
                    
                    if template_screen_count >= max_template_warnings:
                        print("[WAIT] ADVERTENCIA: Parece que no se entro al editor")
                        print("[WAIT] Intentando detectar y clickear el template seleccionado...")
                        
                        # Intentar hacer click en algun template visible
                        await self._try_enter_editor()
                        template_screen_count = 0  # Reset contador
                    
                    await asyncio.sleep(check_interval)
                    continue
                
                if result.get("ready"):
                    print(f"[WAIT] Editor listo! (tiempo: {i}s)")
                    return {"success": True, "time_waited": i, "details": result.get("details")}
                
                loading_msg = result.get("loading_message", "")
                loading_pct = result.get("loading_percent", "")
                
                if loading_msg or loading_pct:
                    pct_str = f"{loading_pct}%" if loading_pct else ""
                    print(f"[WAIT] {loading_msg} {pct_str} ({i}s)")
                else:
                    print(f"[WAIT] Esperando carga del editor... ({i}s)")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                print(f"[WAIT] Error verificando: {e}")
                await asyncio.sleep(check_interval)
        
        return {"success": False, "error": f"Timeout despues de {timeout}s"}
    
    async def _try_enter_editor(self):
        """
        Intenta entrar al editor si estamos atascados en la pantalla de templates.
        
        El flujo correcto es:
        1. Click en la CARD del template (imagen) para seleccionarlo
        2. Click en uno de los botones de relleno (manual/rapido/smart)
        """
        try:
            print("[WAIT] Intentando seleccionar template y entrar al editor...")
            
            # Primero scroll al top para ver los templates
            await self.scroll_page("top")
            await asyncio.sleep(0.5)
            
            # PASO 1: Buscar y clickear la IMAGEN/CARD de un template
            # Las cards de templates tienen imágenes y están en el área central
            template_clicked = False
            
            # Buscar imágenes de templates (las cards tienen imágenes de preview)
            try:
                # Buscar cualquier imagen en el área de templates
                # Evitar imágenes pequeñas (logos) y buscar las de tamaño mediano (cards)
                template_images = await self.page.query_selector_all("img")
                
                for img in template_images:
                    try:
                        box = await img.bounding_box()
                        if box and box["width"] > 100 and box["height"] > 100:
                            # Esta parece una card de template
                            # Verificar que no es un logo o icono pequeño
                            if box["width"] < 500 and box["x"] > 100:  # En el área central
                                await img.click()
                                template_clicked = True
                                print(f"[WAIT] Click en imagen de template ({box['width']:.0f}x{box['height']:.0f})")
                                await asyncio.sleep(1)
                                break
                    except:
                        continue
            except Exception as e:
                print(f"[WAIT] Error buscando imágenes: {e}")
            
            # Si no encontramos imagen, buscar por texto del template
            if not template_clicked:
                try:
                    # Buscar el texto "Vacío - CL" y clickear arriba de él (donde está la imagen)
                    text_locator = self.page.locator("text=/Vacío.*CL/i").first
                    if await text_locator.count() > 0:
                        box = await text_locator.bounding_box()
                        if box:
                            # Click arriba del texto donde está la imagen
                            click_y = max(box["y"] - 80, 100)
                            await self.page.mouse.click(box["x"] + box["width"]/2, click_y)
                            template_clicked = True
                            print(f"[WAIT] Click arriba del texto del template")
                            await asyncio.sleep(1)
                except:
                    pass
            
            # PASO 2: Si se clickeó el template, ahora clickear el botón de relleno
            if template_clicked:
                await asyncio.sleep(1)
                
                # Scroll abajo para ver los botones de relleno
                await self.scroll_page("bottom")
                await asyncio.sleep(0.5)
                
                # Clickear "Relleno fotos manual"
                try:
                    manual_btn = self.page.locator("text=Relleno fotos manual").first
                    if await manual_btn.count() > 0 and await manual_btn.is_visible():
                        await manual_btn.click(force=True)
                        print("[WAIT] Click en 'Relleno fotos manual'")
                        await asyncio.sleep(3)  # Esperar que inicie la carga del editor
                except Exception as e:
                    print(f"[WAIT] Error clickeando botón de relleno: {e}")
            
        except Exception as e:
            print(f"[WAIT] Error intentando entrar al editor: {e}")
    
    async def drag_drop_with_vision(
        self, 
        photo_index: int = 0, 
        slot_index: int = 0,
        use_fallback: bool = True,
        max_retries: int = 2
    ) -> dict:
        """
        Hace drag & drop de una foto al canvas usando Vision para detectar posiciones.
        Si Vision falla, usa fallback DOM.
        
        Args:
            photo_index: Indice de la foto en el panel (0 = primera)
            slot_index: Indice del slot destino (0 = principal)
            use_fallback: Si True, usa fallback DOM cuando Vision falla
            max_retries: Número de reintentos
        """
        await self._ensure_browser()
        
        from .vision_designer import VisionDesigner
        vision = VisionDesigner(api_key=self.model_api_key)
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Drag & drop intento {attempt + 1}/{max_retries}")
                print(f"[DRAG] Planificando drag & drop con Vision...")
                
                # Obtener plan de drag & drop
                plan = await vision.plan_drag_drop(self.page)
                
                # Si Vision falla, intentar fallback
                if not plan.get("success") and use_fallback:
                    logger.warning("Vision falló, usando fallback DOM")
                    print("[DRAG] Vision falló, usando fallback DOM...")
                    
                    # Fallback: detectar con DOM
                    photos_fb = await VisionFallback.detect_photos_fallback(self.page)
                    slots_fb = await VisionFallback.detect_slots_fallback(self.page)
                    
                    if photos_fb.get("photos") and slots_fb.get("slots"):
                        plan = {
                            "success": True,
                            "photos": photos_fb["photos"],
                            "slots": slots_fb["slots"],
                            "actions": [],
                            "method": "dom_fallback"
                        }
                    else:
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2)
                            continue
                        return {"success": False, "error": "No se pudieron detectar elementos", "details": plan}
                
                if not plan.get("success"):
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                        continue
                    return {"success": False, "error": "No se pudo planificar drag & drop", "details": plan}
                
                photos = plan.get("photos", [])
                slots = plan.get("slots", [])
                actions = plan.get("actions", [])
                
                print(f"[DRAG] Fotos detectadas: {len(photos)}")
                print(f"[DRAG] Slots detectados: {len(slots)}")
                print(f"[DRAG] Acciones planificadas: {len(actions)}")
                
                if not photos:
                    return {"success": False, "error": "No se detectaron fotos en el panel"}
                
                if not slots:
                    return {"success": False, "error": "No se detectaron slots en el canvas"}
                
                # Usar la accion planificada o calcular una
                if actions and len(actions) > 0:
                    # Usar la primera accion del plan
                    action = actions[0]
                    from_x = action.get("foto_x", photos[0]["x"])
                    from_y = action.get("foto_y", photos[0]["y"])
                    to_x = action.get("slot_x", slots[0]["x"])
                    to_y = action.get("slot_y", slots[0]["y"])
                    razon = action.get("razon", "")
                    print(f"[DRAG] Usando plan de Vision: {razon}")
                else:
                    # Fallback: primera foto al primer slot
                    if photo_index < len(photos):
                        from_x = photos[photo_index]["x"]
                        from_y = photos[photo_index]["y"]
                    else:
                        from_x = photos[0]["x"]
                        from_y = photos[0]["y"]
                    
                    if slot_index < len(slots):
                        to_x = slots[slot_index]["x"]
                        to_y = slots[slot_index]["y"]
                    else:
                        to_x = slots[0]["x"]
                        to_y = slots[0]["y"]
                
                print(f"[DRAG] Arrastrando de ({from_x}, {from_y}) a ({to_x}, {to_y})")
                
                # Ejecutar drag & drop
                await self.page.mouse.move(from_x, from_y)
                await asyncio.sleep(0.3)
                await self.page.mouse.down()
                await asyncio.sleep(0.2)
                
                # Movimiento suave en pasos
                steps = 15
                for i in range(steps + 1):
                    progress = i / steps
                    current_x = from_x + (to_x - from_x) * progress
                    current_y = from_y + (to_y - from_y) * progress
                    await self.page.mouse.move(current_x, current_y)
                    await asyncio.sleep(0.03)
                
                await asyncio.sleep(0.2)
                await self.page.mouse.up()
                await asyncio.sleep(1)
                
                print(f"[DRAG] Drag & drop completado")
                
                # Verificar resultado
                verify = await vision.verify_photo_placement(self.page)
                
                logger.info("Drag & drop exitoso")
                return {
                    "success": True,
                    "from": {"x": from_x, "y": from_y},
                    "to": {"x": to_x, "y": to_y},
                    "verification": verify,
                    "plan": plan,
                    "attempt": attempt + 1
                }
                
            except Exception as e:
                logger.error(f"Error en drag & drop intento {attempt + 1}", exc=e)
                print(f"[DRAG] Error: {e}")
                
                if attempt < max_retries - 1:
                    print(f"[DRAG] Reintentando en 2s...")
                    await asyncio.sleep(2)
                    continue
                
                import traceback
                traceback.print_exc()
                return {"success": False, "error": str(e), "attempts": max_retries}
        
        # Si llegamos aquí sin return, algo salió mal
        return {"success": False, "error": "Max retries alcanzado sin resultado"}
    
    async def auto_fill_page_with_vision(self, max_photos: int = 4, retry_per_photo: int = 2) -> dict:
        """
        Llena automaticamente la pagina actual con fotos usando Vision.
        Detecta slots vacios y arrastra fotos apropiadas.
        Incluye reintentos por foto individual.
        
        Args:
            max_photos: Máximo de fotos a colocar
            retry_per_photo: Reintentos por cada foto
        """
        await self._ensure_browser()
        
        from .vision_designer import VisionDesigner
        vision = VisionDesigner(api_key=self.model_api_key)
        
        results = []
        errors = []
        consecutive_failures = 0
        
        logger.info(f"Auto-fill iniciado: max {max_photos} fotos")
        print(f"[AUTO] Llenando pagina automaticamente (max {max_photos} fotos)...")
        
        for i in range(max_photos):
            print(f"\n[AUTO] --- Foto {i+1}/{max_photos} ---")
            
            photo_placed = False
            actions = []  # Inicializar actions para evitar UnboundLocalError
            
            for attempt in range(retry_per_photo):
                try:
                    # Obtener plan actualizado
                    plan = await vision.plan_drag_drop(self.page)
                    
                    # Si Vision falla, intentar fallback
                    if not plan.get("success"):
                        logger.warning(f"Vision falló para foto {i+1}, usando fallback")
                        photos_fb = await VisionFallback.detect_photos_fallback(self.page)
                        slots_fb = await VisionFallback.detect_slots_fallback(self.page)
                        
                        if photos_fb.get("photos") and slots_fb.get("slots"):
                            # Crear acción simple: primera foto disponible al primer slot
                            plan = {
                                "success": True,
                                "photos": photos_fb["photos"],
                                "slots": slots_fb["slots"],
                                "actions": [{
                                    "foto_x": photos_fb["photos"][0]["x"],
                                    "foto_y": photos_fb["photos"][0]["y"],
                                    "slot_x": slots_fb["slots"][0]["x"],
                                    "slot_y": slots_fb["slots"][0]["y"],
                                    "razon": "Fallback DOM"
                                }] if photos_fb["photos"] and slots_fb["slots"] else []
                            }
                        else:
                            if attempt < retry_per_photo - 1:
                                await asyncio.sleep(1)
                                continue
                            print(f"[AUTO] No se pudo obtener plan después de {retry_per_photo} intentos")
                            consecutive_failures += 1
                            break
                    
                    actions = plan.get("actions", [])
                    
                    if not actions:
                        print(f"[AUTO] No hay mas acciones pendientes")
                        break
                    
                    # Ejecutar primera accion
                    action = actions[0]
                    from_x = action.get("foto_x")
                    from_y = action.get("foto_y")
                    to_x = action.get("slot_x")
                    to_y = action.get("slot_y")
                    
                    if not all([from_x, from_y, to_x, to_y]):
                        print(f"[AUTO] Coordenadas incompletas: {action}")
                        if attempt < retry_per_photo - 1:
                            await asyncio.sleep(1)
                            continue
                        break
                    
                    print(f"[AUTO] Ejecutando: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
                    print(f"[AUTO] Razon: {action.get('razon', 'N/A')}")
                    
                    # Drag & drop
                    await self.page.mouse.move(from_x, from_y)
                    await asyncio.sleep(0.2)
                    await self.page.mouse.down()
                    await asyncio.sleep(0.1)
                    
                    steps = 12
                    for j in range(steps + 1):
                        progress = j / steps
                        cx = from_x + (to_x - from_x) * progress
                        cy = from_y + (to_y - from_y) * progress
                        await self.page.mouse.move(cx, cy)
                        await asyncio.sleep(0.02)
                    
                    await asyncio.sleep(0.1)
                    await self.page.mouse.up()
                    await asyncio.sleep(1.5)
                    
                    results.append({
                        "photo": i,
                        "from": {"x": from_x, "y": from_y},
                        "to": {"x": to_x, "y": to_y},
                        "success": True,
                        "attempt": attempt + 1
                    })
                    
                    photo_placed = True
                    consecutive_failures = 0  # Reset en éxito
                    break
                    
                except Exception as e:
                    logger.error(f"Error colocando foto {i+1} intento {attempt+1}", exc=e)
                    errors.append({"photo": i, "attempt": attempt + 1, "error": str(e)})
                    
                    if attempt < retry_per_photo - 1:
                        await asyncio.sleep(1)
                        continue
                    
                    consecutive_failures += 1
            
            # Si tenemos muchos fallos consecutivos, parar
            if consecutive_failures >= 3:
                logger.warning("Demasiados fallos consecutivos, deteniendo auto-fill")
                print("[AUTO] Demasiados fallos consecutivos, deteniendo...")
                break
            
            # Si no se pudo colocar la foto y no hay más acciones, parar
            if not photo_placed and not actions:
                break
        
        logger.info(f"Auto-fill completado: {len(results)} fotos colocadas")
        print(f"\n[AUTO] Completado: {len(results)} fotos colocadas")
        
        return {
            "success": len(results) > 0,
            "photos_placed": len(results),
            "results": results,
            "errors": errors
        }
    
    async def get_uploaded_photos(self) -> dict:
        """Obtiene las fotos subidas en el panel"""
        await self._ensure_browser()
        
        try:
            # Buscar miniaturas de fotos
            selectors = [
                ".photo-thumb",
                ".thumbnail", 
                ".uploaded-photo",
                ".foto-item",
                ".photo-item",
                "[data-photo]",
                ".galeria img",
                ".photos-list img"
            ]
            
            photos = []
            for selector in selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    for i, el in enumerate(elements):
                        box = await el.bounding_box()
                        if box:
                            photos.append({
                                "index": i,
                                "selector": selector,
                                "x": box["x"] + box["width"] / 2,
                                "y": box["y"] + box["height"] / 2,
                                "width": box["width"],
                                "height": box["height"]
                            })
                    break
            
            return {"success": True, "photos": photos, "count": len(photos)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_canvas_slots(self) -> dict:
        """Detecta los slots/áreas donde se pueden colocar fotos en el canvas"""
        await self._ensure_browser()
        
        try:
            # Buscar el canvas o área de trabajo
            canvas_selectors = [
                "#canvas",
                ".canvas-container",
                ".workspace",
                ".editor-canvas",
                ".page-preview",
                "[data-canvas]"
            ]
            
            canvas = None
            for selector in canvas_selectors:
                canvas = await self.page.query_selector(selector)
                if canvas:
                    break
            
            if not canvas:
                # Intentar encontrar el área principal del editor
                canvas = await self.page.query_selector(".editor-main, .main-content, #editorContainer")
            
            slots = []
            if canvas:
                box = await canvas.bounding_box()
                if box:
                    # Crear slots predefinidos basados en el tamaño del canvas
                    # Layout típico: foto central grande
                    slots.append({
                        "id": "main",
                        "x": box["x"] + box["width"] * 0.5,
                        "y": box["y"] + box["height"] * 0.5,
                        "width": box["width"] * 0.8,
                        "height": box["height"] * 0.8
                    })
            
            # También buscar slots explícitos
            slot_selectors = [
                ".photo-slot",
                ".drop-zone",
                ".placeholder",
                "[data-slot]",
                ".foto-area"
            ]
            
            for selector in slot_selectors:
                elements = await self.page.query_selector_all(selector)
                for i, el in enumerate(elements):
                    box = await el.bounding_box()
                    if box:
                        slots.append({
                            "id": f"slot_{i}",
                            "selector": selector,
                            "x": box["x"] + box["width"] / 2,
                            "y": box["y"] + box["height"] / 2,
                            "width": box["width"],
                            "height": box["height"]
                        })
            
            return {"success": True, "slots": slots, "count": len(slots)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def drag_photo_to_canvas(self, photo_index: int = 0, target_x: float = None, target_y: float = None) -> dict:
        """Arrastra una foto al canvas"""
        await self._ensure_browser()
        
        try:
            # Obtener fotos disponibles
            photos_result = await self.get_uploaded_photos()
            if not photos_result.get("success") or not photos_result.get("photos"):
                return {"success": False, "error": "No hay fotos disponibles para arrastrar"}
            
            photos = photos_result["photos"]
            if photo_index >= len(photos):
                return {"success": False, "error": f"Foto index {photo_index} no existe (hay {len(photos)})"}
            
            photo = photos[photo_index]
            
            # Si no hay target, obtener el centro del canvas
            if target_x is None or target_y is None:
                slots_result = await self.get_canvas_slots()
                if slots_result.get("slots"):
                    target_x = slots_result["slots"][0]["x"]
                    target_y = slots_result["slots"][0]["y"]
                else:
                    # Fallback: centro de la pantalla
                    viewport = self.page.viewport_size
                    target_x = viewport["width"] * 0.6
                    target_y = viewport["height"] * 0.5
            
            print(f"[DOM] Arrastrando foto {photo_index} de ({photo['x']:.0f}, {photo['y']:.0f}) a ({target_x:.0f}, {target_y:.0f})")
            
            # Ejecutar drag & drop
            await self.page.mouse.move(photo["x"], photo["y"])
            await asyncio.sleep(0.2)
            await self.page.mouse.down()
            await asyncio.sleep(0.1)
            
            # Movimiento suave
            steps = 10
            for i in range(steps + 1):
                progress = i / steps
                current_x = photo["x"] + (target_x - photo["x"]) * progress
                current_y = photo["y"] + (target_y - photo["y"]) * progress
                await self.page.mouse.move(current_x, current_y)
                await asyncio.sleep(0.05)
            
            await asyncio.sleep(0.1)
            await self.page.mouse.up()
            await asyncio.sleep(0.5)
            
            print("[DOM] Drag & drop completado")
            return {
                "success": True,
                "photo_index": photo_index,
                "from": {"x": photo["x"], "y": photo["y"]},
                "to": {"x": target_x, "y": target_y}
            }
            
        except Exception as e:
            print(f"[DOM] Error en drag: {e}")
            return {"success": False, "error": str(e)}
    
    async def click_at_position(self, x: float, y: float) -> dict:
        """Click en una posición específica"""
        await self._ensure_browser()
        
        try:
            await self.page.mouse.click(x, y)
            return {"success": True, "x": x, "y": y}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def save_project(self) -> dict:
        """Guarda el proyecto actual"""
        await self._ensure_browser()
        
        try:
            save_selectors = [
                "text=Guardar",
                "text=Save",
                "button:has-text('Guardar')",
                ".save-btn",
                "[data-action='save']",
                "text=Grabar"
            ]
            
            for selector in save_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector, timeout=5000)
                        print(f"[DOM] Guardando con: {selector}")
                        await asyncio.sleep(2)
                        return {"success": True, "message": "Proyecto guardado"}
                except:
                    continue
            
            return {"success": False, "error": "Botón guardar no encontrado"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def go_to_checkout(self) -> dict:
        """Navega al checkout/finalizar pedido"""
        await self._ensure_browser()
        
        try:
            # Primero scroll al final donde suelen estar los botones
            await self.scroll_page("bottom")
            await asyncio.sleep(0.5)
            
            # Selectores específicos de FDF (en orden de prioridad)
            checkout_selectors = [
                # Botones específicos del editor FDF
                "text=Pedir",
                "text=Enviar a Imprimir",
                "text=Finalizar Pedido",
                "text=Agregar al Carrito",
                "text=Ir al Carrito",
                # Botones genéricos
                "text=Finalizar",
                "text=Comprar",
                "text=Checkout",
                "button:has-text('Pedir')",
                "button:has-text('Finalizar')",
                ".checkout-btn",
                "[data-action='checkout']",
                "text=Enviar pedido",
                # Botón en el header del editor
                ".header-actions >> text=Pedir",
                ".toolbar >> text=Pedir"
            ]
            
            for selector in checkout_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(force=True, timeout=5000)
                        print(f"[DOM] Checkout con: {selector}")
                        await asyncio.sleep(3)
                        return {"success": True, "message": "Navegando a checkout"}
                except:
                    continue
            
            # Intentar buscar en el toolbar/header (puede estar fijo arriba)
            await self.scroll_page("top")
            await asyncio.sleep(0.3)
            
            for selector in checkout_selectors[:5]:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(force=True, timeout=5000)
                        print(f"[DOM] Checkout (header) con: {selector}")
                        await asyncio.sleep(3)
                        return {"success": True, "message": "Navegando a checkout"}
                except:
                    continue
            
            return {"success": False, "error": "Botón checkout no encontrado"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # =========================================
    # NAVEGACION ENTRE PAGINAS DEL LIBRO
    # =========================================
    
    async def get_book_pages_info(self) -> dict:
        """
        Obtiene información sobre las páginas del libro:
        - Número total de páginas
        - Página actual
        - Miniaturas de navegación
        
        Usa DOM primero, y si falla usa Vision para detectar el navegador de páginas.
        """
        await self._ensure_browser()
        
        try:
            # Buscar el panel de páginas/miniaturas (generalmente abajo o a un costado)
            pages_info = await self.page.evaluate("""
                () => {
                    const result = {
                        total_pages: 0,
                        current_page: 0,
                        page_thumbnails: [],
                        navigation_type: null
                    };
                    
                    // Buscar indicador de página actual (ej: "Página 1 de 20")
                    const pageText = document.body.innerText.match(/[Pp][áa]gina\\s*(\\d+)\\s*(?:de|\\/)\\s*(\\d+)/);
                    if (pageText) {
                        result.current_page = parseInt(pageText[1]);
                        result.total_pages = parseInt(pageText[2]);
                        result.navigation_type = 'text_indicator';
                    }
                    
                    // Buscar miniaturas de páginas - selectores específicos de FDF
                    const thumbSelectors = [
                        '.page-thumbnail', '.page-thumb', '.pagina-miniatura',
                        '.book-pages img', '.pages-nav img', '.timeline-page',
                        '[data-page]', '.page-item',
                        // Selectores adicionales para FDF
                        '.nav-pages img', '.pages-bar img', '.page-nav-item',
                        '.spread-thumb', '.book-nav img', '.editor-pages img'
                    ];
                    
                    for (const sel of thumbSelectors) {
                        const thumbs = document.querySelectorAll(sel);
                        if (thumbs.length > 0) {
                            result.total_pages = thumbs.length;
                            result.navigation_type = 'thumbnails';
                            
                            thumbs.forEach((thumb, i) => {
                                const rect = thumb.getBoundingClientRect();
                                const isActive = thumb.classList.contains('active') || 
                                               thumb.classList.contains('selected') ||
                                               thumb.classList.contains('current');
                                if (isActive) result.current_page = i + 1;
                                
                                result.page_thumbnails.push({
                                    index: i,
                                    x: rect.x + rect.width / 2,
                                    y: rect.y + rect.height / 2,
                                    is_active: isActive
                                });
                            });
                            break;
                        }
                    }
                    
                    // Buscar botones de navegación
                    const nextBtn = document.querySelector('[class*="next"], [class*="siguiente"], [aria-label*="next"]');
                    const prevBtn = document.querySelector('[class*="prev"], [class*="anterior"], [aria-label*="prev"]');
                    
                    if (nextBtn || prevBtn) {
                        result.has_nav_buttons = true;
                    }
                    
                    return result;
                }
            """)
            
            # Si el DOM no encontró páginas, usar Vision como fallback
            if pages_info.get("total_pages", 0) == 0:
                print("[NAV] DOM no detectó páginas, usando Vision...")
                from .vision_designer import VisionDesigner
                vision = VisionDesigner(api_key=self.model_api_key)
                
                vision_result = await vision.detect_page_navigator(self.page)
                
                if vision_result.get("success") and vision_result.get("navigator_found"):
                    # Convertir formato de Vision al formato esperado
                    thumbnails = vision_result.get("thumbnails", [])
                    current_idx = vision_result.get("current_index", 0)
                    
                    pages_info = {
                        "total_pages": vision_result.get("total_pages", len(thumbnails)),
                        "current_page": current_idx + 1,  # Vision usa 0-indexed
                        "page_thumbnails": [
                            {
                                "index": t.get("index", i),
                                "x": t.get("x", 0),
                                "y": t.get("y", 0),
                                "is_active": t.get("es_activa", i == current_idx),
                                "label": t.get("label", "")
                            }
                            for i, t in enumerate(thumbnails)
                        ],
                        "navigation_type": "vision",
                        "view_type": vision_result.get("view_type", "spreads"),
                        "total_thumbnails": vision_result.get("total_thumbnails", len(thumbnails))
                    }
                    
                    print(f"[NAV] Vision detectó {len(thumbnails)} miniaturas")
                    print(f"[NAV] Total páginas del libro: {pages_info.get('total_pages')}")
                    print(f"[NAV] Vista actual: {vision_result.get('description', 'N/A')}")
                else:
                    print("[NAV] Vision tampoco pudo detectar el navegador de páginas")
                    # Usar valores por defecto basados en configuración típica de FDF
                    pages_info["total_pages"] = 24  # Valor por defecto común
                    pages_info["current_page"] = 1
                    pages_info["navigation_type"] = "default"
            
            print(f"[NAV] Páginas: {pages_info.get('current_page', '?')}/{pages_info.get('total_pages', '?')}")
            print(f"[NAV] Tipo navegación: {pages_info.get('navigation_type', 'unknown')}")
            
            return {"success": True, **pages_info}
            
        except Exception as e:
            print(f"[NAV] Error obteniendo info páginas: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e), "total_pages": 24, "current_page": 1}
    
    async def navigate_to_page(self, page_number: int) -> dict:
        """
        Navega a una página específica del libro.
        
        Args:
            page_number: Número de página (1-indexed)
        """
        await self._ensure_browser()
        
        try:
            print(f"[NAV] Navegando a página {page_number}...")
            
            # Método 1: Clickear en miniatura de página
            pages_info = await self.get_book_pages_info()
            
            if pages_info.get("page_thumbnails"):
                thumbs = pages_info["page_thumbnails"]
                if 0 < page_number <= len(thumbs):
                    thumb = thumbs[page_number - 1]
                    await self.page.mouse.click(thumb["x"], thumb["y"])
                    print(f"[NAV] Clickeada miniatura de página {page_number}")
                    await asyncio.sleep(1.5)
                    return {"success": True, "page": page_number, "method": "thumbnail"}
            
            # Método 2: Usar botones de navegación
            current = pages_info.get("current_page", 1)
            
            if page_number > current:
                # Necesitamos ir hacia adelante
                for _ in range(page_number - current):
                    result = await self.next_page()
                    if not result.get("success"):
                        return result
                    await asyncio.sleep(0.5)
            elif page_number < current:
                # Necesitamos ir hacia atrás
                for _ in range(current - page_number):
                    result = await self.previous_page()
                    if not result.get("success"):
                        return result
                    await asyncio.sleep(0.5)
            
            return {"success": True, "page": page_number, "method": "nav_buttons"}
            
        except Exception as e:
            print(f"[NAV] Error navegando: {e}")
            return {"success": False, "error": str(e)}
    
    async def next_page(self) -> dict:
        """Navega a la siguiente página del libro"""
        await self._ensure_browser()
        
        try:
            # Selectores para botón siguiente
            next_selectors = [
                "text=Siguiente",
                "text=Next",
                "text=>>",
                "text=>",
                "button:has-text('>')",
                "[class*='next']",
                "[class*='siguiente']",
                "[aria-label*='next']",
                "[aria-label*='siguiente']",
                ".page-next",
                ".btn-next",
                "svg[class*='right']",  # Flecha derecha
            ]
            
            for selector in next_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(force=True, timeout=3000)
                        print(f"[NAV] Página siguiente clickeada")
                        await asyncio.sleep(1)
                        return {"success": True, "action": "next"}
                except:
                    continue
            
            # Fallback: Tecla flecha derecha
            await self.page.keyboard.press("ArrowRight")
            print("[NAV] Página siguiente (tecla ->)")
            await asyncio.sleep(1)
            return {"success": True, "action": "next", "method": "keyboard"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def previous_page(self) -> dict:
        """Navega a la página anterior del libro"""
        await self._ensure_browser()
        
        try:
            # Selectores para botón anterior
            prev_selectors = [
                "text=Anterior",
                "text=Previous",
                "text=<<",
                "text=<",
                "button:has-text('<')",
                "[class*='prev']",
                "[class*='anterior']",
                "[aria-label*='prev']",
                "[aria-label*='anterior']",
                ".page-prev",
                ".btn-prev",
                "svg[class*='left']",  # Flecha izquierda
            ]
            
            for selector in prev_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(force=True, timeout=3000)
                        print(f"[NAV] Página anterior clickeada")
                        await asyncio.sleep(1)
                        return {"success": True, "action": "previous"}
                except:
                    continue
            
            # Fallback: Tecla flecha izquierda
            await self.page.keyboard.press("ArrowLeft")
            print("[NAV] Página anterior (tecla <-)")
            await asyncio.sleep(1)
            return {"success": True, "action": "previous", "method": "keyboard"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_current_page_type(self) -> dict:
        """
        Detecta el tipo de página actual:
        - tapa_frontal: Portada del libro
        - tapa_trasera: Contraportada
        - pagina_doble: Dos páginas visibles (interior)
        - pagina_simple: Una sola página
        - lomo: Vista del lomo
        """
        await self._ensure_browser()
        
        from .vision_designer import VisionDesigner
        vision = VisionDesigner(api_key=self.model_api_key)
        
        try:
            # Usar Vision para detectar tipo de página
            result = await vision.analyze_editor(self.page)
            
            if result.get("success"):
                analysis = result.get("analysis", {})
                page_type = analysis.get("tipo_pagina", "unknown")
                
                return {
                    "success": True,
                    "page_type": page_type,
                    "is_cover": page_type in ["tapa_frontal", "tapa_trasera", "portada", "contraportada"],
                    "is_double": page_type in ["pagina_doble", "doble_pagina", "spread"],
                    "details": analysis
                }
            
            return {"success": False, "error": "No se pudo analizar tipo de página"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def design_all_pages(self, estilo: str = "minimalista", max_photos_per_page: int = 4) -> dict:
        """
        Diseña TODAS las páginas del libro automáticamente.
        
        IMPORTANTE: FDF usa "spreads" (vistas de doble página) para navegar.
        Un libro de 24 páginas tiene aproximadamente:
        - 1 vista de Contratapa-Tapa (portada y contraportada)
        - ~11 spreads de páginas interiores (2 páginas por vista)
        
        Args:
            estilo: Estilo del libro (afecta reglas de diseño)
            max_photos_per_page: Máximo de fotos por spread/vista
            
        Returns:
            dict con resumen de páginas diseñadas
        """
        await self._ensure_browser()
        
        from .vision_designer import VisionDesigner
        vision = VisionDesigner(api_key=self.model_api_key)
        
        results = {
            "pages_designed": [],
            "spreads_designed": [],
            "total_photos_placed": 0,
            "errors": []
        }
        
        try:
            # Obtener info del libro
            pages_info = await self.get_book_pages_info()
            total_pages = pages_info.get("total_pages", 24)
            view_type = pages_info.get("view_type", "spreads")
            total_thumbnails = pages_info.get("total_thumbnails", 0)
            page_thumbnails = pages_info.get("page_thumbnails", [])
            
            # FDF muestra spreads (doble página), no páginas individuales
            # Un libro de 24 páginas tiene ~12 spreads (incluyendo tapas)
            if view_type == "spreads" and total_thumbnails > 0:
                total_spreads = total_thumbnails
            else:
                # Si no detectó miniaturas, estimar spreads
                total_spreads = max(1, (total_pages + 1) // 2)
            
            print(f"\n[DESIGN] Iniciando diseño automático")
            print(f"[DESIGN] Total páginas del libro: {total_pages}")
            print(f"[DESIGN] Total spreads/vistas a diseñar: {total_spreads}")
            print(f"[DESIGN] Estilo: {estilo}")
            print(f"[DESIGN] Miniaturas detectadas: {len(page_thumbnails)}")
            print("=" * 60)
            
            # Navegar usando las miniaturas detectadas
            for spread_idx in range(total_spreads):
                print(f"\n[DESIGN] --- Spread {spread_idx + 1}/{total_spreads} ---")
                
                try:
                    # Navegar a esta miniatura/spread
                    if page_thumbnails and spread_idx < len(page_thumbnails):
                        thumb = page_thumbnails[spread_idx]
                        label = thumb.get("label", f"Spread {spread_idx + 1}")
                        print(f"[DESIGN] Navegando a: {label}")
                        
                        # Click en la miniatura
                        if thumb.get("x") and thumb.get("y"):
                            await self.page.mouse.click(thumb["x"], thumb["y"])
                            await asyncio.sleep(2)  # Esperar que cargue el spread
                    else:
                        # Sin miniaturas, usar navegación secuencial
                        if spread_idx > 0:
                            await self.next_page()
                            await asyncio.sleep(1.5)
                    
                    # Detectar tipo de spread actual
                    page_type_info = await self.get_current_page_type()
                    page_type = page_type_info.get("page_type", "interior")
                    is_cover = page_type_info.get("is_cover", False)
                    is_double = page_type_info.get("is_double", True)  # Casi siempre es doble en FDF
                    
                    print(f"[DESIGN] Tipo: {page_type} (cover={is_cover}, double={is_double})")
                    
                    # Determinar cantidad de fotos para este spread
                    if is_cover:
                        # Tapa: portada + contraportada (2-3 fotos)
                        photos_for_spread = min(3, max_photos_per_page)
                    else:
                        # Interior: es doble página, puede tener más fotos
                        photos_for_spread = max_photos_per_page
                    
                    # Auto-fill con Vision
                    fill_result = await self.auto_fill_page_with_vision(max_photos=photos_for_spread)
                    
                    photos_placed = fill_result.get("photos_placed", 0)
                    results["total_photos_placed"] += photos_placed
                    
                    # Verificar reglas de diseño
                    verify = await vision.verify_design_rules(self.page)
                    
                    spread_result = {
                        "spread": spread_idx + 1,
                        "type": page_type,
                        "photos_placed": photos_placed,
                        "rules_score": verify.get("score", 0),
                        "issues": verify.get("critical_issues", [])
                    }
                    results["spreads_designed"].append(spread_result)
                    results["pages_designed"].append(spread_result)  # Compatibilidad
                    
                    print(f"[DESIGN] Fotos colocadas: {photos_placed}")
                    print(f"[DESIGN] Score diseño: {verify.get('score', 0)}/100")
                    
                    # Tomar screenshot del spread diseñado
                    await self.take_screenshot(f"design_spread_{spread_idx + 1:02d}.png")
                    
                except Exception as e:
                    print(f"[DESIGN] Error en spread {spread_idx + 1}: {e}")
                    results["errors"].append({
                        "spread": spread_idx + 1,
                        "error": str(e)
                    })
                    # Continuar con el siguiente spread
                    try:
                        await self.next_page()
                        await asyncio.sleep(1)
                    except:
                        pass
            
            print(f"\n[DESIGN] === DISEÑO COMPLETADO ===")
            print(f"[DESIGN] Spreads diseñados: {len(results['spreads_designed'])}")
            print(f"[DESIGN] Total fotos colocadas: {results['total_photos_placed']}")
            print(f"[DESIGN] Errores: {len(results['errors'])}")
            
            return {"success": True, **results}
            
        except Exception as e:
            print(f"[DESIGN] Error general: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e), **results}
    
    async def take_screenshot(self, path: Optional[str] = None, full_page: bool = False) -> dict:
        """Captura screenshot para debug"""
        await self._ensure_browser()
        
        if not path:
            path = f"screenshot_{asyncio.get_event_loop().time():.0f}.png"
        
        await self.page.screenshot(path=path, full_page=full_page)
        return {"success": True, "path": path, "full_page": full_page}
    
    # =========================================
    # FUNCIONES DE LOMO Y DOBLE PÁGINA
    # =========================================
    
    async def add_spine_text(self, text: str, font_size: int = 12) -> dict:
        """
        Agrega texto rotado 90 grados al lomo del libro.
        
        PROCESO:
        1. Detectar zona del lomo (entre líneas punteadas)
        2. Insertar cuadro de texto
        3. Escribir el texto
        4. Rotar 90 grados usando el tirador circular
        5. Centrar en el lomo
        
        Args:
            text: Texto a colocar en el lomo
            font_size: Tamaño de fuente (ajustar según grosor del lomo)
        """
        await self._ensure_browser()
        
        try:
            from .vision_designer import VisionDesigner
            vision = VisionDesigner(api_key=self.model_api_key)
            
            print(f"[LOMO] Agregando texto al lomo: '{text}'")
            
            # 1. Detectar zona del lomo con Vision
            spine_plan = await vision.plan_spine_text(self.page, text)
            
            if not spine_plan.get("success") or not spine_plan.get("spine_detected"):
                return {"success": False, "error": "No se detectó la zona del lomo"}
            
            spine_coords = spine_plan.get("spine_coords", {})
            text_position = spine_plan.get("text_position", {})
            
            print(f"[LOMO] Lomo detectado en x={spine_coords.get('centro_x')}")
            
            # 2. Click en herramienta de texto
            text_tool_selectors = [
                "text=Texto",
                "[data-tool='text']",
                ".text-tool",
                "button:has-text('T')",
                ".tool-text"
            ]
            
            tool_clicked = False
            for selector in text_tool_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector, force=True, timeout=3000)
                        tool_clicked = True
                        print(f"[LOMO] Herramienta texto activada: {selector}")
                        break
                except:
                    continue
            
            if not tool_clicked:
                return {"success": False, "error": "No se pudo activar herramienta de texto"}
            
            await asyncio.sleep(0.5)
            
            # 3. Click en la posición del lomo para crear cuadro de texto
            target_x = text_position.get("x", spine_coords.get("centro_x", 500))
            target_y = text_position.get("y", 400)
            
            await self.page.mouse.click(target_x, target_y)
            await asyncio.sleep(0.5)
            
            # 4. Escribir el texto
            await self.page.keyboard.type(text, delay=50)
            await asyncio.sleep(0.3)
            
            # 5. Rotar 90 grados - buscar el tirador de rotación
            # Primero seleccionar el cuadro de texto si no está seleccionado
            await self.page.mouse.click(target_x, target_y)
            await asyncio.sleep(0.3)
            
            # Buscar y usar el control de rotación
            rotation_applied = False
            
            # Método 1: Buscar input de rotación en panel de propiedades
            rotation_selectors = [
                "input[name='rotation']",
                "input[type='number'][max='360']",
                ".rotation-input",
                "[data-property='rotation']"
            ]
            
            for selector in rotation_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.fill(selector, "90")
                        rotation_applied = True
                        print("[LOMO] Rotación aplicada via input")
                        break
                except:
                    continue
            
            # Método 2: Usar JavaScript para rotar el elemento seleccionado
            if not rotation_applied:
                try:
                    await self.page.evaluate("""
                        () => {
                            // Buscar elemento seleccionado y rotarlo
                            const selected = document.querySelector('.selected, .active, [data-selected]');
                            if (selected) {
                                selected.style.transform = 'rotate(90deg)';
                                return true;
                            }
                            return false;
                        }
                    """)
                    rotation_applied = True
                    print("[LOMO] Rotación aplicada via JavaScript")
                except:
                    pass
            
            await asyncio.sleep(0.5)
            
            return {
                "success": True,
                "text": text,
                "position": {"x": target_x, "y": target_y},
                "rotation_applied": rotation_applied,
                "spine_coords": spine_coords
            }
            
        except Exception as e:
            print(f"[LOMO] Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def adjust_photo_for_double_page(self, direction: str = "auto") -> dict:
        """
        Ajusta una foto en doble página para evitar que los rostros queden en el lomo.
        
        REGLA CRÍTICA: Para fotos que ocupan ambas páginas, desplazar el motivo 
        principal (personas/caras) hacia un lado para que no queden cortados por el lomo.
        
        Args:
            direction: Dirección del ajuste (auto|izquierda|derecha)
                      'auto' analiza la foto y decide la mejor dirección
        """
        await self._ensure_browser()
        
        try:
            from .vision_designer import VisionDesigner
            vision = VisionDesigner(api_key=self.model_api_key)
            
            print(f"[DOUBLE] Ajustando foto para doble página (dirección: {direction})")
            
            # 1. Analizar si la foto es apta para doble página
            analysis = await vision.analyze_double_page_photo(self.page)
            
            if not analysis.get("success"):
                return {"success": False, "error": "No se pudo analizar la foto"}
            
            print(f"[DOUBLE] Tipo contenido: {analysis.get('content_type')}")
            print(f"[DOUBLE] Tiene rostros: {analysis.get('has_faces')}")
            print(f"[DOUBLE] Rostros en centro: {analysis.get('faces_in_center')}")
            
            # 2. Determinar si necesita ajuste
            needs_adjustment = analysis.get("needs_adjustment", False)
            
            if not needs_adjustment:
                print("[DOUBLE] La foto no necesita ajuste - contenido seguro en el lomo")
                return {
                    "success": True,
                    "adjustment_needed": False,
                    "reason": "Contenido seguro en zona del lomo"
                }
            
            # 3. Determinar dirección del ajuste
            if direction == "auto":
                adjustment = analysis.get("adjustment", {})
                direction = adjustment.get("accion", "desplazar_derecha")
                if "izquierda" in direction:
                    direction = "izquierda"
                elif "derecha" in direction:
                    direction = "derecha"
                else:
                    direction = "derecha"  # Default
            
            print(f"[DOUBLE] Dirección de ajuste: {direction}")
            
            # 4. Activar herramienta mano y ajustar
            # Click en la foto para seleccionarla
            # La herramienta mano aparece automáticamente al hacer click en una foto
            
            # Obtener sugerencia de ajuste precisa
            pan_suggestion = await vision.suggest_photo_pan_adjustment(self.page, direction)
            
            if pan_suggestion.get("success") and pan_suggestion.get("needs_adjustment"):
                pan_info = pan_suggestion.get("pan_adjustment", {})
                intensity = pan_info.get("intensidad_px", 50)
                
                # Calcular movimiento
                delta_x = -intensity if direction == "izquierda" else intensity
                
                # Ejecutar el pan (mover imagen dentro del marco)
                # Esto simula arrastrar con la herramienta mano
                try:
                    # Obtener centro de la foto
                    hand_tool = pan_suggestion.get("hand_tool", {})
                    current_pos = hand_tool.get("posicion_actual", {"x": 500, "y": 400})
                    
                    start_x = current_pos.get("x", 500)
                    start_y = current_pos.get("y", 400)
                    
                    # Simular drag
                    await self.page.mouse.move(start_x, start_y)
                    await self.page.mouse.down()
                    await self.page.mouse.move(start_x + delta_x, start_y, steps=10)
                    await self.page.mouse.up()
                    
                    print(f"[DOUBLE] Pan aplicado: {delta_x}px en X")
                    
                    await asyncio.sleep(0.5)
                    
                    return {
                        "success": True,
                        "adjustment_needed": True,
                        "direction": direction,
                        "pan_applied": delta_x,
                        "reason": pan_info.get("motivo", "Ajuste para evitar lomo"),
                        "instructions_followed": pan_suggestion.get("instructions", [])
                    }
                    
                except Exception as e:
                    print(f"[DOUBLE] Error aplicando pan: {e}")
                    return {
                        "success": False,
                        "error": f"Error aplicando ajuste: {e}",
                        "instructions": pan_suggestion.get("instructions", [])
                    }
            
            return {
                "success": True,
                "adjustment_needed": needs_adjustment,
                "manual_adjustment_required": True,
                "instructions": pan_suggestion.get("instructions", []),
                "expected_result": pan_suggestion.get("expected_result", "")
            }
            
        except Exception as e:
            print(f"[DOUBLE] Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def detect_and_highlight_cover_zones(self) -> dict:
        """
        Detecta y resalta las zonas de la tapa: Contratapa, Lomo, Portada.
        Útil para debugging y para mostrar al usuario dónde colocar elementos.
        """
        await self._ensure_browser()
        
        try:
            from .vision_designer import VisionDesigner
            vision = VisionDesigner(api_key=self.model_api_key)
            
            print("[COVER] Detectando zonas de la tapa...")
            
            zones = await vision.detect_cover_zones(self.page)
            
            if not zones.get("success"):
                return {"success": False, "error": "No se pudieron detectar las zonas"}
            
            if not zones.get("is_cover_view"):
                return {
                    "success": False,
                    "error": "No estamos en la vista de tapa",
                    "current_view": "interior"
                }
            
            zone_info = zones.get("zones", {})
            
            print(f"[COVER] Vista de tapa detectada:")
            print(f"  - Contratapa: {zone_info.get('contratapa', {})}")
            print(f"  - Lomo: {zone_info.get('lomo', {})}")
            print(f"  - Portada: {zone_info.get('portada', {})}")
            
            return {
                "success": True,
                "is_cover_view": True,
                "zones": zone_info,
                "dotted_lines_visible": zones.get("dotted_lines_visible", False),
                "current_elements": zones.get("current_elements", {}),
                "recommendations": zones.get("recommendations", [])
            }
            
        except Exception as e:
            print(f"[COVER] Error: {e}")
            return {"success": False, "error": str(e)}
    
    async def verify_spine_safety(self) -> dict:
        """
        Verifica que no haya contenido peligroso en la zona del lomo.
        
        REGLA: NUNCA colocar rostros, caras o texto importante en el centro exacto.
        """
        await self._ensure_browser()
        
        try:
            from .vision_designer import VisionDesigner
            vision = VisionDesigner(api_key=self.model_api_key)
            
            print("[SAFETY] Verificando seguridad del lomo...")
            
            # Verificar reglas de diseño
            verification = await vision.verify_design_rules(self.page)
            
            if not verification.get("success"):
                return {"success": False, "error": "No se pudo verificar el diseño"}
            
            # Buscar problemas específicos del lomo
            critical_issues = verification.get("critical_issues", [])
            spine_issues = [
                issue for issue in critical_issues 
                if "lomo" in issue.get("tipo", "").lower() or 
                   "rostro" in issue.get("descripcion", "").lower() or
                   "centro" in issue.get("descripcion", "").lower()
            ]
            
            is_safe = len(spine_issues) == 0
            
            result = {
                "success": True,
                "spine_is_safe": is_safe,
                "overall_score": verification.get("score", 0),
                "spine_issues": spine_issues,
                "all_issues": critical_issues,
                "warnings": verification.get("warnings", []),
                "recommendations": verification.get("recommendations", [])
            }
            
            if is_safe:
                print("[SAFETY] Lomo seguro - no hay contenido peligroso")
            else:
                print(f"[SAFETY] ADVERTENCIA: {len(spine_issues)} problema(s) en el lomo")
                for issue in spine_issues:
                    print(f"  - {issue.get('descripcion')}")
                    print(f"    Solución: {issue.get('solucion')}")
            
            return result
            
        except Exception as e:
            print(f"[SAFETY] Error: {e}")
            return {"success": False, "error": str(e)}
    
    # =========================================
    # FUNCIONES DE TEXTO Y STICKERS
    # =========================================
    
    async def add_cover_title(self, text: str, font_size: int = 24) -> dict:
        """
        Agrega un título en la PORTADA del libro (zona derecha de la vista Tapa).
        
        PROCESO:
        1. Verificar que estamos en vista de Tapa (Contratapa-Tapa)
        2. Detectar zona de portada con Vision
        3. Click en herramienta de texto (icono "Tt" en lateral izquierdo)
        4. Click en posición centro-inferior de la portada
        5. Escribir el texto
        
        Args:
            text: Título a agregar en la portada
            font_size: Tamaño de fuente (default 24)
        """
        await self._ensure_browser()
        
        try:
            from .vision_designer import VisionDesigner
            vision = VisionDesigner(api_key=self.model_api_key)
            
            print(f"[TITLE] Agregando título en portada: '{text}'")
            
            # 1. Detectar zonas de la tapa
            zones = await vision.detect_cover_zones(self.page)
            
            if not zones.get("success"):
                # Si no detecta, usar posición estimada (centro-derecha del canvas)
                print("[TITLE] No se detectaron zonas, usando posición estimada")
                viewport = self.page.viewport_size
                target_x = int(viewport["width"] * 0.7)  # 70% a la derecha (portada)
                target_y = int(viewport["height"] * 0.6)  # 60% abajo
            else:
                portada = zones.get("zones", {}).get("portada", {})
                if portada:
                    target_x = portada.get("centro_x", 800)
                    target_y = portada.get("centro_y", 400) + 100  # Un poco más abajo del centro
                else:
                    viewport = self.page.viewport_size
                    target_x = int(viewport["width"] * 0.7)
                    target_y = int(viewport["height"] * 0.6)
            
            print(f"[TITLE] Posición objetivo: ({target_x}, {target_y})")
            
            # 2. Activar herramienta de texto
            text_tool_selectors = [
                "text=Tt",
                ".text-tool",
                "[data-tool='text']",
                "button:has-text('T')",
                ".btn-add-text",
                "[aria-label='Texto']",
                "[aria-label='Agregar texto']"
            ]
            
            tool_clicked = False
            for selector in text_tool_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(force=True, timeout=3000)
                        tool_clicked = True
                        print(f"[TITLE] Herramienta texto activada: {selector}")
                        break
                except:
                    continue
            
            # Fallback: buscar en el panel lateral izquierdo
            if not tool_clicked:
                try:
                    # Buscar icono de texto en el panel de herramientas
                    lateral_tools = await self.page.query_selector_all(".tool-item, .toolbar-item, .btn-tool")
                    for tool in lateral_tools[:10]:
                        text_content = await tool.text_content() or ""
                        if "T" in text_content or "texto" in text_content.lower():
                            await tool.click()
                            tool_clicked = True
                            print("[TITLE] Herramienta texto activada (panel lateral)")
                            break
                except:
                    pass
            
            if not tool_clicked:
                print("[TITLE] ADVERTENCIA: No se encontró herramienta de texto, intentando click directo")
            
            await asyncio.sleep(0.5)
            
            # 3. Click en la posición de la portada para crear cuadro de texto
            await self.page.mouse.click(target_x, target_y)
            await asyncio.sleep(0.5)
            
            # 4. Escribir el texto
            await self.page.keyboard.type(text, delay=30)
            await asyncio.sleep(0.3)
            
            # 5. Click fuera para deseleccionar
            await self.page.mouse.click(target_x + 200, target_y + 100)
            await asyncio.sleep(0.3)
            
            print(f"[TITLE] Título agregado en portada")
            
            return {
                "success": True,
                "text": text,
                "position": {"x": target_x, "y": target_y},
                "font_size": font_size
            }
            
        except Exception as e:
            print(f"[TITLE] Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def add_sticker(self, sticker_type: str = "estrella", x: int = None, y: int = None) -> dict:
        """
        Agrega un sticker/clipart al canvas.
        
        PROCESO:
        1. Abrir panel de Cliparts (buscar en menú "Temas" o panel lateral)
        2. Buscar sticker por tipo
        3. Arrastrarlo a la posición indicada
        4. Si no se indica posición, usar esquina inferior derecha
        
        Args:
            sticker_type: Tipo de sticker (estrella, corazon, globo, flor, etc.)
            x: Posición X (opcional, si no se indica se usa posición automática)
            y: Posición Y (opcional)
        
        Stickers disponibles según estilo:
        - divertido: estrellas, corazones, globos, confeti, emojis
        - clasico: marcos dorados, esquinas decorativas, adornos florales
        - premium: elementos dorados, plateados, marcos elegantes
        """
        await self._ensure_browser()
        
        try:
            print(f"[STICKER] Agregando sticker tipo '{sticker_type}'")
            
            # Determinar posición si no se especificó
            if x is None or y is None:
                viewport = self.page.viewport_size
                # Por defecto, esquina inferior derecha del canvas
                x = x or int(viewport["width"] * 0.85)
                y = y or int(viewport["height"] * 0.75)
            
            print(f"[STICKER] Posición objetivo: ({x}, {y})")
            
            # 1. Buscar y abrir panel de cliparts/stickers
            clipart_selectors = [
                "text=Temas",
                "text=Cliparts",
                "text=Stickers",
                "text=Adornos",
                ".btn-stickers",
                "[aria-label='Stickers']",
                "[aria-label='Cliparts']",
                ".clipart-panel-toggle"
            ]
            
            panel_opened = False
            for selector in clipart_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(force=True, timeout=3000)
                        panel_opened = True
                        print(f"[STICKER] Panel abierto con: {selector}")
                        await asyncio.sleep(1)
                        break
                except:
                    continue
            
            if not panel_opened:
                print("[STICKER] ADVERTENCIA: No se pudo abrir panel de cliparts")
                # Continuar de todas formas - el template puede tener stickers integrados
            
            # 2. Buscar sticker específico
            sticker_keywords = {
                "estrella": ["estrella", "star", "★"],
                "corazon": ["corazon", "corazón", "heart", "♥", "❤"],
                "globo": ["globo", "balloon", "🎈"],
                "flor": ["flor", "flower", "🌸", "🌺"],
                "confeti": ["confeti", "confetti"],
                "marco": ["marco", "frame", "borde"],
                "dorado": ["dorado", "gold", "golden"],
            }
            
            keywords = sticker_keywords.get(sticker_type.lower(), [sticker_type])
            
            sticker_found = False
            for keyword in keywords:
                try:
                    # Buscar elementos que coincidan
                    sticker_locator = self.page.locator(f"text=/{keyword}/i, img[alt*='{keyword}'], [title*='{keyword}']").first
                    if await sticker_locator.count() > 0 and await sticker_locator.is_visible():
                        # Obtener posición del sticker
                        sticker_box = await sticker_locator.bounding_box()
                        if sticker_box:
                            sticker_x = sticker_box["x"] + sticker_box["width"] / 2
                            sticker_y = sticker_box["y"] + sticker_box["height"] / 2
                            
                            # Drag & drop al canvas
                            await self.page.mouse.move(sticker_x, sticker_y)
                            await self.page.mouse.down()
                            await asyncio.sleep(0.1)
                            
                            # Mover al destino
                            steps = 10
                            for i in range(steps):
                                progress = (i + 1) / steps
                                current_x = sticker_x + (x - sticker_x) * progress
                                current_y = sticker_y + (y - sticker_y) * progress
                                await self.page.mouse.move(current_x, current_y)
                                await asyncio.sleep(0.02)
                            
                            await self.page.mouse.up()
                            sticker_found = True
                            print(f"[STICKER] Sticker '{keyword}' arrastrado a ({x}, {y})")
                            break
                except:
                    continue
            
            # Si no se encontró sticker específico, intentar agregar uno genérico
            if not sticker_found:
                print(f"[STICKER] No se encontró sticker '{sticker_type}', intentando alternativa...")
                
                # Buscar cualquier elemento de clipart disponible
                try:
                    cliparts = await self.page.query_selector_all(".clipart-item, .sticker-item, .decoration-item")
                    if cliparts and len(cliparts) > 0:
                        # Usar el primer clipart disponible
                        first_clipart = cliparts[0]
                        box = await first_clipart.bounding_box()
                        if box:
                            await self.page.mouse.move(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                            await self.page.mouse.down()
                            await asyncio.sleep(0.1)
                            await self.page.mouse.move(x, y)
                            await self.page.mouse.up()
                            sticker_found = True
                            print("[STICKER] Clipart genérico agregado")
                except:
                    pass
            
            # Cerrar panel si estaba abierto
            if panel_opened:
                await self.page.keyboard.press("Escape")
                await asyncio.sleep(0.3)
            
            return {
                "success": sticker_found,
                "sticker_type": sticker_type,
                "position": {"x": x, "y": y},
                "note": "Sticker agregado" if sticker_found else "No se encontró sticker, pero se intentó"
            }
            
        except Exception as e:
            print(f"[STICKER] Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def add_photo_caption(self, text: str, photo_index: int = 0) -> dict:
        """
        Agrega un pie de foto debajo de una foto en la página actual.
        
        PROCESO:
        1. Detectar fotos en la página con Vision
        2. Calcular posición debajo de la foto indicada
        3. Activar herramienta de texto
        4. Click debajo de la foto
        5. Escribir el texto con fuente pequeña
        
        Args:
            text: Texto del pie de foto
            photo_index: Índice de la foto (0 = primera foto visible)
        """
        await self._ensure_browser()
        
        try:
            from .vision_designer import VisionDesigner
            vision = VisionDesigner(api_key=self.model_api_key)
            
            print(f"[CAPTION] Agregando pie de foto: '{text}'")
            
            # 1. Detectar fotos/slots en la página
            analysis = await vision.analyze_current_spread(self.page)
            
            if not analysis.get("success"):
                print("[CAPTION] No se pudo analizar la página, usando posición estimada")
                viewport = self.page.viewport_size
                target_x = int(viewport["width"] * 0.5)
                target_y = int(viewport["height"] * 0.7)
            else:
                slots = analysis.get("slots_detectados", [])
                if slots and photo_index < len(slots):
                    slot = slots[photo_index]
                    # Posicionar debajo del slot
                    target_x = slot.get("x", 500)
                    target_y = slot.get("y", 400) + slot.get("alto", 100) + 20  # 20px debajo
                else:
                    # Usar posición central inferior
                    viewport = self.page.viewport_size
                    target_x = int(viewport["width"] * 0.5)
                    target_y = int(viewport["height"] * 0.7)
            
            print(f"[CAPTION] Posición objetivo: ({target_x}, {target_y})")
            
            # 2. Activar herramienta de texto
            text_tool_selectors = [
                "text=Tt",
                ".text-tool",
                "[data-tool='text']",
                ".btn-add-text"
            ]
            
            tool_clicked = False
            for selector in text_tool_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0 and await locator.is_visible():
                        await locator.click(force=True, timeout=3000)
                        tool_clicked = True
                        print(f"[CAPTION] Herramienta texto activada")
                        break
                except:
                    continue
            
            await asyncio.sleep(0.5)
            
            # 3. Click en la posición para crear cuadro de texto
            await self.page.mouse.click(target_x, target_y)
            await asyncio.sleep(0.5)
            
            # 4. Escribir el texto
            await self.page.keyboard.type(text, delay=30)
            await asyncio.sleep(0.3)
            
            # 5. Click fuera para deseleccionar
            await self.page.mouse.click(target_x + 100, target_y + 50)
            
            print(f"[CAPTION] Pie de foto agregado")
            
            return {
                "success": True,
                "text": text,
                "position": {"x": target_x, "y": target_y},
                "photo_index": photo_index
            }
            
        except Exception as e:
            print(f"[CAPTION] Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def scroll_page(self, direction: str = "down", amount: int = 500) -> dict:
        """
        Hace scroll en la página.
        direction: 'down', 'up', 'bottom', 'top'
        amount: píxeles a scrollear (para down/up)
        """
        await self._ensure_browser()
        
        try:
            if direction == "bottom":
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                print("[DOM] Scroll al final de la página")
            elif direction == "top":
                await self.page.evaluate("window.scrollTo(0, 0)")
                print("[DOM] Scroll al inicio de la página")
            elif direction == "down":
                await self.page.evaluate(f"window.scrollBy(0, {amount})")
                print(f"[DOM] Scroll down {amount}px")
            elif direction == "up":
                await self.page.evaluate(f"window.scrollBy(0, -{amount})")
                print(f"[DOM] Scroll up {amount}px")
            
            await asyncio.sleep(0.5)  # Esperar que se renderice
            return {"success": True, "direction": direction}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_scroll_info(self) -> dict:
        """Obtiene información sobre el scroll de la página"""
        await self._ensure_browser()
        
        try:
            info = await self.page.evaluate("""
                () => ({
                    scrollTop: window.scrollY,
                    scrollHeight: document.body.scrollHeight,
                    clientHeight: window.innerHeight,
                    canScrollDown: window.scrollY + window.innerHeight < document.body.scrollHeight,
                    canScrollUp: window.scrollY > 0,
                    scrollPercent: Math.round((window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100)
                })
            """)
            return {"success": True, "info": info}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_page_info(self) -> dict:
        """Obtiene información de la página actual"""
        await self._ensure_browser()
        
        url = self.page.url
        title = await self.page.title()
        
        # Detectar tipo de página
        content = await self.page.content()
        
        page_type = "unknown"
        if "login" in url.lower() or "email_log" in content:
            page_type = "login"
        elif "online.fabricadefotolibros.com" in url:
            # Estamos en el editor online
            if "canvas" in content.lower() or "editorContainer" in content or "workspace" in content.lower():
                page_type = "editor"
            else:
                page_type = "editor_loading"
        elif "Fotolibros" in content and "Calendarios" in content:
            page_type = "catalog_main"
        elif "21x21" in content or "Tapa Dura" in content:
            page_type = "catalog_products"
        elif "Crear Proyecto" in content:
            page_type = "product_config"
        
        return {
            "url": url,
            "title": title,
            "page_type": page_type
        }
    
    async def wait_for_editor(self, timeout: int = 30) -> dict:
        """Espera a que el editor esté completamente cargado"""
        await self._ensure_browser()
        
        print("[DOM] Esperando que cargue el editor...")
        
        for i in range(timeout):
            info = await self.get_page_info()
            if info["page_type"] == "editor":
                print(f"[DOM] Editor cargado en {i+1} segundos")
                return {"success": True, "page_info": info}
            await asyncio.sleep(1)
        
        return {"success": False, "error": "Timeout esperando editor", "page_info": info}
    
    # =========================================
    # METODOS HIBRIDOS (Pattern Cache + Stagehand)
    # =========================================
    
    async def select_template_hybrid(self, template_name: str, for_editors: bool = True) -> dict:
        """
        Seleccion HIBRIDA de template:
        1. Intenta con Pattern Cache (si tenemos coordenadas guardadas)
        2. Si no, intenta con Stagehand (self-healing)
        3. Fallback a metodo Playwright original
        
        Args:
            template_name: Nombre del template (ej: "Vacio", "Clasico")
            for_editors: Si True, busca version "para Editores"
        """
        await self._ensure_browser()
        viewport = self.page.viewport_size
        
        # 1. Intentar con Pattern Cache
        cache_key = f"{template_name}_{'ED' if for_editors else 'CL'}"
        cached = self.cache.get_cached_template(
            cache_key,
            viewport["width"],
            viewport["height"]
        )
        
        if cached:
            self._stats["cache_hits"] += 1
            logger.info(f"[Hybrid] Template '{template_name}' desde cache")
            
            try:
                await self.page.mouse.click(cached["x"], cached["y"])
                await asyncio.sleep(1)
                self.cache.mark_slot_success(cache_key, "card", viewport["width"], viewport["height"])
                return {"success": True, "method": "cache", "template": template_name}
            except Exception as e:
                logger.warning(f"[Hybrid] Cache click fallo: {e}")
                self.cache.mark_slot_failure(cache_key, "card", viewport["width"], viewport["height"])
        
        self._stats["cache_misses"] += 1
        
        # 2. Intentar con Stagehand (si disponible)
        if self.use_stagehand:
            try:
                if await self._ensure_stagehand():
                    self._stats["stagehand_calls"] += 1
                    logger.info(f"[Hybrid] Usando Stagehand para '{template_name}'")
                    
                    result = await self._stagehand_actions.select_template(template_name, for_editors)
                    
                    if result.get("success"):
                        # Guardar en cache para proxima vez
                        # Detectar posicion del template clickeado
                        await asyncio.sleep(0.5)
                        return {"success": True, "method": "stagehand", "template": template_name}
            except Exception as e:
                logger.warning(f"[Hybrid] Stagehand fallo: {e}")
        
        # 3. Fallback a metodo original (Playwright)
        self._stats["playwright_calls"] += 1
        logger.info(f"[Hybrid] Fallback a Playwright para '{template_name}'")
        return await self.select_template(template_name, for_editors)
    
    async def drag_photo_to_slot_hybrid(
        self,
        photo_index: int,
        layout_name: str,
        slot_id: str
    ) -> dict:
        """
        Drag & drop HIBRIDO:
        1. Busca coordenadas en Pattern Cache (rapido, sin Vision)
        2. Si no hay cache, usa Vision para detectar y guarda en cache
        3. Ejecuta drag con Playwright
        
        Args:
            photo_index: Indice de la foto (0-based)
            layout_name: Nombre del layout actual
            slot_id: ID del slot destino
        """
        await self._ensure_browser()
        viewport = self.page.viewport_size
        
        # 1. Intentar obtener slot del cache
        cached_slot = self.cache.get_cached_slot(
            layout_name, slot_id,
            viewport["width"], viewport["height"]
        )
        
        if cached_slot:
            self._stats["cache_hits"] += 1
            logger.info(f"[Hybrid] Slot '{slot_id}' desde cache (hit #{cached_slot.get('hit_count', 1)})")
            
            target_x = cached_slot["center_x"]
            target_y = cached_slot["center_y"]
        else:
            self._stats["cache_misses"] += 1
            self._stats["vision_calls"] += 1
            
            # 2. Usar Vision para detectar
            logger.info(f"[Hybrid] Detectando slot '{slot_id}' con Vision...")
            
            from .vision_designer import VisionDesigner
            vision = VisionDesigner(api_key=self.model_api_key)
            
            slots_info = await vision.find_photo_slots(self.page)
            
            if not slots_info.get("success") or not slots_info.get("slots"):
                return {"success": False, "error": "No se pudieron detectar slots"}
            
            # Buscar el slot especifico o usar el primero
            slots = slots_info.get("slots", [])
            target_slot = None
            
            for slot in slots:
                if slot.get("id") == slot_id or slot.get("tipo") == slot_id:
                    target_slot = slot
                    break
            
            if not target_slot and slots:
                target_slot = slots[0]
            
            if not target_slot:
                return {"success": False, "error": f"Slot '{slot_id}' no encontrado"}
            
            target_x = target_slot.get("x", target_slot.get("center_x", 500))
            target_y = target_slot.get("y", target_slot.get("center_y", 400))
            
            # Guardar en cache para proximas veces
            self.cache.save_slot_pattern(
                layout_name, slot_id,
                viewport["width"], viewport["height"],
                {
                    "x": target_slot.get("x", target_x - 50),
                    "y": target_slot.get("y", target_y - 50),
                    "width": target_slot.get("width", 100),
                    "height": target_slot.get("height", 100),
                    "center_x": target_x,
                    "center_y": target_y
                },
                confidence=0.8
            )
            logger.info(f"[Hybrid] Slot '{slot_id}' guardado en cache")
        
        # 3. Obtener foto del panel
        photos_result = await self.get_uploaded_photos()
        if not photos_result.get("success") or not photos_result.get("photos"):
            return {"success": False, "error": "No hay fotos disponibles"}
        
        photos = photos_result["photos"]
        if photo_index >= len(photos):
            return {"success": False, "error": f"Foto index {photo_index} no existe"}
        
        photo = photos[photo_index]
        
        # 4. Ejecutar drag & drop
        self._stats["playwright_calls"] += 1
        
        logger.info(f"[Hybrid] Drag foto {photo_index} de ({photo['x']:.0f},{photo['y']:.0f}) a ({target_x:.0f},{target_y:.0f})")
        
        await self.page.mouse.move(photo["x"], photo["y"])
        await asyncio.sleep(0.2)
        await self.page.mouse.down()
        await asyncio.sleep(0.1)
        
        # Movimiento suave
        steps = 12
        for i in range(steps + 1):
            progress = i / steps
            current_x = photo["x"] + (target_x - photo["x"]) * progress
            current_y = photo["y"] + (target_y - photo["y"]) * progress
            await self.page.mouse.move(current_x, current_y)
            await asyncio.sleep(0.02)
        
        await asyncio.sleep(0.1)
        await self.page.mouse.up()
        await asyncio.sleep(0.5)
        
        # Marcar exito en cache
        if cached_slot:
            self.cache.mark_slot_success(layout_name, slot_id, viewport["width"], viewport["height"])
        
        return {
            "success": True,
            "method": "cache" if cached_slot else "vision",
            "photo_index": photo_index,
            "slot_id": slot_id,
            "from": {"x": photo["x"], "y": photo["y"]},
            "to": {"x": target_x, "y": target_y}
        }
    
    async def auto_fill_page_hybrid(self, max_photos: int = 4, layout_name: str = "auto") -> dict:
        """
        Llena automaticamente la pagina usando enfoque hibrido:
        1. Detecta slots (cache o Vision)
        2. Detecta fotos disponibles
        3. Asigna fotos a slots inteligentemente
        4. Ejecuta drag & drop para cada foto
        
        Args:
            max_photos: Maximo de fotos a colocar
            layout_name: Nombre del layout (o "auto" para detectar)
        """
        await self._ensure_browser()
        
        results = []
        errors = []
        
        logger.info(f"[Hybrid] Auto-fill iniciado (max {max_photos} fotos)")
        
        # Detectar layout si es auto
        if layout_name == "auto":
            layout_name = self.current_layout or "default"
        
        for i in range(max_photos):
            slot_id = f"slot_{i}"
            
            result = await self.drag_photo_to_slot_hybrid(
                photo_index=i,
                layout_name=layout_name,
                slot_id=slot_id
            )
            
            if result.get("success"):
                results.append(result)
            else:
                errors.append({"photo": i, "error": result.get("error")})
                # Si falla, puede que no haya mas slots o fotos
                if "no hay fotos" in result.get("error", "").lower():
                    break
        
        stats = self.get_stats()
        
        return {
            "success": len(results) > 0,
            "photos_placed": len(results),
            "results": results,
            "errors": errors,
            "stats": stats
        }
    
    async def execute_with_stagehand(self, instruction: str, max_steps: int = 10) -> dict:
        """
        Ejecuta una tarea compleja usando el agente autonomo de Stagehand.
        Util para tareas que requieren multiples pasos y decision-making.
        
        Args:
            instruction: Instruccion en lenguaje natural
            max_steps: Maximo de pasos a ejecutar
            
        Ejemplos:
            - "Upload all photos and fill empty slots"
            - "Navigate to page 5 and add a photo"
            - "Find the save button and click it"
        """
        if not self.use_stagehand:
            return {"success": False, "error": "Stagehand no disponible"}
        
        if not await self._ensure_stagehand():
            return {"success": False, "error": "No se pudo iniciar Stagehand"}
        
        self._stats["stagehand_calls"] += 1
        
        logger.info(f"[Stagehand Execute] {instruction}")
        
        result = await self._stagehand.execute_task(instruction, max_steps)
        
        return result
    
    # =========================================
    # DRAG & DROP MEJORADO (HTML5 + ALTERNATIVAS)
    # =========================================
    
    async def drag_with_html5_events(
        self,
        from_x: float, from_y: float,
        to_x: float, to_y: float
    ) -> dict:
        """
        Drag & drop usando eventos HTML5 nativos via JavaScript.
        Esto funciona con editores que usan HTML5 Drag and Drop API.
        """
        await self._ensure_browser()
        
        try:
            logger.info(f"[HTML5 Drag] ({from_x:.0f},{from_y:.0f}) -> ({to_x:.0f},{to_y:.0f})")
            
            # JavaScript que simula drag & drop con eventos HTML5
            result = await self.page.evaluate("""
                async ({fromX, fromY, toX, toY}) => {
                    // Encontrar elementos en las coordenadas
                    const sourceElement = document.elementFromPoint(fromX, fromY);
                    const targetElement = document.elementFromPoint(toX, toY);
                    
                    if (!sourceElement) {
                        return { success: false, error: 'No element found at source position' };
                    }
                    if (!targetElement) {
                        return { success: false, error: 'No element found at target position' };
                    }
                    
                    // Crear DataTransfer
                    const dataTransfer = new DataTransfer();
                    
                    // Si es una imagen, agregar sus datos
                    if (sourceElement.tagName === 'IMG') {
                        dataTransfer.setData('text/uri-list', sourceElement.src);
                        dataTransfer.setData('text/plain', sourceElement.src);
                    }
                    
                    // Evento dragstart en el origen
                    const dragStartEvent = new DragEvent('dragstart', {
                        bubbles: true,
                        cancelable: true,
                        dataTransfer: dataTransfer,
                        clientX: fromX,
                        clientY: fromY
                    });
                    sourceElement.dispatchEvent(dragStartEvent);
                    
                    // Pequeña pausa
                    await new Promise(r => setTimeout(r, 100));
                    
                    // Evento dragenter en el destino
                    const dragEnterEvent = new DragEvent('dragenter', {
                        bubbles: true,
                        cancelable: true,
                        dataTransfer: dataTransfer,
                        clientX: toX,
                        clientY: toY
                    });
                    targetElement.dispatchEvent(dragEnterEvent);
                    
                    // Evento dragover en el destino
                    const dragOverEvent = new DragEvent('dragover', {
                        bubbles: true,
                        cancelable: true,
                        dataTransfer: dataTransfer,
                        clientX: toX,
                        clientY: toY
                    });
                    targetElement.dispatchEvent(dragOverEvent);
                    
                    await new Promise(r => setTimeout(r, 50));
                    
                    // Evento drop en el destino
                    const dropEvent = new DragEvent('drop', {
                        bubbles: true,
                        cancelable: true,
                        dataTransfer: dataTransfer,
                        clientX: toX,
                        clientY: toY
                    });
                    targetElement.dispatchEvent(dropEvent);
                    
                    // Evento dragend en el origen
                    const dragEndEvent = new DragEvent('dragend', {
                        bubbles: true,
                        cancelable: true,
                        dataTransfer: dataTransfer,
                        clientX: toX,
                        clientY: toY
                    });
                    sourceElement.dispatchEvent(dragEndEvent);
                    
                    return { 
                        success: true, 
                        method: 'html5_events',
                        source: sourceElement.tagName,
                        target: targetElement.tagName
                    };
                }
            """, {"fromX": from_x, "fromY": from_y, "toX": to_x, "toY": to_y})
            
            await asyncio.sleep(0.5)
            return result
            
        except Exception as e:
            logger.error(f"[HTML5 Drag] Error: {e}")
            return {"success": False, "error": str(e), "method": "html5_events"}
    
    async def drag_with_mouse_events(
        self,
        from_x: float, from_y: float,
        to_x: float, to_y: float
    ) -> dict:
        """
        Drag & drop usando eventos de mouse via JavaScript.
        Alternativa para editores que no usan HTML5 Drag and Drop.
        """
        await self._ensure_browser()
        
        try:
            logger.info(f"[Mouse Events] ({from_x:.0f},{from_y:.0f}) -> ({to_x:.0f},{to_y:.0f})")
            
            result = await self.page.evaluate("""
                async ({fromX, fromY, toX, toY}) => {
                    const sourceElement = document.elementFromPoint(fromX, fromY);
                    const targetElement = document.elementFromPoint(toX, toY);
                    
                    if (!sourceElement) {
                        return { success: false, error: 'No element at source' };
                    }
                    
                    // MouseDown en origen
                    sourceElement.dispatchEvent(new MouseEvent('mousedown', {
                        bubbles: true,
                        cancelable: true,
                        clientX: fromX,
                        clientY: fromY,
                        button: 0
                    }));
                    
                    await new Promise(r => setTimeout(r, 100));
                    
                    // Movimientos intermedios
                    const steps = 10;
                    for (let i = 1; i <= steps; i++) {
                        const progress = i / steps;
                        const currentX = fromX + (toX - fromX) * progress;
                        const currentY = fromY + (toY - fromY) * progress;
                        
                        document.dispatchEvent(new MouseEvent('mousemove', {
                            bubbles: true,
                            cancelable: true,
                            clientX: currentX,
                            clientY: currentY,
                            button: 0
                        }));
                        
                        await new Promise(r => setTimeout(r, 20));
                    }
                    
                    await new Promise(r => setTimeout(r, 50));
                    
                    // MouseUp en destino
                    const finalTarget = document.elementFromPoint(toX, toY) || targetElement;
                    finalTarget.dispatchEvent(new MouseEvent('mouseup', {
                        bubbles: true,
                        cancelable: true,
                        clientX: toX,
                        clientY: toY,
                        button: 0
                    }));
                    
                    // Click en destino (algunos editores lo necesitan)
                    finalTarget.dispatchEvent(new MouseEvent('click', {
                        bubbles: true,
                        cancelable: true,
                        clientX: toX,
                        clientY: toY,
                        button: 0
                    }));
                    
                    return { success: true, method: 'mouse_events' };
                }
            """, {"fromX": from_x, "fromY": from_y, "toX": to_x, "toY": to_y})
            
            await asyncio.sleep(0.5)
            return result
            
        except Exception as e:
            logger.error(f"[Mouse Events] Error: {e}")
            return {"success": False, "error": str(e), "method": "mouse_events"}
    
    async def click_to_select_and_place(
        self,
        photo_x: float, photo_y: float,
        slot_x: float, slot_y: float
    ) -> dict:
        """
        Alternativa: Click para seleccionar foto, click para colocar.
        Algunos editores soportan este metodo.
        """
        await self._ensure_browser()
        
        try:
            logger.info(f"[Click-Select] foto({photo_x:.0f},{photo_y:.0f}) slot({slot_x:.0f},{slot_y:.0f})")
            
            # Click en la foto para seleccionarla
            await self.page.mouse.click(photo_x, photo_y)
            await asyncio.sleep(0.3)
            
            # Doble click para "activar"
            await self.page.mouse.dblclick(photo_x, photo_y)
            await asyncio.sleep(0.3)
            
            # Click en el slot destino
            await self.page.mouse.click(slot_x, slot_y)
            await asyncio.sleep(0.5)
            
            return {"success": True, "method": "click_select"}
            
        except Exception as e:
            logger.error(f"[Click-Select] Error: {e}")
            return {"success": False, "error": str(e), "method": "click_select"}
    
    async def drag_photo_smart(
        self,
        photo_index: int = 0,
        slot_index: int = 0,
        methods: list = None
    ) -> dict:
        """
        Drag & drop INTELIGENTE que prueba multiples metodos hasta que uno funcione.
        
        Args:
            photo_index: Indice de la foto
            slot_index: Indice del slot destino
            methods: Lista de metodos a probar (default: todos)
        
        Metodos disponibles:
            - 'playwright': Mouse events de Playwright
            - 'html5': Eventos HTML5 Drag and Drop
            - 'mouse_js': Eventos de mouse via JavaScript
            - 'click_select': Click para seleccionar y colocar
        """
        await self._ensure_browser()
        
        if methods is None:
            methods = ['html5', 'mouse_js', 'playwright', 'click_select']
        
        # Obtener coordenadas
        photos_result = await self.get_uploaded_photos()
        if not photos_result.get("success") or not photos_result.get("photos"):
            return {"success": False, "error": "No hay fotos disponibles"}
        
        photos = photos_result["photos"]
        if photo_index >= len(photos):
            return {"success": False, "error": f"Foto {photo_index} no existe"}
        
        photo = photos[photo_index]
        from_x, from_y = photo["x"], photo["y"]
        
        # Obtener slot destino
        slots_result = await self.get_canvas_slots()
        if slots_result.get("slots") and slot_index < len(slots_result["slots"]):
            slot = slots_result["slots"][slot_index]
            to_x, to_y = slot["x"], slot["y"]
        else:
            # Fallback: centro del canvas
            viewport = self.page.viewport_size
            to_x = viewport["width"] * 0.6
            to_y = viewport["height"] * 0.5
        
        logger.info(f"[Smart Drag] foto {photo_index} -> slot {slot_index}")
        print(f"[DRAG] Probando metodos: {methods}")
        
        # Tomar screenshot antes
        before_screenshot = await self.page.screenshot()
        
        errors = []
        for method in methods:
            print(f"[DRAG] Probando: {method}...")
            
            try:
                if method == 'html5':
                    result = await self.drag_with_html5_events(from_x, from_y, to_x, to_y)
                elif method == 'mouse_js':
                    result = await self.drag_with_mouse_events(from_x, from_y, to_x, to_y)
                elif method == 'playwright':
                    # Metodo original de Playwright
                    await self.page.mouse.move(from_x, from_y)
                    await asyncio.sleep(0.2)
                    await self.page.mouse.down()
                    await asyncio.sleep(0.1)
                    
                    steps = 12
                    for i in range(steps + 1):
                        progress = i / steps
                        current_x = from_x + (to_x - from_x) * progress
                        current_y = from_y + (to_y - from_y) * progress
                        await self.page.mouse.move(current_x, current_y)
                        await asyncio.sleep(0.02)
                    
                    await asyncio.sleep(0.1)
                    await self.page.mouse.up()
                    result = {"success": True, "method": "playwright"}
                elif method == 'click_select':
                    result = await self.click_to_select_and_place(from_x, from_y, to_x, to_y)
                else:
                    continue
                
                if result.get("success"):
                    await asyncio.sleep(0.5)
                    
                    # Verificar si hubo cambio (screenshot despues)
                    after_screenshot = await self.page.screenshot()
                    
                    # Comparacion simple: si los bytes son diferentes, algo cambio
                    if before_screenshot != after_screenshot:
                        print(f"[DRAG] Exito con metodo: {method}")
                        return {
                            "success": True,
                            "method": method,
                            "photo_index": photo_index,
                            "slot_index": slot_index,
                            "from": {"x": from_x, "y": from_y},
                            "to": {"x": to_x, "y": to_y}
                        }
                    else:
                        errors.append({"method": method, "error": "No visual change detected"})
                else:
                    errors.append({"method": method, "error": result.get("error")})
                    
            except Exception as e:
                errors.append({"method": method, "error": str(e)})
                continue
        
        logger.warning(f"[Smart Drag] Todos los metodos fallaron: {errors}")
        return {
            "success": False,
            "error": "Todos los metodos de drag fallaron",
            "attempts": errors
        }
    
    async def close(self):
        """Cierra el browser, cache y stagehand"""
        # Cerrar Stagehand
        if self._stagehand:
            try:
                await self._stagehand.stop()
            except:
                pass
            self._stagehand = None
        
        # Cerrar browser
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        
        # Cerrar cache
        if self.cache:
            self.cache.close()
        
        # Log stats finales
        logger.info(f"[Toolkit] Cerrado. Stats: {self._stats}")
    
    # =========================================
    # FLUJO COMPLETO
    # =========================================
    
    async def full_flow_to_editor(self, product_search: str = "21x21", project_title: str = "Mi Fotolibro") -> dict:
        """
        Ejecuta el flujo completo hasta llegar al editor:
        1. Login
        2. Navegar a Fotolibros  
        3. Seleccionar producto
        4. Configurar y crear proyecto (modal)
        5. Esperar que cargue el editor
        """
        results = {"steps": []}
        
        # Step 1: Login
        print("\n=== PASO 1: Login ===")
        login_result = await self.login()
        results["steps"].append({"step": "login", "result": login_result})
        if not login_result.get("success"):
            return {"success": False, "error": "Login falló", "results": results}
        
        await asyncio.sleep(1)
        
        # Step 2: Navegar a Fotolibros
        print("\n=== PASO 2: Navegar a Fotolibros ===")
        nav_result = await self.navigate_to_fotolibros()
        results["steps"].append({"step": "navigate", "result": nav_result})
        
        await asyncio.sleep(1)
        
        # Step 3: Seleccionar producto
        print(f"\n=== PASO 3: Seleccionar producto '{product_search}' ===")
        product_result = await self.select_product_by_text(product_search)
        results["steps"].append({"step": "select_product", "result": product_result})
        
        await asyncio.sleep(1)
        
        # Step 4: Configurar y crear proyecto (incluye llenar título)
        print(f"\n=== PASO 4: Configurar proyecto '{project_title}' ===")
        create_result = await self.click_create_project(project_title)
        results["steps"].append({"step": "create_project", "result": create_result})
        
        # Step 5: Esperar que cargue el editor
        print("\n=== PASO 5: Esperar editor ===")
        editor_result = await self.wait_for_editor(timeout=30)
        results["steps"].append({"step": "wait_editor", "result": editor_result})
        
        # Verificar estado final
        page_info = await self.get_page_info()
        results["final_page"] = page_info
        
        success = page_info.get("page_type") in ["editor", "editor_loading"]
        
        return {
            "success": success,
            "results": results
        }


def get_fdf_stagehand_tools(
    model_api_key: str,
    fdf_email: str,
    fdf_password: str,
    headless: bool = False
) -> list:
    """Retorna las herramientas del toolkit para usar con AGNO"""
    toolkit = FDFStagehandToolkit(
        model_api_key=model_api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=headless
    )
    
    return [
        toolkit.login,
        toolkit.navigate_to_fotolibros,
        toolkit.select_product_by_text,
        toolkit.click_create_project,
        toolkit.fill_project_title,
        toolkit.upload_photos,
        toolkit.take_screenshot,
        toolkit.get_page_info,
        toolkit.full_flow_to_editor,
        toolkit.close
    ]
