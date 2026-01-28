"""
API FastAPI - Backend de PIKSY (Fotolibros Argentina)
=====================================================
Endpoints para:
- Recibir pedidos del frontend
- Disparar automatización con AGNO + Browserbase
- Consultar estado de pedidos
- Guardar en SQLite
"""

import os
import sys
import asyncio

# Fix para Windows + Playwright + Uvicorn
if sys.platform == 'win32':
    import asyncio
    try:
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            print("✅ WindowsProactorEventLoopPolicy activado globalmente")
    except Exception as e:
        print(f"⚠️ Error configurando loop policy: {e}")

import uuid
import json
from datetime import datetime
from typing import Optional, List
from enum import Enum
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import aiosqlite

from dotenv import load_dotenv
load_dotenv()

# ============================================================
# CONFIGURACIÓN
# ============================================================

DATABASE_PATH = os.getenv("DB_PATH", "data/fotolibros.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")

# Asegurar que existan los directorios
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# MODELOS
# ============================================================

class EstadoPedido(str, Enum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    CREANDO_PROYECTO = "creando_proyecto"
    SUBIENDO_FOTOS = "subiendo_fotos"
    APLICANDO_DISEÑO = "aplicando_diseño"
    ENVIANDO_GRAFICA = "enviando_grafica"
    COMPLETADO = "completado"
    ERROR = "error"
    VERIFICANDO_PAGO = "verificando_pago"


class DireccionCliente(BaseModel):
    calle: str
    ciudad: str
    provincia: str
    cp: str


class Cliente(BaseModel):
    nombre: str
    email: EmailStr
    telefono: Optional[str] = None
    direccion: DireccionCliente


class NuevoPedido(BaseModel):
    producto_codigo: str
    estilo_diseno: str = "clasico"
    paginas_total: int = 22
    cliente: Cliente
    metodo_pago: str = "mercadopago"
    titulo_tapa: Optional[str] = None
    texto_lomo: Optional[str] = None


class PedidoResponse(BaseModel):
    id: str
    estado: EstadoPedido
    mensaje: str
    created_at: str
    updated_at: str


class EstadoPedidoResponse(BaseModel):
    id: str
    estado: EstadoPedido
    progreso: int  # 0-100
    mensaje: str
    detalles: Optional[dict] = None


# ============================================================
# BASE DE DATOS
# ============================================================

async def init_db():
    """Inicializa la base de datos SQLite"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id TEXT PRIMARY KEY,
                producto_codigo TEXT NOT NULL,
                estilo_diseno TEXT DEFAULT 'clasico',
                paginas_total INTEGER DEFAULT 22,
                cliente_json TEXT NOT NULL,
                metodo_pago TEXT DEFAULT 'mercadopago',
                titulo_tapa TEXT,
                texto_lomo TEXT,
                estado TEXT DEFAULT 'pendiente',
                progreso INTEGER DEFAULT 0,
                mensaje TEXT,
                detalles_json TEXT,
                fotos_json TEXT,
                browserbase_session_id TEXT,
                grafica_proyecto_id TEXT,
                total_precio REAL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # Migración: agregar columna verificacion_json si no existe
        try:
            await db.execute("ALTER TABLE pedidos ADD COLUMN verificacion_json TEXT")
        except:
            pass  # La columna ya existe
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS fotos_pedido (
                id TEXT PRIMARY KEY,
                pedido_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                analisis_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
            )
        """)
        
        await db.commit()


async def guardar_pedido(pedido: NuevoPedido, pedido_id: str):
    """Guarda un nuevo pedido en la base de datos"""
    now = datetime.utcnow().isoformat()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            INSERT INTO pedidos (
                id, producto_codigo, estilo_diseno, paginas_total,
                cliente_json, metodo_pago, titulo_tapa, texto_lomo,
                estado, progreso, mensaje, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pedido_id,
            pedido.producto_codigo,
            pedido.estilo_diseno,
            pedido.paginas_total,
            pedido.cliente.model_dump_json(),
            pedido.metodo_pago,
            pedido.titulo_tapa,
            pedido.texto_lomo,
            EstadoPedido.PENDIENTE.value,
            0,
            "Pedido recibido",
            now,
            now
        ))
        await db.commit()


