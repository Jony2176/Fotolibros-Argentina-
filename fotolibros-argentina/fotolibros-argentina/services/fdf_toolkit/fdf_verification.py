import base64
import httpx
from playwright.async_api import Page


class GeminiVisionVerifier:
    """Verificador visual usando Gemini via OpenRouter"""
    
    def __init__(self, api_key: str, model: str = "google/gemini-2.0-flash-001"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
    
    async def verify_photo_placement(
        self,
        page: Page,
        slot_description: str
    ) -> dict:
        """
        Verifica si una foto fue colocada correctamente en un slot.
        """
        # Capturar screenshot
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        
        prompt = f"""Analiza esta captura de pantalla de un editor de fotolibros.

Tarea: Verificar si hay una foto correctamente posicionada en {slot_description}.

Responde EXACTAMENTE en este formato JSON:
{{
    "foto_presente": true/false,
    "bien_posicionada": true/false,
    "confianza": 0.0-1.0,
    "observaciones": "breve descripción"
}}

Solo responde con el JSON."""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json", 
                        "HTTP-Referer": "https://fotolibros.ar",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{screenshot_b64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        # Enable reasoning just in case
                        "thinking": { "type": "enabled", "budget_tokens": 1024 },
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                result = response.json()
                if "choices" not in result:
                    return {"success": False, "error": f"API Error: {result}"}
                    
                content = result["choices"][0]["message"]["content"]
                
                # Parsear respuesta JSON
                import json
                import re
                
                # Extraer JSON si hay texto alrededor
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    verification = json.loads(json_match.group())
                    return {
                        "success": verification.get("foto_presente", False) and verification.get("bien_posicionada", False),
                        "confidence": verification.get("confianza", 0.0),
                        "details": verification.get("observaciones", "")
                    }
                else:
                     return {"success": False, "error": "No JSON found in response"}
                     
            except Exception as e:
                return {
                    "success": False,
                    "confidence": 0.0,
                    "details": f"Error parseando respuesta: {str(e)}"
                }
    
    async def detect_slot_position(
        self,
        page: Page,
        slot_description: str
    ) -> dict:
        """
        Detecta la posición de un slot usando visión.
        """
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport['width'] if viewport else 1280
        h = viewport['height'] if viewport else 720
        
        prompt = f"""Analiza esta captura de un editor de fotolibros.
Dimensiones: {w}x{h} píxeles.

Encuentra el slot de foto descrito como: "{slot_description}"

Responde EXACTAMENTE en este formato JSON con las coordenadas en píxeles:
{{
    "encontrado": true/false,
    "x": número (borde izquierdo),
    "y": número (borde superior),
    "width": número,
    "height": número,
    "center_x": número,
    "center_y": número
}}"""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{screenshot_b64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "thinking": { "type": "enabled", "budget_tokens": 1024 },
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                
                result = response.json()
                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
                    import json
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        return json.loads(json_match.group())
            except:
                pass
        
        return {"encontrado": False}
    
    async def find_element_to_click(
        self,
        page: Page,
        element_description: str,
        max_retries: int = 3
    ) -> dict:
        """
        Encuentra un elemento clickeable en la pagina usando vision.
        Retorna las coordenadas donde hacer click.
        Incluye retry con backoff para manejar rate limiting.
        """
        import asyncio as aio
        
        for attempt in range(max_retries):
            if attempt > 0:
                wait_time = 2 + attempt  # Modelo pago: 3, 4, 5 seconds
                print(f"[Vision] Retry {attempt + 1}/{max_retries} despues de {wait_time}s...")
                await aio.sleep(wait_time)
            
            try:
                # Capturar screenshot en cada intento
                screenshot_bytes = await page.screenshot()
                screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                
                viewport = page.viewport_size
                w = viewport['width'] if viewport else 1920
                h = viewport['height'] if viewport else 1080
                
                prompt = f"""Analiza esta captura de pantalla de una pagina web.
Dimensiones de la pantalla: {w}x{h} pixeles.

TAREA: Encuentra el elemento descrito como: "{element_description}"

Busca botones, links, iconos, imagenes de productos, o cualquier elemento interactivo que coincida con la descripcion.

Responde EXACTAMENTE en este formato JSON:
{{
    "encontrado": true/false,
    "descripcion_encontrada": "que encontraste exactamente",
    "x": numero (coordenada X del centro del elemento),
    "y": numero (coordenada Y del centro del elemento),
    "confianza": 0.0-1.0,
    "alternativas": ["descripcion de otros elementos similares si los hay"]
}}

IMPORTANTE: Las coordenadas deben ser numeros enteros en pixeles, relativas a la esquina superior izquierda de la pantalla.
Si no encuentras el elemento, pon encontrado: false y sugiere que podria estar buscando."""

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://fotolibros.ar",
                        },
                        json={
                            "model": self.model,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/png;base64,{screenshot_b64}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            "max_tokens": 1500,
                            "temperature": 0.1
                        },
                        timeout=45.0
                    )
                    
                    result = response.json()
                    
                    # Check for rate limiting
                    if "error" in result:
                        error_msg = str(result.get("error", ""))
                        if "429" in error_msg or "rate" in error_msg.lower():
                            print(f"[Vision] Rate limited, will retry...")
                            continue
                        print(f"[Vision] API Error: {result}")
                        return {"encontrado": False, "error": str(result)}
                    
                    if "choices" not in result:
                        print(f"[Vision] No choices in response: {result}")
                        continue
                        
                    content = result["choices"][0]["message"]["content"]
                    
                    # Parsear JSON
                    import json
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        data = json.loads(json_match.group())
                        print(f"[Vision] Encontrado: {data.get('descripcion_encontrada', 'N/A')} en ({data.get('x')}, {data.get('y')})")
                        return data
                    else:
                        print(f"[Vision] No se pudo parsear JSON de: {content[:200]}")
                        return {"encontrado": False, "error": "No JSON in response"}
                        
            except Exception as e:
                print(f"[Vision] Error en intento {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    continue  # Retry
                return {"encontrado": False, "error": str(e)}
        
        return {"encontrado": False, "error": "Max retries exceeded"}
    
    async def describe_page(self, page: Page) -> dict:
        """
        Describe el contenido actual de la pagina para entender donde estamos.
        """
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        
        prompt = """Analiza esta captura de pantalla y describe:

1. Que tipo de pagina es (login, catalogo de productos, editor, checkout, etc.)
2. Que elementos interactivos principales ves (botones, menus, formularios)
3. Si es una pagina de productos, lista los productos visibles
4. Si hay algun mensaje de error o alerta visible

Responde en formato JSON:
{
    "tipo_pagina": "string",
    "elementos_principales": ["lista de elementos"],
    "productos_visibles": ["lista si aplica"],
    "alertas_errores": ["lista si hay"],
    "siguiente_accion_sugerida": "que deberia hacer el usuario"
}"""

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://fotolibros.ar",
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:image/png;base64,{screenshot_b64}"
                                        }
                                    }
                                ]
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.1
                    },
                    timeout=45.0
                )
                
                result = response.json()
                if "choices" in result:
                    content = result["choices"][0]["message"]["content"]
                    import json
                    import re
                    json_match = re.search(r'\{[\s\S]*\}', content)
                    if json_match:
                        return json.loads(json_match.group())
            except Exception as e:
                print(f"[Vision] Error describiendo pagina: {e}")
        
        return {"tipo_pagina": "desconocido", "error": "No se pudo analizar"}
