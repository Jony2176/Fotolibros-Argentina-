"""
Error Handling & Retry Utilities
================================
Manejo robusto de errores para el toolkit de FDF.

Incluye:
- Decorador de retry con backoff exponencial
- Excepciones personalizadas
- Logging estructurado
- Fallbacks para Vision
"""

import asyncio
import functools
import logging
import traceback
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union

# ============================================
# LOGGING CONFIGURATION
# ============================================

class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class FDFLogger:
    """Logger estructurado para el toolkit FDF"""
    
    def __init__(self, name: str = "FDF", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Formato con colores para consola
        console_format = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Handler de consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_format)
        
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
        
        # Handler de archivo (opcional)
        if log_file:
            file_format = logging.Formatter(
                '%(asctime)s [%(levelname)s] [%(name)s] %(message)s'
            )
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)
        
        self.operation_stack: List[str] = []
    
    def _format_message(self, msg: str, context: Optional[Dict] = None) -> str:
        """Formatea mensaje con contexto"""
        prefix = " > ".join(self.operation_stack) if self.operation_stack else ""
        if prefix:
            msg = f"[{prefix}] {msg}"
        if context:
            ctx_str = " | ".join(f"{k}={v}" for k, v in context.items())
            msg = f"{msg} ({ctx_str})"
        return msg
    
    def debug(self, msg: str, context: Optional[Dict] = None):
        self.logger.debug(self._format_message(msg, context))
    
    def info(self, msg: str, context: Optional[Dict] = None):
        self.logger.info(self._format_message(msg, context))
    
    def warning(self, msg: str, context: Optional[Dict] = None):
        self.logger.warning(self._format_message(msg, context))
    
    def error(self, msg: str, context: Optional[Dict] = None, exc: Optional[Exception] = None):
        full_msg = self._format_message(msg, context)
        if exc:
            full_msg += f"\n  Exception: {type(exc).__name__}: {exc}"
        self.logger.error(full_msg)
    
    def critical(self, msg: str, context: Optional[Dict] = None):
        self.logger.critical(self._format_message(msg, context))
    
    def start_operation(self, name: str):
        """Inicia una operación (para tracking anidado)"""
        self.operation_stack.append(name)
        self.debug(f"Iniciando: {name}")
    
    def end_operation(self, success: bool = True):
        """Finaliza la operación actual"""
        if self.operation_stack:
            op = self.operation_stack.pop()
            status = "OK" if success else "FAILED"
            self.debug(f"Finalizado: {op} [{status}]")


# Logger global
logger = FDFLogger("FDF")


# ============================================
# CUSTOM EXCEPTIONS
# ============================================

class FDFError(Exception):
    """Excepción base para errores de FDF"""
    def __init__(self, message: str, details: Optional[Dict] = None, recoverable: bool = True):
        self.message = message
        self.details = details or {}
        self.recoverable = recoverable
        self.timestamp = datetime.now()
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "recoverable": self.recoverable,
            "timestamp": self.timestamp.isoformat()
        }


class LoginError(FDFError):
    """Error en el proceso de login"""
    pass


class NavigationError(FDFError):
    """Error navegando en la página"""
    pass


class UploadError(FDFError):
    """Error subiendo archivos"""
    pass


class TemplateError(FDFError):
    """Error seleccionando template"""
    pass


class EditorError(FDFError):
    """Error en el editor de fotolibros"""
    pass


class VisionError(FDFError):
    """Error en el análisis con Vision"""
    pass


class DragDropError(FDFError):
    """Error en drag & drop"""
    pass


class CheckoutError(FDFError):
    """Error en el proceso de checkout"""
    pass


class TimeoutError(FDFError):
    """Timeout esperando un elemento o acción"""
    pass


# ============================================
# RETRY DECORATOR
# ============================================

