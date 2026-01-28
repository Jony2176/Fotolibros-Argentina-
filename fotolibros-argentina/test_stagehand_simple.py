"""
Test Simple de Stagehand V3 - Prueba directa del navegador
==========================================================
Este script prueba Stagehand directamente sin pasar por la API.
Abre Chrome, navega a FDF, y ejecuta acciones basicas.
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_stagehand_directo():
    """Test directo de Stagehand V3 sin API"""
    
    print("=" * 60)
    print("TEST DIRECTO: Stagehand V3 + Gemini Vision")
    print("=" * 60)
    
    # Verificar API key
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    if not api_key:
        print("ERROR: Falta OPENROUTER_API_KEY o GOOGLE_GENERATIVE_AI_API_KEY")
        return
    
    print(f"\n[1] API Key encontrada: {api_key[:20]}...")
    
    # Importar Stagehand
    try:
        from stagehand import AsyncStagehand
        print("[2] Stagehand importado correctamente")
    except ImportError as e:
        print(f"ERROR: No se pudo importar Stagehand: {e}")
        return
    
    # Probar conexion basica
    print("\n[3] Iniciando Stagehand en modo LOCAL...")
    print("    (Esto abrira Chrome visible)")
    
    try:
        async with AsyncStagehand(
            server="local",
            model_api_key=api_key,
        ) as client:
            
            print("[4] Cliente Stagehand creado")
            
            # Iniciar sesion
            print("\n[5] Iniciando sesion con Gemini 2.5 Flash Lite...")
            session = await client.sessions.start(
                model_name="google/gemini-2.5-flash-lite-preview-02-05"
            )
            
            print(f"[6] Sesion iniciada: {session.id}")
            
            # Navegar a Google primero como test simple
            print("\n[7] Navegando a Google.com (test simple)...")
            await session.navigate(url="https://www.google.com")
            
            print("[8] Pagina cargada")
            
            # Extraer titulo
            print("\n[9] Extrayendo titulo de la pagina...")
            try:
                result = await session.extract(
                    instruction="What is the main heading or title of this page?",
                    schema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"}
                        }
                    }
                )
                print(f"[10] Titulo extraido: {result}")
            except Exception as e:
                print(f"[10] Error extrayendo: {e}")
            
            # Ahora probar FDF
            print("\n" + "=" * 40)
            print("Ahora probando Fabrica de Fotolibros...")
            print("=" * 40)
            
            fdf_url = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
            print(f"\n[11] Navegando a FDF: {fdf_url[:50]}...")
            
            await session.navigate(url=fdf_url)
            await asyncio.sleep(3)
            
            print("[12] Pagina FDF cargada")
            
            # Observar elementos disponibles
            print("\n[13] Observando elementos en la pagina...")
            try:
                observe_result = await session.observe(
                    instruction="Find the login form elements: email input, password input, and login button"
                )
                print(f"[14] Elementos encontrados: {observe_result}")
            except Exception as e:
                print(f"[14] Error observando: {e}")
            
            # Intentar llenar login
            fdf_email = os.getenv("GRAFICA_EMAIL", "demo@test.com")
            fdf_password = os.getenv("GRAFICA_PASSWORD", "demo123")
            
            print(f"\n[15] Intentando login con: {fdf_email}")
            
            try:
                await session.act(
                    input=f"Fill the email input field with: {fdf_email}"
                )
                print("[16] Email llenado")
            except Exception as e:
                print(f"[16] Error llenando email: {e}")
            
            try:
                await session.act(
                    input=f"Fill the password input field with: {fdf_password}"
                )
                print("[17] Password llenado")
            except Exception as e:
                print(f"[17] Error llenando password: {e}")
            
            try:
                await session.act(
                    input="Click the login button (might say 'INGRESAR' or 'Login')"
                )
                print("[18] Boton login clickeado")
            except Exception as e:
                print(f"[18] Error clickeando login: {e}")
            
            # Esperar y ver resultado
            await asyncio.sleep(5)
            
            print("\n[19] Esperando 10 segundos para ver el resultado...")
            print("    (Observa la ventana de Chrome)")
            await asyncio.sleep(10)
            
            # Cerrar sesion
            print("\n[20] Cerrando sesion...")
            await session.end()
            
            print("\n" + "=" * 60)
            print("TEST COMPLETADO")
            print("=" * 60)
            
    except Exception as e:
        print(f"\nERROR FATAL: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\nEste test abrira Chrome en modo visible.")
    print("Asegurate de tener Chrome instalado.\n")
    
    asyncio.run(test_stagehand_directo())
