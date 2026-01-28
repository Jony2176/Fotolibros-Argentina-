"""
Worker - Procesador de Cola de Pedidos
Procesa pedidos secuencialmente (uno a la vez)
"""

import asyncio
import logging
from datetime import datetime

from app.config import settings
from app.services.queue_service import (
    obtener_siguiente_pedido,
    marcar_completado,
    marcar_error,
    init_redis
)
from app.services.agno_service import analizar_fotolibro, formatear_config_para_clawdbot
from app.services.clawdbot_service import enviar_a_clawdbot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def procesar_pedido(pedido_data: dict):
    """
    Procesar un pedido completo
    
    Flujo:
    1. Ejecutar AGNO para análisis
    2. Formatear config para Clawdbot
    3. Enviar webhook a Clawdbot
    4. Marcar como completado
    """
    
    pedido_id = pedido_data['pedido_id']
    logger.info(f"\n{'='*80}")
    logger.info(f"🎨 PROCESANDO PEDIDO {pedido_id}")
    logger.info(f"{'='*80}\n")
    
    try:
        # ===============================================
        # FASE 1: ANÁLISIS AGNO
        # ===============================================
        logger.info(f"🔍 FASE 1: Ejecutando análisis AGNO...")
        
        agno_config = await analizar_fotolibro(
            pedido_id=pedido_id,
            directorio_fotos=pedido_data['directorio_fotos'],
            cliente_nombre=pedido_data['cliente_nombre'],
            hint=pedido_data.get('hint'),
            titulo_personalizado=pedido_data.get('titulo_personalizado')
        )
        
        logger.info(f"✅ Análisis AGNO completado")
        logger.info(f"   Motivo: {agno_config['motif']['type']}")
        logger.info(f"   Fotos: {len(agno_config['photos'])}")
        
        # ===============================================
        # FASE 2: FORMATEAR PARA CLAWDBOT
        # ===============================================
        logger.info(f"\n📋 FASE 2: Formateando configuración...")
        
        config_completo = formatear_config_para_clawdbot(agno_config, pedido_data)
        
        logger.info(f"✅ Configuración formateada")
        
        # ===============================================
        # FASE 3: ENVIAR A CLAWDBOT
        # ===============================================
        logger.info(f"\n📤 FASE 3: Enviando a Clawdbot...")
        
        response = await enviar_a_clawdbot(config_completo)
        
        logger.info(f"✅ Pedido enviado a Clawdbot")
        logger.info(f"   Response: {response}")
        
        # ===============================================
        # FINALIZACIÓN
        # ===============================================
        await marcar_completado(pedido_id)
        
        logger.info(f"\n{'='*80}")
        logger.info(f"✅ PEDIDO {pedido_id} PROCESADO EXITOSAMENTE")
        logger.info(f"{'='*80}\n")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR EN PEDIDO {pedido_id}: {e}")
        
        import traceback
        traceback.print_exc()
        
        # Marcar error
        await marcar_error(pedido_id, str(e))
        
        # TODO: Decidir si reintentar
        if pedido_data.get('intentos', 0) < settings.WORKER_MAX_RETRIES:
            logger.info(f"🔄 Reintentando pedido (intento {pedido_data.get('intentos', 0) + 1}/{settings.WORKER_MAX_RETRIES})...")
            # TODO: Implementar lógica de reintento
        else:
            logger.error(f"❌ Pedido {pedido_id} falló después de {settings.WORKER_MAX_RETRIES} intentos")


async def worker_loop():
    """
    Loop principal del worker
    Procesa pedidos de la cola secuencialmente
    """
    
    logger.info("\n" + "="*80)
    logger.info("🚀 WORKER DE FOTOLIBROS INICIADO")
    logger.info("="*80 + "\n")
    
    # Inicializar Redis
    await init_redis()
    
    while True:
        try:
            # Obtener siguiente pedido
            pedido = await obtener_siguiente_pedido()
            
            if pedido:
                # Procesar pedido
                await procesar_pedido(pedido)
            else:
                # Cola vacía, esperar 10 segundos
                logger.debug("📭 Cola vacía, esperando...")
                await asyncio.sleep(10)
                
        except KeyboardInterrupt:
            logger.info("\n⚠️  Worker detenido por usuario")
            break
            
        except Exception as e:
            logger.error(f"❌ Error en worker loop: {e}")
            import traceback
            traceback.print_exc()
            
            # Esperar antes de reintentar
            await asyncio.sleep(30)


def main():
    """Entry point del worker"""
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        logger.info("\n👋 Worker cerrado")


if __name__ == "__main__":
    main()
