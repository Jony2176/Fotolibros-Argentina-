"""
Stagehand v3 Wrapper - Actualizado para API v3
===============================================
Wrapper para usar Stagehand v3 con el SDK de Python oficial.

Modos de operacion:
- LOCAL: Usa Chrome local (requiere Chrome instalado)
- BROWSERBASE: Usa Browserbase cloud (requiere cuenta con minutos)

Uso:
    wrapper = FDFStagehandWrapper(model_api_key="...")
    await wrapper.start()
    
    # Accion con lenguaje natural
    await wrapper.act("click the login button")
    await wrapper.act("drag the first photo to the empty slot on the canvas")
    
    # Agente autonomo para tareas complejas
    await wrapper.execute_task("fill all empty slots with photos", max_steps=10)
    
    await wrapper.stop()
"""

import asyncio
import os
from typing import Optional, Dict, Any, List
from contextlib import asynccontextmanager

# Logging
import logging
logger = logging.getLogger(__name__)

# Import Stagehand (manejo de error si no esta instalado)
try:
    from stagehand import AsyncStagehand
    STAGEHAND_AVAILABLE = True
except ImportError:
    STAGEHAND_AVAILABLE = False
    logger.warning("[Stagehand] stagehand no instalado. pip install stagehand")


class FDFStagehandWrapper:
    """
    Wrapper para Stagehand v3 SDK de Python.
    Provee una interfaz simplificada para acciones AI-driven.
    """
    
    def __init__(
        self,
        model_name: str = "google/gemini-2.0-flash",
        model_api_key: Optional[str] = None,
        headless: bool = False,
        timeout: int = 30000,
        use_browserbase: bool = False  # Default a LOCAL
    ):
        """
        Inicializa el wrapper.
        
        Args:
            model_name: Modelo LLM a usar. Opciones soportadas:
                - "google/gemini-2.0-flash" (recomendado, rapido)
                - "openai/gpt-4o" (alternativa)
                - "anthropic/claude-sonnet-4-20250514" (alternativa)
            model_api_key: API key para el modelo (GEMINI_API_KEY o MODEL_API_KEY)
            headless: Si True, corre el browser sin ventana (solo LOCAL)
            timeout: Timeout por defecto en ms
            use_browserbase: Si True, usa Browserbase cloud. Si False, usa Chrome local.
        """
        if not STAGEHAND_AVAILABLE:
            raise ImportError("stagehand no esta instalado. Ejecuta: pip install stagehand")
        
        self.model_name = model_name
        self.model_api_key = model_api_key or os.getenv("MODEL_API_KEY") or os.getenv("GEMINI_API_KEY")
        self.headless = headless
        self.timeout = timeout
        self.use_browserbase = use_browserbase
        
        # Browserbase credentials
        self.browserbase_api_key = os.getenv("BROWSERBASE_API_KEY")
        self.browserbase_project_id = os.getenv("BROWSERBASE_PROJECT_ID")
        
        # Chrome path para modo local
        self.chrome_path = os.getenv("CHROME_PATH") or self._detect_chrome_path()
        
        self.client: Optional[AsyncStagehand] = None
        self.session = None
        self._started = False
        
        mode = "BROWSERBASE" if use_browserbase else "LOCAL"
        logger.info(f"[Stagehand] Wrapper inicializado - Modo: {mode}, Modelo: {model_name}")
    
    def _detect_chrome_path(self) -> Optional[str]:
        """Detecta la ruta de Chrome en Windows"""
        common_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
        return None
    
    async def start(self):
        """
        Inicia una sesion de Stagehand.
        Usa Browserbase (cloud) o Chrome local segun configuracion.
        """
        if self._started:
            logger.warning("[Stagehand] Ya esta iniciado")
            return
        
        try:
            if self.use_browserbase and self.browserbase_api_key:
                # Modo Browserbase (cloud)
                logger.info("[Stagehand] Iniciando sesion (Browserbase cloud)...")
                self.client = AsyncStagehand(
                    browserbase_api_key=self.browserbase_api_key,
                    browserbase_project_id=self.browserbase_project_id,
                    model_api_key=self.model_api_key,
                )
                await self.client.__aenter__()
                
                # Crear sesion
                self.session = await self.client.sessions.create(
                    model_name=self.model_name
                )
            else:
                # Modo LOCAL (Chrome local)
                logger.info("[Stagehand] Iniciando sesion (Chrome local)...")
                
                # Configurar cliente para modo local
                self.client = AsyncStagehand(
                    server="local",
                    model_api_key=self.model_api_key,
                )
                await self.client.__aenter__()
                
                # Crear sesion con browser local
                browser_config = {
                    "type": "local",
                    "headless": self.headless,
                }
                
                # Agregar chrome path si lo detectamos
                if self.chrome_path:
                    browser_config["launchOptions"] = {
                        "executablePath": self.chrome_path,
                        "headless": self.headless,
                    }
                
                self.session = await self.client.sessions.create(
                    model_name=self.model_name,
                    browser=browser_config,
                )
            
            self._started = True
            session_id = getattr(self.session, 'id', 'unknown')
            logger.info(f"[Stagehand] Sesion iniciada: {session_id}")
            
        except Exception as e:
            logger.error(f"[Stagehand] Error iniciando: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    async def stop(self):
        """Cierra la sesion y el browser"""
        if not self._started:
            return
        
        try:
            if self.session:
                await self.session.end()
                self.session = None
            
            if self.client:
                await self.client.__aexit__(None, None, None)
                self.client = None
            
            self._started = False
            logger.info("[Stagehand] Sesion cerrada")
            
        except Exception as e:
            logger.error(f"[Stagehand] Error cerrando: {e}")
    
    async def _ensure_started(self):
        """Asegura que la sesion este iniciada"""
        if not self._started:
            await self.start()
    
    @property
    def is_started(self) -> bool:
        return self._started
    
    # =========================================
    # NAVEGACION
    # =========================================
    
    async def navigate(self, url: str) -> Dict:
        """
        Navega a una URL.
        
        Args:
            url: URL a navegar
            
        Returns:
            dict con resultado
        """
        await self._ensure_started()
        
        try:
            logger.info(f"[Stagehand NAVIGATE] {url}")
            await self.session.navigate(url=url)
            return {"success": True, "url": url}
        except Exception as e:
            logger.error(f"[Stagehand NAVIGATE ERROR] {e}")
            return {"success": False, "error": str(e), "url": url}
    
    # =========================================
    # ACCIONES
    # =========================================
    
    async def act(self, instruction: str) -> Dict:
        """
        Ejecuta una accion con lenguaje natural.
        
        Args:
            instruction: Instruccion en lenguaje natural.
                Ejemplos:
                - "click the login button"
                - "type 'hello' in the search box"
                - "drag the first photo to the empty slot"
                - "scroll down"
                - "select 'Option 2' from the dropdown"
                
        Returns:
            dict con resultado
        """
        await self._ensure_started()
        
        try:
            logger.info(f"[Stagehand ACT] {instruction}")
            response = await self.session.act(input=instruction)
            
            # Extraer mensaje del resultado
            message = "Action completed"
            if hasattr(response, 'data') and hasattr(response.data, 'result'):
                if hasattr(response.data.result, 'message'):
                    message = response.data.result.message
            
            return {"success": True, "action": instruction, "message": message}
        except Exception as e:
            logger.error(f"[Stagehand ACT ERROR] {e}")
            return {"success": False, "error": str(e), "action": instruction}
    
    async def observe(self, instruction: str) -> Dict:
        """
        Observa la pagina y encuentra elementos.
        
        Args:
            instruction: Que buscar.
                Ejemplos:
                - "find the login button"
                - "find all product cards"
                - "find the 'Submit' button"
                - "find empty slots on the canvas"
                
        Returns:
            dict con elementos encontrados
        """
        await self._ensure_started()
        
        try:
            logger.info(f"[Stagehand OBSERVE] {instruction}")
            response = await self.session.observe(instruction=instruction)
            
            results = []
            if hasattr(response, 'data') and hasattr(response.data, 'result'):
                results = response.data.result or []
            
            return {
                "success": True,
                "found": len(results) > 0,
                "count": len(results),
                "elements": [
                    {
                        "description": getattr(el, 'description', str(el)),
                        "action": el.to_dict(exclude_none=True) if hasattr(el, 'to_dict') else el
                    }
                    for el in results
                ]
            }
        except Exception as e:
            logger.error(f"[Stagehand OBSERVE ERROR] {e}")
            return {"success": False, "error": str(e), "found": False, "count": 0}
    
    async def find_and_act(self, description: str) -> Dict:
        """
        Encuentra un elemento y ejecuta una accion sobre el.
        Combina observe() + act().
        
        Args:
            description: Descripcion del elemento y accion.
                Ejemplos:
                - "click the 'Create Project' button"
                - "click the template card named 'Classic'"
                
        Returns:
            dict con resultado
        """
        await self._ensure_started()
        
        try:
            # Primero observar
            observation = await self.observe(f"find {description}")
            
            if observation.get("found") and observation.get("elements"):
                # Actuar sobre el primer elemento encontrado
                element = observation["elements"][0]
                action = element.get("action")
                
                if action:
                    response = await self.session.act(input=action)
                    logger.info(f"[Stagehand FIND_AND_ACT] {description}")
                    return {
                        "success": True,
                        "acted_on": description,
                        "element": element.get("description")
                    }
            
            # Fallback: intentar act directo
            logger.warning(f"[Stagehand] Elemento no encontrado, intentando act directo")
            return await self.act(f"click {description}")
                
        except Exception as e:
            logger.error(f"[Stagehand FIND_AND_ACT ERROR] {e}")
            return {"success": False, "error": str(e)}
    
    # =========================================
    # EXTRACCION DE DATOS
    # =========================================
    
    async def extract(self, instruction: str, schema: Dict) -> Dict:
        """
        Extrae datos estructurados de la pagina.
        
        Args:
            instruction: Que extraer.
                Ejemplo: "extract the product name and price"
            schema: Schema JSON del resultado esperado.
                Ejemplo: {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "price": {"type": "number"}
                    }
                }
                
        Returns:
            dict con datos extraidos
        """
        await self._ensure_started()
        
        try:
            logger.info(f"[Stagehand EXTRACT] {instruction}")
            response = await self.session.extract(
                instruction=instruction,
                schema=schema
            )
            
            result = {}
            if hasattr(response, 'data') and hasattr(response.data, 'result'):
                result = response.data.result or {}
            
            return {"success": True, "data": result}
        except Exception as e:
            logger.error(f"[Stagehand EXTRACT ERROR] {e}")
            return {"success": False, "error": str(e), "data": {}}
    
    # =========================================
    # AGENTE AUTONOMO
    # =========================================
    
    async def execute_task(self, instruction: str, max_steps: int = 10) -> Dict:
        """
        Ejecuta una tarea compleja usando el agente autonomo.
        El agente planifica y ejecuta multiples pasos automaticamente.
        
        Args:
            instruction: Instruccion de la tarea.
                Ejemplos:
                - "fill all empty slots with photos from the panel"
                - "navigate to page 3 and add a photo to the main slot"
                - "login with email test@test.com and password 123456"
            max_steps: Maximo de pasos a ejecutar (default: 10)
            
        Returns:
            dict con resultado
        """
        await self._ensure_started()
        
        try:
            logger.info(f"[Stagehand EXECUTE] {instruction} (max_steps={max_steps})")
            
            response = await self.session.execute(
                execute_options={
                    "instruction": instruction,
                    "max_steps": max_steps,
                },
                agent_config={"model": self.model_name},
                timeout=300.0,  # 5 minutos
            )
            
            message = "Task completed"
            success = False
            
            if hasattr(response, 'data') and hasattr(response.data, 'result'):
                result = response.data.result
                if hasattr(result, 'message'):
                    message = result.message
                if hasattr(result, 'success'):
                    success = result.success
            
            return {
                "success": success,
                "message": message,
                "instruction": instruction
            }
        except Exception as e:
            logger.error(f"[Stagehand EXECUTE ERROR] {e}")
            return {"success": False, "error": str(e), "instruction": instruction}
    
    # =========================================
    # ACCIONES ESPECIFICAS PARA FDF
    # =========================================
    
    async def drag_photo_to_slot(self, photo_description: str = "first photo", slot_description: str = "empty slot") -> Dict:
        """
        Arrastra una foto a un slot usando lenguaje natural.
        Stagehand interpreta visualmente donde estan los elementos.
        
        Args:
            photo_description: Descripcion de la foto a arrastrar
            slot_description: Descripcion del slot destino
            
        Returns:
            dict con resultado
        """
        instruction = f"drag {photo_description} from the photo panel to {slot_description} on the canvas"
        return await self.act(instruction)
    
    async def fill_all_slots(self, max_photos: int = 4) -> Dict:
        """
        Llena todos los slots vacios con fotos usando el agente.
        
        Args:
            max_photos: Maximo de fotos a colocar
            
        Returns:
            dict con resultado
        """
        instruction = f"drag photos from the left panel to fill all empty slots on the canvas, place up to {max_photos} photos"
        return await self.execute_task(instruction, max_steps=max_photos * 2)
    
    async def click_button(self, button_text: str) -> Dict:
        """Hace click en un boton por su texto"""
        return await self.act(f"click the button that says '{button_text}'")
    
    async def type_in_field(self, text: str, field_description: str) -> Dict:
        """Escribe texto en un campo"""
        return await self.act(f"type '{text}' in {field_description}")
    
    async def select_option(self, option: str, dropdown_description: str) -> Dict:
        """Selecciona una opcion de un dropdown"""
        return await self.act(f"select '{option}' from {dropdown_description}")


# =========================================
# CONTEXT MANAGER
# =========================================

@asynccontextmanager
async def stagehand_session(
    model_name: str = "google/gemini-2.0-flash",
    model_api_key: Optional[str] = None,
    headless: bool = False,
    use_browserbase: bool = False
):
    """
    Context manager para usar Stagehand facilmente.
    
    Uso:
        async with stagehand_session() as stagehand:
            await stagehand.navigate("https://example.com")
            await stagehand.act("click the login button")
    """
    wrapper = FDFStagehandWrapper(
        model_name=model_name,
        model_api_key=model_api_key,
        headless=headless,
        use_browserbase=use_browserbase
    )
    
    try:
        await wrapper.start()
        yield wrapper
    finally:
        await wrapper.stop()


# =========================================
# ACCIONES PRE-DEFINIDAS PARA FDF
# =========================================

class FDFStagehandActions:
    """Acciones pre-definidas para el editor de FDF"""
    
    def __init__(self, wrapper: FDFStagehandWrapper):
        self.wrapper = wrapper
    
    async def login(self, email: str, password: str) -> Dict:
        """Login a FDF"""
        result = await self.wrapper.execute_task(
            f"login with email '{email}' and password '{password}'",
            max_steps=5
        )
        return result
    
    async def select_template(self, template_name: str, for_editors: bool = True) -> Dict:
        """Selecciona un template por nombre"""
        version = "para Editores" if for_editors else ""
        return await self.wrapper.act(f"click the template named '{template_name}' {version}")
    
    async def upload_photos_from_computer(self) -> Dict:
        """Selecciona 'Desde computadora' como fuente de fotos"""
        return await self.wrapper.act("click the option to upload from computer or 'Desde computadora'")
    
    async def drag_photo_to_slot(self, photo_index: int, slot_description: str) -> Dict:
        """
        Arrastra una foto a un slot usando lenguaje natural.
        
        Args:
            photo_index: Indice de la foto (1-based para lenguaje natural)
            slot_description: Descripcion del slot destino
        """
        instruction = f"drag photo number {photo_index + 1} from the photo panel on the left to {slot_description}"
        return await self.wrapper.act(instruction)
    
    async def navigate_to_page(self, page_number: int) -> Dict:
        """Navega a una pagina especifica del libro"""
        return await self.wrapper.act(f"click on page {page_number} in the page navigator at the bottom")
    
    async def select_fill_mode(self, mode: str = "manual") -> Dict:
        """
        Selecciona el modo de relleno de fotos.
        
        Args:
            mode: "manual", "rapido" o "smart"
        """
        mode_map = {
            "manual": "Relleno fotos manual",
            "rapido": "Relleno fotos rapido",
            "smart": "Relleno fotos smart"
        }
        button_text = mode_map.get(mode, mode_map["manual"])
        return await self.wrapper.act(f"click the '{button_text}' button")
    
    async def get_page_info(self) -> Dict:
        """Extrae informacion de la pagina actual"""
        return await self.wrapper.extract(
            instruction="extract information about the current editor state",
            schema={
                "type": "object",
                "properties": {
                    "current_page": {"type": "integer"},
                    "total_pages": {"type": "integer"},
                    "has_empty_slots": {"type": "boolean"},
                    "photos_in_panel": {"type": "integer"}
                }
            }
        )
    
    async def go_to_checkout(self) -> Dict:
        """Navega al checkout"""
        return await self.wrapper.act("click the 'Pedir' or 'Finalizar' button to go to checkout")
    
    async def save_project(self) -> Dict:
        """Guarda el proyecto"""
        return await self.wrapper.act("click the 'Guardar' or 'Save' button")
