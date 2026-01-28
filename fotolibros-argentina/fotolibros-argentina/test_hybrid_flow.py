"""
Test del Flujo Híbrido Completo con Orquestador
=================================================
Prueba el OrquestadorFotolibros con el enfoque híbrido.
"""

import os
import asyncio
from dotenv import load_dotenv
load_dotenv()


async def main():
    from agents.orquestador import OrquestadorFotolibros, PedidoInfo
    
    print("=" * 60)
    print("TEST: Orquestador con Flujo Híbrido")
    print("=" * 60)
    
    # Crear pedido de prueba
    pedido = PedidoInfo(
        pedido_id="TEST-HYBRID-001",
        producto_codigo="CU-21x21-DURA",  # Cuadrado 21x21 Tapa Dura
        estilo_diseno="clasico",
        paginas_total=22,
        cliente_nombre="Usuario Test",
        cliente_email="test@example.com",
        titulo_tapa="Recuerdos de Prueba",
        texto_lomo="2026",
        fotos_paths=[]  # Sin fotos por ahora
    )
    
    print(f"\nPedido: {pedido.pedido_id}")
    print(f"Producto: {pedido.producto_codigo}")
    print(f"Estilo: {pedido.estilo_diseno}")
    print(f"Fotos: {len(pedido.fotos_paths)}\n")
    
    # Crear orquestador
    orquestador = OrquestadorFotolibros()
    
    # Callback de progreso
    async def on_progress(msg, prog):
        print(f"[{prog:3d}%] {msg}")
    
    # Ejecutar flujo completo
    resultado = await orquestador.procesar_pedido(pedido, on_progress=on_progress)
    
    print("\n" + "=" * 60)
    print("RESULTADO:")
    print(f"  Éxito: {resultado.get('exito', False)}")
    print(f"  Proyecto ID: {resultado.get('proyecto_id')}")
    print(f"  Estado: {resultado.get('estado')}")
    print(f"  Replay URL: {resultado.get('replay_url')}")
    if resultado.get('error'):
        print(f"  Error: {resultado['error']}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