async def actualizar_estado_pedido(
    pedido_id: str,
    estado: EstadoPedido,
    progreso: int = 0,
    mensaje: str = "",
    detalles: dict = None
):
    """Actualiza el estado de un pedido"""
    now = datetime.utcnow().isoformat()
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            UPDATE pedidos SET
                estado = ?,
                progreso = ?,
                mensaje = ?,
                detalles_json = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            estado.value,
            progreso,
            mensaje,
            json.dumps(detalles) if detalles else None,
            now,
            pedido_id
        ))
        await db.commit()


async def obtener_pedido(pedido_id: str) -> Optional[dict]:
    """Obtiene un pedido por ID"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
        row = await cursor.fetchone()
        return dict(row) if row else None


# ============================================================
# PROCESAMIENTO EN BACKGROUND
# ============================================================

async def procesar_pedido_async(pedido_id: str):
    """
    Procesa un pedido en background usando el Orquestador.
    """
    # Fix para Windows en tarea de background
    import sys
    import asyncio
    if sys.platform == 'win32':
        try:
            if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy):
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except:
            pass

    try:
        from agents.orquestador import procesar_pedido_desde_db
        
        # Iniciar procesamiento con el orquestador
        # El orquestador se encarga de todo el flujo y devuelve el resultado
        resultado = await procesar_pedido_desde_db(pedido_id)
        
        # El orquestador no actualiza la DB directamente (por diseño de separación),
        # así que actualizamos el estado final aquí
        
        if resultado["exito"]:
            await actualizar_estado_pedido(
                pedido_id,
                EstadoPedido.COMPLETADO,
                100,
                "¡Pedido completado exitosamente!",
                {
                    "proyecto_id": resultado.get("proyecto_id"),
                    "browserbase_session": resultado.get("browserbase_session"),
                    "replay_url": resultado.get("replay_url")
                }
            )
        else:
            await actualizar_estado_pedido(
                pedido_id,
                EstadoPedido.ERROR,
                resultado.get("progreso", 0),
                f"Error: {resultado.get('error', 'Error desconocido')}",
                {"logs": resultado.get("logs")}
            )
            
    except Exception as e:
        print(f"Error procesando pedido {pedido_id}: {e}")
        await actualizar_estado_pedido(
            pedido_id,
            EstadoPedido.ERROR,
            0,
            f"Error crítico: {str(e)}"
        )


# ============================================================
# FASTAPI APP
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialización al arrancar la app"""
    await init_db()
    yield

app = FastAPI(
    title="PIKSY API",
    description="Backend para automatización de fotolibros",
    version="1.0.0",
    lifespan=lifespan
)

# CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Health check"""
    return {"status": "ok", "service": "PIKSY API", "version": "1.0.0"}


@app.post("/pedidos", response_model=PedidoResponse)
async def crear_pedido(pedido: NuevoPedido, background_tasks: BackgroundTasks):
    """
    Crea un nuevo pedido de fotolibro.
    El procesamiento se hace en background.
    """
    from services.email_service import enviar_email_pedido_recibido
    
    pedido_id = str(uuid.uuid4())
    
    # Guardar en DB
    await guardar_pedido(pedido, pedido_id)
    
    # Enviar email de confirmación al cliente
    try:
        enviar_email_pedido_recibido(
            email_cliente=pedido.cliente.email,
            nombre_cliente=pedido.cliente.nombre,
            pedido_id=pedido_id,
            producto=pedido.producto_codigo,
            total=0,  # Se calcularía en frontend, aquí es informativo
            metodo_pago=pedido.metodo_pago
        )
    except Exception as e:
        print(f"Error enviando email de confirmación: {e}")
    
    # NO disparar aquí automáticamente, esperar a fotos y pago
    # background_tasks.add_task(procesar_pedido_async, pedido_id)
    
    now = datetime.utcnow().isoformat()
    
    return PedidoResponse(
        id=pedido_id,
        estado=EstadoPedido.PENDIENTE,
        mensaje="Pedido recibido. Procesando...",
        created_at=now,
        updated_at=now
    )


@app.get("/pedidos/{pedido_id}", response_model=EstadoPedidoResponse)
async def obtener_estado_pedido(pedido_id: str):
    """Obtiene el estado actual de un pedido"""
    pedido = await obtener_pedido(pedido_id)
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    detalles = None
    if pedido.get("detalles_json"):
        try:
            detalles = json.loads(pedido["detalles_json"])
        except:
            pass
    
    return EstadoPedidoResponse(
        id=pedido_id,
        estado=EstadoPedido(pedido["estado"]),
        progreso=pedido["progreso"],
        mensaje=pedido["mensaje"] or "",
        detalles=detalles
    )


