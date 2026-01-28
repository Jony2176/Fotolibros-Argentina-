"""
Base de datos unificada con SQLite
Reemplaza PostgreSQL + Redis por SQLite simple
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Dict, List
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Ruta de la base de datos
DB_PATH = Path("/var/fotolibros/fotolibros.db")


def init_database():
    """Inicializar base de datos con todas las tablas"""
    
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabla de pedidos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id TEXT UNIQUE NOT NULL,
            
            -- Cliente
            cliente_nombre TEXT NOT NULL,
            cliente_email TEXT NOT NULL,
            cliente_telefono TEXT,
            
            -- Libro
            codigo_producto TEXT NOT NULL,
            tamano TEXT,
            tapa TEXT,
            estilo TEXT,
            ocasion TEXT,
            titulo_personalizado TEXT,
            
            -- Fotos
            directorio_fotos TEXT,
            cantidad_fotos INTEGER,
            
            -- Configuración
            modo_confirmacion BOOLEAN DEFAULT 1,
            
            -- Estado
            estado TEXT DEFAULT 'pendiente',
            
            -- AGNO
            agno_config TEXT,  -- JSON
            
            -- Clawdbot
            clawdbot_session_key TEXT,
            
            -- Metadatos
            fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_pago TIMESTAMP,
            fecha_completado TIMESTAMP,
            
            -- Errores
            intentos INTEGER DEFAULT 0,
            ultimo_error TEXT,
            
            -- Extra
            notas_cliente TEXT,
            notas_internas TEXT
        )
    """)
    
    # Tabla de cola (reemplaza Redis)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cola (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id TEXT NOT NULL,
            pedido_data TEXT NOT NULL,  -- JSON
            estado TEXT DEFAULT 'pendiente',  -- pendiente, procesando, completado, error
            prioridad INTEGER DEFAULT 0,
            fecha_encolado TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_inicio_proceso TIMESTAMP,
            fecha_fin_proceso TIMESTAMP,
            error TEXT,
            
            FOREIGN KEY (pedido_id) REFERENCES pedidos(pedido_id)
        )
    """)
    
    # Índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cola_estado ON cola(estado)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cola_prioridad ON cola(prioridad DESC, fecha_encolado ASC)")
    
    conn.commit()
    conn.close()
    
    logger.info(f"✅ Base de datos inicializada: {DB_PATH}")


@contextmanager
def get_db():
    """Context manager para conexión a la DB"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceso por nombre de columna
    try:
        yield conn
    finally:
        conn.close()


# ==========================================
# OPERACIONES DE PEDIDOS
# ==========================================

def crear_pedido(pedido_data: Dict) -> str:
    """Crear un nuevo pedido"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO pedidos (
                pedido_id, cliente_nombre, cliente_email, cliente_telefono,
                codigo_producto, tamano, tapa, estilo, ocasion,
                titulo_personalizado, directorio_fotos, cantidad_fotos,
                modo_confirmacion, notas_cliente
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pedido_data['pedido_id'],
            pedido_data['cliente_nombre'],
            pedido_data['cliente_email'],
            pedido_data.get('cliente_telefono'),
            pedido_data['codigo_producto'],
            pedido_data.get('tamano'),
            pedido_data.get('tapa'),
            pedido_data.get('estilo'),
            pedido_data.get('ocasion'),
            pedido_data.get('titulo_personalizado'),
            pedido_data.get('directorio_fotos'),
            pedido_data.get('cantidad_fotos'),
            pedido_data.get('modo_confirmacion', True),
            pedido_data.get('notas_cliente')
        ))
        conn.commit()
        return pedido_data['pedido_id']


def obtener_pedido(pedido_id: str) -> Optional[Dict]:
    """Obtener un pedido por ID"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE pedido_id = ?", (pedido_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def actualizar_estado_pedido(pedido_id: str, estado: str, notas: str = None):
    """Actualizar estado de un pedido"""
    with get_db() as conn:
        cursor = conn.cursor()
        if notas:
            cursor.execute("""
                UPDATE pedidos 
                SET estado = ?, notas_internas = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE pedido_id = ?
            """, (estado, notas, pedido_id))
        else:
            cursor.execute("""
                UPDATE pedidos 
                SET estado = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE pedido_id = ?
            """, (estado, pedido_id))
        conn.commit()


def guardar_agno_config(pedido_id: str, config: Dict):
    """Guardar configuración de AGNO en el pedido"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE pedidos 
            SET agno_config = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE pedido_id = ?
        """, (json.dumps(config), pedido_id))
        conn.commit()


# ==========================================
# OPERACIONES DE COLA (reemplaza Redis)
# ==========================================

