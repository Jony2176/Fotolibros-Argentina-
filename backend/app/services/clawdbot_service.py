"""
Servicio de integración con Clawdbot
Envía pedidos vía webhook
"""

import httpx
from typing import Dict
import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def enviar_a_clawdbot(config_completo: Dict) -> Dict:
    """
    Enviar configuración a Clawdbot vía webhook
    
    Args:
        config_completo: Configuración completa (AGNO + pedido)
    
    Returns:
        Respuesta del webhook
    """
    
    pedido_id = config_completo['pedido_id']
    logger.info(f"📤 Enviando pedido {pedido_id} a Clawdbot...")
    
    # Construir mensaje narrativo para Clawdbot
    mensaje = construir_mensaje_pedido(config_completo)
    
    # Payload del webhook
    payload = {
        "message": mensaje,
        "name": "Fotolibros",
        "sessionKey": f"fotolibro:{pedido_id}",
        "wakeMode": "now",
        "deliver": True,
        "channel": "telegram",
        "to": config_completo['configuracion']['telegram_notificar'],
        "model": "anthropic/claude-opus-4-5",
        "thinking": "high",
        "timeoutSeconds": config_completo['configuracion']['timeout_minutos'] * 60
    }
    
    # Enviar webhook
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.CLAWDBOT_URL}/hooks/agent",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.CLAWDBOT_HOOK_TOKEN}",
                    "Content-Type": "application/json"
                }
            )
            
            if response.status_code not in [200, 202]:
                raise Exception(f"Clawdbot error: {response.status_code} - {response.text}")
            
            logger.info(f"✅ Pedido {pedido_id} enviado a Clawdbot")
            
            return response.json()
            
    except Exception as e:
        logger.error(f"❌ Error enviando a Clawdbot: {e}")
        raise


def construir_mensaje_pedido(config: Dict) -> str:
    """
    Construir mensaje narrativo para Clawdbot
    
    Args:
        config: Configuración completa del pedido
    
    Returns:
        Mensaje formateado
    """
    
    agno = config['agno_config']
    
    mensaje = f"""
NUEVO PEDIDO DE FOTOLIBRO

Pedido ID: {config['pedido_id']}
Cliente: {config['cliente']['nombre']}

Producto: {config['libro']['codigo']}
- Tamaño: {config['libro']['tamano']}
- Tapa: {config['libro']['tapa']}
- Estilo: {config['libro']['estilo']}

Directorio de fotos: {config['directorio_fotos']}

==============================================
CONFIGURACIÓN DE AGNO (PRE-ANALIZADA)
==============================================

MOTIVO DETECTADO: {agno['motif']['type']} ({agno['motif']['confidence']}% confianza)

CRONOLOGÍA: {agno['chronology']['type']}
- Fotos ordenadas: {len(agno['photos'])}

DISEÑO:
- Título: "{agno['story']['cover']['title']}"
- Subtítulo: "{agno['story']['cover'].get('subtitle', '')}"
- Template: {agno['design']['template_choice']['primary']}
- Páginas hero: {len(agno['design']['layout_strategy'].get('hero_pages', []))}
- Capítulos: {len(agno['story'].get('chapters', []))}

==============================================
INSTRUCCIONES DE EJECUCIÓN
==============================================

1. Abre el editor de Fábrica de Fotolibros
2. Login con credenciales (de variables de entorno)
3. Crea nuevo proyecto: {config['libro']['codigo']}
4. Sube las fotos EN EL ORDEN EXACTO de agno_config.photos
5. Aplica el template: {agno['design']['template_choice']['primary']}
6. Inserta los textos de agno_config.story
7. Genera preview
8. Notifica y pide confirmación (modo: {config['configuracion']['modo_confirmacion']})
9. Si aprobado: finaliza en FDF

IMPORTANTE:
- NO cambies el orden de las fotos (AGNO ya lo decidió cronológicamente)
- NO elijas otro template (AGNO ya decidió el óptimo)
- NO modifiques los textos (AGNO ya los generó emotivamente)
- Ejecuta EXACTAMENTE lo que indica el JSON

Usa el skill 'fotolibros-fdf' para las instrucciones detalladas del editor.
"""
    
    return mensaje.strip()
