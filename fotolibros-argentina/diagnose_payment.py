
import asyncio
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🔍 Iniciando diagnóstico del sistema de pagos...")

# 1. Probar importaciones
try:
    print("⏳ Probando importaciones...")
    from services.payment_verifier import verificar_comprobante
    from services.email_service import enviar_email_pago_pendiente_admin
    print("✅ Importaciones exitosas.")
except Exception as e:
    print(f"❌ Error importando servicios: {e}")
    sys.exit(1)

# 2. Probar conexión a BD
try:
    print("⏳ Probando conexión a Base de Datos...")
    import aiosqlite
    DB_PATH = os.getenv("DB_PATH", "data/fotolibros.db")
    async def check_db():
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("SELECT 1")
            # Verificar columna nueva
            try:
                await db.execute("SELECT verificacion_json FROM pedidos LIMIT 1")
                print("✅ Columna 'verificacion_json' detectada.")
            except Exception as e:
                print(f"❌ Columna 'verificacion_json' NO existe: {e}")
    
    asyncio.run(check_db())
    print("✅ Base de datos OK.")
except Exception as e:
    print(f"❌ Error en BD: {e}")
    sys.exit(1)

# 3. Probar verificación IA (Gemini Direct)
try:
    print("⏳ Probando verificación IA con Gemini...")
    # Imagen dummy en base64 (pixel negro)
    dummy_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
    
    # Check google-genai
    try:
        from google import genai
        print("✅ Librería google-genai importada correctamente.")
    except ImportError:
        print("❌ ERROR: google-genai no está instalado.")
        sys.exit(1)

    GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_KEY:
        print("❌ ERROR: GOOGLE_API_KEY no está en .env")
    else:
        print(f"✅ GOOGLE_API_KEY encontrada ({GOOGLE_KEY[:5]}...)")

    async def test_ia():
        print("   Llamando a verificar_comprobante...")
        resultado = await verificar_comprobante(
            imagen_base64=dummy_b64,
            monto_esperado=100.0,
            pedido_id="test-diagnostic"
        )
        print(f"✅ Resultado IA: {resultado}")
        
    asyncio.run(test_ia())
    print("✅ Servicio IA responde correctamente.")
except Exception as e:
    print(f"❌ Error fatal en servicio IA: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Diagnóstico finalizado.")
