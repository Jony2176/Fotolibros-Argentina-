"""
Servicio de Notificaciones por Telegram
========================================
Envía alertas al admin cuando hay pagos pendientes de verificar.

Configuración:
1. Crear bot con @BotFather en Telegram
2. Obtener TELEGRAM_BOT_TOKEN
3. Obtener tu TELEGRAM_CHAT_ID (envía /start al bot y usa el endpoint /telegram/setup)
"""

import os
import httpx
import html
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def enviar_mensaje_telegram(
    mensaje: str,
    chat_id: Optional[str] = None,
    parse_mode: str = "HTML",
    reply_markup: Optional[dict] = None
) -> bool:
    """
    Envía un mensaje de texto por Telegram.
    """
    if not TELEGRAM_BOT_TOKEN:
        print(f"[Telegram] Bot no configurado. Mensaje simulado: {mensaje[:100]}...")
        return True
    
    target_chat = chat_id or TELEGRAM_CHAT_ID
    if not target_chat:
        print(f"[Telegram] CHAT_ID no configurado. Mensaje simulado: {mensaje[:100]}...")
        return True
    
    try:
        payload = {
            "chat_id": target_chat,
            "text": mensaje,
            "parse_mode": parse_mode
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{TELEGRAM_API_URL}/sendMessage",
                json=payload
            )
            
            if response.status_code == 200:
                print(f"[Telegram] Mensaje enviado correctamente")
                return True
            else:
                print(f"[Telegram] Error: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"[Telegram] Error enviando mensaje: {e}")
        return False


async def notificar_pago_pendiente(
    pedido_id: str,
    nombre_cliente: str,
    email_cliente: str,
    producto: str,
    monto_esperado: float,
    verificacion_ia: dict
) -> bool:
    """
    Notifica al admin sobre un pago pendiente de verificación.
    """
    ia_valido = verificacion_ia.get("valido", False)
    ia_confianza = verificacion_ia.get("confianza", 0)
    ia_monto = verificacion_ia.get("monto_detectado")
    ia_mensaje = verificacion_ia.get("mensaje", "Sin análisis")
    
    # Determinar emoji según resultado
    if ia_valido:
        status_emoji = "✅"
        status_text = "IA APROBÓ"
    elif ia_confianza >= 50:
        status_emoji = "⚠️"
        status_text = "REVISAR"
    else:
        status_emoji = "❌"
        status_text = "SOSPECHOSO"
    
    # Formatear montos de forma segura para evitar errores si son None
    try:
        if ia_monto is not None:
             txt_monto_ia = f"${ia_monto:,.0f}"
        else:
             txt_monto_ia = "No detectado"
    except:
        txt_monto_ia = "Error formato"

    mensaje = f"""
{status_emoji} <b>NUEVO PAGO PENDIENTE</b>

<b>Estado IA:</b> {status_text}
<i>{html.escape(str(ia_mensaje))}</i>

📦 <b>Pedido:</b> <code>{html.escape(pedido_id)[:12]}...</code>
👤 <b>Cliente:</b> {html.escape(nombre_cliente)}
📧 <b>Email:</b> {html.escape(email_cliente)}
🖼️ <b>Producto:</b> {html.escape(producto)}

💰 <b>Monto esperado:</b> ${monto_esperado:,.0f}
💵 <b>Monto detectado:</b> {txt_monto_ia}
📊 <b>Confianza IA:</b> {ia_confianza}%

<b>👉 <a href="http://localhost:3000/admin/pedidos">GESTIONAR EN PANEL ADMIN</a></b>
"""
    
    return await enviar_mensaje_telegram(mensaje.strip())


async def notificar_nuevo_pedido(
    pedido_id: str,
    nombre_cliente: str,
    producto: str,
    total: float
) -> bool:
    """
    Notifica al admin sobre un nuevo pedido.
    """
    mensaje = f"""
🆕 <b>NUEVO PEDIDO</b>

📦 <b>ID:</b> <code>{html.escape(pedido_id)[:12]}...</code>
👤 <b>Cliente:</b> {html.escape(nombre_cliente)}
🖼️ <b>Producto:</b> {html.escape(producto)}
💰 <b>Total:</b> ${total:,.0f}

Esperando comprobante de pago...
"""
    
    return await enviar_mensaje_telegram(mensaje.strip())


async def notificar_pedido_completado(
    pedido_id: str,
    nombre_cliente: str
) -> bool:
    """
    Notifica cuando un pedido se completó exitosamente.
    """
    mensaje = f"""
🎉 <b>PEDIDO COMPLETADO</b>

📦 <b>ID:</b> <code>{html.escape(pedido_id)[:12]}...</code>
👤 <b>Cliente:</b> {html.escape(nombre_cliente)}

El fotolibro fue creado y está listo para enviar.
"""
    
    return await enviar_mensaje_telegram(mensaje.strip())


# Test
if __name__ == "__main__":
    import asyncio
    
    async def test():
        result = await notificar_pago_pendiente(
            pedido_id="test-12345678-abcd",
            nombre_cliente="Juan Pérez",
            email_cliente="juan@test.com",
            producto="Fotolibro 21x21 Tapa Dura",
            monto_esperado=45000,
            verificacion_ia={
                "valido": True,
                "monto_detectado": 45000,
                "confianza": 85,
                "mensaje": "✅ Pago verificado automáticamente"
            }
        )
        print(f"Test result: {result}")
    
    asyncio.run(test())
