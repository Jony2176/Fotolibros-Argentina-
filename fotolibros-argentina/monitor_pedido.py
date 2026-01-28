"""
Monitor de Pedidos en Tiempo Real
Muestra el último pedido creado y su progreso
"""

import sqlite3
import time
import sys

DB_PATH = r"C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-argentina\data\fotolibros.db"

def get_latest_pedido():
    """Obtiene el último pedido creado"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute('''
        SELECT id, estado, progreso, mensaje, created_at 
        FROM pedidos 
        ORDER BY created_at DESC 
        LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()
    return row

def monitor():
    """Monitorea el último pedido"""
    print("="*70)
    print("  MONITOR DE PEDIDOS - AGNO TEAM")
    print("="*70)
    print("\nEsperando nuevo pedido...\n")
    
    last_pedido_id = None
    last_estado = None
    last_progreso = None
    
    while True:
        try:
            pedido = get_latest_pedido()
            
            if pedido:
                pedido_id, estado, progreso, mensaje, created_at = pedido
                
                # Si es un pedido nuevo, mostrarlo
                if pedido_id != last_pedido_id:
                    print(f"\n[NUEVO PEDIDO DETECTADO]")
                    print(f"  ID: {pedido_id[:8]}...")
                    print(f"  Creado: {created_at}")
                    print(f"  Estado: {estado}")
                    print("-"*70)
                    last_pedido_id = pedido_id
                    last_estado = None
                    last_progreso = None
                
                # Si cambió el estado o progreso
                if estado != last_estado or progreso != last_progreso:
                    print(f"[{time.strftime('%H:%M:%S')}] Estado: {estado:15} | Progreso: {progreso or 0:3}% | {mensaje or ''}")
                    last_estado = estado
                    last_progreso = progreso
                    
                    # Si terminó, salir
                    if estado in ['completado', 'error', 'fallido']:
                        print("\n" + "="*70)
                        print(f"  PEDIDO FINALIZADO: {estado.upper()}")
                        print("="*70)
                        break
            
            time.sleep(2)  # Revisar cada 2 segundos
            
        except KeyboardInterrupt:
            print("\n\nMonitoreo detenido por el usuario")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    monitor()
