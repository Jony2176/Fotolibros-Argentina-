"""
Test del nuevo FDF Stagehand Toolkit (modo LOCAL)
=================================================
Usa Playwright directo para acciones DOM (rápido y estable).
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_full_flow():
    """Test del flujo completo hasta el editor"""
    
    print("=" * 60)
    print("TEST: FDF Stagehand Toolkit (Playwright Local)")
    print("=" * 60)
    
    # Verificar credenciales
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    print(f"\nCredenciales:")
    print(f"  API Key: {'OK' if api_key else 'FALTA'}")
    print(f"  Email: {fdf_email}")
    print(f"  Password: {'*' * len(fdf_password) if fdf_password else 'FALTA'}")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("\nERROR: Faltan credenciales en .env")
        return
    
    # Importar toolkit
    print("\n[1] Importando FDF Stagehand Toolkit...")
    from services.fdf_stagehand import FDFStagehandToolkit
    
    # Crear instancia
    print("[2] Creando toolkit...")
    toolkit = FDFStagehandToolkit(
        model_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=False
    )
    
    try:
        # Ejecutar flujo completo hasta editor
        print("\n[3] Ejecutando flujo hasta editor...")
        result = await toolkit.full_flow_to_editor(product_search="21x21")
        
        print("\n" + "=" * 60)
        print("RESULTADOS NAVEGACION:")
        print("=" * 60)
        
        for step in result.get("results", {}).get("steps", []):
            status = "OK" if step["result"].get("success") else "FAIL"
            print(f"  [{status}] {step['step']}")
        
        if not result.get("success"):
            print("\nNo se llego al editor, abortando...")
            await asyncio.sleep(10)
            return
        
        # Ahora explorar el editor
        print("\n" + "=" * 60)
        print("EXPLORANDO EDITOR:")
        print("=" * 60)
        
        await asyncio.sleep(3)
        
        # Ver info de la pagina
        print("\n[4] Obteniendo info de pagina...")
        info = await toolkit.get_page_info()
        print(f"    URL: {info.get('url')}")
        print(f"    Tipo: {info.get('page_type')}")
        
        # Buscar slots del canvas
        print("\n[5] Buscando slots en el canvas...")
        slots = await toolkit.get_canvas_slots()
        print(f"    Slots encontrados: {slots.get('count', 0)}")
        if slots.get("slots"):
            for slot in slots["slots"][:3]:
                print(f"      - {slot.get('id')}: ({slot.get('x'):.0f}, {slot.get('y'):.0f})")
        
        # Buscar fotos subidas
        print("\n[6] Buscando fotos en el panel...")
        photos = await toolkit.get_uploaded_photos()
        print(f"    Fotos encontradas: {photos.get('count', 0)}")
        
        # Screenshot para debug
        print("\n[7] Tomando screenshot...")
        await toolkit.take_screenshot("editor_state.png")
        print("    Guardado: editor_state.png")
        
        # Mantener abierto para inspección
        print("\n[8] Navegador abierto por 30 segundos para inspeccion...")
        print("    Observa el editor y el archivo editor_state.png")
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n[9] Cerrando navegador...")
        await toolkit.close()
        print("    Cerrado.")


async def test_step_by_step():
    """Test paso a paso con control manual"""
    
    print("=" * 60)
    print("TEST: Paso a paso con inspección")
    print("=" * 60)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    from services.fdf_stagehand import FDFStagehandToolkit
    
    toolkit = FDFStagehandToolkit(
        model_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=False
    )
    
    try:
        # Paso 1: Login
        print("\n--- PASO 1: Login ---")
        result = await toolkit.login()
        print(f"Resultado: {result}")
        input("Presiona Enter para continuar...")
        
        # Paso 2: Info de página
        print("\n--- PASO 2: Verificar página ---")
        info = await toolkit.get_page_info()
        print(f"Página actual: {info}")
        input("Presiona Enter para continuar...")
        
        # Paso 3: Navegar a Fotolibros
        print("\n--- PASO 3: Navegar a Fotolibros ---")
        result = await toolkit.navigate_to_fotolibros()
        print(f"Resultado: {result}")
        input("Presiona Enter para continuar...")
        
        # Paso 4: Seleccionar producto
        print("\n--- PASO 4: Seleccionar producto 21x21 ---")
        result = await toolkit.select_product_by_text("21x21")
        print(f"Resultado: {result}")
        input("Presiona Enter para continuar...")
        
        # Paso 5: Crear proyecto
        print("\n--- PASO 5: Crear proyecto ---")
        result = await toolkit.click_create_project()
        print(f"Resultado: {result}")
        input("Presiona Enter para cerrar...")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await toolkit.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        asyncio.run(test_step_by_step())
    else:
        asyncio.run(test_full_flow())
