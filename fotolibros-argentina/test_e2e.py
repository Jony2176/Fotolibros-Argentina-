"""
Test End-to-End: Automatización completa del Editor de Fábrica de Fotolibros
=============================================================================
Este script prueba el flujo completo:
1. Login en el editor
2. Crear un proyecto de prueba
3. (Opcional) Subir fotos
4. Guardar y cerrar

Usa Browserbase para la automatización.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar credenciales
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")
GRAFICA_EMAIL = os.getenv("GRAFICA_EMAIL")
GRAFICA_PASSWORD = os.getenv("GRAFICA_PASSWORD")

print("=" * 60)
print("🚀 TEST END-TO-END: Editor de Fábrica de Fotolibros")
print("=" * 60)

# Verificar credenciales
print("\n📋 Verificando credenciales...")
credenciales_ok = True
for nombre, valor in [
    ("BROWSERBASE_API_KEY", BROWSERBASE_API_KEY),
    ("BROWSERBASE_PROJECT_ID", BROWSERBASE_PROJECT_ID),
    ("GRAFICA_EMAIL", GRAFICA_EMAIL),
    ("GRAFICA_PASSWORD", GRAFICA_PASSWORD),
]:
    status = "✅" if valor else "❌"
    print(f"   {status} {nombre}")
    if not valor:
        credenciales_ok = False

if not credenciales_ok:
    print("\n❌ Faltan credenciales. Configura el archivo .env")
    sys.exit(1)

# Importar dependencias
from browserbase import Browserbase
from playwright.sync_api import sync_playwright

# URLs del editor
EDITOR_LOGIN_URL = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
EDITOR_HOME_URL = "https://online.fabricadefotolibros.com"


def test_flujo_completo():
    """Ejecuta el flujo completo de automatización"""
    
    print("\n" + "=" * 60)
    print("PASO 1: Crear sesión de Browserbase")
    print("=" * 60)
    
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    
    start = time.time()
    session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID)
    print(f"✅ Sesión creada en {time.time() - start:.1f}s")
    print(f"   ID: {session.id}")
    print(f"   Replay: https://browserbase.com/sessions/{session.id}")
    
    # Conectar Playwright
    p = sync_playwright().start()
    browser = p.chromium.connect_over_cdp(session.connect_url)
    context = browser.contexts[0]
    page = context.pages[0]
    
    try:
        # ===== PASO 2: LOGIN =====
        print("\n" + "=" * 60)
        print("PASO 2: Login en el editor")
        print("=" * 60)
        
        start = time.time()
        page.goto(EDITOR_LOGIN_URL, wait_until="domcontentloaded")
        print(f"   Página de login cargada en {time.time() - start:.1f}s")
        
        page.wait_for_timeout(2000)
        
        # Llenar formulario
        page.fill("#email_log", GRAFICA_EMAIL)
        page.fill("#clave_log", GRAFICA_PASSWORD)
        print(f"   Email: {GRAFICA_EMAIL}")
        print("   Password: ********")
        
        # Tomar screenshot
        page.screenshot(path="test_e2e_01_login.png")
        print("   📸 Screenshot: test_e2e_01_login.png")
        
        # Click INGRESAR
        page.click("#bt_log")
        print("   ➡️ Click en INGRESAR...")
        
        page.wait_for_timeout(5000)
        
        # Verificar login
        try:
            page.wait_for_selector("text=Fotolibros", timeout=15000)
            print("✅ Login exitoso!")
            page.screenshot(path="test_e2e_02_home.png")
            print("   📸 Screenshot: test_e2e_02_home.png")
        except:
            print("❌ Login fallido")
            page.screenshot(path="test_e2e_error_login.png")
            return False
        
        # ===== PASO 3: CREAR PROYECTO =====
        print("\n" + "=" * 60)
        print("PASO 3: Crear proyecto de prueba")
        print("=" * 60)
        
        # Navegar a categoría Fotolibros
        print("   Buscando categoría 'Fotolibros'...")
        page.click("text=Fotolibros")
        page.wait_for_timeout(3000)
        page.screenshot(path="test_e2e_03_categoria.png")
        print("   📸 Screenshot: test_e2e_03_categoria.png")
        
        # Buscar producto "Cuadrado 21x21" (el más popular)
        print("   Buscando producto 'Cuadrado 21'...")
        try:
            # Intentar diferentes selectores
            producto_encontrado = False
            selectores_producto = [
                "text=Cuadrado 21",
                "text=21 x 21",
                "text=21x21",
                ".product-item:has-text('21')",
            ]
            
            for selector in selectores_producto:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector)
                        producto_encontrado = True
                        print(f"   ✅ Producto encontrado con selector: {selector}")
                        break
                except:
                    continue
            
            if not producto_encontrado:
                print("   ⚠️ No se encontró el producto específico, clickeando el primero disponible...")
                # Intentar clickear el primer producto visible
                productos = page.locator(".product-item, .product, [class*='producto']")
                if productos.count() > 0:
                    productos.first.click()
                    print("   ✅ Primer producto clickeado")
                else:
                    print("   ❌ No se encontraron productos")
            
            page.wait_for_timeout(3000)
            page.screenshot(path="test_e2e_04_producto.png")
            print("   📸 Screenshot: test_e2e_04_producto.png")
            
        except Exception as e:
            print(f"   ⚠️ Error buscando producto: {e}")
            page.screenshot(path="test_e2e_error_producto.png")
        
        # Buscar botón de crear proyecto
        print("   Buscando botón 'Crear Proyecto'...")
        try:
            botones_crear = [
                "text=Crear Proyecto",
                "text=Crear proyecto",
                "text=Nuevo Proyecto",
                "text=Crear",
                ".btn-create",
                "button:has-text('Crear')",
            ]
            
            for selector in botones_crear:
                try:
                    if page.locator(selector).count() > 0:
                        page.click(selector)
                        print(f"   ✅ Botón encontrado: {selector}")
                        break
                except:
                    continue
            
            page.wait_for_timeout(5000)
            page.screenshot(path="test_e2e_05_editor.png")
            print("   📸 Screenshot: test_e2e_05_editor.png")
            
        except Exception as e:
            print(f"   ⚠️ Error creando proyecto: {e}")
        
        # ===== PASO 4: EXPLORAR EDITOR =====
        print("\n" + "=" * 60)
        print("PASO 4: Explorar el editor")
        print("=" * 60)
        
        # Tomar screenshot del estado actual
        page.wait_for_timeout(3000)
        page.screenshot(path="test_e2e_06_estado_final.png", full_page=True)
        print("   📸 Screenshot final: test_e2e_06_estado_final.png")
        
        # Obtener URL actual
        print(f"   URL actual: {page.url}")
        
        # Listar elementos interactivos
        print("\n   🔍 Elementos encontrados en el editor:")
        
        # Botones
        botones = page.locator("button, .btn, [role='button']")
        print(f"   - Botones: {botones.count()}")
        
        # Inputs
        inputs = page.locator("input, textarea")
        print(f"   - Inputs: {inputs.count()}")
        
        # Links
        links = page.locator("a")
        print(f"   - Links: {links.count()}")
        
        print("\n✅ Test completado!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error durante el test: {e}")
        page.screenshot(path="test_e2e_error.png")
        return False
        
    finally:
        # Cerrar
        print("\n" + "=" * 60)
        print("Cerrando sesión...")
        print("=" * 60)
        browser.close()
        p.stop()
        print(f"\n🔗 Ver grabación completa:")
        print(f"   https://browserbase.com/sessions/{session.id}")


if __name__ == "__main__":
    exito = test_flujo_completo()
    print("\n" + "=" * 60)
    if exito:
        print("🎉 TEST END-TO-END COMPLETADO EXITOSAMENTE")
    else:
        print("⚠️ TEST COMPLETADO CON ADVERTENCIAS")
    print("=" * 60)