@app.post("/pedidos/{pedido_id}/fotos")
async def subir_fotos(
    pedido_id: str,
    fotos: List[UploadFile] = File(...)
):
    """Sube fotos a un pedido existente"""
    pedido = await obtener_pedido(pedido_id)
    
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    # Crear directorio para el pedido
    pedido_dir = os.path.join(UPLOAD_DIR, pedido_id)
    os.makedirs(pedido_dir, exist_ok=True)
    
    fotos_guardadas = []
    
    for foto in fotos:
        # Generar nombre único
        foto_id = str(uuid.uuid4())
        extension = os.path.splitext(foto.filename)[1]
        nuevo_nombre = f"{foto_id}{extension}"
        filepath = os.path.join(pedido_dir, nuevo_nombre)
        
        # Guardar archivo
        with open(filepath, "wb") as f:
            content = await foto.read()
            f.write(content)
        
        # Registrar en DB
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
                INSERT INTO fotos_pedido (id, pedido_id, filename, filepath, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (foto_id, pedido_id, foto.filename, filepath, now))
            await db.commit()
        
        fotos_guardadas.append({
            "id": foto_id,
            "filename": foto.filename,
            "size": len(content)
        })
    
    return {
        "pedido_id": pedido_id,
        "fotos_subidas": len(fotos_guardadas),
        "fotos": fotos_guardadas
    }


