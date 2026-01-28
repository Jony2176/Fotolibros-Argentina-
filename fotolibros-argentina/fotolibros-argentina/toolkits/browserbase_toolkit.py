"""
Browserbase Toolkit - Automatización del Editor de Fábrica de Fotolibros
=========================================================================
Toolkit para crear proyectos de fotolibros automáticamente usando Browserbase.

Características:
- Login automático al editor SunPics
- Selección de producto y configuración
- Subida de fotos
- Layout automático de páginas
- Envío a producción

Usa el tier GRATUITO de Browserbase:
- 1 hora/mes de navegación
- Sesiones de hasta 15 minutos
- Suficiente para ~12-20 pedidos/mes de prueba

Requiere:
- pip install browserbase playwright
- BROWSERBASE_API_KEY
- BROWSERBASE_PROJECT_ID
"""
import os
import asyncio
import time
from typing import Optional, List, Dict, Any
from playwright.sync_api import sync_playwright, Page, Browser
from playwright.async_api import async_playwright
from agno.tools import tool
from loguru import logger

# Configuración
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")

# Credenciales del editor (configurar en .env)
GRAFICA_EMAIL = os.getenv("GRAFICA_EMAIL", "")
GRAFICA_PASSWORD = os.getenv("GRAFICA_PASSWORD", "")

# URLs del editor
EDITOR_LOGIN_URL = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
EDITOR_HOME_URL = "https://online.fabricadefotolibros.com/"

# Mapeo de productos del catálogo a selectores del editor
PRODUCTOS_EDITOR = {
    "AP-21x15-BLANDA": {"nombre": "Fotolibro 21 x 15 Tapa Blanda", "categoria": "Fotolibros"},
    "AP-21x15-DURA": {"nombre": "Fotolibro 21 x 15 Tapa Dura", "categoria": "Fotolibros"},
    "AP-28x22-DURA": {"nombre": "Fotolibro 28 x 22 Tapa Dura", "categoria": "Fotolibros"},
    "CU-21x21-BLANDA": {"nombre": "Fotolibro 21 x 21 Tapa Blanda", "categoria": "Fotolibros"},
    "CU-21x21-DURA": {"nombre": "Fotolibro 21 x 21 Tapa Dura", "categoria": "Fotolibros"},
    "CU-29x29-DURA": {"nombre": "Fotolibro 29 x 29 Tapa Dura", "categoria": "Fotolibros"},
    "VE-22x28-BLANDA": {"nombre": "Fotolibro A4 Vertical Tapa Blanda", "categoria": "Fotolibros"},
    "VE-22x28-DURA": {"nombre": "Fotolibro A4 Vertical Tapa Dura", "categoria": "Fotolibros"},
}