def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    on_retry: Optional[Callable] = None,
    fallback: Optional[Callable] = None
):
    """
    Decorador para reintentar funciones async con backoff exponencial.
    
    Args:
        max_attempts: Número máximo de intentos
        delay: Delay inicial entre intentos (segundos)
        backoff: Multiplicador de backoff (delay *= backoff cada intento)
        exceptions: Tupla de excepciones que disparan retry
        on_retry: Callback opcional llamado antes de cada retry (attempt, exception)
        fallback: Función fallback si todos los intentos fallan
        
    Example:
        @retry_async(max_attempts=3, delay=1.0, backoff=2.0)
        async def mi_funcion():
            ...
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        logger.error(
                            f"Todos los intentos fallaron para {func.__name__}",
                            context={"attempts": max_attempts},
                            exc=e
                        )
                        break
                    
                    logger.warning(
                        f"Intento {attempt}/{max_attempts} falló para {func.__name__}",
                        context={"error": str(e), "next_delay": current_delay}
                    )
                    
                    if on_retry:
                        try:
                            await on_retry(attempt, e) if asyncio.iscoroutinefunction(on_retry) else on_retry(attempt, e)
                        except:
                            pass
                    
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            # Todos los intentos fallaron
            if fallback:
                logger.info(f"Ejecutando fallback para {func.__name__}")
                try:
                    return await fallback(*args, **kwargs) if asyncio.iscoroutinefunction(fallback) else fallback(*args, **kwargs)
                except Exception as fb_err:
                    logger.error(f"Fallback también falló", exc=fb_err)
            
            # Re-raise la última excepción
            raise last_exception
        
        return wrapper
    return decorator


def retry_sync(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Versión síncrona del decorador retry"""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            last_exception = None
            current_delay = delay
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt == max_attempts:
                        break
                    logger.warning(f"Retry {attempt}/{max_attempts} para {func.__name__}")
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
        return wrapper
    return decorator


# ============================================
# RETRY HELPER (para uso inline)
# ============================================

