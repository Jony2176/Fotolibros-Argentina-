"""
Servicio de Cola con SQLite
Wrapper async sobre db.py para mantener compatibilidad
"""

from typing import Optional, Dict
import logging
import asyncio

from app.db import (
    init_database,
    encolar_pedido as _encolar_pedido,
    obtener_siguiente_pedido as _obtener_siguiente_pedido,
    marcar_completado as _marcar_completado,
    marcar_error as _marcar_error,
    obtener_posicion_cola as _obtener_posicion_cola,
    get_queue_stats as _get_queue_stats
)

logger = logging.getLogger(__name__)


async def init_redis():
    """Inicializar base de datos SQLite (nombre mantenido por compatibilidad)"""
    init_database()
    logger.info("✅ SQLite conectado (cola de trabajos)")


async def encolar_pedido(pedido_data: Dict) -> int:
    """Agregar pedido a la cola"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _encolar_pedido, pedido_data, 0)


async def obtener_posicion_cola(pedido_id: str) -> int:
    """Obtener posición en cola"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _obtener_posicion_cola, pedido_id)


async def obtener_siguiente_pedido() -> Optional[Dict]:
    """Obtener siguiente pedido de la cola"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _obtener_siguiente_pedido)


async def marcar_completado(pedido_id: str):
    """Marcar pedido como completado"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _marcar_completado, pedido_id)


async def marcar_error(pedido_id: str, error: str):
    """Marcar pedido con error"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _marcar_error, pedido_id, error)


async def get_queue_stats() -> Dict:
    """Obtener estadísticas de la cola"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_queue_stats)
