"""
Demo Simple - Crear Fotolibro en FDF con Playwright
====================================================
Versión simplificada que abre el navegador y muestra el proceso

Uso:
    python demo_fdf_simple.py a309ddfc
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from playwright.async_api import async_playwright

# Configuración
FDF_URL = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
FDF_EMAIL = "revelacionesocultas72@gmail.com"
FDF_PASSWORD = "Jony.2176"


async def demo_crear_fotolibro(pedido_id: str):
    """
    Demo que muestra cómo se crearía el fotolibro en FDF
    """
    
    # Cargar configuración AGNO
    config_file = f"fotolibros-argentina/data/agno_config_{pedido_id[:8]}.json"
    
    if not os.path.exists(config_file):
        print(f"[ERROR] No se encontró: {config_file}")
        print("Primero ejecuta: python procesar_pedido_agno.py")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("=" * 70)
    print("  DEMO: CREANDO FOTOLIBRO EN FDF")
    print("=" * 70)
    print(f"\nTítulo: \"{config['story']['cover']['title']}\"")
    print(f"Fotos: {len(config['photos'])}")
    print(f"Capítulos: {len(config['story']['chapters'])}")
    print("")
    
    async with async_playwright() as p:
        # Abrir navegador (visible)
        print("[1/8] Abriendo navegador Chrome...")
        browser = await p.chromium.launch(
            headless=False,  # Visible
            slow_mo=1000     # Slow motion para ver las acciones
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = await context.new_page()
        
        try:
            # Paso 1: Ir a FDF
            print(f"[2/8] Navegando a FDF...")
            await page.goto(FDF_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(3000)
            
            # Paso 2: Login
            print(f"[3/8] Iniciando sesión...")
            print(f"      Email: {FDF_EMAIL}")
            
            # Intentar encontrar el formulario de login
            try:
                # Esperar el campo de email
                await page.wait_for_selector('input[type="email"], input[name="email"], #email', timeout=10000)
                
                # Llenar email
                email_input = await page.query_selector('input[type="email"], input[name="email"], #email')
                if email_input:
                    await email_input.fill(FDF_EMAIL)
                    print("      ✓ Email ingresado")
                
                # Llenar password
                password_input = await page.query_selector('input[type="password"], input[name="password"], #password')
                if password_input:
                    await password_input.fill(FDF_PASSWORD)
                    print("      ✓ Password ingresado")
                
                # Click en login
                login_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Entrar")')
                if login_button:
                    await login_button.click()
                    print("      ✓ Click en login")
                    await page.wait_for_timeout(5000)
                
            except Exception as e:
                print(f"      ⚠ No se encontró formulario de login: {e}")
                print("      Puede que ya estés logueado o la página cambió")
            
            # Paso 3: Mostrar página actual
            print(f"\n[4/8] Página actual: {page.url}")
            print(f"      Título: {await page.title()}")
            
            # Paso 4: Mostrar diseño que se creará
            print(f"\n[5/8] DISEÑO QUE SE CREARÁ:")
            print(f"\n   📕 TAPA:")
            print(f"      Título: \"{config['story']['cover']['title']}\"")
            print(f"      Subtítulo: \"{config['story']['cover']['subtitle']}\"")
            print(f"      Autor: {config['story']['cover']['author_line']}")
            
            print(f"\n   📄 DEDICATORIA (Página 1):")
            print(f"      {config['story']['dedication']['text'][:100]}...")
            
            for i, chapter in enumerate(config['story']['chapters'], 1):
                print(f"\n   📘 CAPÍTULO {i}: \"{chapter['title']}\"")
                print(f"      Tono: {chapter['emotional_tone']}")
                print(f"      Intro: \"{chapter['chapter_intro']}\"")
                print(f"      Fotos: {len(chapter['photo_indices'])}")
            
            print(f"\n   📕 CONTRATAPA:")
            print(f"      {config['story']['back_cover']['text'][:80]}...")
            
            # Paso 5: Explicar proceso
            print(f"\n[6/8] PROCESO DE AUTOMATIZACIÓN:")
            print(f"\n   El navegador haría estos pasos:")
            print(f"   1. ✓ Login en FDF (completado)")
            print(f"   2. → Crear nuevo proyecto (template: {config['design']['template_choice']['primary']})")
            print(f"   3. → Subir {len(config['photos'])} fotos en orden cronológico")
            print(f"   4. → Configurar tapa con título emotivo")
            print(f"   5. → Agregar dedicatoria en página 1")
            print(f"   6. → Crear {len(config['story']['chapters'])} capítulos con intros")
            print(f"   7. → Agregar {len(config['story']['photo_captions'])} leyendas emotivas")
            print(f"   8. → Configurar contratapa con texto de cierre")
            print(f"   9. → Guardar proyecto")
            
            # Paso 6: Listar fotos
            print(f"\n[7/8] FOTOS EN ORDEN CRONOLÓGICO:")
            for i, foto in enumerate(config['chronology']['ordered_photos'], 1):
                caption = next(
                    (c['caption'] for c in config['story']['photo_captions'] if c['photo_index'] == i),
                    'Sin leyenda'
                )
                print(f"   {i}. {foto['filename']}")
                print(f"      Emoción: {foto.get('emotion', 'neutral')} | Importancia: {foto.get('importance', 5)}/10")
                print(f"      Leyenda: \"{caption[:60]}...\"")
            
            # Paso 7: Mantener navegador abierto
            print(f"\n[8/8] NAVEGADOR ABIERTO")
            print(f"\n{'=' * 70}")
            print(f"  El navegador quedará abierto para que explores FDF")
            print(f"  Presiona ENTER para cerrar...")
            print(f"{'=' * 70}\n")
            
            input()
            
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            
            print(f"\nPresiona ENTER para cerrar...")
            input()
        
        finally:
            await browser.close()
            print("\n[OK] Navegador cerrado")


async def main():
    if len(sys.argv) < 2:
        print("Uso: python demo_fdf_simple.py <pedido_id>")
        print("\nEjemplo:")
        print("  python demo_fdf_simple.py a309ddfc")
        sys.exit(1)
    
    pedido_id = sys.argv[1]
    await demo_crear_fotolibro(pedido_id)


if __name__ == "__main__":
    asyncio.run(main())
