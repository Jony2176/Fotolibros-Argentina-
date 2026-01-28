"""
Notification Toolkit - Fotolibros Argentina
===========================================
Notificaciones por Discord y Email.
"""
import os
import json
import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any
from agno.tools import tool
from loguru import logger

# Configuración
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
EMAIL_FROM = os.getenv("EMAIL_FROM", "notificaciones@fotolibros.ar")


class NotificationToolkit:
    """
    Toolkit para enviar notificaciones por Discord y Email.
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("🔔 NotificationToolkit inicializado")
    
    async def _send_discord_message(self, content: str, embeds: List[Dict] = None) -> bool:
        """Envía mensaje a Discord via webhook."""
        if not DISCORD_WEBHOOK_URL:
            logger.warning("DISCORD_WEBHOOK_URL no configurado")
            return False
        
        try:
            payload = {"content": content}
            if embeds:
                payload["embeds"] = embeds
            
            response = await self.client.post(DISCORD_WEBHOOK_URL, json=payload)
            return response.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error enviando a Discord: {e}")
            return False
    
    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Envía email via SendGrid."""
        if not SENDGRID_API_KEY:
            logger.warning("SENDGRID_API_KEY no configurado, simulando envío")
            logger.info(f"📧 [SIMULADO] Email a {to_email}: {subject}")
            return True
        
        try:
            payload = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": EMAIL_FROM},
                "subject": subject,
                "content": [{"type": "text/html", "value": html_content}]
            }
            
            response = await self.client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json=payload,
                headers={
                    "Authorization": f"Bearer {SENDGRID_API_KEY}",
                    "Content-Type": "application/json"
                }
            )
            return response.status_code in [200, 201, 202]
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    @tool
    async def notificar_nuevo_pedido(
        self,
        numero_pedido: str,
        producto: str,
        cliente_nombre: str,
        monto_total: float
    ) -> str:
        """
        Notifica sobre un nuevo pedido (Discord + Email admin).
        
        Args:
            numero_pedido: Número del pedido
            producto: Nombre del producto
            cliente_nombre: Nombre del cliente
            monto_total: Monto total del pedido
        """
        # Discord
        embed = {
            "title": "🆕 Nuevo Pedido",
            "color": 3447003,  # Azul
            "fields": [
                {"name": "Pedido", "value": numero_pedido, "inline": True},
                {"name": "Cliente", "value": cliente_nombre, "inline": True},
                {"name": "Producto", "value": producto, "inline": False},
                {"name": "Monto", "value": f"${monto_total:,.0f}", "inline": True},
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        discord_ok = await self._send_discord_message("", embeds=[embed])
        
        return json.dumps({
            "success": True,
            "discord": discord_ok,
            "mensaje": f"Notificación enviada para pedido {numero_pedido}"
        })
    
    @tool
    async def notificar_pago_verificado(
        self,
        numero_pedido: str,
        cliente_nombre: str,
        monto: float,
        verificado: bool
    ) -> str:
        """
        Notifica resultado de verificación de pago.
        
        Args:
            numero_pedido: Número del pedido
            cliente_nombre: Nombre del cliente
            monto: Monto verificado
            verificado: Si fue aprobado o rechazado
        """
        titulo = "✅ Pago Verificado" if verificado else "❌ Pago Rechazado"
        color = 5763719 if verificado else 15548997  # Verde o Rojo
        
        embed = {
            "title": titulo,
            "color": color,
            "fields": [
                {"name": "Pedido", "value": numero_pedido, "inline": True},
                {"name": "Cliente", "value": cliente_nombre, "inline": True},
                {"name": "Monto", "value": f"${monto:,.0f}", "inline": True},
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        discord_ok = await self._send_discord_message("", embeds=[embed])
        
        return json.dumps({
            "success": True,
            "discord": discord_ok,
            "verificado": verificado
        })
    
    @tool
    async def notificar_produccion_enviada(
        self,
        numero_pedido: str,
        numero_pedido_grafica: str
    ) -> str:
        """
        Notifica que el pedido fue enviado a la gráfica.
        
        Args:
            numero_pedido: Número de nuestro pedido
            numero_pedido_grafica: Número asignado por la gráfica
        """
        embed = {
            "title": "🏭 En Producción",
            "color": 16776960,  # Amarillo
            "fields": [
                {"name": "Nuestro Pedido", "value": numero_pedido, "inline": True},
                {"name": "Pedido Gráfica", "value": numero_pedido_grafica, "inline": True},
            ],
            "description": "El pedido fue enviado a Fábrica de Fotolibros",
            "timestamp": datetime.now().isoformat()
        }
        
        discord_ok = await self._send_discord_message("", embeds=[embed])
        
        return json.dumps({"success": True, "discord": discord_ok})
    
    @tool
    async def notificar_recibido_domicilio(
        self,
        numero_pedido: str,
        cliente_nombre: str
    ) -> str:
        """
        Notifica que el pedido fue recibido en tu domicilio.
        
        Args:
            numero_pedido: Número del pedido
            cliente_nombre: Nombre del cliente
        """
        embed = {
            "title": "📦 Recibido en Domicilio",
            "color": 10181046,  # Púrpura
            "fields": [
                {"name": "Pedido", "value": numero_pedido, "inline": True},
                {"name": "Cliente", "value": cliente_nombre, "inline": True},
            ],
            "description": "⚠️ **ACCIÓN REQUERIDA:** Preparar envío al cliente",
            "timestamp": datetime.now().isoformat()
        }
        
        discord_ok = await self._send_discord_message("@here Pedido listo para enviar 📦", embeds=[embed])
        
        return json.dumps({"success": True, "discord": discord_ok})
    
    @tool
    async def notificar_enviado_cliente(
        self,
        numero_pedido: str,
        cliente_email: str,
        cliente_nombre: str,
        codigo_seguimiento: str,
        empresa_envio: str
    ) -> str:
        """
        Notifica al cliente que su pedido fue enviado.
        
        Args:
            numero_pedido: Número del pedido
            cliente_email: Email del cliente
            cliente_nombre: Nombre del cliente
            codigo_seguimiento: Código de tracking
            empresa_envio: Empresa de envío
        """
        # Email al cliente
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #1a365d;">¡Tu fotolibro está en camino! 📦</h1>
            <p>Hola {cliente_nombre},</p>
            <p>Tu pedido <strong>{numero_pedido}</strong> ha sido despachado.</p>
            
            <div style="background: #f0f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Empresa de envío:</strong> {empresa_envio}</p>
                <p><strong>Código de seguimiento:</strong> {codigo_seguimiento}</p>
            </div>
            
            <p>Podrás rastrear tu envío con el código proporcionado.</p>
            
            <p style="margin-top: 30px;">
                Gracias por confiar en nosotros,<br>
                <strong>Fotolibros Argentina</strong>
            </p>
        </div>
        """
        
        email_ok = await self._send_email(
            cliente_email,
            f"Tu fotolibro está en camino - Pedido {numero_pedido}",
            html
        )
        
        # Discord
        embed = {
            "title": "🚚 Enviado al Cliente",
            "color": 5763719,  # Verde
            "fields": [
                {"name": "Pedido", "value": numero_pedido, "inline": True},
                {"name": "Cliente", "value": cliente_nombre, "inline": True},
                {"name": "Tracking", "value": codigo_seguimiento, "inline": False},
                {"name": "Envío", "value": empresa_envio, "inline": True},
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        discord_ok = await self._send_discord_message("", embeds=[embed])
        
        return json.dumps({
            "success": True,
            "email": email_ok,
            "discord": discord_ok
        })
    
    @tool
    async def notificar_error(
        self,
        numero_pedido: str,
        tipo_error: str,
        detalle: str
    ) -> str:
        """
        Notifica un error en el sistema.
        
        Args:
            numero_pedido: Número del pedido (si aplica)
            tipo_error: Tipo de error
            detalle: Detalle del error
        """
        embed = {
            "title": "🚨 Error en Sistema",
            "color": 15548997,  # Rojo
            "fields": [
                {"name": "Pedido", "value": numero_pedido or "N/A", "inline": True},
                {"name": "Tipo", "value": tipo_error, "inline": True},
                {"name": "Detalle", "value": detalle[:1000], "inline": False},
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        discord_ok = await self._send_discord_message("@here ⚠️ Error que requiere atención", embeds=[embed])
        
        return json.dumps({"success": True, "discord": discord_ok})
    
    @tool
    async def enviar_email_confirmacion_pedido(
        self,
        cliente_email: str,
        cliente_nombre: str,
        numero_pedido: str,
        producto: str,
        monto_total: float,
        fecha_entrega_estimada: str
    ) -> str:
        """
        Envía email de confirmación de pedido al cliente.
        
        Args:
            cliente_email: Email del cliente
            cliente_nombre: Nombre del cliente
            numero_pedido: Número del pedido
            producto: Nombre del producto
            monto_total: Monto total
            fecha_entrega_estimada: Fecha estimada de entrega
        """
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #1a365d;">¡Gracias por tu pedido! 📸</h1>
            <p>Hola {cliente_nombre},</p>
            <p>Hemos recibido tu pedido correctamente.</p>
            
            <div style="background: #f0f4f8; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h2 style="margin-top: 0; color: #2d3748;">Resumen del Pedido</h2>
                <p><strong>Número de pedido:</strong> {numero_pedido}</p>
                <p><strong>Producto:</strong> {producto}</p>
                <p><strong>Total:</strong> ${monto_total:,.0f}</p>
                <p><strong>Entrega estimada:</strong> {fecha_entrega_estimada}</p>
            </div>
            
            <h3>Próximos pasos:</h3>
            <ol>
                <li>Verificaremos tu pago</li>
                <li>Enviaremos tu fotolibro a producción</li>
                <li>Te notificaremos cuando esté en camino</li>
            </ol>
            
            <p style="margin-top: 30px;">
                Si tenés alguna consulta, respondé a este email.<br><br>
                <strong>Fotolibros Argentina</strong>
            </p>
        </div>
        """
        
        email_ok = await self._send_email(
            cliente_email,
            f"Confirmación de Pedido {numero_pedido} - Fotolibros Argentina",
            html
        )
        
        return json.dumps({"success": True, "email": email_ok})
    
    async def close(self):
        """Cierra el cliente HTTP"""
        await self.client.aclose()
    
    def get_tools(self) -> List:
        """Retorna todas las herramientas para AGNO."""
        return [
            self.notificar_nuevo_pedido,
            self.notificar_pago_verificado,
            self.notificar_produccion_enviada,
            self.notificar_recibido_domicilio,
            self.notificar_enviado_cliente,
            self.notificar_error,
            self.enviar_email_confirmacion_pedido,
        ]


# Instancia singleton
notification_toolkit = NotificationToolkit()
