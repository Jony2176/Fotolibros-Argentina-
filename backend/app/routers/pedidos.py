"""
Router de Pedidos
Endpoints para crear y gestionar pedidos
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
from pathlib import Path
import shutil
import logging
from datetime import datetime

from app.schemas import PedidoCreate, PedidoResponse
from app.db import (
    crear_pedido as db_crear_pedido,
    obtener_pedido,
    actualizar_estado_pedido,
    encolar_pedido,
    obtener_posicion_cola
)
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=PedidoResponse)
async def crear_pedido(pedido: PedidoCreate):
    """
    Crear un nuevo pedido de fotolibro
    
    1. Valida datos
    2. Crea directorio para fotos
    3. Guarda en base de datos
    """
    
    # Generar ID de pedido
    pedido_id = f"PED-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"
    
    # Crear directorio para fotos
    directorio_fotos = Path(settings.PHOTOS_BASE_DIR) / pedido_id
    directorio_fotos.mkdir(parents=True, exist_ok=True)
    
    # Preparar datos para la DB
    pedido_data = {
        'pedido_id': pedido_id,
        'cliente_nombre': pedido.cliente.nombre,
        'cliente_email': pedido.cliente.email,
        'cliente_telefono': pedido.cliente.telefono,
        'codigo_producto': pedido.libro.codigo_producto,
        'tamano': pedido.libro.tamano,
        'tapa': pedido.libro.tapa,
        'estilo': pedido.libro.estilo,
        'ocasion': pedido.libro.ocasion,
        'titulo_personalizado': pedido.libro.titulo_personalizado,
        'directorio_fotos': str(directorio_fotos),
        'cantidad_fotos': 0,
        'modo_confirmacion': pedido.modo_confirmacion,
        'notas_cliente': pedido.notas_cliente
    }
    
    # Guardar en base de datos
    try:
        db_crear_pedido(pedido_data)
        logger.info(f"📝 Nuevo pedido creado: {pedido_id}")
    except Exception as e:
        logger.error(f"❌ Error creando pedido: {e}")
        raise HTTPException(500, f"Error creando pedido: {str(e)}")
    
    # Obtener el pedido recién creado para tener el ID correcto
    pedido_creado = obtener_pedido(pedido_id)
    
    return PedidoResponse(
        id=pedido_creado['id'] if pedido_creado else 0,
        pedido_id=pedido_id,
        cliente_nombre=pedido.cliente.nombre,
        cliente_email=pedido.cliente.email,
        codigo_producto=pedido.libro.codigo_producto,
        estado="pendiente",
        cantidad_fotos=0,
        fecha_creacion=datetime.now(),
        fecha_actualizacion=datetime.now()
    )


@router.post("/{pedido_id}/fotos")
async def subir_fotos(
    pedido_id: str,
    fotos: List[UploadFile] = File(...)
):
    """
    Subir fotos para un pedido
    """
    
    # Verificar que el pedido existe
    pedido = obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    directorio = Path(pedido['directorio_fotos']) if pedido['directorio_fotos'] else Path(settings.PHOTOS_BASE_DIR) / pedido_id
    directorio.mkdir(parents=True, exist_ok=True)
    
    # Guardar archivos
    cantidad_subidas = 0
    for file in fotos:
        filepath = directorio / file.filename
        with filepath.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        cantidad_subidas += 1
    
    logger.info(f"📸 {cantidad_subidas} fotos subidas para {pedido_id}")
    
    # Actualizar cantidad de fotos en DB
    from app.db import get_db
    with get_db() as conn:
        cursor = conn.cursor()
        # Contar fotos totales en el directorio
        extensions = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
        total_fotos = sum(len(list(directorio.glob(f'*{ext}')) + list(directorio.glob(f'*{ext.upper()}'))) for ext in extensions)
        
        cursor.execute("""
            UPDATE pedidos 
            SET cantidad_fotos = ?, directorio_fotos = ?, fecha_actualizacion = CURRENT_TIMESTAMP
            WHERE pedido_id = ?
        """, (total_fotos, str(directorio), pedido_id))
        conn.commit()
    
    return {
        "success": True,
        "cantidad_subidas": cantidad_subidas,
        "total_fotos": total_fotos,
        "directorio": str(directorio),
        "mensaje": f"{cantidad_subidas} fotos subidas correctamente"
    }


@router.post("/{pedido_id}/procesar")
async def procesar_pedido(pedido_id: str):
    """
    Encolar pedido para procesamiento AGNO
    """
    
    # Obtener pedido de la DB
    pedido = obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    directorio = Path(pedido['directorio_fotos']) if pedido['directorio_fotos'] else Path(settings.PHOTOS_BASE_DIR) / pedido_id
    
    if not directorio.exists():
        raise HTTPException(404, f"Directorio de fotos no existe: {directorio}")
    
    # Contar fotos
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
    fotos = []
    for ext in extensions:
        fotos.extend(list(directorio.glob(f'*{ext}')))
        fotos.extend(list(directorio.glob(f'*{ext.upper()}')))
    
    if len(fotos) < 5:  # Reducido para testing
        raise HTTPException(
            400,
            f"Muy pocas fotos ({len(fotos)}). Mínimo 5 requeridas."
        )
    
    # Preparar datos para la cola
    pedido_data = {
        "pedido_id": pedido_id,
        "cliente_nombre": pedido['cliente_nombre'],
        "cliente_email": pedido['cliente_email'],
        "codigo_producto": pedido['codigo_producto'],
        "tamano": pedido['tamano'],
        "tapa": pedido['tapa'],
        "estilo": pedido['estilo'],
        "directorio_fotos": str(directorio),
        "cantidad_fotos": len(fotos),
        "modo_confirmacion": bool(pedido['modo_confirmacion']),
        "telegram_notificar": settings.TELEGRAM_ADMIN_CHAT,
        "titulo_personalizado": pedido.get('titulo_personalizado'),
        "hint": pedido.get('ocasion')
    }
    
    # Encolar
    posicion = encolar_pedido(pedido_data)
    
    # Actualizar estado
    actualizar_estado_pedido(pedido_id, "en_cola")
    
    logger.info(f"📥 Pedido {pedido_id} encolado en posición {posicion}")
    
    return {
        "success": True,
        "pedido_id": pedido_id,
        "estado": "en_cola",
        "posicion": posicion,
        "cantidad_fotos": len(fotos),
        "mensaje": f"Pedido encolado en posición {posicion}"
    }


@router.get("/{pedido_id}/estado")
async def obtener_estado(pedido_id: str):
    """Obtener estado actual del pedido"""
    
    # Obtener pedido de la DB
    pedido = obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    # Obtener posición en cola
    posicion = obtener_posicion_cola(pedido_id)
    
    if posicion == 0:
        estado = "procesando"
        mensaje = "Tu pedido está siendo procesado ahora"
    elif posicion > 0:
        estado = "en_cola"
        mensaje = f"Tu pedido está en cola (posición {posicion})"
    else:
        estado = pedido['estado']
        if estado == 'completado':
            mensaje = "Tu pedido ha sido completado"
        elif estado == 'pendiente':
            if pedido['cantidad_fotos'] > 0:
                mensaje = "Pedido recibido correctamente. ¡Gracias!"
                estado = "recibido"
            else:
                mensaje = "Pedido creado, esperando fotos"
        else:
            mensaje = f"Estado: {estado}"
    
    return {
        "pedido_id": pedido_id,
        "estado": estado,
        "posicion": posicion if posicion > 0 else None,
        "cantidad_fotos": pedido['cantidad_fotos'],
        "mensaje": mensaje
    }


@router.post("/{pedido_id}/comprobante")
async def subir_comprobante(
    pedido_id: str,
    comprobante: UploadFile = File(...),
    monto_esperado: float = Form(0)
):
    """
    Subir comprobante de pago para un pedido
    """
    
    # Verificar que el pedido existe
    pedido = obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(404, "Pedido no encontrado")
    
    # Crear directorio para comprobantes si no existe
    directorio = Path(pedido['directorio_fotos']) if pedido['directorio_fotos'] else Path(settings.PHOTOS_BASE_DIR) / pedido_id
    directorio.mkdir(parents=True, exist_ok=True)
    
    # Guardar comprobante
    extension = Path(comprobante.filename).suffix or '.jpg'
    filepath = directorio / f"comprobante{extension}"
    with filepath.open("wb") as buffer:
        shutil.copyfileobj(comprobante.file, buffer)
    
    logger.info(f"💳 Comprobante subido para {pedido_id} (monto esperado: ${monto_esperado})")
    
    return {
        "success": True,
        "pedido_id": pedido_id,
        "archivo": str(filepath),
        "monto_esperado": monto_esperado,
        "mensaje": "Comprobante recibido correctamente"
    }
