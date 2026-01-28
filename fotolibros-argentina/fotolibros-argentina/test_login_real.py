"""
Test de Login Real en Fábrica de Fotolibros
============================================
Prueba el login completo usando Browserbase + credenciales reales.
"""

import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()

# Verificar credenciales
print("📋 Verificando credenciales...")
print(f"   BROWSERBASE_API_KEY: {'✅' if os.getenv('BROWSERBASE_API_KEY') else '❌'}")
print(f"   BROWSERBASE_PROJECT_ID: {'✅' if os.getenv('BROWSERBASE_PROJECT_ID') else '❌'}")
print(f"   GRAFICA_EMAIL: {'✅' if os.getenv('GRAFICA_EMAIL') else '❌'}")
print(f"   GRAFICA_PASSWORD: {'✅' if os.getenv('GRAFICA_PASSWORD') else '❌'}")

from browserbase import Browserbase
from playwright.sync_api import sync_playwright
import time

# Configuración desde .env
BROWSERBASE_API_KEY = os.getenv("BROWSERBASE_API_KEY")
BROWSERBASE_PROJECT_ID = os.getenv("BROWSERBASE_PROJECT_ID")
GRAFICA_EMAIL = os.getenv("GRAFICA_EMAIL")
GRAFICA_PASSWORD = os.getenv("GRAFICA_PASSWORD")

EDITOR_LOGIN_URL = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"

def test_login():
    print("\n🚀 Iniciando test de login en Fábrica de Fotolibros...")
    
    # Crear sesión de Browserbase
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
        # Navegar a login
        print("\n🌐 Navegando a página de login...")
        start = time.time()
        page.goto(EDITOR_LOGIN_URL, wait_until="domcontentloaded")
        print(f"   Página cargada en {time.time() - start:.1f}s")
        
        # Screenshot antes de login
        page.screenshot(path="screenshot_login_page.png")
        print("   📸 Screenshot: screenshot_login_page.png")
        
        # Llenar formulario
        print("\n🔐 Llenando formulario de login...")
        page.wait_for_timeout(2000)
        
        # Buscar campos de login
        email_field = page.locator("#email_log")
        password_field = page.locator("#clave_log")
        
        if email_field.count() > 0:
            email_field.fill(GRAFICA_EMAIL)
            password_field.fill(GRAFICA_PASSWORD)
            print(f"   Email: {GRAFICA_EMAIL}")
            print("   Password: ********")
            
            # Click en INGRESAR
            page.click("#bt_log")
            print("   ➡️ Click en INGRESAR...")
            
            page.wait_for_timeout(5000)
            
            # Screenshot después de login
            page.screenshot(path="screenshot_after_login.png")
            print("   📸 Screenshot: screenshot_after_login.png")
            
            # Verificar login exitoso
            try:
                page.wait_for_selector("text=Fotolibros", timeout=10000)
                print("\n✅ ¡LOGIN EXITOSO! - Se encontró sección 'Fotolibros'")
                
                # Screenshot del dashboard
                page.screenshot(path="screenshot_dashboard.png")
                print("   📸 Screenshot: screenshot_dashboard.png")
                
                return True
            except:
                print("\n❌ Login fallido - No se encontró sección 'Fotolibros'")
                # Capturar error
                page.screenshot(path="screenshot_error.png")
                print("   📸 Screenshot de error: screenshot_error.png")
                return False
        else:
            print("   ❌ No se encontró el formulario de login")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        page.screenshot(path="screenshot_error.png")
        return False
        
    finally:
        # Cerrar
        browser.close()
        p.stop()
        print(f"\n🔗 Ver grabación completa: https://browserbase.com/sessions/{session.id}")

if __name__ == "__main__":
    test_login()