@app.get("/pedidos")
async def listar_pedidos(limit: int = 20, offset: int = 0):
    """Lista los pedidos más recientes"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT id, producto_codigo, estado, progreso, mensaje, created_at, updated_at
            FROM pedidos
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = await cursor.fetchall()
        
        return {
            "pedidos": [dict(row) for row in rows],
            "total": len(rows)
        }


# ============================================================
# VERIFICACIÓN DE PAGOS
# ============================================================

@app.post("/pedidos/{pedido_id}/comprobante")
async def subir_comprobante(
    pedido_id: str,
    background_tasks: BackgroundTasks,
    comprobante: UploadFile = File(...),
    monto_esperado: str = Form(...)  # Recibir como string para evitar error 422/500 de validación
):
    """
    Recibe el comprobante de pago, lo verifica con IA y notifica al admin.
    """
    import base64
    
    # Importar servicios opcionales
    try:
        from services.payment_verifier import verificar_comprobante
        PAYMENT_VERIFIER_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ Payment verifier no disponible: {e}")
        PAYMENT_VERIFIER_AVAILABLE = False
    
    try:
        from services.email_service import enviar_email_pago_pendiente_admin
        EMAIL_SERVICE_AVAILABLE = True
    except ImportError as e:
        print(f"⚠️ Email service no disponible: {e}")
        EMAIL_SERVICE_AVAILABLE = False
    
    # Parsear monto manualmente
    try:
        # Limpiar $ y formatos 1.000,00 -> 1000.00
        clean_monto = monto_esperado.replace("$", "").replace(".", "").replace(",", ".").strip()
        monto_float = float(clean_monto)
    except:
        monto_float = 0.0
        print(f"⚠️ Error parseando monto_esperado: {monto_esperado}")
    
    # Verificar que el pedido existe
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, producto_codigo, cliente_json FROM pedidos WHERE id = ?",
            (pedido_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        pedido = dict(row)
        cliente_json = json.loads(pedido.get("cliente_json", "{}"))
    
    # Guardar comprobante
    comprobante_dir = os.path.join(UPLOAD_DIR, pedido_id, "comprobante")
    os.makedirs(comprobante_dir, exist_ok=True)
    
    file_ext = os.path.splitext(comprobante.filename)[1] or ".jpg"
    file_path = os.path.join(comprobante_dir, f"comprobante{file_ext}")
    
    content = await comprobante.read()
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Convertir a base64 para IA
    imagen_base64 = base64.b64encode(content).decode("utf-8")
    
    # Verificar con IA (si está disponible)
    if PAYMENT_VERIFIER_AVAILABLE:
        print(f"DEBUG: Llamando a verificar_comprobante para {pedido_id} con monto {monto_float}")
        try:
            verificacion = await verificar_comprobante(
                imagen_base64=imagen_base64,
                monto_esperado=monto_float,
                pedido_id=pedido_id
            )
            print(f"DEBUG: Verificación IA completada: {verificacion.valido}")
            verificacion_dict = verificacion.model_dump()
        except Exception as e:
            print(f"⚠️ Error en verificación IA: {e}")
            # Fallback: aceptar manualmente
            verificacion_dict = {
                "valido": False,
                "confianza": 0,
                "mensaje": "Verificación manual requerida - Error en IA",
                "monto_detectado": None,
                "requiere_revision_manual": True
            }
    else:
        # Sin verificador: marcar para revisión manual
        verificacion_dict = {
            "valido": False,
            "confianza": 0,
            "mensaje": "Verificación manual requerida - Servicio no disponible",
            "monto_detectado": None,
            "requiere_revision_manual": True
        }
    
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            await db.execute("""
                UPDATE pedidos 
                SET estado = ?, mensaje = ?, verificacion_json = ?, updated_at = ?
                WHERE id = ?
            """, (
                "verificando_pago",
                verificacion_dict.get("mensaje", "Verificación en proceso"),
                json.dumps(verificacion_dict),
                datetime.now().isoformat(),
                pedido_id
            ))
            await db.commit()
        print("DEBUG: BD actualizada correctamente")
    except Exception as e:
        print(f"❌ ERROR BD: {e}")
        raise HTTPException(status_code=500, detail=f"Error actualizando BD: {e}")
    
    # Notificar al admin por email (No bloqueante)
    if EMAIL_SERVICE_AVAILABLE:
        try:
            enviar_email_pago_pendiente_admin(
                pedido_id=pedido_id,
                nombre_cliente=cliente_json.get("nombre", "Cliente"),
                email_cliente=cliente_json.get("email", ""),
                producto=pedido.get("producto_codigo", "Fotolibro"),
                monto_esperado=monto_float,
                verificacion_ia=verificacion_dict
            )
            print("DEBUG: Email enviado (o intentado)")
        except Exception as e:
            print(f"⚠️ Error enviando email: {e}")
    else:
        print("ℹ️ Email service no disponible - omitiendo notificación")
    
    # Notificar al admin por Telegram (No bloqueante)
    try:
        from services.telegram_service import notificar_pago_pendiente
        
        await notificar_pago_pendiente(
            pedido_id=pedido_id,
            nombre_cliente=cliente_json.get("nombre", "Cliente"),
            email_cliente=cliente_json.get("email", ""),
            producto=pedido.get("producto_codigo", "Fotolibro"),
            monto_esperado=monto_float,
            verificacion_ia=verificacion_dict
        )
        print("DEBUG: Telegram enviado")
    except Exception as e:
        print(f"⚠️ Error enviando Telegram: {e}")
    
    # SI EL PAGO ES VÁLIDO (O estamos en DEBUG), DISPARAR AUTOMATIZACIÓN
    # Para esta fase de pruebas, disparamos siempre para ver el navegador, 
    # pero reportamos el estado real del pago.
    print(f"🚀 [AUTO] Iniciando orquestador para {pedido_id}...")
    background_tasks.add_task(procesar_pedido_async, pedido_id)
    
    es_valido = verificacion_dict.get("valido", False)
    mensaje_verificacion = verificacion_dict.get("mensaje", "Verificación completada")
    
    return {
        "pedido_id": pedido_id,
        "verificacion": verificacion_dict,
        "mensaje": "Pago verificado. Iniciando automatización..." if es_valido else f"⚠️ {mensaje_verificacion}. Iniciando de todas formas para pruebas.",
        "estado": "procesando"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    error_msg = traceback.format_exc()
    print(f"❌ ERROR 500 NO CAPTURADO: {error_msg}")
    return {"detail": "Internal Server Error", "error": str(exc)}


# ============================================================
# ENDPOINT DE TEST PARA STAGEHAND (OMITE VERIFICACION IA)
# ============================================================

@app.post("/test/iniciar-stagehand/{pedido_id}")
async def test_iniciar_stagehand(pedido_id: str, background_tasks: BackgroundTasks):
    """
    Endpoint de TEST que dispara el orquestador directamente sin verificacion IA.
    Util para probar Stagehand sin esperar la verificacion de comprobante.
    """
    # Verificar que el pedido existe
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, estado FROM pedidos WHERE id = ?",
            (pedido_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        # Actualizar estado
        await db.execute("""
            UPDATE pedidos 
            SET estado = ?, mensaje = ?, updated_at = ?
            WHERE id = ?
        """, (
            "procesando",
            "Test Stagehand iniciado manualmente",
            datetime.now().isoformat(),
            pedido_id
        ))
        await db.commit()
    
    # Disparar orquestador en background
    print(f"🧪 [TEST] Iniciando Stagehand para {pedido_id} (sin verificacion IA)...")
    background_tasks.add_task(procesar_pedido_async, pedido_id)
    
    return {
        "pedido_id": pedido_id,
        "mensaje": "Stagehand iniciado en modo TEST (sin verificacion IA)",
        "estado": "procesando"
    }


# ============================================================
# TRACKING PARA CLIENTES
# ============================================================

@app.post("/tracking")
async def buscar_pedido_cliente(email: str, pedido_id: str):
    """
    Endpoint para que clientes consulten su pedido usando email + ID.
    """
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT id, producto_codigo, estado, progreso, mensaje, cliente_json, created_at, updated_at
            FROM pedidos WHERE id = ?
        """, (pedido_id,))
        row = await cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Pedido no encontrado")
        
        pedido = dict(row)
        
        # Verificar que el email coincide
        try:
            cliente = json.loads(pedido["cliente_json"])
            if cliente.get("email", "").lower() != email.lower():
                raise HTTPException(status_code=403, detail="Email no coincide con el pedido")
        except json.JSONDecodeError:
            pass
        
        # Mapeo de estados a timeline
        estados_timeline = [
            {"estado": "pendiente", "label": "Pedido Recibido", "done": False, "current": False},
            {"estado": "procesando", "label": "Verificando Pago", "done": False, "current": False},
            {"estado": "creando_proyecto", "label": "Creando tu Fotolibro", "done": False, "current": False},
            {"estado": "aplicando_diseño", "label": "Aplicando Diseño", "done": False, "current": False},
            {"estado": "enviando_grafica", "label": "Enviando a Producción", "done": False, "current": False},
            {"estado": "completado", "label": "En Camino a tu Casa", "done": False, "current": False},
        ]
        
        estado_actual = pedido["estado"]
        estado_encontrado = False
        for step in estados_timeline:
            if step["estado"] == estado_actual:
                step["current"] = True
                estado_encontrado = True
            elif not estado_encontrado:
                step["done"] = True
        
        return {
            "id": pedido["id"],
            "producto": pedido["producto_codigo"],
            "estado": pedido["estado"],
            "progreso": pedido["progreso"],
            "mensaje": pedido["mensaje"],
            "timeline": estados_timeline,
            "created_at": pedido["created_at"],
            "updated_at": pedido["updated_at"]
        }


