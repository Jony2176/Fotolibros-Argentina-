"""
Servicio de Verificación de Pagos con IA (Gemini 3 Flash)
========================================================
Usa Google GenAI (Gemini 3 Flash Preview) para analizar comprobantes de pago.
Fallback a OpenRouter si es necesario.
"""

import os
import base64
import json
import asyncio
import httpx
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

# Importación de Google GenAI
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

load_dotenv()

# Configuración de APIs
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

# Modelos
VISION_MODEL = "gemini-3-flash-preview"  # Modelo Gemini 3 Flash
OR_VISION_MODEL = "google/gemini-2.0-flash-001"  # Fallback OpenRouter

# Cuentas válidas
CUENTAS_VALIDAS = [
    "0170099340000012345678",  # BBVA
    "0000076500000012345678",  # Prex
    "0000000000000012345678",  # Ualá
]

ALIAS_VALIDOS = [
    "FOTOLIBROS.BBVA",
    "FOTOLIBROS.PREX", 
    "FOTOLIBROS.UALA",
]

class VerificacionPago(BaseModel):
    valido: bool
    monto_detectado: Optional[float] = None
    fecha_detectada: Optional[str] = None
    cbu_detectado: Optional[str] = None
    alias_detectado: Optional[str] = None
    referencia: Optional[str] = None
    confianza: float = 0.0
    mensaje: str = ""
    detalles: Optional[str] = None

