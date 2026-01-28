"""
SQLite Toolkit - Fotolibros Argentina
=====================================
Gestión de base de datos SQLite para pedidos, clientes y estados.
"""
import os
import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from agno.tools import tool
from loguru import logger
from contextlib import contextmanager

# Ruta de la base de datos
DB_PATH = os.getenv("DB_PATH", "data/fotolibros.db")


class SQLiteToolkit:
    """
    Toolkit para gestión de base de datos SQLite.
    Maneja pedidos, clientes, fotos y estados.
    """
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_db_directory()
        self._init_database()
        logger.info(f"🗄️ SQLiteToolkit inicializado: {db_path}")
    
    def _ensure_db_directory(self):
        """Crea el directorio de la BD si no existe"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexiones"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()
    
    def _init_database(self):
        """Inicializa las tablas de la base de datos"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de pedidos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pedidos (
                    id TEXT PRIMARY KEY,
                    numero_pedido TEXT UNIQUE NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    fecha_actualizacion TIMESTAMP,
                    fecha_finalizacion TIMESTAMP,
                    
                    -- Producto
                    producto_id TEXT NOT NULL,
                    producto_nombre TEXT NOT NULL,
                    paquete_id TEXT,
                    paginas_totales INTEGER DEFAULT 22,
                    margen_aplicado TEXT DEFAULT 'estandar',
                    cantidad_fotos INTEGER DEFAULT 0,
                    
                    -- Estado
                    estado TEXT DEFAULT 'pendiente_pago',
                    
                    -- Precios
                    monto_producto REAL DEFAULT 0,
                    monto_paginas_extra REAL DEFAULT 0,
                    monto_envio REAL DEFAULT 0,
                    monto_total REAL DEFAULT 0,
                    
                    -- Notas
                    notas_admin TEXT
                )
            """)
            
            # Tabla de clientes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id TEXT UNIQUE NOT NULL,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    email TEXT NOT NULL,
                    telefono TEXT NOT NULL,
                    calle TEXT,
                    numero TEXT,
                    piso TEXT,
                    departamento TEXT,
                    codigo_postal TEXT,
                    ciudad TEXT,
                    provincia TEXT,
                    pais TEXT DEFAULT 'Argentina',
                    notas_entrega TEXT,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
                )
            """)
            
            # Tabla de envíos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS envios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id TEXT UNIQUE NOT NULL,
                    zona_id TEXT,
                    costo_envio REAL DEFAULT 0,
                    dias_estimados_min INTEGER,
                    dias_estimados_max INTEGER,
                    codigo_seguimiento TEXT,
                    empresa_envio TEXT,
                    fecha_despacho TIMESTAMP,
                    fecha_entrega_estimada TIMESTAMP,
                    fecha_entrega_real TIMESTAMP,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
                )
            """)
            
            # Tabla de pagos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id TEXT UNIQUE NOT NULL,
                    metodo TEXT DEFAULT 'transferencia',
                    monto_total REAL DEFAULT 0,
                    comprobante_path TEXT,
                    verificado INTEGER DEFAULT 0,
                    fecha_verificacion TIMESTAMP,
                    resultado_verificacion TEXT,
                    motivo_rechazo TEXT,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
                )
            """)
            
            # Tabla de producción (tracking con la gráfica)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS produccion (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id TEXT UNIQUE NOT NULL,
                    fecha_pedido_grafica TIMESTAMP,
                    numero_pedido_grafica TEXT,
                    fecha_produccion_estimada TIMESTAMP,
                    fecha_produccion_real TIMESTAMP,
                    fecha_envio_grafica TIMESTAMP,
                    fecha_recepcion_jonatan TIMESTAMP,
                    tracking_grafica TEXT,
                    notas_produccion TEXT,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
                )
            """)
            
            # Tabla de fotos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fotos (
                    id TEXT PRIMARY KEY,
                    pedido_id TEXT NOT NULL,
                    nombre_original TEXT,
                    ruta_almacenamiento TEXT,
                    tamaño_bytes INTEGER,
                    ancho_px INTEGER,
                    alto_px INTEGER,
                    orientacion TEXT,
                    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    orden INTEGER DEFAULT 0,
                    fecha_toma TIMESTAMP,
                    camara TEXT,
                    dpi INTEGER,
                    calidad_score REAL,
                    advertencias TEXT,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
                )
            """)
            
            # Tabla de historial de estados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS historial_estados (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pedido_id TEXT NOT NULL,
                    estado TEXT NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    nota TEXT,
                    actor TEXT DEFAULT 'sistema',
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
                )
            """)
            
            # Índices para búsquedas rápidas
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos(estado)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pedidos_fecha ON pedidos(fecha_creacion)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_email ON clientes(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_fotos_pedido ON fotos(pedido_id)")
    
    # ============================================
    # TOOLS PARA AGNO
    # ============================================
    
    @tool
    def crear_pedido(
        self,
        producto_id: str,
        producto_nombre: str,
        paginas_totales: int = 22,
        paquete_id: Optional[str] = None,
        margen: str = "estandar"
    ) -> str:
        """
        Crea un nuevo pedido en la base de datos.
        
        Args:
            producto_id: ID del producto (ej: "CU-21x21-DURA")
            producto_nombre: Nombre del producto
            paginas_totales: Cantidad de páginas
            paquete_id: ID del paquete si aplica
            margen: Tipo de margen ("penetracion", "estandar", "premium")
            
        Returns:
            JSON con datos del pedido creado
        """
        import uuid
        
        pedido_id = str(uuid.uuid4())
        
        # Generar número de pedido
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pedidos WHERE strftime('%Y', fecha_creacion) = strftime('%Y', 'now')")
            count = cursor.fetchone()[0] + 1
            numero_pedido = f"FA-{datetime.now().year}-{count:04d}"
            
            # Insertar pedido
            cursor.execute("""
                INSERT INTO pedidos (id, numero_pedido, producto_id, producto_nombre, 
                                    paquete_id, paginas_totales, margen_aplicado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (pedido_id, numero_pedido, producto_id, producto_nombre, 
                  paquete_id, paginas_totales, margen))
            
            # Registrar estado inicial
            cursor.execute("""
                INSERT INTO historial_estados (pedido_id, estado, nota, actor)
                VALUES (?, 'pendiente_pago', 'Pedido creado', 'sistema')
            """, (pedido_id,))
        
        return json.dumps({
            "success": True,
            "pedido_id": pedido_id,
            "numero_pedido": numero_pedido,
            "estado": "pendiente_pago"
        })
    
    @tool
    def obtener_pedido(self, pedido_id: str) -> str:
        """
        Obtiene todos los datos de un pedido.
        
        Args:
            pedido_id: ID del pedido
            
        Returns:
            JSON con datos completos del pedido
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Pedido principal
            cursor.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
            pedido = cursor.fetchone()
            
            if not pedido:
                return json.dumps({"error": "Pedido no encontrado"})
            
            pedido_dict = dict(pedido)
            
            # Cliente
            cursor.execute("SELECT * FROM clientes WHERE pedido_id = ?", (pedido_id,))
            cliente = cursor.fetchone()
            if cliente:
                pedido_dict["cliente"] = dict(cliente)
            
            # Envío
            cursor.execute("SELECT * FROM envios WHERE pedido_id = ?", (pedido_id,))
            envio = cursor.fetchone()
            if envio:
                pedido_dict["envio"] = dict(envio)
            
            # Pago
            cursor.execute("SELECT * FROM pagos WHERE pedido_id = ?", (pedido_id,))
            pago = cursor.fetchone()
            if pago:
                pedido_dict["pago"] = dict(pago)
            
            # Producción
            cursor.execute("SELECT * FROM produccion WHERE pedido_id = ?", (pedido_id,))
            produccion = cursor.fetchone()
            if produccion:
                pedido_dict["produccion"] = dict(produccion)
            
            # Fotos (solo resumen)
            cursor.execute("SELECT COUNT(*) FROM fotos WHERE pedido_id = ?", (pedido_id,))
            pedido_dict["cantidad_fotos"] = cursor.fetchone()[0]
            
            # Historial
            cursor.execute("""
                SELECT estado, fecha, nota, actor 
                FROM historial_estados 
                WHERE pedido_id = ? 
                ORDER BY fecha DESC
            """, (pedido_id,))
            pedido_dict["historial"] = [dict(row) for row in cursor.fetchall()]
        
        return json.dumps(pedido_dict, default=str)
    
    @tool
    def actualizar_estado_pedido(
        self,
        pedido_id: str,
        nuevo_estado: str,
        nota: Optional[str] = None,
        actor: str = "sistema"
    ) -> str:
        """
        Actualiza el estado de un pedido.
        
        Args:
            pedido_id: ID del pedido
            nuevo_estado: Nuevo estado (pendiente_pago, verificando_pago, pago_aprobado, 
                         en_produccion, producido, en_mi_domicilio, enviado_cliente, 
                         entregado, cancelado, rechazado)
            nota: Nota opcional
            actor: Quién hace el cambio (sistema, admin, cliente)
            
        Returns:
            JSON con resultado
        """
        estados_validos = [
            "pendiente_pago", "verificando_pago", "pago_aprobado",
            "en_produccion", "producido", "en_mi_domicilio",
            "enviado_cliente", "entregado", "cancelado", "rechazado"
        ]
        
        if nuevo_estado not in estados_validos:
            return json.dumps({"error": f"Estado inválido. Válidos: {estados_validos}"})
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Actualizar pedido
            cursor.execute("""
                UPDATE pedidos 
                SET estado = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (nuevo_estado, pedido_id))
            
            # Si es estado final, marcar fecha_finalizacion
            if nuevo_estado in ["entregado", "cancelado", "rechazado"]:
                cursor.execute("""
                    UPDATE pedidos SET fecha_finalizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (pedido_id,))
            
            # Registrar en historial
            cursor.execute("""
                INSERT INTO historial_estados (pedido_id, estado, nota, actor)
                VALUES (?, ?, ?, ?)
            """, (pedido_id, nuevo_estado, nota, actor))
        
        return json.dumps({
            "success": True,
            "pedido_id": pedido_id,
            "nuevo_estado": nuevo_estado
        })
    
    @tool
    def guardar_datos_cliente(
        self,
        pedido_id: str,
        nombre: str,
        apellido: str,
        email: str,
        telefono: str,
        calle: str,
        numero: str,
        ciudad: str,
        provincia: str,
        codigo_postal: str = "",
        piso: Optional[str] = None,
        departamento: Optional[str] = None,
        notas_entrega: Optional[str] = None
    ) -> str:
        """
        Guarda los datos del cliente para un pedido.
        
        Args:
            pedido_id: ID del pedido
            nombre: Nombre del cliente
            apellido: Apellido del cliente
            email: Email del cliente
            telefono: Teléfono del cliente
            calle: Calle de envío
            numero: Número de calle
            ciudad: Ciudad
            provincia: Provincia
            codigo_postal: Código postal
            piso: Piso (opcional)
            departamento: Departamento (opcional)
            notas_entrega: Notas para el envío (opcional)
            
        Returns:
            JSON con resultado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("SELECT id FROM clientes WHERE pedido_id = ?", (pedido_id,))
            existe = cursor.fetchone()
            
            if existe:
                # Actualizar
                cursor.execute("""
                    UPDATE clientes SET
                        nombre = ?, apellido = ?, email = ?, telefono = ?,
                        calle = ?, numero = ?, piso = ?, departamento = ?,
                        codigo_postal = ?, ciudad = ?, provincia = ?, notas_entrega = ?
                    WHERE pedido_id = ?
                """, (nombre, apellido, email, telefono, calle, numero, piso,
                      departamento, codigo_postal, ciudad, provincia, notas_entrega, pedido_id))
            else:
                # Insertar
                cursor.execute("""
                    INSERT INTO clientes (pedido_id, nombre, apellido, email, telefono,
                                         calle, numero, piso, departamento, codigo_postal,
                                         ciudad, provincia, notas_entrega)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (pedido_id, nombre, apellido, email, telefono, calle, numero,
                      piso, departamento, codigo_postal, ciudad, provincia, notas_entrega))
        
        return json.dumps({"success": True, "pedido_id": pedido_id})
    
    @tool
    def listar_pedidos(
        self,
        estado: Optional[str] = None,
        limite: int = 50,
        offset: int = 0
    ) -> str:
        """
        Lista pedidos con filtros opcionales.
        
        Args:
            estado: Filtrar por estado (opcional)
            limite: Cantidad máxima de resultados
            offset: Desplazamiento para paginación
            
        Returns:
            JSON con lista de pedidos
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if estado:
                cursor.execute("""
                    SELECT p.*, c.nombre, c.apellido, c.email
                    FROM pedidos p
                    LEFT JOIN clientes c ON p.id = c.pedido_id
                    WHERE p.estado = ?
                    ORDER BY p.fecha_creacion DESC
                    LIMIT ? OFFSET ?
                """, (estado, limite, offset))
            else:
                cursor.execute("""
                    SELECT p.*, c.nombre, c.apellido, c.email
                    FROM pedidos p
                    LEFT JOIN clientes c ON p.id = c.pedido_id
                    ORDER BY p.fecha_creacion DESC
                    LIMIT ? OFFSET ?
                """, (limite, offset))
            
            pedidos = [dict(row) for row in cursor.fetchall()]
        
        return json.dumps({"pedidos": pedidos, "total": len(pedidos)}, default=str)
    
    @tool
    def registrar_pago(
        self,
        pedido_id: str,
        monto_total: float,
        comprobante_path: str,
        metodo: str = "transferencia"
    ) -> str:
        """
        Registra un pago pendiente de verificación.
        
        Args:
            pedido_id: ID del pedido
            monto_total: Monto total del pago
            comprobante_path: Ruta al archivo del comprobante
            metodo: Método de pago
            
        Returns:
            JSON con resultado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Verificar si ya existe
            cursor.execute("SELECT id FROM pagos WHERE pedido_id = ?", (pedido_id,))
            existe = cursor.fetchone()
            
            if existe:
                cursor.execute("""
                    UPDATE pagos SET
                        monto_total = ?, comprobante_path = ?, metodo = ?,
                        verificado = 0, fecha_verificacion = NULL
                    WHERE pedido_id = ?
                """, (monto_total, comprobante_path, metodo, pedido_id))
            else:
                cursor.execute("""
                    INSERT INTO pagos (pedido_id, monto_total, comprobante_path, metodo)
                    VALUES (?, ?, ?, ?)
                """, (pedido_id, monto_total, comprobante_path, metodo))
            
            # Actualizar estado del pedido
            cursor.execute("""
                UPDATE pedidos SET estado = 'verificando_pago', fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (pedido_id,))
            
            cursor.execute("""
                INSERT INTO historial_estados (pedido_id, estado, nota, actor)
                VALUES (?, 'verificando_pago', 'Comprobante subido, pendiente verificación', 'cliente')
            """, (pedido_id,))
        
        return json.dumps({"success": True, "pedido_id": pedido_id, "estado": "verificando_pago"})
    
    @tool
    def actualizar_verificacion_pago(
        self,
        pedido_id: str,
        verificado: bool,
        resultado: Dict[str, Any],
        motivo_rechazo: Optional[str] = None
    ) -> str:
        """
        Actualiza el resultado de verificación de un pago.
        
        Args:
            pedido_id: ID del pedido
            verificado: Si el pago fue verificado correctamente
            resultado: Diccionario con resultado de la verificación
            motivo_rechazo: Motivo si fue rechazado
            
        Returns:
            JSON con resultado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            nuevo_estado = "pago_aprobado" if verificado else "rechazado"
            
            cursor.execute("""
                UPDATE pagos SET
                    verificado = ?, fecha_verificacion = CURRENT_TIMESTAMP,
                    resultado_verificacion = ?, motivo_rechazo = ?
                WHERE pedido_id = ?
            """, (1 if verificado else 0, json.dumps(resultado), motivo_rechazo, pedido_id))
            
            cursor.execute("""
                UPDATE pedidos SET estado = ?, fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (nuevo_estado, pedido_id))
            
            nota = "Pago verificado correctamente" if verificado else f"Pago rechazado: {motivo_rechazo}"
            cursor.execute("""
                INSERT INTO historial_estados (pedido_id, estado, nota, actor)
                VALUES (?, ?, ?, 'sistema')
            """, (pedido_id, nuevo_estado, nota))
        
        return json.dumps({
            "success": True,
            "pedido_id": pedido_id,
            "verificado": verificado,
            "nuevo_estado": nuevo_estado
        })
    
    @tool
    def obtener_estadisticas(self) -> str:
        """
        Obtiene estadísticas generales del sistema.
        
        Returns:
            JSON con estadísticas
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total pedidos
            cursor.execute("SELECT COUNT(*) FROM pedidos")
            stats["total_pedidos"] = cursor.fetchone()[0]
            
            # Por estado
            cursor.execute("""
                SELECT estado, COUNT(*) as cantidad
                FROM pedidos
                GROUP BY estado
            """)
            stats["por_estado"] = {row["estado"]: row["cantidad"] for row in cursor.fetchall()}
            
            # Este mes
            cursor.execute("""
                SELECT COUNT(*) FROM pedidos
                WHERE strftime('%Y-%m', fecha_creacion) = strftime('%Y-%m', 'now')
            """)
            stats["pedidos_este_mes"] = cursor.fetchone()[0]
            
            # Ingresos este mes
            cursor.execute("""
                SELECT COALESCE(SUM(monto_total), 0) FROM pedidos
                WHERE estado NOT IN ('cancelado', 'rechazado', 'pendiente_pago')
                AND strftime('%Y-%m', fecha_creacion) = strftime('%Y-%m', 'now')
            """)
            stats["ingresos_este_mes"] = cursor.fetchone()[0]
            
            # Pendientes de acción
            cursor.execute("""
                SELECT COUNT(*) FROM pedidos
                WHERE estado IN ('verificando_pago', 'pago_aprobado', 'producido', 'en_mi_domicilio')
            """)
            stats["pendientes_accion"] = cursor.fetchone()[0]
        
        return json.dumps(stats)
    
    def get_tools(self) -> List:
        """Retorna todas las herramientas para AGNO."""
        return [
            self.crear_pedido,
            self.obtener_pedido,
            self.actualizar_estado_pedido,
            self.guardar_datos_cliente,
            self.listar_pedidos,
            self.registrar_pago,
            self.actualizar_verificacion_pago,
            self.obtener_estadisticas,
        ]


# Instancia singleton
sqlite_toolkit = SQLiteToolkit()


if __name__ == "__main__":
    # Test básico
    tk = SQLiteToolkit(db_path="test_fotolibros.db")
    
    # Crear pedido de prueba
    result = tk.crear_pedido(
        producto_id="CU-21x21-DURA",
        producto_nombre="Fotolibro 21x21 Tapa Dura",
        paginas_totales=30,
        margen="estandar"
    )
    print("Pedido creado:", result)
    
    # Ver estadísticas
    stats = tk.obtener_estadisticas()
    print("Estadísticas:", stats)
    
    # Limpiar test
    os.remove("test_fotolibros.db")