# ============================================================
# ADMIN ENDPOINTS
# ============================================================

@app.get("/admin/pedidos")
async def admin_listar_pedidos(
    estado: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Lista todos los pedidos con filtros para admin"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        if estado:
            cursor = await db.execute("""
                SELECT * FROM pedidos WHERE estado = ?
                ORDER BY created_at DESC LIMIT ? OFFSET ?
            """, (estado, limit, offset))
        else:
            cursor = await db.execute("""
                SELECT * FROM pedidos ORDER BY created_at DESC LIMIT ? OFFSET ?
            """, (limit, offset))
        
        rows = await cursor.fetchall()
        
        pedidos = []
        for row in rows:
            pedido = dict(row)
            # Parsear cliente JSON
            try:
                pedido["cliente"] = json.loads(pedido.get("cliente_json", "{}"))
            except:
                pedido["cliente"] = {}
            del pedido["cliente_json"]
            pedidos.append(pedido)
        
        # Contar totales por estado
        count_cursor = await db.execute("""
            SELECT estado, COUNT(*) as count FROM pedidos GROUP BY estado
        """)
        stats = {row["estado"]: row["count"] for row in await count_cursor.fetchall()}
        
        return {
            "pedidos": pedidos,
            "stats": stats,
            "total": len(pedidos)
        }


@app.patch("/admin/pedidos/{pedido_id}/estado")
async def admin_cambiar_estado(
    pedido_id: str,
    nuevo_estado: str,
    mensaje: Optional[str] = None,
    codigo_seguimiento: Optional[str] = None
):
    """
    Admin: Cambiar estado de un pedido manualmente.
    Si cambia a 'completado' (enviado), envía email al cliente.
    """
    from services.email_service import enviar_email_pedido_enviado
    
    pedido = await obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    
    try:
        estado = EstadoPedido(nuevo_estado)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Estado inválido: {nuevo_estado}")
    
    # Actualizar estado
    await actualizar_estado_pedido(
        pedido_id,
        estado,
        progreso=100 if estado == EstadoPedido.COMPLETADO else 50,
        mensaje=mensaje or f"Estado actualizado a {estado.value}",
        detalles={"codigo_seguimiento": codigo_seguimiento} if codigo_seguimiento else None
    )
    
    # Enviar email si se marca como enviado/completado
    if estado == EstadoPedido.COMPLETADO:
        try:
            cliente = json.loads(pedido.get("cliente_json", "{}"))
            direccion_obj = cliente.get("direccion", {})
            direccion = f"{direccion_obj.get('calle', '')}, {direccion_obj.get('ciudad', '')}, {direccion_obj.get('provincia', '')}"
            
            enviar_email_pedido_enviado(
                email_cliente=cliente.get("email", ""),
                nombre_cliente=cliente.get("nombre", "Cliente"),
                pedido_id=pedido_id,
                producto=pedido.get("producto_codigo", "Fotolibro"),
                direccion=direccion,
                codigo_seguimiento=codigo_seguimiento
            )
        except Exception as e:
            print(f"Error enviando email: {e}")
    
    return {"success": True, "pedido_id": pedido_id, "nuevo_estado": estado.value}


@app.get("/admin/export")
async def admin_exportar_pedidos(formato: str = "csv"):
    """Exporta todos los pedidos como CSV"""
    from fastapi.responses import StreamingResponse
    import io
    import csv
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM pedidos ORDER BY created_at DESC")
        rows = await cursor.fetchall()
    
    # Crear CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "ID", "Producto", "Estilo", "Páginas", "Estado", "Progreso",
        "Cliente Nombre", "Cliente Email", "Ciudad", "Provincia",
        "Método Pago", "Total", "Creado", "Actualizado"
    ])
    
    for row in rows:
        pedido = dict(row)
        try:
            cliente = json.loads(pedido.get("cliente_json", "{}"))
        except:
            cliente = {}
        
        direccion = cliente.get("direccion", {})
        
        writer.writerow([
            pedido["id"][:18],
            pedido["producto_codigo"],
            pedido["estilo_diseno"],
            pedido["paginas_total"],
            pedido["estado"],
            pedido["progreso"],
            cliente.get("nombre", ""),
            cliente.get("email", ""),
            direccion.get("ciudad", ""),
            direccion.get("provincia", ""),
            pedido["metodo_pago"],
            pedido.get("total_precio", 0),
            pedido["created_at"][:10],
            pedido["updated_at"][:10]
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=pedidos_export.csv"}
    )


# ============================================================
# N8N WEBHOOK ENDPOINTS
# ============================================================

@app.post("/webhook/n8n/nuevo-pedido")
async def webhook_n8n_nuevo_pedido(data: dict, background_tasks: BackgroundTasks):
    """
    Webhook para recibir pedidos desde n8n.
    Permite integración con workflows externos.
    """
    try:
        # Convertir datos de n8n a nuestro modelo
        pedido = NuevoPedido(
            producto_codigo=data.get("producto_codigo", "CU-21x21-DURA"),
            estilo_diseno=data.get("estilo_diseno", "clasico"),
            paginas_total=data.get("paginas_total", 22),
            cliente=Cliente(
                nombre=data.get("cliente_nombre", ""),
                email=data.get("cliente_email", ""),
                telefono=data.get("cliente_telefono"),
                direccion=DireccionCliente(
                    calle=data.get("direccion_calle", ""),
                    ciudad=data.get("direccion_ciudad", ""),
                    provincia=data.get("direccion_provincia", ""),
                    cp=data.get("direccion_cp", "")
                )
            ),
            metodo_pago=data.get("metodo_pago", "mercadopago"),
            titulo_tapa=data.get("titulo_tapa"),
            texto_lomo=data.get("texto_lomo")
        )
        
        pedido_id = str(uuid.uuid4())
        await guardar_pedido(pedido, pedido_id)
        background_tasks.add_task(procesar_pedido_async, pedido_id)
        
        return {
            "success": True,
            "pedido_id": pedido_id,
            "estado": "pendiente",
            "mensaje": "Pedido creado y en procesamiento"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/webhook/n8n/estado/{pedido_id}")
async def webhook_n8n_estado(pedido_id: str):
    """Webhook para que n8n consulte el estado de un pedido"""
    pedido = await obtener_pedido(pedido_id)
    
    if not pedido:
        return {"success": False, "error": "Pedido no encontrado"}
    
    return {
        "success": True,
        "pedido_id": pedido_id,
        "estado": pedido["estado"],
        "progreso": pedido["progreso"],
        "mensaje": pedido["mensaje"]
    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
