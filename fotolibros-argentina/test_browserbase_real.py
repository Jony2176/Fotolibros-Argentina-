import asyncio
import os
import sys
import os
import asyncio

# Asegurar que el directorio raíz está en el path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from agents.orquestador import OrquestadorFotolibros, PedidoInfo
from services.browserbase_service import BrowserbaseService

# Ruta absoluta a la foto de prueba
FOTO_PATH = os.path.abspath("uploads/fotos/test_photo_1_1768764473172.png")

async def test_real():
    print("=" * 60)
    print("🚀 INICIANDO PRUEBA REAL DE AUTOMATIZACIÓN (BROWSERBASE)")
    print("=" * 60)
    
    # Verificar que la foto existe
    if not os.path.exists(FOTO_PATH):
        print(f"⚠️ Foto de prueba no encontrada en: {FOTO_PATH}")
        print("Usando imagen dummy...")
        # (Opcional: crear dummy si falla, pero asumamos que existe por el find anterior)
    
    print(f"📸 Usando foto: {FOTO_PATH}")
    
    # Datos de prueba
    pedido = PedidoInfo(
        pedido_id="TEST-AUTO-001",
        producto_codigo="CU-21x21-DURA", # Cuadrado 21x21 Tapa Dura (común)
        estilo_diseno="minimalista",     # Para probar layout simple
        paginas_total=22,
        cliente_nombre="Bot Test",
        cliente_email="bot@test.com",
        titulo_tapa="Prueba Automatizada",
        texto_lomo="2026",
        fotos_paths=[FOTO_PATH]
    )
    
    # Instanciar orquestador
    orquestador = OrquestadorFotolibros()
    
    # Callback para ver progreso en tiempo real
    async def mostrar_progreso(msg, p):
        barra = "▓" * (p // 2) + "░" * ((100 - p) // 2)
        print(f"\r[{barra}] {p}% - {msg}", end="")
        if p == 100: print() # Nueva línea al final

    print("\nEjecutando orquestador...\n")
    
    # Ejecutar
    resultado = await orquestador.procesar_pedido(pedido, on_progress=mostrar_progreso)
    
    print("\n" + "=" * 60)
    print("🏁 RESULTADO FINAL")
    print("=" * 60)
    
    if resultado["exito"]:
        print(f"✅ ÉXITO TOTAL")
        print(f"🆔 Proyecto ID: {resultado.get('proyecto_id')}")
        print(f"🔗 Replay URL: {resultado.get('replay_url')}")
        print(f"💻 Session ID: {resultado.get('browserbase_session')}")
    else:
        print(f"❌ FALLÓ")
        print(f"Error: {resultado.get('error')}")
        print(f"Logs recientes: {resultado.get('logs')[-3:]}")

if __name__ == "__main__":
    asyncio.run(test_real())
