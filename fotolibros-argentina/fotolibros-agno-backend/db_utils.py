"""
Database Utils - Lectura de pedidos desde SQLite
Helper para leer pedidos y fotos de la base de datos fotolibros.db
"""

import sqlite3
import json
from pathlib import Path
from typing import Optional, List, Dict


# Ruta a la base de datos (ajustar según ubicación)
DB_PATH = Path(__file__).parent.parent / "fotolibros-argentina" / "data" / "fotolibros.db"


def get_pedido(pedido_id: str) -> Optional[Dict]:
    """
    Obtiene un pedido por ID
    
    Args:
        pedido_id: ID del pedido
    
    Returns:
        dict con datos del pedido o None si no existe
    """
    if not DB_PATH.exists():
        print(f"⚠️  Base de datos no encontrada: {DB_PATH}")
        return None
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, producto_codigo, estilo_diseno, paginas_total,
                   cliente_json, titulo_tapa, titulo_contratapa, texto_lomo,
                   incluir_qr, qr_url, adornos_extras, estado, created_at
            FROM pedidos
            WHERE id = ?
        """, (pedido_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convertir a dict
        pedido = dict(row)
        
        # Parsear JSON fields
        if pedido.get('cliente_json'):
            try:
                pedido['cliente'] = json.loads(pedido['cliente_json'])
            except json.JSONDecodeError:
                pedido['cliente'] = {}
        
        if pedido.get('adornos_extras'):
            try:
                pedido['adornos'] = json.loads(pedido['adornos_extras'])
            except json.JSONDecodeError:
                pedido['adornos'] = {}
        
        return pedido
        
    finally:
        conn.close()


def get_photos_from_db(pedido_id: str) -> List[str]:
    """
    Obtiene las rutas de fotos de un pedido
    
    Args:
        pedido_id: ID del pedido
    
    Returns:
        Lista de rutas absolutas de fotos
    """
    if not DB_PATH.exists():
        print(f"⚠️  Base de datos no encontrada: {DB_PATH}")
        return []
    
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT filepath
            FROM fotos_pedido
            WHERE pedido_id = ?
            ORDER BY created_at ASC
        """, (pedido_id,))
        
        rows = cursor.fetchall()
        
        # Filtrar solo fotos que existen
        valid_photos = []
        for row in rows:
            filepath = row[0]
            if Path(filepath).exists():
                valid_photos.append(filepath)
            else:
                print(f"⚠️  Foto no encontrada: {filepath}")
        
        return valid_photos
        
    finally:
        conn.close()


def get_last_pedido_with_photos() -> Optional[Dict]:
    """
    Obtiene el último pedido que tenga fotos
    
    Returns:
        dict con 'pedido' y 'photos' o None
    """
    if not DB_PATH.exists():
        print(f"⚠️  Base de datos no encontrada: {DB_PATH}")
        return None
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    try:
        cursor = conn.cursor()
        
        # Buscar último pedido con fotos
        cursor.execute("""
            SELECT DISTINCT p.id
            FROM pedidos p
            INNER JOIN fotos_pedido fp ON p.id = fp.pedido_id
            ORDER BY p.created_at DESC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        pedido_id = row[0]
        
        # Obtener datos completos
        pedido = get_pedido(pedido_id)
        photos = get_photos_from_db(pedido_id)
        
        if not pedido or not photos:
            return None
        
        return {
            'pedido': pedido,
            'photos': photos
        }
        
    finally:
        conn.close()


def process_pedido_from_db(pedido_id: str, output_path: str = None) -> Optional[Dict]:
    """
    Procesa un pedido completo desde la BD usando AGNO Team
    
    Args:
        pedido_id: ID del pedido
        output_path: Ruta donde guardar config (opcional)
    
    Returns:
        dict con configuración del fotolibro o None
    """
    from team import process_fotolibro
    
    # Obtener pedido
    pedido = get_pedido(pedido_id)
    if not pedido:
        print(f"❌ Pedido {pedido_id} no encontrado")
        return None
    
    # Obtener fotos
    photos = get_photos_from_db(pedido_id)
    if not photos:
        print(f"❌ No se encontraron fotos para el pedido {pedido_id}")
        return None
    
    print(f"📦 Procesando pedido {pedido_id}")
    print(f"   Fotos: {len(photos)}")
    
    # Preparar contexto del cliente
    cliente = pedido.get('cliente', {})
    client_context = {
        "client_name": cliente.get('nombre', 'Cliente'),
        "hint": pedido.get('estilo_diseno'),  # Puede ser None
    }
    
    # Intentar extraer recipient del cliente_json
    if cliente.get('destinatario'):
        client_context['recipient_name'] = cliente['destinatario']
    
    # Output path por defecto
    if not output_path:
        output_path = f"data/fotolibro_{pedido_id}.json"
    
    # Procesar con AGNO Team
    config = process_fotolibro(
        photos,
        client_context,
        output_path
    )
    
    # Agregar ID del pedido al config
    if config and config.get('success') != False:
        config['metadata']['pedido_id'] = pedido_id
    
    return config


if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) > 1:
        pedido_id = sys.argv[1]
        print(f"Testeando lectura de pedido {pedido_id}...")
        
        pedido = get_pedido(pedido_id)
        if pedido:
            print(f"\nPedido encontrado:")
            print(f"  ID: {pedido['id']}")
            print(f"  Cliente: {pedido.get('cliente', {}).get('nombre', 'N/A')}")
            
            photos = get_photos_from_db(pedido_id)
            print(f"  Fotos: {len(photos)}")
        else:
            print("Pedido no encontrado")
    else:
        print("Testeando último pedido con fotos...")
        result = get_last_pedido_with_photos()
        
        if result:
            print(f"\nÚltimo pedido:")
            print(f"  ID: {result['pedido']['id']}")
            print(f"  Fotos: {len(result['photos'])}")
        else:
            print("No hay pedidos con fotos")