class BrowserbaseToolkit:
    """
    Toolkit para automatizar el editor de Fábrica de Fotolibros usando Browserbase.
    
    Flujo de uso:
    1. iniciar_sesion_editor() - Abre navegador e inicia sesión
    2. crear_proyecto() - Selecciona producto y crea proyecto
    3. subir_fotos() - Sube las fotos del cliente
    4. configurar_paginas() - Distribuye fotos en páginas
    5. enviar_a_produccion() - Confirma y envía el pedido
    6. cerrar_sesion() - Cierra el navegador
    """
    
    def __init__(self):
        self.bb = None
        self.session = None
        self.browser = None
        self.page = None
        self.playwright = None
        self.session_id = None
        
        # Intentar importar Browserbase
        try:
            from browserbase import Browserbase
            if BROWSERBASE_API_KEY:
                self.bb = Browserbase(api_key=BROWSERBASE_API_KEY)
                logger.info("✅ Browserbase SDK inicializado")
            else:
                logger.warning("⚠️ BROWSERBASE_API_KEY no configurada - modo local")
        except ImportError:
            logger.warning("⚠️ Browserbase no instalado - usando Playwright local")
    
    def _usar_browserbase(self) -> bool:
        """Determina si usar Browserbase o Playwright local."""
        return self.bb is not None and BROWSERBASE_PROJECT_ID is not None
    
    @tool
    def iniciar_sesion_editor(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        usar_proxies: bool = False,
        reutilizar_sesion: bool = True
    ) -> str:
        """
        Inicia sesión en el editor de Fábrica de Fotolibros.
        
        ⚡ OPTIMIZADO: Reutiliza sesiones existentes para mayor velocidad.
        
        Crea una sesión de navegador (Browserbase o local) y hace login
        en el editor SunPics de la gráfica.
        
        Args:
            email: Email de la cuenta (usa GRAFICA_EMAIL si no se provee)
            password: Password de la cuenta (usa GRAFICA_PASSWORD si no se provee)
            usar_proxies: Si usar proxies residenciales (solo Browserbase)
            reutilizar_sesion: Si True, reutiliza sesión existente (más rápido)
            
        Returns:
            JSON con resultado del login y session_id
        """
        import json
        
        email = email or GRAFICA_EMAIL
        password = password or GRAFICA_PASSWORD
        
        if not email or not password:
            return json.dumps({
                "success": False,
                "error": "Credenciales no configuradas. Configura GRAFICA_EMAIL y GRAFICA_PASSWORD"
            })
        
        try:
            # ⚡ OPTIMIZACIÓN: Reutilizar sesión existente
            if reutilizar_sesion and self.page and self.browser:
                logger.info("⚡ Reutilizando sesión existente (más rápido)")
                # Solo navegar si no estamos ya en el editor
                if "fabricadefotolibros" not in self.page.url:
                    self.page.goto(EDITOR_LOGIN_URL, wait_until="domcontentloaded")
                return json.dumps({
                    "success": True,
                    "session_id": self.session_id,
                    "modo": "reutilizada",
                    "replay_url": f"https://browserbase.com/sessions/{self.session_id}" if self._usar_browserbase() else None
                })
            
            # Iniciar nueva sesión
            if self._usar_browserbase():
                logger.info("🌐 Iniciando sesión con Browserbase...")
                
                session_config = {
                    "project_id": BROWSERBASE_PROJECT_ID,
                }
                if usar_proxies:
                    session_config["proxies"] = True
                
                self.session = self.bb.sessions.create(**session_config)
                self.session_id = self.session.id
                
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.connect_over_cdp(
                    self.session.connect_url
                )
                context = self.browser.contexts[0]
                self.page = context.pages[0]
                
                logger.info(f"   Session ID: {self.session_id}")
            else:
                logger.info("🖥️ Iniciando sesión con Playwright local...")
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.launch(headless=False)
                context = self.browser.new_context()
                self.page = context.new_page()
                self.session_id = "local"
            
            # ⚡ OPTIMIZACIÓN: wait_until="domcontentloaded" es más rápido
            self.page.goto(EDITOR_LOGIN_URL, wait_until="domcontentloaded")
            self.page.wait_for_timeout(2000)
            
            # Llenar formulario de login
            self.page.fill("#email_log", email)
            self.page.fill("#clave_log", password)
            
            # Click en INGRESAR
            self.page.click("#bt_log")
            self.page.wait_for_timeout(3000)
            
            # Verificar login exitoso (debe mostrar categorías)
            try:
                self.page.wait_for_selector("text=Fotolibros", timeout=10000)
                login_exitoso = True
            except:
                login_exitoso = False
            
            if login_exitoso:
                logger.info("✅ Login exitoso en el editor")
                return json.dumps({
                    "success": True,
                    "session_id": self.session_id,
                    "modo": "browserbase" if self._usar_browserbase() else "local",
                    "replay_url": f"https://browserbase.com/sessions/{self.session_id}" if self._usar_browserbase() else None
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": "Login fallido - verificar credenciales",
                    "session_id": self.session_id
                })
                
        except Exception as e:
            logger.error(f"❌ Error iniciando sesión: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @tool
    def crear_proyecto(
        self,
        producto_id: str,
        titulo: str,
        paginas: int = 22
    ) -> str:
        """
        Crea un nuevo proyecto de fotolibro en el editor.
        
        Args:
            producto_id: ID del producto (ej: "CU-21x21-DURA")
            titulo: Título del proyecto (ej: "Boda Juan y María")
            paginas: Cantidad de páginas (mínimo 22)
            
        Returns:
            JSON con resultado de la creación
        """
        import json
        
        if not self.page:
            return json.dumps({
                "success": False,
                "error": "No hay sesión activa. Ejecutar iniciar_sesion_editor primero."
            })
        
        producto_info = PRODUCTOS_EDITOR.get(producto_id)
        if not producto_info:
            return json.dumps({
                "success": False,
                "error": f"Producto {producto_id} no encontrado en el mapeo del editor"
            })
        
        try:
            # 1. Navegar a home del editor si no estamos ahí
            if "online.fabricadefotolibros.com" not in self.page.url:
                self.page.goto(EDITOR_HOME_URL, wait_until="domcontentloaded")
                self.page.wait_for_timeout(1500)
            
            # 2. Click en categoría "Fotolibros"
            self.page.click(f"text={producto_info['categoria']}")
            self.page.wait_for_timeout(1500)
            
            # 3. Click en el producto específico
            self.page.click(f"text={producto_info['nombre']}")
            self.page.wait_for_timeout(1500)
            
            # 4. Llenar título del proyecto
            try:
                titulo_input = self.page.locator("input").first
                titulo_input.fill(titulo)
            except:
                logger.warning("No se encontró campo de título")
            
            # 5. Click en "Crear Proyecto"
            self.page.click("text=Crear Proyecto")
            self.page.wait_for_timeout(3000)
            
            logger.info(f"✅ Proyecto creado: {titulo}")
            
            return json.dumps({
                "success": True,
                "producto": producto_id,
                "titulo": titulo,
                "paginas": paginas
            })
            
        except Exception as e:
            logger.error(f"❌ Error creando proyecto: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @tool
    def subir_fotos(self, rutas_fotos: List[str]) -> str:
        """
        Sube fotos al proyecto actual.
        
        Args:
            rutas_fotos: Lista de rutas absolutas a las fotos
            
        Returns:
            JSON con resultado de la subida
        """
        import json
        
        if not self.page:
            return json.dumps({
                "success": False,
                "error": "No hay sesión activa."
            })
        
        try:
            # Click en "Desde computador" si aparece el selector de origen
            try:
                self.page.click("text=Desde computador", timeout=5000)
                self.page.wait_for_timeout(2000)
            except:
                # Ya estamos en el editor, buscar botón de subir
                self.page.click("text=Subir fotos")
                self.page.wait_for_timeout(2000)
            
            # Subir archivos
            # El input de archivos suele estar oculto, lo buscamos
            file_input = self.page.locator("input[type='file']").first
            
            fotos_subidas = 0
            for ruta in rutas_fotos:
                if os.path.exists(ruta):
                    file_input.set_input_files(ruta)
                    self.page.wait_for_timeout(1500)  # Esperar carga
                    fotos_subidas += 1
                else:
                    logger.warning(f"Foto no encontrada: {ruta}")
            
            # Esperar a que terminen de subir
            self.page.wait_for_timeout(3000)
            
            logger.info(f"✅ {fotos_subidas}/{len(rutas_fotos)} fotos subidas")
            
            return json.dumps({
                "success": True,
                "fotos_subidas": fotos_subidas,
                "total_solicitadas": len(rutas_fotos)
            })
            
        except Exception as e:
            logger.error(f"❌ Error subiendo fotos: {e}")
            return json.dumps({
                "success": False,
                "error": str(e)
            })
    
    @tool
    def seleccionar_tema_vacio(self) -> str:
        """
        Selecciona el tema "Vacío" para layout manual de las fotos.
        
        Returns:
            JSON con resultado
        """
        import json
        
        if not self.page:
            return json.dumps({"success": False, "error": "No hay sesión activa."})
        
        try:
            # Buscar y seleccionar tema vacío
            self.page.click("text=Vacío")
            self.page.wait_for_timeout(2000)
            
            # Confirmar con "Relleno fotos manual" o "Continuar"
            try:
                self.page.click("text=Relleno fotos manual")
            except:
                self.page.click("text=Continuar")
            
            self.page.wait_for_timeout(3000)
            
            logger.info("✅ Tema vacío seleccionado")
            return json.dumps({"success": True, "tema": "vacio"})
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    @tool
    def distribuir_fotos_en_paginas(self, fotos_por_pagina: int = 1) -> str:
        """
        Distribuye las fotos subidas en las páginas del libro.
        
        Este proceso arrastra cada foto desde la galería lateral
        hacia los placeholders de cada página.
        
        Args:
            fotos_por_pagina: Cantidad de fotos por página (1-4)
            
        Returns:
            JSON con resultado
        """
        import json
        
        if not self.page:
            return json.dumps({"success": False, "error": "No hay sesión activa."})
        
        try:
            # Esta es una operación compleja que requiere:
            # 1. Identificar las fotos en la galería derecha
            # 2. Identificar los placeholders en el canvas
            # 3. Drag & drop de cada foto
            
            # Por ahora, intentamos usar el auto-fill si está disponible
            try:
                self.page.click("text=Rellenar automáticamente")
                self.page.wait_for_timeout(5000)
                logger.info("✅ Auto-relleno aplicado")
                return json.dumps({"success": True, "modo": "automatico"})
            except:
                pass
            
            # Si no hay auto-fill, navegamos página por página
            miniaturas = self.page.locator(".pageThumbs, .page-thumb, [class*='thumb']")
            cantidad_paginas = miniaturas.count()
            
            logger.info(f"📖 Distribuyendo fotos en {cantidad_paginas} páginas...")
            
            # Obtener fotos de la galería
            fotos_galeria = self.page.locator(".photo-gallery img, .gallery-item img, [class*='photo'] img")
            
            for i in range(min(cantidad_paginas, fotos_galeria.count())):
                try:
                    # Click en miniatura de página
                    miniaturas.nth(i).click()
                    self.page.wait_for_timeout(500)
                    
                    # Drag foto al canvas principal
                    foto = fotos_galeria.nth(i)
                    canvas = self.page.locator(".canvas, .editor-canvas, [class*='canvas']").first
                    
                    foto.drag_to(canvas)
                    self.page.wait_for_timeout(500)
                except Exception as inner_e:
                    logger.warning(f"Error en página {i}: {inner_e}")
            
            return json.dumps({
                "success": True,
                "paginas_procesadas": cantidad_paginas,
                "modo": "manual"
            })
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    @tool
    def enviar_a_produccion(self) -> str:
        """
        Envía el proyecto a producción (hace click en COMPRAR).
        
        ⚠️ IMPORTANTE: Esta acción genera un pedido real en la gráfica.
        
        Returns:
            JSON con resultado y número de pedido si está disponible
        """
        import json
        
        if not self.page:
            return json.dumps({"success": False, "error": "No hay sesión activa."})
        
        try:
            # Click en botón COMPRAR (verde, arriba derecha)
            self.page.click("text=COMPRAR")
            self.page.wait_for_timeout(3000)
            
            # Puede aparecer un modal de confirmación
            try:
                self.page.click("text=Confirmar")
                self.page.wait_for_timeout(3000)
            except:
                pass
            
            # Intentar capturar número de pedido
            numero_pedido = None
            try:
                # Buscar texto que contenga número de pedido
                pedido_text = self.page.locator("text=/Pedido.*\\d+/i").first
                numero_pedido = pedido_text.inner_text()
            except:
                pass
            
            # Tomar screenshot como evidencia
            screenshot_path = f"uploads/comprobantes/pedido_grafica_{int(time.time())}.png"
            self.page.screenshot(path=screenshot_path)
            
            logger.info(f"✅ Proyecto enviado a producción")
            
            return json.dumps({
                "success": True,
                "numero_pedido_grafica": numero_pedido,
                "screenshot": screenshot_path,
                "replay_url": f"https://browserbase.com/sessions/{self.session_id}" if self._usar_browserbase() else None
            })
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    @tool
    def guardar_proyecto(self) -> str:
        """
        Guarda el proyecto actual sin enviarlo a producción.
        
        Returns:
            JSON con resultado
        """
        import json
        
        if not self.page:
            return json.dumps({"success": False, "error": "No hay sesión activa."})
        
        try:
            self.page.click("text=Guardar")
            self.page.wait_for_timeout(3000)
            
            logger.info("✅ Proyecto guardado")
            return json.dumps({"success": True})
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    @tool
    def tomar_screenshot(self, nombre: str = "screenshot") -> str:
        """
        Toma un screenshot del estado actual del editor.
        
        Args:
            nombre: Nombre base del archivo
            
        Returns:
            JSON con ruta del screenshot
        """
        import json
        
        if not self.page:
            return json.dumps({"success": False, "error": "No hay sesión activa."})
        
        try:
            ruta = f"uploads/screenshots/{nombre}_{int(time.time())}.png"
            os.makedirs(os.path.dirname(ruta), exist_ok=True)
            self.page.screenshot(path=ruta)
            
            return json.dumps({
                "success": True,
                "path": ruta
            })
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    @tool
    def cerrar_sesion(self) -> str:
        """
        Cierra la sesión del navegador.
        
        Returns:
            JSON con URL del replay (si usó Browserbase)
        """
        import json
        
        replay_url = None
        
        try:
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            
            if self._usar_browserbase() and self.session_id:
                replay_url = f"https://browserbase.com/sessions/{self.session_id}"
            
            logger.info("✅ Sesión cerrada")
            
            # Limpiar referencias
            self.browser = None
            self.page = None
            self.playwright = None
            
            return json.dumps({
                "success": True,
                "replay_url": replay_url
            })
            
        except Exception as e:
            return json.dumps({"success": False, "error": str(e)})
    
    def get_tools(self) -> list:
        """Retorna todas las herramientas para usar con AGNO."""
        return [
            self.iniciar_sesion_editor,
            self.crear_proyecto,
            self.subir_fotos,
            self.seleccionar_tema_vacio,
            self.distribuir_fotos_en_paginas,
            self.enviar_a_produccion,
            self.guardar_proyecto,
            self.tomar_screenshot,
            self.cerrar_sesion,
        ]


# Instancia singleton
browserbase_toolkit = BrowserbaseToolkit()


# ============================================
# Test standalone
# ============================================
if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     BROWSERBASE TOOLKIT - Fábrica de Fotolibros              ║
╠══════════════════════════════════════════════════════════════╣
║  Automatiza el editor SunPics de la gráfica                  ║
║                                                              ║
║  Herramientas disponibles:                                   ║
║  • iniciar_sesion_editor() - Login en el editor              ║
║  • crear_proyecto() - Nuevo proyecto de fotolibro            ║
║  • subir_fotos() - Upload de imágenes                        ║
║  • seleccionar_tema_vacio() - Layout manual                  ║
║  • distribuir_fotos_en_paginas() - Auto-layout               ║
║  • enviar_a_produccion() - COMPRAR (pedido real!)            ║
║  • guardar_proyecto() - Guardar sin enviar                   ║
║  • tomar_screenshot() - Captura de pantalla                  ║
║  • cerrar_sesion() - Cerrar navegador                        ║
║                                                              ║
║  Modo: {'Browserbase Cloud' if BROWSERBASE_API_KEY else 'Playwright Local':<43} ║
╚══════════════════════════════════════════════════════════════╝
""")
