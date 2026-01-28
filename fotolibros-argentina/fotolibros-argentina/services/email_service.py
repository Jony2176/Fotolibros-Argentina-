"""
Servicio de Email - PIKSY
==========================
Envía emails a clientes en momentos clave:
1. Pedido recibido (confirmación)
2. Pedido enviado (tracking)

Usa SMTP con configuración por variables de entorno.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Configuración SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "hola@fotolibros-argentina.com")
EMPRESA_NOMBRE = "PIKSY - Fotolibros Argentina"


def _enviar_email(to: str, subject: str, html_body: str) -> bool:
    """Envía un email usando SMTP"""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"[Email] SMTP no configurado. Email simulado a {to}: {subject}")
        return True  # Simular éxito si no hay SMTP configurado
    
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{EMPRESA_NOMBRE} <{SMTP_FROM}>"
        msg["To"] = to
        
        msg.attach(MIMEText(html_body, "html"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, to, msg.as_string())
        
        print(f"[Email] Enviado a {to}: {subject}")
        return True
        
    except Exception as e:
        print(f"[Email] Error enviando a {to}: {e}")
        return False


# ============================================================
# TEMPLATES DE EMAIL
# ============================================================

def _template_base(content: str) -> str:
    """Template base con estilos"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 0; background: #f5f5f5; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); color: white; padding: 30px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 28px; }}
            .content {{ padding: 40px 30px; }}
            .footer {{ background: #f8f9fa; padding: 20px 30px; text-align: center; color: #666; font-size: 12px; }}
            .btn {{ display: inline-block; background: #ed8936; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: bold; margin: 20px 0; }}
            .info-box {{ background: #f0f4f8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .tracking-box {{ background: #e6fffa; border: 2px solid #38b2ac; padding: 20px; border-radius: 8px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📸 {EMPRESA_NOMBRE}</h1>
            </div>
            <div class="content">
                {content}
            </div>
            <div class="footer">
                <p>© 2026 {EMPRESA_NOMBRE}. Hecho con ❤️ para tus recuerdos.</p>
                <p>¿Dudas? Contactanos por <a href="https://wa.me/5491155554444">WhatsApp</a></p>
            </div>
        </div>
    </body>
    </html>
    """


# ============================================================
# EMAILS ESPECÍFICOS
# ============================================================

def enviar_email_pedido_recibido(
    email_cliente: str,
    nombre_cliente: str,
    pedido_id: str,
    producto: str,
    total: float,
    metodo_pago: str
):
    """
    Email 1: Confirmación de pedido recibido
    """
    descuento_msg = ""
    if metodo_pago == "transferencia":
        descuento_msg = "<p style='color:#38a169;font-weight:bold;'>🎉 ¡Aplicaste el 15% de descuento por transferencia!</p>"
    
    content = f"""
    <h2>¡Hola {nombre_cliente}! 👋</h2>
    <p>Recibimos tu pedido y ya estamos trabajando en él.</p>
    
    <div class="info-box">
        <p><strong>📦 Número de pedido:</strong> {pedido_id[:18]}...</p>
        <p><strong>🖼️ Producto:</strong> {producto}</p>
        <p><strong>💰 Total:</strong> ${total:,.0f}</p>
        <p><strong>💳 Método de pago:</strong> {metodo_pago.capitalize()}</p>
        {descuento_msg}
    </div>
    
    <p>Podés seguir el estado de tu pedido en cualquier momento:</p>
    
    <a href="http://localhost:3000/#status" class="btn">Ver Estado de mi Pedido →</a>
    
    <p style="color:#666;font-size:14px;">
        <strong>¿Qué sigue?</strong><br>
        1. Confirmamos tu pago<br>
        2. Diseñamos tu fotolibro<br>
        3. Lo imprimimos y empaquetamos<br>
        4. Te lo enviamos a tu casa 🚚
    </p>
    """
    
    return _enviar_email(
        to=email_cliente,
        subject=f"✅ Recibimos tu pedido #{pedido_id[:8]}",
        html_body=_template_base(content)
    )


def enviar_email_pedido_enviado(
    email_cliente: str,
    nombre_cliente: str,
    pedido_id: str,
    producto: str,
    direccion: str,
    codigo_seguimiento: Optional[str] = None
):
    """
    Email 2: Pedido enviado - En camino a domicilio
    """
    tracking_html = ""
    if codigo_seguimiento:
        tracking_html = f"""
        <div class="tracking-box">
            <p style="margin:0;color:#285e61;font-weight:bold;">📍 Código de seguimiento</p>
            <p style="font-size:24px;margin:10px 0;letter-spacing:2px;">{codigo_seguimiento}</p>
            <a href="https://www.correoargentino.com.ar/formularios/ondnc" target="_blank" style="color:#319795;">Rastrear en Correo Argentino</a>
        </div>
        """
    
    content = f"""
    <h2>¡{nombre_cliente}, tu fotolibro está en camino! 🎉</h2>
    
    <p>¡Gran noticia! Tu fotolibro ya salió de nuestra imprenta y va rumbo a tu casa.</p>
    
    <div class="info-box">
        <p><strong>📦 Pedido:</strong> {pedido_id[:18]}...</p>
        <p><strong>🖼️ Producto:</strong> {producto}</p>
        <p><strong>📍 Dirección de entrega:</strong><br>{direccion}</p>
    </div>
    
    {tracking_html}
    
    <p><strong>⏱️ Tiempo estimado:</strong> 3-5 días hábiles</p>
    
    <p style="color:#666;font-size:14px;">
        Recordá que alguien debe recibir el paquete en el domicilio.<br>
        Si no hay nadie, el correo dejará un aviso de visita.
    </p>
    
    <a href="http://localhost:3000/#status" class="btn">Ver Estado del Envío →</a>
    
    <p style="margin-top:30px;">¡Gracias por confiar en nosotros! 💙</p>
    """
    
    return _enviar_email(
        to=email_cliente,
        subject=f"🚚 ¡Tu fotolibro está en camino!",
        html_body=_template_base(content)
    )


def enviar_email_pago_pendiente_admin(
    pedido_id: str,
    nombre_cliente: str,
    email_cliente: str,
    producto: str,
    monto_esperado: float,
    verificacion_ia: dict
):
    """
    Email 3: Notificación al admin de pago pendiente de verificación
    """
    admin_email = os.getenv("SMTP_USER", "")  # El admin recibe en su mismo email
    
    if not admin_email:
        print(f"[Email] SMTP no configurado. Notificación admin simulada para pedido {pedido_id}")
        return True
    
    # Determinar color según resultado IA
    ia_valido = verificacion_ia.get("valido", False)
    ia_confianza = verificacion_ia.get("confianza", 0)
    ia_monto = verificacion_ia.get("monto_detectado")
    ia_mensaje = verificacion_ia.get("mensaje", "Sin análisis")
    
    if ia_valido:
        status_color = "#38a169"  # verde
        status_icon = "✅"
        status_text = "LA IA APROBÓ ESTE COMPROBANTE"
    elif ia_confianza >= 50:
        status_color = "#d69e2e"  # amarillo
        status_icon = "⚠️"
        status_text = "REQUIERE REVISIÓN MANUAL"
    else:
        status_color = "#e53e3e"  # rojo
        status_icon = "❌"
        status_text = "COMPROBANTE SOSPECHOSO"
    
    content = f"""
    <h2>{status_icon} Nuevo pago pendiente de verificación</h2>
    
    <div style="background:{status_color}20; border:2px solid {status_color}; padding:15px; border-radius:8px; margin:20px 0;">
        <p style="font-weight:bold; color:{status_color}; margin:0;">{status_text}</p>
        <p style="margin:5px 0 0 0; color:#333;">{ia_mensaje}</p>
    </div>
    
    <div class="info-box">
        <p><strong>📦 Pedido:</strong> {pedido_id[:18]}...</p>
        <p><strong>👤 Cliente:</strong> {nombre_cliente} ({email_cliente})</p>
        <p><strong>🖼️ Producto:</strong> {producto}</p>
        <p><strong>💰 Monto esperado:</strong> ${monto_esperado:,.0f}</p>
        <p><strong>💵 Monto detectado:</strong> ${ia_monto:,.0f if ia_monto else 'No detectado'}</p>
        <p><strong>📊 Confianza IA:</strong> {ia_confianza}%</p>
    </div>
    
    <p style="font-weight:bold; color:#1a365d;">📱 Próximo paso:</p>
    <ol style="color:#666;">
        <li>Abrí tu app de <strong>BBVA / Prex / Ualá</strong></li>
        <li>Verificá que el pago de ${monto_esperado:,.0f} está acreditado</li>
        <li>Si está OK, confirmá en el <a href="http://localhost:3000/#admin" style="color:#ed8936;">Panel Admin</a></li>
    </ol>
    
    <a href="http://localhost:3000/#admin" class="btn">Ir al Panel de Administración →</a>
    """
    
    return _enviar_email(
        to=admin_email,
        subject=f"{status_icon} Pago pendiente - Pedido #{pedido_id[:8]}",
        html_body=_template_base(content)
    )


# ============================================================
# PRUEBA
# ============================================================

if __name__ == "__main__":
    # Test de emails (simula si no hay SMTP configurado)
    print("Testing email service...")
    
    enviar_email_pedido_recibido(
        email_cliente="test@example.com",
        nombre_cliente="Juan Pérez",
        pedido_id="FL-12345678-abcd-efgh",
        producto="Fotolibro 21x21 Tapa Dura",
        total=40800,
        metodo_pago="transferencia"
    )
    
    enviar_email_pedido_enviado(
        email_cliente="test@example.com",
        nombre_cliente="Juan Pérez",
        pedido_id="FL-12345678-abcd-efgh",
        producto="Fotolibro 21x21 Tapa Dura",
        direccion="Av. Pellegrini 1234, Rosario, Santa Fe",
        codigo_seguimiento="CA123456789AR"
    )
    
    print("Done!")
