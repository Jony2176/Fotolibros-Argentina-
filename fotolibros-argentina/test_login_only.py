"""
Test rapido solo para verificar login en FDF
"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_login():
    print("=" * 50)
    print("TEST: Login en FDF con credenciales reales")
    print("=" * 50)
    
    email = os.getenv("GRAFICA_EMAIL")
    password = os.getenv("GRAFICA_PASSWORD")
    print(f"Email: {email}")
    print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
    
    from services.fdf_toolkit import FDFBrowserToolkit as FDFToolkit
    
    toolkit = FDFToolkit(
        openrouter_api_key=os.getenv("OPENROUTER_API_KEY"),
        fdf_email=email,
        fdf_password=password,
        headless=False
    )
    
    print("\n[1] Ejecutando login...")
    result = await toolkit.login()
    print(f"    Resultado: {result}")
    
    if result.get("success"):
        print("\n[2] Login exitoso! Esperando 5 segundos...")
        await asyncio.sleep(5)
        
        # Describir la pagina actual
        print("\n[3] Analizando pagina actual...")
        if toolkit.verifier and toolkit.page:
            page_info = await toolkit.verifier.describe_page(toolkit.page)
            print(f"    Tipo: {page_info.get('tipo_pagina')}")
            print(f"    Elementos: {page_info.get('elementos_principales', [])[:5]}")
            if page_info.get('alertas_errores'):
                print(f"    ERRORES: {page_info.get('alertas_errores')}")
    else:
        print(f"\n    ERROR: {result.get('error', 'Login fallido')}")
    
    print("\n[4] Cerrando navegador en 10 segundos...")
    await asyncio.sleep(10)
    await toolkit.close()
    print("    Cerrado.")

if __name__ == "__main__":
    asyncio.run(test_login())
