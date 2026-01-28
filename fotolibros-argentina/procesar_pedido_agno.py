"""
Procesador de pedido con AGNO Team
Sin emojis para compatibilidad con Windows console
"""

import sys
import os
import asyncio
import json

# Setup paths
backend_path = r'C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-argentina'
os.chdir(backend_path)
sys.path.insert(0, backend_path)

import aiosqlite

async def procesar_pedido(pedido_id):
    """Procesa un pedido con AGNO Team"""
    
    DB_PATH = os.path.join(backend_path, 'data', 'fotolibros.db')
    
    print("="*70)
    print("  PROCESAMIENTO CON AGNO TEAM")
    print("="*70)
    print(f"\nPedido ID: {pedido_id[:8]}...")
    
    # Obtener pedido
    print("\n[1/6] Obteniendo datos del pedido...")
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute('SELECT * FROM pedidos WHERE id = ?', (pedido_id,))
        row = await cursor.fetchone()
        if not row:
            print(f"ERROR: Pedido {pedido_id} no encontrado")
            return
        pedido = dict(row)
    
    # Obtener fotos
    print("[2/6] Obteniendo fotos...")
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('SELECT filepath FROM fotos_pedido WHERE pedido_id = ?', (pedido_id,))
        rows = await cursor.fetchall()
        fotos_paths = [r[0] for r in rows]
    
    print(f"      Fotos encontradas: {len(fotos_paths)}")
    
    if not fotos_paths:
        print("ERROR: No hay fotos para este pedido")
        return
    
    # Parsear cliente
    cliente = json.loads(pedido.get('cliente_json', '{}'))
    print(f"      Cliente: {cliente.get('nombre', 'N/A')}")
    
    # Importar AGNO Team processor
    print("\n[3/6] Cargando AGNO Team...")
    try:
        from agents.orquestador_agno_team import AGNOTeamProcessor
        processor = AGNOTeamProcessor()
        print("      AGNO Team cargado correctamente")
    except Exception as e:
        print(f"      ERROR cargando AGNO Team: {e}")
        print("      Usando sistema legacy")
        return
    
    # Procesar con AGNO Team
    print("\n[4/6] Procesando con 5 agentes especializados...")
    print("-"*70)
    
    try:
        result = await processor.procesar_con_agno_team(
            fotos_paths=fotos_paths,
            cliente_nombre=cliente.get('nombre', 'Cliente'),
            motif_hint=pedido.get('estilo_diseno'),
            recipient=None
        )
        
        print("-"*70)
        
        if result['success']:
            print("\n[5/6] PROCESAMIENTO EXITOSO!")
            print(f"      Motivo detectado: {result['motif']['motif']}")
            print(f"      Confianza: {result['motif']['confidence']}%")
            print(f"      Titulo: \"{result['story']['cover']['title']}\"")
            print(f"      Template: {result['design']['template_choice']['primary']}")
            print(f"      Fotos ordenadas: {len(result['photos'])}")
            
            # Guardar config
            print("\n[6/6] Guardando configuracion...")
            config_path = os.path.join(backend_path, 'data', f'agno_config_{pedido_id[:8]}.json')
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"      Guardado en: {config_path}")
            
            print("\n" + "="*70)
            print("  EXITO - AGNO TEAM COMPLETO")
            print("="*70)
            
        else:
            print(f"\n[ERROR] Procesamiento fallo: {result.get('error')}")
            
    except Exception as e:
        print(f"\n[ERROR] Excepcion durante procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    pedido_id = "a309ddfc-ae43-40e7-ba66-80dc1a330cdf"
    
    if len(sys.argv) > 1:
        pedido_id = sys.argv[1]
    
    asyncio.run(procesar_pedido(pedido_id))