def encolar_pedido(pedido_data: Dict, prioridad: int = 0) -> int:
    """Agregar pedido a la cola"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO cola (pedido_id, pedido_data, prioridad)
            VALUES (?, ?, ?)
        """, (
            pedido_data['pedido_id'],
            json.dumps(pedido_data),
            prioridad
        ))
        conn.commit()
        
        # Obtener posición en cola
        cursor.execute("""
            SELECT COUNT(*) FROM cola 
            WHERE estado = 'pendiente' AND id <= ?
        """, (cursor.lastrowid,))
        posicion = cursor.fetchone()[0]
        
        logger.info(f"📥 Pedido {pedido_data['pedido_id']} encolado en posición {posicion}")
        return posicion


def obtener_siguiente_pedido() -> Optional[Dict]:
    """Obtener siguiente pedido de la cola (por prioridad)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Obtener pedido pendiente con mayor prioridad
        cursor.execute("""
            SELECT id, pedido_id, pedido_data FROM cola
            WHERE estado = 'pendiente'
            ORDER BY prioridad DESC, fecha_encolado ASC
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if not row:
            return None
        
        cola_id, pedido_id, pedido_data_json = row
        
        # Marcar como procesando
        cursor.execute("""
            UPDATE cola 
            SET estado = 'procesando', fecha_inicio_proceso = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (cola_id,))
        conn.commit()
        
        pedido_data = json.loads(pedido_data_json)
        pedido_data['_cola_id'] = cola_id
        
        logger.info(f"🎨 Procesando pedido {pedido_id}")
        return pedido_data


def marcar_completado(pedido_id: str):
    """Marcar pedido como completado"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cola 
            SET estado = 'completado', fecha_fin_proceso = CURRENT_TIMESTAMP
            WHERE pedido_id = ? AND estado = 'procesando'
        """, (pedido_id,))
        conn.commit()
        logger.info(f"✅ Pedido {pedido_id} completado")


def marcar_error(pedido_id: str, error: str):
    """Marcar pedido con error"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE cola 
            SET estado = 'error', error = ?, fecha_fin_proceso = CURRENT_TIMESTAMP
            WHERE pedido_id = ? AND estado = 'procesando'
        """, (error, pedido_id))
        conn.commit()
        logger.error(f"❌ Pedido {pedido_id} falló: {error}")


def obtener_posicion_cola(pedido_id: str) -> int:
    """
    Obtener posición en cola
    Returns: 0 si procesando, N si en cola, -1 si no está
    """
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar si está procesando
        cursor.execute("""
            SELECT estado FROM cola 
            WHERE pedido_id = ? 
            ORDER BY fecha_encolado DESC 
            LIMIT 1
        """, (pedido_id,))
        row = cursor.fetchone()
        
        if not row:
            return -1
        
        estado = row[0]
        if estado == 'procesando':
            return 0
        elif estado == 'pendiente':
            # Contar cuántos hay antes
            cursor.execute("""
                SELECT COUNT(*) FROM cola
                WHERE estado = 'pendiente' AND pedido_id = ?
            """, (pedido_id,))
            # Esto retorna 1 si está en cola, usamos query más compleja
            cursor.execute("""
                SELECT COUNT(*) + 1 FROM cola c1
                WHERE c1.estado = 'pendiente'
                AND (c1.prioridad > (SELECT prioridad FROM cola WHERE pedido_id = ?)
                     OR (c1.prioridad = (SELECT prioridad FROM cola WHERE pedido_id = ?)
                         AND c1.fecha_encolado < (SELECT fecha_encolado FROM cola WHERE pedido_id = ?)))
            """, (pedido_id, pedido_id, pedido_id))
            posicion = cursor.fetchone()[0]
            return posicion
        else:
            return -1  # completado o error


def get_queue_stats() -> Dict:
    """Obtener estadísticas de la cola"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM cola WHERE estado = 'pendiente'")
        en_cola = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cola WHERE estado = 'procesando'")
        procesando = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cola WHERE estado = 'completado'")
        completados = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM cola WHERE estado = 'error'")
        errores = cursor.fetchone()[0]
        
        # Pedido actual procesando
        cursor.execute("""
            SELECT pedido_id, fecha_inicio_proceso FROM cola
            WHERE estado = 'procesando'
            LIMIT 1
        """)
        procesando_row = cursor.fetchone()
        procesando_data = None
        if procesando_row:
            procesando_data = {
                'pedido_id': procesando_row[0],
                'inicio': procesando_row[1]
            }
        
        return {
            "en_cola": en_cola,
            "procesando": procesando,
            "completados": completados,
            "errores": errores,
            "procesando_data": procesando_data
        }


if __name__ == "__main__":
    # Test de inicialización
    init_database()
    print("✅ Base de datos inicializada correctamente")
    print(f"   Ubicación: {DB_PATH}")
    print(f"   Stats: {get_queue_stats()}")
