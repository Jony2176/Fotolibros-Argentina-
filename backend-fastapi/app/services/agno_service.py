"""
Servicio de integración con AGNO
Ejecuta el análisis de fotolibros
"""

import sys
import os
from pathlib import Path
from typing import Dict, List
import logging

# Agregar directorio de AGNO al path
AGNO_DIR = Path(__file__).parent.parent.parent / "agno"
sys.path.insert(0, str(AGNO_DIR))

from fotolibro_agents.team import process_fotolibro

logger = logging.getLogger(__name__)


async def analizar_fotolibro(
    pedido_id: str,
    directorio_fotos: str,
    cliente_nombre: str,
    hint: str = None,
    titulo_personalizado: str = None
) -> Dict:
    """
    Ejecutar análisis AGNO de un fotolibro
    
    Args:
        pedido_id: ID del pedido
        directorio_fotos: Ruta al directorio con fotos
        cliente_nombre: Nombre del cliente
        hint: Hint del tipo de evento (opcional)
        titulo_personalizado: Título personalizado (opcional)
    
    Returns:
        Dict con configuración completa del fotolibro
    """
    
    logger.info(f"🔍 Iniciando análisis AGNO para pedido {pedido_id}")
    
    # Recolectar fotos del directorio
    fotos_dir = Path(directorio_fotos)
    if not fotos_dir.exists():
        raise FileNotFoundError(f"Directorio de fotos no existe: {directorio_fotos}")
    
    # Buscar archivos de imagen
    extensions = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
    photo_paths = []
    
    for ext in extensions:
        photo_paths.extend(list(fotos_dir.glob(f'*{ext}')))
        photo_paths.extend(list(fotos_dir.glob(f'*{ext.upper()}')))
    
    photo_paths = [str(p.absolute()) for p in photo_paths]
    
    if not photo_paths:
        raise ValueError(f"No se encontraron fotos en {directorio_fotos}")
    
    logger.info(f"📸 Encontradas {len(photo_paths)} fotos")
    
    # Preparar contexto
    client_context = {
        "client_name": cliente_nombre
    }
    
    if hint:
        client_context["hint"] = hint
    
    if titulo_personalizado:
        client_context["custom_title"] = titulo_personalizado
    
    # Ejecutar AGNO
    try:
        config = process_fotolibro(
            photo_paths,
            client_context,
            output_path=None  # No guardar a archivo, solo retornar
        )
        
        if config.get('success') == False:
            raise Exception(config.get('error', 'Error desconocido en AGNO'))
        
        logger.info(f"✅ Análisis AGNO completado para {pedido_id}")
        logger.info(f"   Motivo: {config['motif']['type']}")
        logger.info(f"   Cronología: {config['chronology']['type']}")
        logger.info(f"   Fotos ordenadas: {len(config['photos'])}")
        
        return config
        
    except Exception as e:
        logger.error(f"❌ Error en análisis AGNO: {e}")
        raise


def formatear_config_para_clawdbot(agno_config: Dict, pedido_data: Dict) -> Dict:
    """
    Formatear configuración de AGNO para el webhook de Clawdbot
    
    Args:
        agno_config: Configuración generada por AGNO
        pedido_data: Datos del pedido original
    
    Returns:
        Dict formateado para Clawdbot
    """
    
    return {
        "pedido_id": pedido_data['pedido_id'],
        "cliente": {
            "nombre": pedido_data['cliente_nombre'],
            "email": pedido_data['cliente_email']
        },
        "libro": {
            "codigo": pedido_data['codigo_producto'],
            "tamano": pedido_data.get('tamano'),
            "tapa": pedido_data.get('tapa'),
            "estilo": pedido_data.get('estilo')
        },
        "directorio_fotos": pedido_data['directorio_fotos'],
        
        # Configuración de AGNO completa
        "agno_config": agno_config,
        
        # Configuración de ejecución
        "configuracion": {
            "modo_confirmacion": pedido_data.get('modo_confirmacion', True),
            "telegram_notificar": pedido_data.get('telegram_notificar'),
            "max_reintentos": 3,
            "timeout_minutos": 45
        }
    }
