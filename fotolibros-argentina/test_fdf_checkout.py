import asyncio
import os
import sys

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orquestador import OrquestadorFotolibros, PedidoInfo

async def test_full_checkout():
    print("=" * 60)
    print("TEST: Verificación de Proceso Completo hasta Pago FDF")
    print("=" * 60)
    
    # IMPORTANTE: Asegúrate de que las credenciales en .env sean correctas
    
    # Crear un pedido de prueba real
    pedido = PedidoInfo(
        pedido_id="VERIFY-CHECKOUT-" + os.urandom(4).hex().upper(),
        producto_codigo="CU-21x21-DURA",
        estilo_diseno="clasico",
        paginas_total=22,
        cliente_nombre="Jonatan Prueba",
        cliente_email="revelacionesocultas72@gmail.com",
        titulo_tapa="PRUEBA CHECKOUT AGENTE",
        texto_lomo="TEST FDF",
        fotos_paths=["test_photo.jpg"],
        comentarios_cliente="Usar estilo moderno y priorizar fotos de paisaje"
    )

    # Puedes agregar una foto real aquí si la tienes en el sistema
    # pedido.fotos_paths = ["ruta/a/foto.jpg"]

    orquestador = OrquestadorFotolibros()
    
    print(f"\n🚀 Iniciando automatización para el pedido: {pedido.pedido_id}")
    resultado = await orquestador.procesar_pedido(pedido)
    
    print("\n" + "=" * 60)
    print("RESULTADO DE LA VERIFICACIÓN:")
    print(f"  ÉXITO: {resultado.get('exito')}")
    print(f"  PROYECTO ID: {resultado.get('proyecto_id')}")
    print(f"  ESTADO FINAL: {resultado.get('estado')}")
    print(f"  BROWSERBASE SESSION: {resultado.get('browserbase_session')}")
    print(f"  REPLAY URL: {resultado.get('replay_url')}")
    
    if not resultado.get("exito"):
        print(f"  ERROR: {resultado.get('error')}")
    
    print("\nLogs del proceso:")
    for log in resultado.get("logs", []):
        print(f"  {log}")
    print("=" * 60)
    
    if resultado.get("replay_url"):
        print(f"\n👉 PUEDES VER EL VIDEO DEL PROCESO AQUÍ: {resultado.get('replay_url')}")
    else:
        print("\nℹ️ MODO LOCAL: El proceso ocurrió en tu navegador local. No hay Replay URL.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_full_checkout())
