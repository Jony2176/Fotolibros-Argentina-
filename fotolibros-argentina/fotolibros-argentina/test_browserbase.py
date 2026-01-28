"""
Script de prueba para Browserbase + Fábrica de Fotolibros

Antes de ejecutar:
1. pip install browserbase playwright
2. playwright install chromium
3. Configurar las variables de entorno abajo
"""

import os
from browserbase import Browserbase
from playwright.sync_api import sync_playwright

# ============ CONFIGURAR AQUÍ ============
BROWSERBASE_API_KEY = "bb_live_uyHSRbZ7_5XT0kNvltt1xJfxfcQ"
BROWSERBASE_PROJECT_ID = "35743d70-110d-427b-adad-1e8fb780bfd3"
GRAFICA_EMAIL = os.getenv("GRAFICA_EMAIL", "tu-email@ejemplo.com")
GRAFICA_PASSWORD = os.getenv("GRAFICA_PASSWORD", "tu-password")
# ==========================================

def test_browserbase():
    """Prueba básica de conexión a Browserbase"""
    print("🚀 Iniciando prueba de Browserbase...")
    
    # Conectar a Browserbase
    bb = Browserbase(api_key=BROWSERBASE_API_KEY)
    
    # Crear sesión
    print("📡 Creando sesión en la nube...")
    session = bb.sessions.create(project_id=BROWSERBASE_PROJECT_ID)
    print(f"✅ Sesión creada: {session.id}")
    
    # Conectar Playwright
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(session.connect_url)
        context = browser.contexts[0]
        page = context.pages[0]
        
        # Navegar al editor
        print("🌐 Navegando a Fábrica de Fotolibros...")
        page.goto("https://online.fabricadefotolibros.com/edit/fotolibro2")
        page.wait_for_load_state("networkidle")
        
        # Tomar screenshot
        page.screenshot(path="browserbase_test.png")
        print("📸 Screenshot guardado: browserbase_test.png")
        
        # Verificar si hay login
        if page.locator("input[type='email']").count() > 0:
            print("🔐 Página de login detectada")
            print(f"   Intentando login con: {GRAFICA_EMAIL}")
            
            # Intentar login
            page.fill("input[type='email']", GRAFICA_EMAIL)
            page.fill("input[type='password']", GRAFICA_PASSWORD)
            page.click("button[type='submit']")
            page.wait_for_load_state("networkidle")
            
            page.screenshot(path="browserbase_after_login.png")
            print("📸 Screenshot post-login: browserbase_after_login.png")
        else:
            print("✅ No requiere login o ya está logueado")
        
        # Cerrar
        browser.close()
    
    print("\n🎉 Prueba completada!")
    print(f"   Ver grabación en: https://browserbase.com/sessions/{session.id}")

if __name__ == "__main__":
    test_browserbase()
