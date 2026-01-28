"""
Payment Verification Toolkit - Versión OpenRouter FREE
=======================================================
Verifica comprobantes de pago usando NVIDIA Nemotron Nano 12B VL (GRATIS).
Soporta BBVA, Ualá y Prex.

Modelo: nvidia/nemotron-nano-12b-v2-vl:free
- Especializado en OCR y documentos
- 74% accuracy en OCRBench v2
- Optimizado para charts, tablas y comprobantes
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

# Configuración OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# Modelo de visión GRATUITO - NVIDIA Nemotron Nano 12B VL
# Especializado en OCR, documentos y comprensión visual
VISION_MODEL = "nvidia/nemotron-nano-12b-v2-vl:free"


class PaymentVerificationToolkit:
    """
    Toolkit para verificar comprobantes de pago bancarios argentinos
    usando NVIDIA Nemotron Nano 12B VL (GRATIS via OpenRouter).
    
    Características del modelo:
    - 12B parámetros optimizados para visión
    - Arquitectura híbrida Transformer-Mamba
    - Líder en OCRBench v2 (~74% accuracy)
    - Excelente para documentos, charts y comprobantes
    """
    
    # CBU/CVU/Alias destino esperado (configurar en .env)
    CUENTA_DESTINO = {
        "cbu": os.getenv("CUENTA_CBU", "0110000000000000000000"),
        "cvu": os.getenv("CUENTA_CVU", "0000003100000000000000"),
        "alias": os.getenv("CUENTA_ALIAS", "fotolibros.arg"),
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
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Detectar tipo de imagen por extensión
        ext = image_path.lower().split(".")[-1]
        mime_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
            "gif": "image/gif",
        }
        media_type = mime_types.get(ext, "image/png")
        
        return base64.standard_b64encode(image_data).decode("utf-8"), media_type
    
    async def _encode_image_from_bytes(self, image_bytes: bytes, filename: str = "image.png") -> tuple[str, str]:
        """Codifica bytes de imagen a base64."""
        ext = filename.lower().split(".")[-1]
        mime_types = {
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "webp": "image/webp",
        }
        media_type = mime_types.get(ext, "image/png")
        
        return base64.standard_b64encode(image_bytes).decode("utf-8"), media_type
    
    async def _call_vision_model(
        self, 
        image_base64: str, 
        media_type: str,
        prompt: str
    ) -> Dict[str, Any]:
        """
        Llama a NVIDIA Nemotron Nano 12B VL via OpenRouter.
        
        Este modelo está especializado en:
        - OCR (Optical Character Recognition)
        - Comprensión de documentos
        - Análisis de charts y tablas
        - Razonamiento visual
        """
        
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY no configurada")
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://fotolibros.ar",
            "X-Title": "Fotolibros Argentina - Payment Verification"
        }
        
        payload = {
            "model": VISION_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{media_type};base64,{image_base64}"
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 1024,
            "temperature": 0.1  # Bajo para respuestas consistentes en OCR
        }
        
        logger.info(f"🔍 Llamando a {VISION_MODEL}...")
        
        response = await self.client.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            error_text = response.text
            logger.error(f"❌ Error OpenRouter API: {response.status_code} - {error_text}")
            raise Exception(f"OpenRouter API error: {response.status_code} - {error_text}")
        
        result = response.json()
        logger.info(f"✅ Respuesta recibida de {VISION_MODEL}")
        
        return result
    
    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parsea la respuesta JSON del modelo, limpiando formato."""
        content = content.strip()
        
        # Remover bloques de código markdown si existen
        if content.startswith("```"):
            lines = content.split("\n")
            # Encontrar inicio y fin del bloque de código
            start_idx = 1 if lines[0].startswith("```") else 0
            end_idx = len(lines)
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].strip() == "```":
                    end_idx = i
                    break
            content = "\n".join(lines[start_idx:end_idx])
        
        # Remover prefijo "json" si existe
        if content.lower().startswith("json"):
            content = content[4:].strip()
        
        return json.loads(content)
    
    @tool
    async def verificar_comprobante(
        self,
        image_path: str,
        monto_esperado: float,
        pedido_id: int
    ) -> str:
        """
        Verifica un comprobante de pago usando NVIDIA Nemotron Nano 12B VL (GRATIS).
        
        Extrae y valida:
        - Banco emisor (BBVA, Ualá, Prex, MercadoPago)
        - Monto transferido (con tolerancia del 5%)
        - Cuenta destino (CBU/CVU/Alias)
        - Fecha de transferencia (máximo 7 días)
        - Número de operación/referencia
        
        Args:
            image_path: Ruta a la imagen del comprobante
            monto_esperado: Monto que debería aparecer en el comprobante
            pedido_id: ID del pedido para logging
            
        Returns:
            JSON con resultado de verificación
        """
        try:
            # Codificar imagen
            image_base64, media_type = await self._encode_image(image_path)
            
            # Prompt optimizado para Nemotron (especializado en OCR)
            prompt = f"""Analiza este comprobante de transferencia bancaria argentina.

EXTRAE la siguiente información y responde ÚNICAMENTE con un JSON válido:

{{
    "banco_detectado": "bbva" | "uala" | "prex" | "mercadopago" | "otro" | "no_detectado",
    "es_comprobante_valido": true | false,
    "fecha_transferencia": "YYYY-MM-DD" | null,
    "monto": <número decimal sin separadores de miles> | null,
    "moneda": "ARS" | "USD",
    "cuenta_destino": {{
        "tipo": "cbu" | "cvu" | "alias" | "no_detectado",
        "valor": "<string>" | null
    }},
    "referencia_operacion": "<string>" | null,
    "nombre_beneficiario": "<string>" | null,
    "estado_transferencia": "exitosa" | "pendiente" | "rechazada" | "no_detectado",
    "observaciones": "<cualquier detalle relevante>"
}}

REGLAS IMPORTANTES:
1. Si NO es un comprobante de transferencia válido, marca es_comprobante_valido: false
2. El monto debe ser un número SIN puntos de miles (ej: 15000.00, NO 15.000,00)
3. Si algún campo no es visible o legible, usa null
4. La cuenta destino esperada es Alias: "{self.CUENTA_DESTINO['alias']}"
5. Responde ÚNICAMENTE con el JSON, sin explicaciones ni markdown"""
            
            # Llamar al modelo de visión
            response = await self._call_vision_model(image_base64, media_type, prompt)
            
            # Extraer contenido de la respuesta
            content = response["choices"][0]["message"]["content"]
            
            # Parsear JSON
            try:
                datos = self._parse_json_response(content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ Error parseando JSON: {e}\nContenido: {content[:500]}")
                return json.dumps({
                    "success": False,
                    "verificado": False,
                    "pedido_id": pedido_id,
                    "error": "No se pudo parsear la respuesta del análisis",
                    "respuesta_raw": content[:500],
                    "modelo": VISION_MODEL,
                    "costo": "$0.00"
                }, ensure_ascii=False)
            
            # Validaciones
            errores = []
            advertencias = []
            
            # 1. ¿Es comprobante válido?
            if not datos.get("es_comprobante_valido"):
                return json.dumps({
                    "success": True,
                    "verificado": False,
                    "pedido_id": pedido_id,
                    "razon": "La imagen no parece ser un comprobante de transferencia válido",
                    "datos_extraidos": datos,
                    "modelo": VISION_MODEL,
                    "costo": "$0.00"
                }, ensure_ascii=False)
            
            # 2. Verificar monto (con tolerancia)
            monto_detectado = datos.get("monto")
            if monto_detectado is not None:
                # Convertir a float si viene como string
                if isinstance(monto_detectado, str):
                    monto_detectado = float(monto_detectado.replace(",", ".").replace(" ", ""))
                
                diferencia = abs(monto_detectado - monto_esperado) / monto_esperado
                if diferencia > self.TOLERANCIA_MONTO:
                    errores.append(
                        f"Monto no coincide: esperado ${monto_esperado:,.2f}, "
                        f"detectado ${monto_detectado:,.2f} (diferencia: {diferencia*100:.1f}%)"
                    )
            else:
                errores.append("No se pudo detectar el monto en el comprobante")
            
            # 3. Verificar cuenta destino
            cuenta_destino = datos.get("cuenta_destino", {})
            if cuenta_destino.get("valor"):
                valor_cuenta = cuenta_destino["valor"].lower().strip()
                alias_esperado = self.CUENTA_DESTINO["alias"].lower()
                cbu_esperado = self.CUENTA_DESTINO["cbu"]
                cvu_esperado = self.CUENTA_DESTINO["cvu"]
                
                cuenta_valida = (
                    valor_cuenta == alias_esperado or
                    valor_cuenta == cbu_esperado or
                    valor_cuenta == cvu_esperado or
                    alias_esperado in valor_cuenta
                )
                
                if not cuenta_valida:
                    errores.append(
                        f"Cuenta destino no coincide: detectado '{cuenta_destino['valor']}', "
                        f"esperado '{self.CUENTA_DESTINO['alias']}'"
                    )
            else:
                advertencias.append("No se pudo verificar la cuenta destino")
            
            # 4. Verificar fecha (no más de X días de antigüedad)
            fecha_str = datos.get("fecha_transferencia")
            if fecha_str:
                try:
                    fecha_transferencia = datetime.strptime(fecha_str, "%Y-%m-%d")
                    dias_antiguedad = (datetime.now() - fecha_transferencia).days
                    
                    if dias_antiguedad > self.MAX_DIAS_ANTIGUEDAD:
                        errores.append(
                            f"Comprobante muy antiguo: {dias_antiguedad} días "
                            f"(máximo permitido: {self.MAX_DIAS_ANTIGUEDAD} días)"
                        )
                    elif dias_antiguedad < 0:
                        advertencias.append("La fecha del comprobante es futura (posible error)")
                except ValueError:
                    advertencias.append(f"Formato de fecha no reconocido: {fecha_str}")
            else:
                advertencias.append("No se pudo detectar la fecha de transferencia")
            
            # 5. Verificar estado de transferencia
            estado = datos.get("estado_transferencia", "no_detectado")
            if estado not in ["exitosa", "no_detectado"]:
                errores.append(f"Estado de transferencia: {estado}")
            
            # Determinar resultado final
            verificado = len(errores) == 0
            
            resultado = {
                "success": True,
                "verificado": verificado,
                "pedido_id": pedido_id,
                "banco_detectado": datos.get("banco_detectado"),
                "monto_esperado": monto_esperado,
                "monto_detectado": monto_detectado,
                "cuenta_destino": cuenta_destino,
                "fecha_transferencia": fecha_str,
                "referencia_operacion": datos.get("referencia_operacion"),
                "estado_transferencia": estado,
                "errores": errores if errores else None,
                "advertencias": advertencias if advertencias else None,
                "datos_completos": datos,
                "modelo": VISION_MODEL,
                "costo": "$0.00"
            }
            
            if verificado:
                logger.info(f"✅ Comprobante VERIFICADO para pedido #{pedido_id}")
            else:
                logger.warning(f"❌ Comprobante RECHAZADO para pedido #{pedido_id}: {errores}")
            
            return json.dumps(resultado, ensure_ascii=False)
            
        except Exception as e:
            logger.error(f"❌ Error verificando comprobante: {e}")
            return json.dumps({
                "success": False,
                "verificado": False,
                "pedido_id": pedido_id,
                "error": str(e),
                "modelo": VISION_MODEL,
                "costo": "$0.00"
            }, ensure_ascii=False)
    
    @tool
    async def detectar_banco(self, image_path: str) -> str:
        """
        Detecta qué banco emitió el comprobante.
        
        Bancos soportados:
        - BBVA Argentina
        - Ualá
        - Prex
        - MercadoPago
        - Otros bancos argentinos
        
        Args:
            image_path: Ruta a la imagen del comprobante
            
        Returns:
            JSON con banco detectado y confianza
        """
        try:
            image_base64, media_type = await self._encode_image(image_path)
            
            prompt = """Identifica el banco o entidad financiera de este comprobante argentino.

Responde ÚNICAMENTE con JSON:
{
    "banco": "bbva" | "uala" | "prex" | "mercadopago" | "santander" | "galicia" | "macro" | "brubank" | "naranja_x" | "otro",
    "nombre_completo": "<nombre oficial del banco>",
    "confianza": "alta" | "media" | "baja",
    "indicadores": ["<lista de elementos visuales que identifican al banco>"]
}"""
            
            response = await self._call_vision_model(image_base64, media_type, prompt)
            content = response["choices"][0]["message"]["content"]
            
            try:
                datos = self._parse_json_response(content)
                datos["modelo"] = VISION_MODEL
                datos["costo"] = "$0.00"
                return json.dumps(datos, ensure_ascii=False)
            except:
                return json.dumps({
                    "banco": "no_detectado",
                    "error": "No se pudo parsear respuesta",
                    "respuesta_raw": content[:300],
                    "modelo": VISION_MODEL,
                    "costo": "$0.00"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "banco": "error",
                "error": str(e),
                "modelo": VISION_MODEL,
                "costo": "$0.00"
            }, ensure_ascii=False)
    
    @tool
    async def extraer_monto(self, image_path: str) -> str:
        """
        Extrae únicamente el monto de un comprobante.
        Útil para verificaciones rápidas.
        
        Args:
            image_path: Ruta a la imagen del comprobante
            
        Returns:
            JSON con monto extraído
        """
        try:
            image_base64, media_type = await self._encode_image(image_path)
            
            prompt = """Extrae el monto principal de esta transferencia/comprobante.

Responde ÚNICAMENTE con JSON:
{
    "monto": <número decimal sin separadores>,
    "moneda": "ARS" | "USD",
    "monto_formateado": "<monto con formato legible>",
    "confianza": "alta" | "media" | "baja"
}

IMPORTANTE: El monto debe ser un número sin puntos de miles (ej: 15000.50, NO 15.000,50)"""
            
            response = await self._call_vision_model(image_base64, media_type, prompt)
            content = response["choices"][0]["message"]["content"]
            
            try:
                datos = self._parse_json_response(content)
                datos["modelo"] = VISION_MODEL
                datos["costo"] = "$0.00"
                return json.dumps(datos, ensure_ascii=False)
            except:
                # Intentar extraer monto del texto
                import re
                numeros = re.findall(r'[\d.,]+', content)
                monto = None
                for n in numeros:
                    try:
                        monto = float(n.replace(".", "").replace(",", "."))
                        break
                    except:
                        continue
                
                return json.dumps({
                    "monto": monto,
                    "moneda": "ARS",
                    "confianza": "baja",
                    "modelo": VISION_MODEL,
                    "costo": "$0.00"
                }, ensure_ascii=False)
                
        except Exception as e:
            return json.dumps({
                "monto": None,
                "error": str(e),
                "modelo": VISION_MODEL,
                "costo": "$0.00"
            }, ensure_ascii=False)
    
    @tool
    async def extraer_datos_completos(self, image_path: str) -> str:
        """
        Extrae TODOS los datos visibles de un comprobante sin validación.
        Útil para debugging o cuando se necesita toda la información.
        
        Args:
            image_path: Ruta a la imagen del comprobante
            
        Returns:
            JSON con todos los datos extraídos
        """
        try:
            image_base64, media_type = await self._encode_image(image_path)
            
            prompt = """Extrae TODA la información visible de este comprobante de transferencia.

Responde ÚNICAMENTE con JSON incluyendo todos los campos que puedas leer:
{
    "tipo_documento": "<tipo de comprobante>",
    "banco_emisor": "<banco o entidad>",
    "fecha": "<fecha visible>",
    "hora": "<hora si visible>",
    "monto": <número>,
    "moneda": "<moneda>",
    "origen": {
        "nombre": "<nombre del remitente>",
        "cuenta": "<número de cuenta origen>",
        "tipo_cuenta": "<tipo>"
    },
    "destino": {
        "nombre": "<nombre del beneficiario>",
        "cuenta": "<CBU/CVU/Alias>",
        "tipo_cuenta": "<tipo>"
    },
    "referencia": "<número de operación>",
    "concepto": "<concepto o descripción>",
    "estado": "<estado de la transferencia>",
    "otros_datos": ["<cualquier otro dato visible>"]
}

Incluye null para campos no visibles."""
            
            response = await self._call_vision_model(image_base64, media_type, prompt)
            content = response["choices"][0]["message"]["content"]
            
            try:
                datos = self._parse_json_response(content)
            except:
                datos = {"raw_response": content}
            
            datos["modelo"] = VISION_MODEL
            datos["costo"] = "$0.00"
            
            return json.dumps(datos, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "modelo": VISION_MODEL,
                "costo": "$0.00"
            }, ensure_ascii=False)
    
    def get_tools(self) -> List:
        """Retorna todas las herramientas como funciones para AGNO."""
        return [
            self.verificar_comprobante,
            self.detectar_banco,
            self.extraer_monto,
            self.extraer_datos_completos,
        ]
    
    async def close(self):
        """Cierra el cliente HTTP."""
        await self.client.aclose()


# Instancia singleton para uso directo
payment_toolkit = PaymentVerificationToolkit()


# ============================================
# Ejemplo de uso standalone
# ============================================
if __name__ == "__main__":
    import asyncio
    
    async def test_verificacion():
        """Test de verificación de comprobante."""
        toolkit = PaymentVerificationToolkit()
        
        # Ejemplo: verificar un comprobante
        resultado = await toolkit.verificar_comprobante(
            image_path="/path/to/comprobante.jpg",
            monto_esperado=15000.00,
            pedido_id=123
        )
        
        print(resultado)
        await toolkit.close()
    
    # Ejecutar test
    # asyncio.run(test_verificacion())
    
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
║  • Optimizado para comprobantes bancarios                    ║
║                                                              ║
║  Herramientas disponibles:                                   ║
║  • verificar_comprobante() - Verificación completa           ║
║  • detectar_banco() - Identifica banco emisor                ║
║  • extraer_monto() - Extrae solo el monto                    ║
║  • extraer_datos_completos() - Todos los datos visibles      ║
╚══════════════════════════════════════════════════════════════╝
""")
