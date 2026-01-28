"""
Payment Verification Toolkit - NVIDIA Nemotron Nano VL (GRATIS)
================================================================
Verifica comprobantes de pago usando modelo de visión gratuito.
Soporta BBVA, Ualá, Prex, MercadoPago y otros bancos argentinos.

Modelo: nvidia/nemotron-nano-12b-v2-vl:free
- Especializado en OCR y documentos
- 74% accuracy en OCRBench v2
- Optimizado para comprobantes bancarios
- 100% GRATIS via OpenRouter
"""
import os
import json
import base64
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from agno.tools import tool
from loguru import logger
from decimal import Decimal

# Configuración OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Modelo de visión GRATUITO - NVIDIA Nemotron Nano 12B VL
VISION_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"


class PaymentVerificationToolkit:
    """
    Toolkit para verificar comprobantes de pago bancarios argentinos.
    Usa NVIDIA Nemotron Nano 12B VL (GRATIS via OpenRouter).
    """
    
    # CBU/CVU/Alias destino esperado (configurar en .env)
    CUENTA_DESTINO = {
        "cbu": os.getenv("CUENTA_CBU", ""),
        "cvu": os.getenv("CUENTA_CVU", ""),
        "alias": os.getenv("CUENTA_ALIAS", ""),
    }
    
    # Tolerancia para verificación de monto (5%)
    TOLERANCIA_MONTO = float(os.getenv("TOLERANCIA_MONTO", "0.05"))
    
    # Días máximos de antigüedad del comprobante
    MAX_DIAS_ANTIGUEDAD = int(os.getenv("MAX_DIAS_ANTIGUEDAD", "7"))
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        logger.info(f"🔧 PaymentVerificationToolkit inicializado con modelo: {VISION_MODEL}")
    
    async def _encode_image(self, image_path: str) -> tuple[str, str]:
        """Codifica imagen a base64 y detecta tipo MIME."""
        extension = image_path.lower().split('.')[-1]
        mime_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'webp': 'image/webp',
            'gif': 'image/gif',
        }
        mime_type = mime_types.get(extension, 'image/jpeg')
        
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        return image_data, mime_type
    
    async def _call_vision_api(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Llama a la API de visión de OpenRouter."""
        if not OPENROUTER_API_KEY:
            return {"error": "OPENROUTER_API_KEY no configurada"}
        
        try:
            image_data, mime_type = await self._encode_image(image_path)
            
            payload = {
                "model": VISION_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.1  # Bajo para mayor precisión
            }
            
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://fotolibros.argentina",
                "X-Title": "FotolibrosArgentina"
            }
            
            response = await self.client.post(
                OPENROUTER_API_URL,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            data = response.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            return {
                "success": True,
                "content": content,
                "model": VISION_MODEL,
                "usage": data.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"Error en API de visión: {e}")
            return {"error": str(e), "success": False}
    
    @tool
    async def verificar_comprobante(
        self,
        image_path: str,
        monto_esperado: float,
        pedido_id: str
    ) -> str:
        """
        Verifica un comprobante de pago contra el monto esperado.
        
        Args:
            image_path: Ruta a la imagen del comprobante
            monto_esperado: Monto que debería figurar en el comprobante
            pedido_id: ID del pedido para referencia
            
        Returns:
            JSON con resultado de verificación
        """
        prompt = f"""Analiza este comprobante de pago/transferencia bancaria argentina.

EXTRAE la siguiente información en formato JSON:
{{
    "banco_emisor": "nombre del banco o app (BBVA, Ualá, Prex, MercadoPago, etc.)",
    "monto": número sin símbolos ni puntos de miles,
    "fecha": "DD/MM/YYYY",
    "hora": "HH:MM" o null,
    "destinatario": "nombre o alias del destinatario",
    "cbu_cvu_destino": "número CBU/CVU si es visible" o null,
    "alias_destino": "alias si es visible" o null,
    "numero_operacion": "número de comprobante/referencia" o null,
    "tipo_operacion": "transferencia/pago/deposito",
    "estado": "exitoso/pendiente/rechazado"
}}

IMPORTANTE:
- El monto debe ser un número (ej: 24500, no "$24.500")
- La fecha en formato DD/MM/YYYY
- Si algo no es legible, usa null

Responde SOLO con el JSON, sin explicaciones."""

        result = await self._call_vision_api(image_path, prompt)
        
        if not result.get("success"):
            return json.dumps({
                "verificado": False,
                "error": result.get("error", "Error desconocido"),
                "pedido_id": pedido_id
            })
        
        try:
            # Parsear respuesta del modelo
            content = result["content"]
            # Limpiar posibles backticks de markdown
            content = content.replace("```json", "").replace("```", "").strip()
            datos_comprobante = json.loads(content)
            
            # Verificar monto
            monto_comprobante = float(datos_comprobante.get("monto", 0))
            tolerancia = monto_esperado * self.TOLERANCIA_MONTO
            monto_valido = abs(monto_comprobante - monto_esperado) <= tolerancia
            
            # Verificar cuenta destino
            cuenta_valida = False
            if self.CUENTA_DESTINO["alias"]:
                alias_comprobante = datos_comprobante.get("alias_destino", "").lower()
                cuenta_valida = self.CUENTA_DESTINO["alias"].lower() in alias_comprobante
            
            if not cuenta_valida and self.CUENTA_DESTINO["cbu"]:
                cbu_comprobante = datos_comprobante.get("cbu_cvu_destino", "")
                cuenta_valida = self.CUENTA_DESTINO["cbu"] in str(cbu_comprobante)
            
            # Verificar fecha (no más antigua que MAX_DIAS_ANTIGUEDAD)
            fecha_valida = True
            fecha_str = datos_comprobante.get("fecha")
            if fecha_str:
                try:
                    fecha_comprobante = datetime.strptime(fecha_str, "%d/%m/%Y")
                    dias_diferencia = (datetime.now() - fecha_comprobante).days
                    fecha_valida = dias_diferencia <= self.MAX_DIAS_ANTIGUEDAD
                except ValueError:
                    fecha_valida = False
            
            # Verificar estado
            estado_valido = datos_comprobante.get("estado", "").lower() == "exitoso"
            
            # Resultado final
            verificado = monto_valido and cuenta_valida and fecha_valida and estado_valido
            
            return json.dumps({
                "verificado": verificado,
                "pedido_id": pedido_id,
                "datos_extraidos": datos_comprobante,
                "validaciones": {
                    "monto_valido": monto_valido,
                    "monto_esperado": monto_esperado,
                    "monto_encontrado": monto_comprobante,
                    "cuenta_valida": cuenta_valida,
                    "fecha_valida": fecha_valida,
                    "estado_valido": estado_valido
                },
                "motivo_rechazo": None if verificado else self._generar_motivo_rechazo(
                    monto_valido, cuenta_valida, fecha_valida, estado_valido
                ),
                "modelo_usado": VISION_MODEL,
                "costo": "$0.00"
            })
            
        except json.JSONDecodeError as e:
            return json.dumps({
                "verificado": False,
                "error": f"No se pudo parsear respuesta del modelo: {e}",
                "contenido_raw": result.get("content", ""),
                "pedido_id": pedido_id
            })
    
    def _generar_motivo_rechazo(
        self,
        monto_valido: bool,
        cuenta_valida: bool,
        fecha_valida: bool,
        estado_valido: bool
    ) -> str:
        """Genera mensaje de motivo de rechazo"""
        motivos = []
        if not monto_valido:
            motivos.append("El monto no coincide con el pedido")
        if not cuenta_valida:
            motivos.append("La cuenta destino no coincide")
        if not fecha_valida:
            motivos.append(f"El comprobante tiene más de {self.MAX_DIAS_ANTIGUEDAD} días")
        if not estado_valido:
            motivos.append("La transferencia no fue exitosa")
        return ". ".join(motivos)
    
    @tool
    async def detectar_banco(self, image_path: str) -> str:
        """
        Detecta el banco o app del comprobante.
        
        Args:
            image_path: Ruta a la imagen del comprobante
            
        Returns:
            JSON con banco detectado
        """
        prompt = """Identifica de qué banco o aplicación financiera argentina es este comprobante.

Opciones comunes:
- BBVA Argentina
- Banco Santander
- Banco Galicia
- Banco Nación
- Banco Provincia
- Brubank
- Ualá
- Prex
- MercadoPago
- Naranja X
- Personal Pay
- Otro (especificar)

Responde SOLO con JSON:
{
    "banco": "nombre del banco/app",
    "confianza": "alta/media/baja"
}"""

        result = await self._call_vision_api(image_path, prompt)
        
        if not result.get("success"):
            return json.dumps({"error": result.get("error")})
        
        try:
            content = result["content"].replace("```json", "").replace("```", "").strip()
            datos = json.loads(content)
            datos["modelo_usado"] = VISION_MODEL
            datos["costo"] = "$0.00"
            return json.dumps(datos)
        except:
            return json.dumps({
                "banco": "No detectado",
                "confianza": "baja",
                "raw": result.get("content", "")
            })
    
    @tool
    async def extraer_monto(self, image_path: str) -> str:
        """
        Extrae solo el monto del comprobante (verificación rápida).
        
        Args:
            image_path: Ruta a la imagen del comprobante
            
        Returns:
            JSON con monto extraído
        """
        prompt = """Extrae SOLO el monto de esta transferencia/comprobante.

Responde SOLO con JSON:
{
    "monto": número sin símbolos (ej: 24500),
    "moneda": "ARS" o "USD"
}"""

        result = await self._call_vision_api(image_path, prompt)
        
        if not result.get("success"):
            return json.dumps({"error": result.get("error")})
        
        try:
            content = result["content"].replace("```json", "").replace("```", "").strip()
            datos = json.loads(content)
            datos["modelo_usado"] = VISION_MODEL
            datos["costo"] = "$0.00"
            return json.dumps(datos)
        except:
            # Intentar extraer número del texto
            import re
            numeros = re.findall(r'[\d.,]+', result.get("content", ""))
            if numeros:
                monto_str = numeros[0].replace(".", "").replace(",", ".")
                try:
                    return json.dumps({
                        "monto": float(monto_str),
                        "moneda": "ARS",
                        "modelo_usado": VISION_MODEL,
                        "costo": "$0.00"
                    })
                except:
                    pass
            return json.dumps({"error": "No se pudo extraer monto"})
    
    @tool
    async def extraer_datos_completos(self, image_path: str) -> str:
        """
        Extrae TODOS los datos visibles del comprobante sin validación.
        Útil para debugging o registro.
        
        Args:
            image_path: Ruta a la imagen del comprobante
            
        Returns:
            JSON con todos los datos extraídos
        """
        prompt = """Extrae TODA la información visible de este comprobante de pago argentino.

Incluye:
- Banco/App emisor
- Fecha y hora
- Monto
- Tipo de operación
- Datos del origen (nombre, CBU/CVU)
- Datos del destino (nombre, alias, CBU/CVU)
- Número de operación/referencia
- Estado de la operación
- Cualquier otro dato visible

Responde en JSON con todos los campos que puedas identificar."""

        result = await self._call_vision_api(image_path, prompt)
        
        if not result.get("success"):
            return json.dumps({"error": result.get("error")})
        
        try:
            content = result["content"].replace("```json", "").replace("```", "").strip()
            datos = json.loads(content)
            return json.dumps({
                "success": True,
                "datos": datos,
                "modelo_usado": VISION_MODEL,
                "costo": "$0.00"
            })
        except:
            return json.dumps({
                "success": True,
                "datos_raw": result.get("content", ""),
                "modelo_usado": VISION_MODEL,
                "costo": "$0.00"
            })
    
    async def close(self):
        """Cierra el cliente HTTP"""
        await self.client.aclose()
    
    def get_tools(self) -> List:
        """Retorna todas las herramientas para AGNO."""
        return [
            self.verificar_comprobante,
            self.detectar_banco,
            self.extraer_monto,
            self.extraer_datos_completos,
        ]


# Instancia singleton
payment_toolkit = PaymentVerificationToolkit()


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  Payment Verification Toolkit - NVIDIA Nemotron Nano VL      ║
╠══════════════════════════════════════════════════════════════╣
║  Modelo: {VISION_MODEL:<43} ║
║  Costo: GRATIS ($0.00 por verificación)                      ║
║                                                              ║
║  Características:                                            ║
║  • Especializado en OCR y documentos                         ║
║  • 74% accuracy en OCRBench v2                               ║
║  • Arquitectura híbrida Transformer-Mamba                    ║
║  • Optimizado para comprobantes bancarios argentinos         ║
║                                                              ║
║  Herramientas disponibles:                                   ║
║  • verificar_comprobante() - Verificación completa           ║
║  • detectar_banco() - Identifica banco emisor                ║
║  • extraer_monto() - Extrae solo el monto                    ║
║  • extraer_datos_completos() - Todos los datos visibles      ║
╚══════════════════════════════════════════════════════════════╝
""")
