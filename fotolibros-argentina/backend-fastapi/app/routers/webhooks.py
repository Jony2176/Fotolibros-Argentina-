"""
Router de Webhooks
Endpoints para recibir callbacks
"""

from fastapi import APIRouter, Request
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/clawdbot-result")
async def clawdbot_result(request: Request):
    """
    Callback de Clawdbot cuando termina un pedido
    
    Clawdbot puede enviarnos el resultado aquí
    (opcional, también podemos polling al estado)
    """
    
    data = await request.json()
    
    logger.info(f"📥 Resultado de Clawdbot recibido: {data}")
    
    # TODO: Actualizar estado en BD
    
    return {"status": "received"}