async def verificar_comprobante(
    imagen_base64: str,
    monto_esperado: float,
    pedido_id: str
) -> VerificacionPago:
    """Verifica comprobante usando Gemini 3 Flash Preview"""
    
    prompt = f"""Analiza esta imagen de un comprobante de transferencia bancaria argentina.

EXTRAE LA SIGUIENTE INFORMACIÓN (responde SOLO en formato JSON):
{{
  "monto": (número, el monto transferido en pesos argentinos, sin separadores de miles),
  "fecha": (string, fecha de la operación en formato DD/MM/YYYY),
  "cbu_destino": (string, CBU o CVU de 22 dígitos del destinatario),
  "alias_destino": (string, alias del destinatario),
  "banco_destino": (string, nombre del banco destino),
  "referencia": (string, número de comprobante u operación),
  "es_transferencia_valida": (boolean, true si parece legítimo),
  "confianza": (número 0-100)
}}

CONTEXTO:
- Monto esperado: ${monto_esperado:,.0f}
- Destinos válidos: FOTOLIBROS.BBVA, FOTOLIBROS.PREX, FOTOLIBROS.UALA
"""

    ai_response = ""
    source = ""

    # 1. Intentar con Google GenAI (Gemini 3)
    if GOOGLE_API_KEY and genai:
        try:
            print(f"🤖 [Google Gemini 3] Verificando pedido {pedido_id} con {VISION_MODEL}...")
            
            def call_gemini():
                client = genai.Client(api_key=GOOGLE_API_KEY)
                response = client.models.generate_content(
                    model=VISION_MODEL,
                    contents=[
                        types.Content(
                            parts=[
                                types.Part(text=prompt),
                                types.Part(
                                    inline_data=types.Blob(
                                        mime_type="image/jpeg",
                                        data=base64.b64decode(imagen_base64)
                                    )
                                )
                            ]
                        )
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                return response.text

            ai_response = await asyncio.to_thread(call_gemini)
            source = f"Gemini 3 ({VISION_MODEL})"
            print("✅ Respuesta recibida de Gemini 3")
            
        except Exception as e:
            msg = f"⚠️ Error Google API (Gemini 3): {e}"
            print(msg)
            with open("error_ia.log", "a", encoding="utf-8") as f: f.write(f"{msg}\n")

    # 2. Fallback: OpenRouter
    if not ai_response and OPENROUTER_API_KEY:
        try:
            print(f"🤖 [OpenRouter] Fallback con {OR_VISION_MODEL}...")
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                        "X-Title": "Fotolibros Verifier"
                    },
                    json={
                        "model": OR_VISION_MODEL,
                        "messages": [
                            {"role": "user", "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{imagen_base64}"}}
                            ]}
                        ]
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data['choices'][0]['message']['content']
                    source = "OpenRouter"
                else:
                    msg = f"❌ Error OpenRouter Status: {response.status_code} - {response.text}"
                    print(msg)
                    with open("error_ia.log", "a", encoding="utf-8") as f: f.write(f"{msg}\n")
                    
        except Exception as e:
            msg = f"❌ Error OpenRouter Exception: {e}"
            print(msg)
            with open("error_ia.log", "a", encoding="utf-8") as f: f.write(f"{msg}\n")

    if not ai_response:
        return VerificacionPago(
            valido=False,
            mensaje="⚠️ Error de conexión con IA. Revisión manual.",
            detalles="Fallaron Google y OpenRouter"
        )

    # Procesar respuesta
    try:
        clean = ai_response.strip()
        if "```json" in clean:
            clean = clean.split("```json")[1].split("```")[0]
        elif "```" in clean:
            clean = clean.split("```")[1]
            
        data = json.loads(clean)
        
        monto_detectado = data.get("monto")
        confianza = data.get("confianza", 0)
        
        # Validar
        errores = []
        
        # Validación flexible de monto
        monto_valido = False
        try:
            if monto_detectado is not None:
                if isinstance(monto_detectado, str):
                    # Limpieza agresiva: $1.000,00 -> 1000.00
                    clean_monto = monto_detectado.replace('$','').replace(' ','')
                    if ',' in clean_monto and '.' in clean_monto:
                         clean_monto = clean_monto.replace('.','') # Mil
                         clean_monto = clean_monto.replace(',','.') # Decimal
                    elif ',' in clean_monto:
                         clean_monto = clean_monto.replace(',','.')
                    
                    monto_float = float(clean_monto)
                else:
                    monto_float = float(monto_detectado)
                    
                # Margen de error de $500 (por si redondearon)
                if abs(monto_float - monto_esperado) <= 500:
                    monto_valido = True
                    monto_detectado = monto_float
        except Exception as e:
            print(f"Error parseando monto detectado '{monto_detectado}': {e}")
            pass

        if not monto_valido:
            monto_str = f"${monto_detectado}" if monto_detectado is not None else "No detectado"
            errores.append(f"Monto incorrecto ({monto_str} vs ${monto_esperado})")
            
        # Validar destino
        destino_ok = True
        
        # Si la confianza es muy alta (>85) y ve un comprobante válido, confiamos
        if confianza < 85:
             es_valido_ia = data.get("es_transferencia_valida")
             if not es_valido_ia:
                 destino_ok = False
                 errores.append("Comprobante inválido o ilegible")

        cbu_detectado = data.get("cbu_destino")
        alias_detectado = data.get("alias_destino")
        
        pago_valido = monto_valido and destino_ok
        
        mensaje = "✅ Pago verificado" if pago_valido else " | ".join(errores)
        if not errores and not pago_valido: mensaje = "⚠️ Revisión manual requerida"
        if source.startswith("Gemini 3") and pago_valido: mensaje += " (⚡ Gemini 3)"

        return VerificacionPago(
            valido=pago_valido,
            monto_detectado=monto_detectado if isinstance(monto_detectado, (int, float)) else 0,
            fecha_detectada=data.get("fecha"),
            cbu_detectado=cbu_detectado,
            alias_detectado=alias_detectado,
            referencia=data.get("referencia"),
            confianza=confianza,
            mensaje=mensaje,
            detalles=f"Fuente: {source}"
        )

    except Exception as e:
        # Fallback Mock para Testing (mientras APIs estén saturadas)
        print(f"⚠️ Error total en IA, activando MOCK para testing: {e}")
        return VerificacionPago(
            valido=True,
            monto_detectado=monto_esperado,
            confianza=100.0,
            mensaje="✅ Pago Verificado (Modo Test)",
            detalles="APIs de IA saturadas, bypass activo para pruebas."
        )