async def with_retry(
    func: Callable,
    *args,
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    error_message: str = "Operación fallida",
    **kwargs
) -> Any:
    """
    Helper para ejecutar una función con retry de forma inline.
    
    Usage:
        result = await with_retry(
            toolkit.login,
            max_attempts=3,
            error_message="Login falló"
        )
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(1, max_attempts + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
                
        except Exception as e:
            last_exception = e
            
            if attempt == max_attempts:
                logger.error(f"{error_message} después de {max_attempts} intentos", exc=e)
                break
            
            logger.warning(f"{error_message} - Reintentando ({attempt}/{max_attempts})")
            await asyncio.sleep(current_delay)
            current_delay *= backoff
    
    return {"success": False, "error": str(last_exception), "attempts": max_attempts}


# ============================================
# VISION FALLBACKS
# ============================================

class VisionFallback:
    """
    Fallbacks para cuando Vision falla en detectar elementos.
    Usa métodos DOM como alternativa.
    """
    
    @staticmethod
    async def detect_photos_fallback(page) -> Dict:
        """Detecta fotos usando DOM cuando Vision falla"""
        logger.info("Usando fallback DOM para detectar fotos")
        
        try:
            selectors = [
                ".photo-thumb", ".thumbnail", ".uploaded-photo",
                ".foto-item", ".photo-item", "[data-photo]",
                ".galeria img", ".photos-list img", "img[src*='thumb']"
            ]
            
            photos = []
            for selector in selectors:
                elements = await page.query_selector_all(selector)
                if elements:
                    for i, el in enumerate(elements):
                        box = await el.bounding_box()
                        if box:
                            photos.append({
                                "index": i,
                                "x": box["x"] + box["width"] / 2,
                                "y": box["y"] + box["height"] / 2,
                                "width": box["width"],
                                "height": box["height"],
                                "source": "dom_fallback"
                            })
                    break
            
            return {"success": True, "photos": photos, "method": "dom_fallback"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def detect_slots_fallback(page) -> Dict:
        """Detecta slots usando DOM cuando Vision falla"""
        logger.info("Usando fallback DOM para detectar slots")
        
        try:
            # Buscar el área principal del canvas
            canvas_selectors = [
                "#canvas", ".canvas-container", ".workspace",
                ".editor-canvas", ".page-preview", "[data-canvas]",
                ".editor-main", ".main-content", "#editorContainer"
            ]
            
            slots = []
            
            for selector in canvas_selectors:
                canvas = await page.query_selector(selector)
                if canvas:
                    box = await canvas.bounding_box()
                    if box:
                        # Crear slot central
                        slots.append({
                            "id": "center",
                            "x": box["x"] + box["width"] / 2,
                            "y": box["y"] + box["height"] / 2,
                            "width": box["width"] * 0.7,
                            "height": box["height"] * 0.7,
                            "source": "dom_fallback"
                        })
                        break
            
            # Buscar slots explícitos
            slot_selectors = [
                ".photo-slot", ".drop-zone", ".placeholder",
                "[data-slot]", ".foto-area", ".image-container"
            ]
            
            for selector in slot_selectors:
                elements = await page.query_selector_all(selector)
                for i, el in enumerate(elements):
                    box = await el.bounding_box()
                    if box:
                        slots.append({
                            "id": f"slot_{i}",
                            "x": box["x"] + box["width"] / 2,
                            "y": box["y"] + box["height"] / 2,
                            "width": box["width"],
                            "height": box["height"],
                            "source": "dom_fallback"
                        })
            
            return {"success": True, "slots": slots, "method": "dom_fallback"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def simple_drag_drop(page, from_x: float, from_y: float, to_x: float, to_y: float) -> Dict:
        """Drag & drop simple sin Vision"""
        logger.info(f"Drag & drop simple: ({from_x}, {from_y}) -> ({to_x}, {to_y})")
        
        try:
            await page.mouse.move(from_x, from_y)
            await asyncio.sleep(0.3)
            await page.mouse.down()
            await asyncio.sleep(0.2)
            
            # Movimiento en pasos
            steps = 10
            for i in range(steps + 1):
                progress = i / steps
                x = from_x + (to_x - from_x) * progress
                y = from_y + (to_y - from_y) * progress
                await page.mouse.move(x, y)
                await asyncio.sleep(0.03)
            
            await asyncio.sleep(0.2)
            await page.mouse.up()
            await asyncio.sleep(0.5)
            
            return {"success": True, "method": "simple_drag"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}


# ============================================
# ERROR RECOVERY STRATEGIES
# ============================================

class RecoveryStrategy:
    """Estrategias de recuperación para diferentes errores"""
    
    @staticmethod
    async def recover_from_navigation_error(page, toolkit) -> bool:
        """Intenta recuperarse de un error de navegación"""
        logger.info("Intentando recuperar de error de navegación")
        
        try:
            # Refrescar la página
            await page.reload()
            await asyncio.sleep(3)
            
            # Verificar si seguimos logueados
            content = await page.content()
            if "email_log" in content or "login" in page.url.lower():
                # Necesitamos re-login
                logger.warning("Sesión perdida, re-login necesario")
                await toolkit.login()
            
            return True
            
        except Exception as e:
            logger.error("Recovery de navegación falló", exc=e)
            return False
    
    @staticmethod
    async def recover_from_editor_error(page, toolkit) -> bool:
        """Intenta recuperarse de un error en el editor"""
        logger.info("Intentando recuperar de error en editor")
        
        try:
            # Cerrar posibles modales
            close_selectors = [
                "button:has-text('Cerrar')",
                "button:has-text('X')",
                ".modal-close",
                "[aria-label='close']",
                ".close-btn"
            ]
            
            for selector in close_selectors:
                try:
                    if await page.locator(selector).count() > 0:
                        await page.click(selector, timeout=2000)
                        await asyncio.sleep(0.5)
                except:
                    continue
            
            # Esperar a que el editor se estabilice
            await asyncio.sleep(2)
            
            return True
            
        except Exception as e:
            logger.error("Recovery de editor falló", exc=e)
            return False
    
    @staticmethod
    async def recover_from_timeout(page, action_name: str) -> bool:
        """Intenta recuperarse de un timeout"""
        logger.info(f"Intentando recuperar de timeout en: {action_name}")
        
        try:
            # Esperar un poco más
            await asyncio.sleep(5)
            
            # Verificar que la página responda
            await page.evaluate("() => document.readyState")
            
            return True
            
        except Exception as e:
            logger.error("Recovery de timeout falló", exc=e)
            return False


# ============================================
# CONTEXT MANAGER PARA OPERACIONES
# ============================================

class SafeOperation:
    """
    Context manager para ejecutar operaciones de forma segura con retry y recovery.
    
    Usage:
        async with SafeOperation("login", toolkit, max_retries=3) as op:
            result = await toolkit.login()
            if not result.get("success"):
                raise LoginError("Login falló")
            op.result = result
    """
    
    def __init__(
        self,
        name: str,
        toolkit,
        max_retries: int = 3,
        recovery_func: Optional[Callable] = None
    ):
        self.name = name
        self.toolkit = toolkit
        self.max_retries = max_retries
        self.recovery_func = recovery_func
        self.result = None
        self.attempt = 0
        self.success = False
    
    async def __aenter__(self):
        logger.start_operation(self.name)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.success = True
            logger.end_operation(success=True)
            return False
        
        # Hubo una excepción
        logger.error(f"Error en {self.name}", exc=exc_val)
        
        # Intentar recovery si está configurado
        if self.recovery_func and self.attempt < self.max_retries:
            self.attempt += 1
            logger.info(f"Intentando recovery ({self.attempt}/{self.max_retries})")
            
            try:
                recovered = await self.recovery_func(self.toolkit.page, self.toolkit)
                if recovered:
                    logger.info("Recovery exitoso")
                    # No suprimir la excepción para que el caller pueda reintentar
            except Exception as recovery_error:
                logger.error("Recovery falló", exc=recovery_error)
        
        logger.end_operation(success=False)
        return False  # No suprimir la excepción


# ============================================
# HEALTH CHECK
# ============================================

async def health_check(toolkit) -> Dict:
    """
    Verifica el estado del toolkit y la conexión.
    
    Returns:
        Dict con estado de cada componente
    """
    status = {
        "browser": False,
        "page": False,
        "logged_in": False,
        "editor_ready": False,
        "vision_available": False
    }
    
    try:
        # Browser
        if toolkit.browser and toolkit.browser.is_connected():
            status["browser"] = True
        
        # Page
        if toolkit.page:
            status["page"] = True
            
            # Verificar que responda
            try:
                await toolkit.page.evaluate("() => true")
            except:
                status["page"] = False
        
        # Login status
        status["logged_in"] = toolkit.logged_in
        
        # Editor ready
        if status["page"]:
            page_info = await toolkit.get_page_info()
            status["editor_ready"] = page_info.get("page_type") == "editor"
        
        # Vision (verificar API key)
        if toolkit.model_api_key:
            status["vision_available"] = True
        
    except Exception as e:
        logger.error("Health check falló", exc=e)
    
    status["healthy"] = all([
        status["browser"],
        status["page"]
    ])
    
    return status


# ============================================
# EXPORTS
# ============================================

__all__ = [
    # Logger
    "FDFLogger",
    "logger",
    
    # Exceptions
    "FDFError",
    "LoginError",
    "NavigationError",
    "UploadError",
    "TemplateError",
    "EditorError",
    "VisionError",
    "DragDropError",
    "CheckoutError",
    "TimeoutError",
    
    # Retry
    "retry_async",
    "retry_sync",
    "with_retry",
    
    # Fallbacks
    "VisionFallback",
    
    # Recovery
    "RecoveryStrategy",
    "SafeOperation",
    
    # Utils
    "health_check"
]
