"""
Crear Fotolibro en FDF - Script Directo
========================================
Toma un pedido procesado por AGNO Team y lo ejecuta en FDF

Uso:
    python crear_fotolibro_en_fdf.py <pedido_id>
"""

import asyncio
import sys
import os

# Agregar path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fotolibros-argentina"))

from agents.orquestador import procesar_pedido_desde_db
from dotenv import load_dotenv

load_dotenv()

async def main():
    if len(sys.argv) < 2:
        print("Uso: python crear_fotolibro_en_fdf.py <pedido_id>")
        print("\nEjemplo:")
        print("  python crear_fotolibro_en_fdf.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf")
        sys.exit(1)
    
    pedido_id = sys.argv[1]
    
    print("=" * 70)
    print("  CREANDO FOTOLIBRO EN FDF CON NAVEGADOR")
    print("=" * 70)
    print(f"\nPedido ID: {pedido_id}")
    print(f"Configuracion AGNO: fotolibros-argentina/data/agno_config_{pedido_id[:8]}.json")
    print("")
    
    # Verificar que existe la configuración AGNO
    agno_config = f"fotolibros-argentina/data/agno_config_{pedido_id[:8]}.json"
    if not os.path.exists(agno_config):
        print(f"[ERROR] No se encontro la configuracion AGNO: {agno_config}")
        print("\nPrimero ejecuta: python procesar_pedido_agno.py")
        sys.exit(1)
    
    print("[OK] Configuracion AGNO encontrada")
    print("")
    
    print("[1/1] Iniciando automatizacion en FDF...")
    print("\n" + "=" * 70)
    print("  IMPORTANTE: El navegador se abrira en unos segundos")
    print("  Veras el proceso automatico de creacion del fotolibro")
    print("=" * 70 + "\n")
    
    try:
        resultado = await procesar_pedido_desde_db(pedido_id)
        
        if resultado.get("exito"):
            print("\n" + "=" * 70)
            print("  OK FOTOLIBRO CREADO EXITOSAMENTE")
            print("=" * 70)
            print(f"\nProyecto ID: {resultado.get('proyecto_id')}")
            print(f"Session: {resultado.get('browserbase_session')}")
            if resultado.get('replay_url'):
                print(f"Replay URL: {resultado.get('replay_url')}")
        else:
            print("\n" + "=" * 70)
            print("  X ERROR EN AUTOMATIZACION")
            print("=" * 70)
            print(f"\nError: {resultado.get('error')}")
            print(f"Progreso: {resultado.get('progreso')}%")
            
    except Exception as e:
        print(f"\n[ERROR] Excepcion durante ejecucion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
