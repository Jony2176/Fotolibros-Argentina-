"""
Browserbase Optimizado - Reutilización de Sesiones

La mayor optimización es NO crear una nueva sesión cada vez.
Browserbase cobra por sesión, y crear una tarda ~5-10 segundos.
"""

import os
os.environ["BROWSERBASE_API_KEY"] = "bb_live_uyHSRbZ7_5XT0kNvltt1xJfxfcQ"
os.environ["BROWSERBASE_PROJECT_ID"] = "35743d70-110d-427b-adad-1e8fb780bfd3"
os.environ["OPENROUTER_API_KEY"] = "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"

from browserbase import Browserbase
from playwright.sync_api import sync_playwright
import time

# Crear cliente de Browserbase
bb = Browserbase(api_key=os.environ["BROWSERBASE_API_KEY"])

# Crear UNA sesión que reutilizaremos
print("🚀 Creando sesión de Browserbase (solo una vez)...")
start = time.time()
session = bb.sessions.create(project_id=os.environ["BROWSERBASE_PROJECT_ID"])
print(f"✅ Sesión creada en {time.time() - start:.1f}s: {session.id}")

# Conectar Playwright
p = sync_playwright().start()
browser = p.chromium.connect_over_cdp(session.connect_url)
context = browser.contexts[0]
page = context.pages[0]

def navigate_fast(url: str, timeout: int = 15000):
    """Navegación rápida sin esperar todos los recursos"""
    start = time.time()
    page.goto(url, wait_until="domcontentloaded", timeout=timeout)  # No esperar networkidle
    print(f"   Navegado a {url} en {time.time() - start:.1f}s")
    return page

def get_content():
    """Obtener contenido de la página"""
    return page.content()

def screenshot(path: str):
    """Capturar screenshot"""
    page.screenshot(path=path)
    print(f"   Screenshot: {path}")

def close():
    """Cerrar sesión"""
    browser.close()
    p.stop()
    print("🔴 Sesión cerrada")

# === PRUEBA DE VELOCIDAD ===
if __name__ == "__main__":
    print("\n📊 Prueba de velocidad con sesión reutilizada:\n")
    
    # Primera navegación (incluye conexión inicial)
    start = time.time()
    navigate_fast("https://quotes.toscrape.com")
    content = get_content()
    print(f"   ➡️ Primera página: {time.time() - start:.1f}s")
    
    # Segunda navegación (sesión ya caliente)
    start = time.time()
    navigate_fast("https://quotes.toscrape.com/page/2/")
    content = get_content()
    print(f"   ➡️ Segunda página: {time.time() - start:.1f}s")
    
    # Tercera navegación
    start = time.time()
    navigate_fast("https://example.com")
    print(f"   ➡️ Tercera página: {time.time() - start:.1f}s")
    
    print("\n✅ La sesión reutilizada es MUCHO más rápida después de la primera conexión")
    print(f"   Ver grabación: https://browserbase.com/sessions/{session.id}")
    
    close()
