"""
Test Stagehand Drag & Drop
==========================
Prueba el drag & drop usando Stagehand v3 en modo LOCAL.

Ejecutar:
    python test_stagehand_drag.py
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_stagehand_basic():
    """Test basico de Stagehand en modo LOCAL"""
    
    print("=" * 60)
    print("TEST: Stagehand v3 - Modo LOCAL")
    print("=" * 60)
    
    # Verificar API key
    api_key = os.getenv("MODEL_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("\nERROR: No hay API key configurada")
        print("Configura MODEL_API_KEY o GEMINI_API_KEY en .env")
        return False
    
    print(f"\nAPI Key: {api_key[:20]}...")
    
    # Importar wrapper
    from services.fdf_stagehand.stagehand_wrapper import (
        FDFStagehandWrapper, 
        STAGEHAND_AVAILABLE,
        stagehand_session
    )
    
    if not STAGEHAND_AVAILABLE:
        print("\nERROR: Stagehand no esta instalado")
        print("Instalar con: pip install stagehand")
        return False
    
    print("\n[1] Creando wrapper (modo LOCAL)...")
    
    try:
        async with stagehand_session(
            model_name="google/gemini-2.0-flash",
            model_api_key=api_key,
            headless=False,  # Ver el browser
            use_browserbase=False  # Modo LOCAL
        ) as stagehand:
            
            print("[2] Sesion iniciada OK")
            
            # Test navegacion
            print("\n[3] Navegando a example.com...")
            result = await stagehand.navigate("https://example.com")
            print(f"    Resultado: {result}")
            
            if not result.get("success"):
                print(f"    ERROR: {result.get('error')}")
                return False
            
            await asyncio.sleep(2)
            
            # Test observe
            print("\n[4] Observando la pagina...")
            result = await stagehand.observe("find all links on the page")
            print(f"    Encontrados: {result.get('count', 0)} elementos")
            
            # Test act
            print("\n[5] Ejecutando accion...")
            result = await stagehand.act("click the 'More information' link")
            print(f"    Resultado: {result}")
            
            await asyncio.sleep(2)
            
            print("\n[6] Cerrando sesion...")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETADO EXITOSAMENTE")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_stagehand_drag_simulation():
    """Test de drag & drop en una pagina de prueba"""
    
    print("\n" + "=" * 60)
    print("TEST: Stagehand Drag & Drop")
    print("=" * 60)
    
    api_key = os.getenv("MODEL_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: No hay API key")
        return False
    
    from services.fdf_stagehand.stagehand_wrapper import stagehand_session
    
    try:
        async with stagehand_session(
            model_name="google/gemini-2.0-flash",
            model_api_key=api_key,
            headless=False,
            use_browserbase=False
        ) as stagehand:
            
            # Ir a una pagina con drag & drop demo
            print("\n[1] Navegando a demo de drag & drop...")
            await stagehand.navigate("https://the-internet.herokuapp.com/drag_and_drop")
            await asyncio.sleep(2)
            
            # Intentar drag & drop
            print("\n[2] Ejecutando drag & drop con lenguaje natural...")
            result = await stagehand.act("drag box A to box B")
            print(f"    Resultado: {result}")
            
            await asyncio.sleep(3)
            
            # Verificar
            print("\n[3] Extrayendo estado...")
            extract_result = await stagehand.extract(
                instruction="extract the text of both boxes",
                schema={
                    "type": "object",
                    "properties": {
                        "box1": {"type": "string"},
                        "box2": {"type": "string"}
                    }
                }
            )
            print(f"    Estado: {extract_result}")
            
        print("\n" + "=" * 60)
        print("TEST DRAG & DROP COMPLETADO")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_stagehand_fdf_login():
    """Test de login a FDF usando Stagehand"""
    
    print("\n" + "=" * 60)
    print("TEST: Stagehand Login a FDF")
    print("=" * 60)
    
    api_key = os.getenv("MODEL_API_KEY") or os.getenv("GEMINI_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("ERROR: Faltan credenciales en .env")
        return False
    
    from services.fdf_stagehand.stagehand_wrapper import stagehand_session, FDFStagehandActions
    
    try:
        async with stagehand_session(
            model_name="google/gemini-2.0-flash",
            model_api_key=api_key,
            headless=False,
            use_browserbase=False
        ) as stagehand:
            
            actions = FDFStagehandActions(stagehand)
            
            # Navegar a FDF
            print("\n[1] Navegando a FDF...")
            await stagehand.navigate("https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com")
            await asyncio.sleep(3)
            
            # Login
            print("\n[2] Ejecutando login...")
            result = await actions.login(fdf_email, fdf_password)
            print(f"    Resultado: {result}")
            
            await asyncio.sleep(5)
            
            # Verificar login
            print("\n[3] Verificando login...")
            extract_result = await stagehand.extract(
                instruction="check if the user is logged in, look for logout button or user menu",
                schema={
                    "type": "object",
                    "properties": {
                        "logged_in": {"type": "boolean"},
                        "user_info": {"type": "string"}
                    }
                }
            )
            print(f"    Estado: {extract_result}")
            
        print("\n" + "=" * 60)
        print("TEST FDF LOGIN COMPLETADO")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Menu de tests"""
    import sys
    
    print("\n" + "=" * 70)
    print(" STAGEHAND v3 - Tests de Drag & Drop")
    print("=" * 70)
    
    if len(sys.argv) > 1:
        test = sys.argv[1]
    else:
        print("\nTests disponibles:")
        print("  1. basic     - Test basico (navigate, observe, act)")
        print("  2. drag      - Test drag & drop en demo")
        print("  3. fdf       - Test login a FDF")
        print("  4. all       - Todos los tests")
        print("\nUso: python test_stagehand_drag.py [basic|drag|fdf|all]")
        test = "basic"
    
    results = {}
    
    if test in ["basic", "all"]:
        results["basic"] = await test_stagehand_basic()
    
    if test in ["drag", "all"]:
        results["drag"] = await test_stagehand_drag_simulation()
    
    if test in ["fdf", "all"]:
        results["fdf"] = await test_stagehand_fdf_login()
    
    # Resumen
    print("\n" + "=" * 70)
    print(" RESUMEN")
    print("=" * 70)
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name:20} {status}")
    
    failed = sum(1 for v in results.values() if not v)
    return 1 if failed else 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
