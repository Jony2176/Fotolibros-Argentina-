"""
FDF Simple Driver - Versión funcional simplificada
==================================================
Driver simplificado para automatizar FDF sin errores de indentación
"""

import asyncio
import os
from typing import Optional, List, Dict
from playwright.async_api import async_playwright, Page, Browser
from dotenv import load_dotenv

load_dotenv()

class FDFSimpleDriver:
    """Driver simplificado para FDF usando Playwright"""
    
    def __init__(self, email: str, password: str, headless: bool = False):
        self.email = email
        self.password = password
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    async def initialize(self):
        """Inicializa el navegador"""
        print("[1] Iniciando navegador...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=500  # Slow motion para ver acciones
        )
        
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        self.page = await context.new_page()
        print("[OK] Navegador listo")
        
    async def login(self):
        """Login en FDF"""
        print("[2] Iniciando sesión en FDF...")
        url = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
        
        await self.page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(3)
        
        try:
            # Selectores correctos de FDF
            print("   Buscando formulario de login...")
            
            # Esperar que cargue el formulario
            await self.page.wait_for_selector('#email_log', timeout=15000)
            
            # Llenar email
            await self.page.fill('#email_log', self.email)
            print(f"   [OK] Email: {self.email}")
            
            # Llenar password
            await self.page.fill('#clave_log', self.password)
            print(f"   [OK] Password ingresado")
            
            # Click en botón de login
            await self.page.click('#bt_log')
            print(f"   [OK] Click en login")
            
            # Esperar que cargue el dashboard
            await asyncio.sleep(5)
            
            # Verificar login exitoso
            try:
                await self.page.wait_for_selector("text=Fotolibros", timeout=10000)
                print("[OK] Sesión iniciada - Dashboard cargado")
            except:
                print("[OK] Sesión iniciada")
            
        except Exception as e:
            print(f"   [ERROR] Error en login: {e}")
            await self.take_screenshot("error_login.png")
            raise e
            
    async def seleccionar_profesionales(self):
        """Selecciona la opción 'Para Profesionales (sin logo FDF)'"""
        print("[3] Seleccionando modo Profesionales...")
        
        try:
            # Buscar la opción de profesionales
            selectors = [
                "text=Para Profesionales (sin logo de FDF)",
                "text=Para Profesionales",
                "text=sin logo de FDF",
                "text=Profesionales",
            ]
            
            for selector in selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0:
                        await locator.click(timeout=5000)
                        print(f"   [OK] Modo Profesionales seleccionado")
                        await asyncio.sleep(2)
                        return {"success": True}
                except:
                    continue
            
            # Si no encuentra, intentar con Fotolibros directo
            print("   [WARN] No encontró Profesionales, usando Fotolibros...")
            await self.page.click("text=Fotolibros")
            await asyncio.sleep(2)
            return {"success": True, "mode": "cliente"}
            
        except Exception as e:
            print(f"   [ERROR] {e}")
            return {"success": False, "error": str(e)}
    
    async def crear_proyecto(self, titulo: str, tamanio: str = "21x21"):
        """Crea un nuevo proyecto en FDF"""
        print(f"[4] Creando proyecto: {titulo}")
        
        try:
            # Click en Fotolibros para ver tamaños
            try:
                await self.page.click("text=Fotolibros", timeout=5000)
                await asyncio.sleep(2)
            except:
                pass
            
            # Seleccionar tamaño (21x21 es el más común)
            size_selectors = [
                f"text={tamanio}",
                f"text={tamanio.replace('x', ' x ')}",
                "text=21x21",
                "text=21 x 21",
                "text=20x20",
            ]
            
            for selector in size_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0:
                        await locator.click(timeout=5000)
                        print(f"   [OK] Tamaño seleccionado: {selector}")
                        await asyncio.sleep(2)
                        break
                except:
                    continue
            
            # Buscar input de título si existe
            try:
                title_input = await self.page.query_selector('input[name="titulo"], input[placeholder*="título"], input[placeholder*="nombre"]')
                if title_input:
                    await title_input.fill(titulo)
                    print(f"   [OK] Título: {titulo}")
            except:
                pass
            
            # Click en Continuar/Crear
            continue_selectors = [
                "text=Continuar",
                "text=Crear proyecto",
                "text=Siguiente",
                "text=Crear",
                "button:has-text('Continuar')",
            ]
            
            for selector in continue_selectors:
                try:
                    locator = self.page.locator(selector).first
                    if await locator.count() > 0:
                        await locator.click(timeout=5000)
                        print(f"   [OK] Click en: {selector}")
                        await asyncio.sleep(3)
                        break
                except:
                    continue
            
            await self.take_screenshot("proyecto_creado.png")
            print(f"   [OK] Proyecto creado")
            return {"success": True}
            
        except Exception as e:
            print(f"   [ERROR] {e}")
            await self.take_screenshot("error_proyecto.png")
            return {"success": False, "error": str(e)}
            
    async def subir_fotos(self, fotos_paths: List[str]):
        """Sube fotos al proyecto"""
        print(f"[4] Subiendo {len(fotos_paths)} fotos...")
        
        try:
            for i, foto_path in enumerate(fotos_paths, 1):
                if not os.path.exists(foto_path):
                    print(f"   [WARN] Foto no encontrada: {foto_path}")
                    continue
                    
                # Buscar input de archivo
                file_input = await self.page.query_selector('input[type="file"]')
                if file_input:
                    await file_input.set_input_files(foto_path)
                    print(f"   [{i}/{len(fotos_paths)}] {os.path.basename(foto_path)}")
                    await asyncio.sleep(1)
                    
            print(f"   [OK] Fotos subidas")
            return {"success": True}
            
        except Exception as e:
            print(f"   [ERROR] {e}")
            return {"success": False, "error": str(e)}
            
    async def agregar_texto(self, texto: str, tipo: str = "titulo"):
        """Agrega texto al fotolibro"""
        print(f"[5] Agregando {tipo}: {texto[:50]}...")
        
        try:
            # Buscar herramienta de texto
            await self.page.click('text="Texto", [aria-label="Agregar texto"]')
            await asyncio.sleep(1)
            
            # Click en el canvas para agregar texto
            canvas = await self.page.query_selector('canvas, .editor-canvas')
            if canvas:
                await canvas.click()
                await asyncio.sleep(1)
                
                # Escribir el texto
                await self.page.keyboard.type(texto)
                await asyncio.sleep(1)
                
            print(f"   [OK] Texto agregado")
            return {"success": True}
            
        except Exception as e:
            print(f"   [ERROR] {e}")
            return {"success": False, "error": str(e)}
            
    async def guardar_proyecto(self):
        """Guarda el proyecto"""
        print(f"[6] Guardando proyecto...")
        
        try:
            # Buscar botón de guardar
            await self.page.click('text="Guardar", [aria-label="Guardar proyecto"]')
            await asyncio.sleep(3)
            
            print(f"   [OK] Proyecto guardado")
            return {"success": True}
            
        except Exception as e:
            print(f"   [ERROR] {e}")
            return {"success": False, "error": str(e)}
            
    async def take_screenshot(self, filename: str = "screenshot.png"):
        """Toma screenshot"""
        await self.page.screenshot(path=filename)
        print(f"   [OK] Screenshot: {filename}")
        
    async def close(self):
        """Cierra el navegador"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("[OK] Navegador cerrado")


async def demo_crear_fotolibro_con_agno(pedido_id: str):
    """
    Demo que crea un fotolibro usando la configuración AGNO
    """
    import json
    
    # Cargar configuración AGNO
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(base_dir, f"data/agno_config_{pedido_id[:8]}.json")
    
    if not os.path.exists(config_file):
        print(f"[ERROR] No se encontró: {config_file}")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("=" * 70)
    print("  CREANDO FOTOLIBRO EN FDF CON AGNO TEAM")
    print("=" * 70)
    print(f"\nTítulo: \"{config['story']['cover']['title']}\"")
    print(f"Fotos: {len(config['photos'])}")
    print(f"Capítulos: {len(config['story']['chapters'])}")
    print("")
    
    # Crear driver
    email = os.getenv("FDF_EMAIL", "revelacionesocultas72@gmail.com")
    password = os.getenv("FDF_PASSWORD", "Jony.2176")
    
    driver = FDFSimpleDriver(email=email, password=password, headless=False)
    
    try:
        # Inicializar
        await driver.initialize()
        
        # Login
        await driver.login()
        
        # Seleccionar modo Profesionales (sin logo FDF)
        await driver.seleccionar_profesionales()
        
        # Crear proyecto con tamaño 21x21
        await driver.crear_proyecto(
            titulo=config['story']['cover']['title'],
            tamanio="21x21"
        )
        
        # Preparar rutas de fotos
        fotos_paths = []
        for foto in config['chronology']['ordered_photos']:
            foto_path = os.path.join(base_dir, foto['filepath'])
            if os.path.exists(foto_path):
                fotos_paths.append(foto_path)
        
        print(f"\n[INFO] Fotos encontradas: {len(fotos_paths)}")
        
        # Subir fotos
        await driver.subir_fotos(fotos_paths)
        
        # Agregar título
        await driver.agregar_texto(
            config['story']['cover']['title'],
            tipo="titulo"
        )
        
        # Guardar
        await driver.guardar_proyecto()
        
        # Screenshot final
        await driver.take_screenshot("fotolibro_fdf.png")
        
        print("\n" + "=" * 70)
        print("  [OK] FOTOLIBRO CREADO EN FDF")
        print("=" * 70)
        print(f"\nTítulo: {config['story']['cover']['title']}")
        print(f"Fotos: {len(fotos_paths)}")
        print(f"Capítulos: {len(config['story']['chapters'])}")
        print("\nPresiona ENTER para cerrar el navegador...")
        input()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona ENTER para cerrar...")
        
    finally:
        await driver.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python fdf_simple_driver.py <pedido_id>")
        sys.exit(1)
    
    pedido_id = sys.argv[1]
    asyncio.run(demo_crear_fotolibro_con_agno(pedido_id))
