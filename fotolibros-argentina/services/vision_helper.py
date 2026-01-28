"""
Vision Helper - Asistente de IA para interacciones complejas en Canvas
=======================================================================
Usa Gemini 3 Flash (free tier) para analizar capturas del editor.
Fallback a OpenRouter (Nemotron) si hay problemas de cuota.
"""

import os
import base64
from typing import Optional, List, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

from config.llm_models import GEMINI_API_KEY, OPENROUTER_API_KEY


@dataclass
class AccionCanvas:
    """Representa una acción a realizar en el canvas"""
    tipo: str  # "click", "drag", "type", "scroll"
    x: int
    y: int
    x_destino: Optional[int] = None  # Para drag
    y_destino: Optional[int] = None
    texto: Optional[str] = None  # Para type
    descripcion: str = ""


@dataclass
class AnalisisEditor:
    """Resultado del análisis del editor"""
    pagina_actual: int
    total_paginas: int
    tiene_fotos: bool
    zonas_disponibles: List[dict]  # {x, y, ancho, alto, tipo}
    elementos_detectados: List[str]
    sugerencia: str


class VisionHelper:
    """
    Usa Gemini 3 Flash Preview para analizar el estado del editor.
    - thinking_level: "low" para respuestas rápidas
    - media_resolution: "high" para mejor análisis de imágenes
    - Fallback a OpenRouter (Nemotron) si hay problemas
    """
    
    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        self.openrouter_key = OPENROUTER_API_KEY
        self.use_gemini = bool(self.gemini_key)
    
    def _encode_image(self, image_path: str) -> str:
        """Codifica imagen a base64"""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _get_mime_type(self, image_path: str) -> str:
        """Determina el tipo MIME de la imagen"""
        ext = image_path.lower().split('.')[-1]
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/png')
    
    def _llamar_gemini_3(self, prompt: str, image_path: str) -> str:
        """Llama a Gemini 3 Flash Preview (free tier)"""
        import httpx
        
        image_data = self._encode_image(image_path)
        mime_type = self._get_mime_type(image_path)
        
        # DEBUG VERIFICACIÓN
        print(f"\n🔍 VERIFICACIÓN RUNTIME:")
        print(f"   ► MODELO: gemini-3-flash-preview")
        print(f"   ► API KEY (final): ...{self.gemini_key[-5:] if self.gemini_key else 'NONE'}")
        print("-" * 30)

        response = httpx.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent",
            headers={
                "x-goog-api-key": self.gemini_key,
                "Content-Type": "application/json"
            },
            json={
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": image_data
                            },
                            "mediaResolution": {"level": "media_resolution_high"}
                        }
                    ]
                }],
                "generationConfig": {
                    "thinkingConfig": {
                        "thinkingLevel": "low"  # Rápido para detección de UI
                    },
                    "maxOutputTokens": 1000
                }
            },
            timeout=60
        )
        
        result = response.json()
        
        if "candidates" in result and len(result["candidates"]) > 0:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in result:
            raise Exception(f"Gemini 3 Error: {result['error'].get('message', 'Unknown')}")
        else:
            raise Exception(f"Respuesta inesperada: {result}")
    
    def _llamar_openrouter(self, prompt: str, image_path: str) -> str:
        """Fallback: Llama a varios modelos via OpenRouter para robustez"""
        import httpx
        
        image_data = self._encode_image(image_path)
        mime_type = self._get_mime_type(image_path)
        
        # Lista de modelos a probar en orden (Usuario pidió Gemini 2.5 Flash Lite)
        modelos = [
            "google/gemini-2.5-flash-lite-preview-02-05:free", # Requested 2.5 specifically
            "google/gemini-2.5-flash-lite-001:free",           # Alternative ID
            "google/gemini-2.0-flash-lite-preview-02-05:free", # Previous working one
            "google/gemini-2.0-pro-exp-02-05:free",            # Fallback potente
            "meta-llama/llama-3.2-11b-vision-instruct:free",    # Fallback no-Google
        ]

        last_error = None
        
        for model in modelos:
            try:
                print(f"   ► Intento con Modelo Vision: {model}...")
                response = httpx.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openrouter_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://fotolibros.ar", 
                        "X-Title": "Fotolibros Agent"
                    },
                    json={
                        "model": model,
                        "messages": [{
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{image_data}"}}
                            ]
                        }],
                        "max_tokens": 1000,
                        "thinking": {
                            "type": "enabled",
                            "budget_tokens": 1024 
                        }
                    },
                    timeout=45
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if "choices" in result:
                        return result["choices"][0]["message"]["content"]
                    else:
                        last_error = f"Resp invalida: {result}"
                else:
                    last_error = f"Status {response.status_code}: {response.text}"
                    # Si es 429, seguimos al siguiente modelo
                    
            except Exception as e:
                last_error = str(e)
                continue
                
        raise Exception(f"Todos los modelos de visión fallaron. Último error: {last_error}")
    
    def _llamar_gemini(self, prompt: str, image_path: str) -> str:
        """Llama a OpenRouter como prioridad (Gemini Lite)"""
        # FORZAR SIEMPRE OPENROUTER PARA EVITAR QUOTAS DE GOOGLE DIRECTO
        if self.openrouter_key:
            return self._llamar_openrouter(prompt, image_path)
            
        # Fallback a la implementación vieja solo si no hay OR Key
        if self.use_gemini:
             return self._llamar_gemini_3(prompt, image_path)
             
        raise ValueError("No API key available (OPENROUTER)")
    
    def analizar_editor(self, screenshot_path: str) -> AnalisisEditor:
        """
        Analiza una captura del editor y devuelve información estructurada.
        """
        prompt = """Analiza esta captura de un editor de fotolibros.

Responde SOLO en este formato JSON exacto:
{
    "pagina_actual": <número>,
    "total_paginas": <número o "desconocido">,
    "tiene_fotos": <true/false>,
    "zonas_vacias": [
        {"x": <coord>, "y": <coord>, "descripcion": "zona para foto"}
    ],
    "elementos_visibles": ["lista de elementos que ves"],
    "sugerencia": "qué acción recomiendas hacer ahora"
}

Si no puedes determinar algo, usa valores por defecto razonables.
"""
        
        try:
            respuesta = self._llamar_gemini(prompt, screenshot_path)
            
            # Parsear JSON de la respuesta
            import json
            import re
            
            # Extraer JSON de la respuesta
            json_match = re.search(r'\{[\s\S]*\}', respuesta)
            if json_match:
                data = json.loads(json_match.group())
                return AnalisisEditor(
                    pagina_actual=data.get("pagina_actual", 1),
                    total_paginas=data.get("total_paginas", 20),
                    tiene_fotos=data.get("tiene_fotos", False),
                    zonas_disponibles=data.get("zonas_vacias", []),
                    elementos_detectados=data.get("elementos_visibles", []),
                    sugerencia=data.get("sugerencia", "")
                )
        except Exception as e:
            print(f"Error analizando editor: {e}")
        
        # Fallback
        return AnalisisEditor(
            pagina_actual=1,
            total_paginas=20,
            tiene_fotos=False,
            zonas_disponibles=[],
            elementos_detectados=[],
            sugerencia="No se pudo analizar"
        )
    
    def encontrar_boton(self, screenshot_path: str, descripcion_boton: str) -> Optional[Tuple[int, int]]:
        """
        Busca un botón específico en la captura y devuelve sus coordenadas.
        """
        prompt = f"""Busca en esta imagen un botón o elemento que coincida con: "{descripcion_boton}"

Si lo encuentras, responde SOLO con las coordenadas X,Y del centro del botón en formato:
COORDENADAS: X, Y

Si no lo encuentras, responde:
NO_ENCONTRADO

Analiza la imagen cuidadosamente. El botón puede ser texto, un icono, o ambos.
"""
        
        try:
            respuesta = self._llamar_gemini(prompt, screenshot_path)
            
            if "NO_ENCONTRADO" in respuesta.upper():
                return None
            
            # Extraer coordenadas
            import re
            match = re.search(r'COORDENADAS:\s*(\d+)\s*,\s*(\d+)', respuesta)
            if match:
                return (int(match.group(1)), int(match.group(2)))
            
            # Intentar otro formato
            match = re.search(r'(\d+)\s*,\s*(\d+)', respuesta)
            if match:
                return (int(match.group(1)), int(match.group(2)))
                
        except Exception as e:
            print(f"Error buscando botón: {e}")
        
        return None
    
    def encontrar_zona_drop(self, screenshot_path: str) -> Optional[Tuple[int, int]]:
        """
        Encuentra la mejor zona para soltar una foto.
        """
        prompt = """En esta imagen de un editor de fotolibros, encuentra una zona vacía 
donde se pueda colocar una foto.

Busca:
- Rectángulos vacíos o con placeholder
- Zonas con texto "Agregar foto" o similar  
- Áreas destacadas para contenido

Responde SOLO con las coordenadas del CENTRO de la mejor zona:
ZONA: X, Y

Si no hay zonas disponibles:
SIN_ZONAS
"""
        
        try:
            respuesta = self._llamar_gemini(prompt, screenshot_path)
            
            if "SIN_ZONAS" in respuesta.upper():
                return None
            
            import re
            match = re.search(r'ZONA:\s*(\d+)\s*,\s*(\d+)', respuesta)
            if match:
                return (int(match.group(1)), int(match.group(2)))
                
        except Exception as e:
            print(f"Error buscando zona: {e}")
        
        return None
    
    def sugerir_siguiente_accion(self, screenshot_path: str, contexto: str) -> AccionCanvas:
        """
        Dado el estado actual, sugiere la siguiente acción.
        """
        prompt = f"""Contexto: {contexto}

Analiza esta imagen del editor de fotolibros y sugiere la siguiente acción.

Responde en este formato JSON:
{{
    "tipo": "click" | "drag" | "type" | "scroll" | "esperar",
    "x": <coordenada X>,
    "y": <coordenada Y>,
    "x_destino": <solo para drag>,
    "y_destino": <solo para drag>,
    "texto": "<solo para type>",
    "descripcion": "explicación breve de la acción"
}}
"""
        
        try:
            respuesta = self._llamar_gemini(prompt, screenshot_path)
            
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', respuesta)
            if json_match:
                data = json.loads(json_match.group())
                return AccionCanvas(
                    tipo=data.get("tipo", "esperar"),
                    x=data.get("x", 0),
                    y=data.get("y", 0),
                    x_destino=data.get("x_destino"),
                    y_destino=data.get("y_destino"),
                    texto=data.get("texto"),
                    descripcion=data.get("descripcion", "")
                )
        except Exception as e:
            print(f"Error sugiriendo acción: {e}")
        
        return AccionCanvas(tipo="esperar", x=0, y=0, descripcion="Error en análisis")


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    helper = VisionHelper()
    
    # Test con una captura existente
    test_images = [
        "test_e2e_05_editor.png",
        "proyecto_Test_Real.png"
    ]
    
    for img in test_images:
        if os.path.exists(img):
            print(f"\n{'='*50}")
            print(f"Analizando: {img}")
            print('='*50)
            
            analisis = helper.analizar_editor(img)
            print(f"Página: {analisis.pagina_actual}/{analisis.total_paginas}")
            print(f"Tiene fotos: {analisis.tiene_fotos}")
            print(f"Elementos: {analisis.elementos_detectados[:5]}...")
            print(f"Sugerencia: {analisis.sugerencia}")
            break
