"""
Test FDF Toolkit - Prueba directa del agente de navegador
=========================================================
Este script prueba el fdf_toolkit directamente usando Playwright + Gemini Vision.
Abre Chrome, navega a FDF, y ejecuta el flujo completo.

Uso:
    python test_fdf_toolkit.py
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_fdf_toolkit_directo():
    """Test directo del FDF Toolkit sin pasar por el orquestador"""
    
    print("=" * 60)
    print("TEST: FDF Toolkit (Playwright + Gemini Vision)")
    print("=" * 60)
    
    # Verificar credenciales
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    print(f"\n[1] Verificando credenciales...")
    print(f"    OPENROUTER_API_KEY: {'OK' if api_key else 'FALTA'}")
    print(f"    GRAFICA_EMAIL: {fdf_email if fdf_email else 'FALTA'}")
    print(f"    GRAFICA_PASSWORD: {'***' if fdf_password else 'FALTA'}")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("\nERROR: Faltan credenciales en .env")
        return
    
    # Importar toolkit
    print("\n[2] Importando FDF Toolkit...")
    try:
        from services.fdf_toolkit import FDFBrowserToolkit
        print("    OK - Toolkit importado")
    except ImportError as e:
        print(f"    ERROR: {e}")
        return
    
    # Crear instancia del toolkit
    print("\n[3] Creando instancia del toolkit...")
    toolkit = FDFBrowserToolkit(
        openrouter_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=False  # Visible para debug
    )
    print("    OK - Toolkit creado")
    
    try:
        # Test 1: Login
        print("\n" + "=" * 40)
        print("TEST 1: Login en FDF")
        print("=" * 40)
        
        print("\n[4] Ejecutando login...")
        print("    (Esto abrira Chrome y navegara a FDF)")
        
        login_result = await toolkit.login()
        print(f"    Resultado: {login_result}")
        
        if not login_result.get("success"):
            print(f"\n    ERROR en login: {login_result.get('error')}")
            print("    Abortando test...")
            return
        
        print("    OK - Login exitoso!")
        
        # Esperar para ver
        print("\n    Esperando 5 segundos...")
        await asyncio.sleep(5)
        
        # Test 2: Seleccionar producto
        print("\n" + "=" * 40)
        print("TEST 2: Seleccionar producto")
        print("=" * 40)
        
        print("\n[5] Seleccionando producto 'Cuadrado 21x21'...")
        
        product_result = await toolkit.select_product("CU-21x21-DURA")
        print(f"    Resultado: {product_result}")
        
        if not product_result.get("success"):
            print(f"    ADVERTENCIA: {product_result.get('error')}")
        else:
            print("    OK - Producto seleccionado!")
        
        await asyncio.sleep(3)
        
        # Test 3: Crear proyecto
        print("\n" + "=" * 40)
        print("TEST 3: Crear proyecto")
        print("=" * 40)
        
        print("\n[6] Creando proyecto 'Test Fotolibro'...")
        
        create_result = await toolkit.create_project("Test Fotolibro E2E")
        print(f"    Resultado: {create_result}")
        
        if not create_result.get("success"):
            print(f"    ADVERTENCIA: {create_result.get('error')}")
        else:
            print("    OK - Proyecto creado!")
        
        await asyncio.sleep(3)
        
        # Test 4: Checkout
        print("\n" + "=" * 40)
        print("TEST 4: Ir al checkout")
        print("=" * 40)
        
        print("\n[7] Intentando ir al checkout...")
        
        checkout_result = await toolkit.checkout()
        print(f"    Resultado: {checkout_result}")
        
        if checkout_result.get("success"):
            print("    OK - Checkout alcanzado!")
        else:
            print(f"    Resultado parcial: {checkout_result.get('message', 'N/A')}")
        
        # Mantener navegador abierto para inspeccionar
        print("\n" + "=" * 40)
        print("TEST COMPLETADO")
        print("=" * 40)
        
        print("\n[8] Manteniendo navegador abierto 30 segundos para inspeccion...")
        print("    (Observa la ventana de Chrome)")
        
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"\nERROR FATAL: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cerrar navegador
        print("\n[9] Cerrando navegador...")
        await toolkit.close()
        print("    OK - Navegador cerrado")


async def test_con_agente():
    """Test usando el agente AGNO completo"""
    
    print("=" * 60)
    print("TEST: Agente AGNO con FDF Toolkit")
    print("=" * 60)
    
    # Verificar credenciales
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("ERROR: Faltan credenciales")
        return
    
    print("\n[1] Importando dependencias...")
    try:
        from agno.agent import Agent
        from agno.models.openrouter import OpenRouter
        from services.fdf_toolkit import get_fdf_tools
        print("    OK")
    except ImportError as e:
        print(f"    ERROR: {e}")
        return
    
    print("\n[2] Creando agente navegador...")
    
    browser_agent = Agent(
        name="Navegador FDF Test",
        model=OpenRouter(id="google/gemini-2.0-flash-001"),
        tools=get_fdf_tools(api_key, fdf_email, fdf_password, headless=False),
        instructions=[
            "Eres un agente de automatizacion web.",
            "USA las herramientas proporcionadas para interactuar con el navegador.",
            "NO inventes acciones, usa SOLO las herramientas.",
        ]
    )
    
    print("    OK - Agente creado")
    
    print("\n[3] Ejecutando tarea de navegacion...")
    print("    (Esto puede tomar varios minutos)")
    
    prompt = """
    Realiza las siguientes tareas en orden:
    
    1. Usa 'fdf_login' para iniciar sesion en Fabrica de Fotolibros
    2. Usa 'fdf_select_product' para seleccionar el producto "CU-21x21-DURA"
    3. Usa 'fdf_create_project' para crear un proyecto llamado "Test Agente"
    4. Usa 'fdf_checkout' para ir al checkout
    
    Reporta el resultado de cada paso.
    """
    
    try:
        response = await browser_agent.arun(prompt)
        content = response.content if hasattr(response, 'content') else str(response)
        
        print("\n[4] Respuesta del agente:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test FDF Toolkit")
    parser.add_argument(
        "--mode",
        choices=["directo", "agente"],
        default="directo",
        help="Modo de test: 'directo' (toolkit solo) o 'agente' (con AGNO)"
    )
    
    args = parser.parse_args()
    
    print("\nEste test abrira Chrome en modo visible.")
    print("Asegurate de tener Chrome instalado.\n")
    
    if args.mode == "directo":
        asyncio.run(test_fdf_toolkit_directo())
    else:
        asyncio.run(test_con_agente())
