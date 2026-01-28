"""
Servicio de integración con Clawdbot (versión optimizada con Skills)
Envía pedidos vía webhook usando el skill fotolibros-fdf
"""

import httpx
from typing import Dict
import logging
import json

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
    
    # Construir mensaje SIMPLE que referencia el skill
    mensaje = construir_mensaje_con_skill(config_completo)
    
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


def construir_mensaje_con_skill(config: Dict) -> str:
    """
    Construir mensaje optimizado que usa el skill fotolibros-fdf
    
    El skill ya tiene todas las instrucciones detalladas,
    aquí solo pasamos la configuración específica del pedido
    
    Args:
        config: Configuración completa del pedido
    
    Returns:
        Mensaje formateado para Clawdbot
    """
    
    agno = config['agno_config']
    
    # Extraer datos clave
    titulo = agno['story']['cover']['title']
    template = agno['design']['template_choice']['primary']
    motivo = agno['motif']['type']
    fotos_count = len(agno['photos'])
    
    mensaje = f"""
NUEVO PEDIDO: {config['pedido_id']}

Cliente: {config['cliente']['nombre']}
Producto: {config['libro']['codigo']} ({config['libro']['tamano']} {config['libro']['tapa']})

📋 CONFIGURACIÓN AGNO:
```json
{json.dumps(agno, indent=2, ensure_ascii=False)}
```

🎯 TAREA:
Ejecuta el pedido usando el skill "fotolibros-fdf".

RESUMEN:
- Motivo: {motivo}
- Título: "{titulo}"
- Template: {template}
- Fotos: {fotos_count} (YA ORDENADAS cronológicamente)
- Directorio: {config['directorio_fotos']}

⚠️ IMPORTANTE:
1. Lee SOUL.md para tu personalidad como FotoBot
2. Usa el skill "fotolibros-fdf" para instrucciones del editor
3. Ejecuta EXACTAMENTE lo que indica agno_config (NO improvises)
4. Notifica tu progreso narrativamente por Telegram
5. Modo confirmación: {config['configuracion']['modo_confirmacion']}

🚀 COMENZAR:
1. Valida que agno_config esté completo
2. Abre editor FDF (online.fabricadefotolibros.com)
3. Sigue el flujo del skill "fotolibros-fdf"
"""
    
    return mensaje.strip()
