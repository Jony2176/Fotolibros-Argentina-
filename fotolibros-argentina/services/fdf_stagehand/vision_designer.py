"""
Vision Designer - Gemini Vision para diseño inteligente de fotolibros
=====================================================================
Usa Gemini para:
- Analizar el editor y detectar slots
- Decidir qué foto va en cada lugar
- Verificar que el resultado se vea bien
"""

import base64
import httpx
import json
import re
from typing import Optional, List, Dict
from playwright.async_api import Page


class VisionDesigner:
    """
    Diseñador visual usando Gemini.
    Analiza screenshots y toma decisiones de diseño.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "google/gemini-2.0-flash-001",
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    async def _call_vision(self, prompt: str, screenshot_b64: str, max_tokens: int = 1500) -> dict:
        """Llama a Gemini Vision con un screenshot"""
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
                        "max_tokens": max_tokens,
                        "temperature": 0.1
                    },
                    timeout=45.0
                )
                
                result = response.json()
                
                if "error" in result:
                    return {"success": False, "error": str(result["error"])}
                
                if "choices" not in result:
                    return {"success": False, "error": "No choices in response"}
                
                content = result["choices"][0]["message"]["content"]
                
                # Intentar parsear JSON de la respuesta
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                        return {"success": True, "data": data, "raw": content}
                    except json.JSONDecodeError:
                        return {"success": True, "data": None, "raw": content}
                
                return {"success": True, "data": None, "raw": content}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def analyze_editor(self, page: Page) -> dict:
        """
        Analiza el estado actual del editor.
        Detecta: tipo de página, slots disponibles, fotos cargadas, etc.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport["width"] if viewport else 1366
        h = viewport["height"] if viewport else 900
        
        prompt = f"""Analiza esta captura del editor de fotolibros (dimensiones: {w}x{h} pixeles).

Identifica y responde en JSON:
{{
    "tipo_pagina": "editor|catalogo|config|otro",
    "editor_visible": true/false,
    "panel_fotos": {{
        "visible": true/false,
        "posicion": "izquierda|derecha|arriba|abajo",
        "fotos_count": numero aproximado de miniaturas visibles
    }},
    "canvas": {{
        "visible": true/false,
        "x": coordenada X del borde izquierdo,
        "y": coordenada Y del borde superior,
        "width": ancho aproximado,
        "height": alto aproximado
    }},
    "slots_vacios": [
        {{"id": "slot_1", "x": centro_x, "y": centro_y, "descripcion": "descripcion del slot"}}
    ],
    "slots_con_foto": [
        {{"id": "slot_1", "x": centro_x, "y": centro_y, "tiene_foto": true}}
    ],
    "botones_visibles": ["lista de botones importantes como Guardar, Continuar, etc"],
    "siguiente_accion": "que deberia hacer el usuario ahora"
}}

IMPORTANTE: Las coordenadas deben ser numeros en pixeles."""

        result = await self._call_vision(prompt, screenshot_b64)
        
        if result.get("success") and result.get("data"):
            return {"success": True, "analysis": result["data"]}
        
        return {"success": False, "error": result.get("error", "No se pudo analizar"), "raw": result.get("raw")}
    
    async def find_photo_slots(self, page: Page) -> dict:
        """
        Encuentra específicamente los slots donde se pueden colocar fotos.
        Retorna coordenadas precisas para drag & drop.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport["width"] if viewport else 1366
        h = viewport["height"] if viewport else 900
        
        prompt = f"""Analiza este editor de fotolibros ({w}x{h} pixeles).

TAREA: Encuentra TODOS los espacios/slots donde se pueden colocar fotos en la pagina del libro.

Busca:
- Rectangulos vacios o con placeholder
- Areas grises o con icono de "agregar foto"
- Marcos o bordes que indican donde va una foto
- Zonas del canvas que esperan contenido

Responde en JSON:
{{
    "slots": [
        {{
            "id": "slot_0",
            "x": coordenada_x_centro,
            "y": coordenada_y_centro,
            "width": ancho_aproximado,
            "height": alto_aproximado,
            "vacio": true/false,
            "tipo": "principal|secundario|miniatura"
        }}
    ],
    "total_slots": numero,
    "slots_vacios": numero,
    "layout_detectado": "1_foto|2_fotos|collage|otro"
}}

IMPORTANTE: Coordenadas en pixeles, relativas a esquina superior izquierda."""

        result = await self._call_vision(prompt, screenshot_b64)
        
        if result.get("success") and result.get("data"):
            return {"success": True, "slots": result["data"].get("slots", []), "info": result["data"]}
        
        return {"success": False, "error": result.get("error"), "raw": result.get("raw")}
    
    async def find_photo_thumbnails(self, page: Page) -> dict:
        """
        Encuentra las miniaturas de fotos en el panel lateral.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport["width"] if viewport else 1366
        h = viewport["height"] if viewport else 900
        
        prompt = f"""Analiza este editor de fotolibros ({w}x{h} pixeles).

TAREA: Encuentra las MINIATURAS de fotos en el panel lateral (generalmente a la izquierda o derecha).

Estas son las fotos que el usuario subio y puede arrastrar al canvas.

Responde en JSON:
{{
    "panel_encontrado": true/false,
    "panel_posicion": "izquierda|derecha",
    "fotos": [
        {{
            "index": 0,
            "x": centro_x,
            "y": centro_y,
            "width": ancho,
            "height": alto
        }}
    ],
    "total_fotos": numero
}}

IMPORTANTE: Coordenadas en pixeles. Solo incluye fotos que se vean claramente como miniaturas arrastrables."""

        result = await self._call_vision(prompt, screenshot_b64)
        
        if result.get("success") and result.get("data"):
            return {"success": True, "photos": result["data"].get("fotos", []), "info": result["data"]}
        
        return {"success": False, "error": result.get("error"), "raw": result.get("raw")}
    
    async def verify_photo_placement(self, page: Page, expected_slot: dict = {}) -> dict:
        """
        Verifica si una foto fue colocada correctamente.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        slot_desc = ""
        if expected_slot:
            slot_desc = f"en la posicion aproximada ({expected_slot.get('x')}, {expected_slot.get('y')})"
        
        prompt = f"""Analiza este editor de fotolibros.

TAREA: Verifica si hay una foto correctamente colocada {slot_desc}.

Responde en JSON:
{{
    "foto_visible": true/false,
    "bien_posicionada": true/false,
    "problemas": ["lista de problemas si hay"],
    "confianza": 0.0-1.0,
    "descripcion": "breve descripcion de lo que ves"
}}"""

        result = await self._call_vision(prompt, screenshot_b64)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": data.get("foto_visible", False) and data.get("bien_posicionada", False),
                "confidence": data.get("confianza", 0),
                "details": data
            }
        
        return {"success": False, "error": result.get("error")}
    
    async def suggest_photo_for_slot(self, page: Page, available_photos: List[dict], slot_info: dict) -> dict:
        """
        Sugiere qué foto usar para un slot específico basándose en el contexto.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        photos_desc = "\n".join([f"- Foto {p['index']}: en ({p['x']}, {p['y']})" for p in available_photos[:10]])
        
        prompt = f"""Analiza este editor de fotolibros.

CONTEXTO:
- Hay un slot vacio en ({slot_info.get('x')}, {slot_info.get('y')}) de tipo "{slot_info.get('tipo', 'principal')}"
- Fotos disponibles en el panel:
{photos_desc}

TAREA: Sugiere cual foto usar para este slot.

Considera:
- Tamaño del slot vs proporcion de la foto
- Si es slot principal, preferir fotos destacadas
- Variedad en el diseño

Responde en JSON:
{{
    "foto_recomendada": indice_de_la_foto,
    "razon": "explicacion breve",
    "confianza": 0.0-1.0
}}"""

        result = await self._call_vision(prompt, screenshot_b64)
        
        if result.get("success") and result.get("data"):
            return {"success": True, "recommendation": result["data"]}
        
        return {"success": False, "error": result.get("error")}
    
    async def find_element(self, page: Page, description: str) -> dict:
        """
        Encuentra un elemento en la página basándose en descripción.
        Útil cuando no hay selectores CSS claros.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport["width"] if viewport else 1366
        h = viewport["height"] if viewport else 900
        
        prompt = f"""Analiza esta captura ({w}x{h} pixeles).

TAREA: Encuentra el elemento descrito como: "{description}"

Responde en JSON:
{{
    "encontrado": true/false,
    "x": coordenada_x_centro,
    "y": coordenada_y_centro,
    "descripcion": "que encontraste exactamente",
    "confianza": 0.0-1.0
}}

Si no lo encuentras, sugiere donde podria estar o que alternativas hay."""

        result = await self._call_vision(prompt, screenshot_b64)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            if data.get("encontrado") and data.get("x") and data.get("y"):
                return {
                    "success": True,
                    "x": data["x"],
                    "y": data["y"],
                    "confidence": data.get("confianza", 0.5),
                    "description": data.get("descripcion")
                }
        
        return {"success": False, "error": "Elemento no encontrado", "raw": result.get("raw")}
    
    async def is_editor_ready(self, page: Page) -> dict:
        """
        Verifica si el editor esta completamente cargado y listo para trabajar.
        Detecta mensajes de carga como "Preparando el Tema X%".
        
        IMPORTANTE: Distingue entre:
        - Pantalla de seleccion de templates (NO es el editor)
        - Editor real (tiene canvas de libro, panel de fotos arrastrables, herramientas)
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        prompt = """Analiza esta captura de la aplicacion de fotolibros.

TAREA CRITICA: Determina si estamos en el EDITOR DE DISEÑO o en otra pantalla.

PANTALLA DE SELECCION DE TEMPLATES (NO es el editor):
- Muestra una GRILLA de templates/temas para elegir
- Tiene botones "Relleno fotos manual", "Relleno fotos rapido", "Relleno fotos smart"
- Menu lateral con categorias (TODOS, Anuarios, Vacio, Solo Fotos, etc.)
- NO tiene canvas de libro editable
- NO tiene panel de fotos arrastrables

EDITOR DE DISEÑO (SI es el editor):
- Tiene un CANVAS central mostrando las paginas del libro (doble pagina o tapa)
- Tiene un PANEL DE FOTOS a la izquierda con miniaturas arrastrables
- Tiene HERRAMIENTAS de edicion (texto, formas, etc.)
- Tiene NAVEGADOR DE PAGINAS abajo (miniaturas de paginas)
- Tiene boton GUARDAR visible

CARGANDO:
- Mensajes como "Preparando...", "Cargando...", "Loading..."
- Barras de progreso o porcentajes visibles
- Spinners o animaciones de carga

Responde en JSON:
{
    "es_editor": true/false,
    "es_pantalla_templates": true/false,
    "editor_listo": true/false,
    "cargando": true/false,
    "mensaje_carga": "texto del mensaje si existe",
    "porcentaje_carga": numero si se ve (o null),
    "canvas_visible": true/false,
    "panel_fotos_visible": true/false,
    "navegador_paginas_visible": true/false,
    "descripcion": "breve descripcion de la pantalla actual"
}"""

        result = await self._call_vision(prompt, screenshot_b64, max_tokens=800)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            
            # El editor esta listo SOLO si es_editor=true y editor_listo=true
            is_editor = data.get("es_editor", False)
            is_templates = data.get("es_pantalla_templates", False)
            editor_ready = data.get("editor_listo", False)
            
            # Si estamos en pantalla de templates, NO estamos listos
            if is_templates:
                return {
                    "success": True,
                    "ready": False,
                    "loading": False,
                    "is_template_screen": True,
                    "loading_message": "En pantalla de templates, no en editor",
                    "loading_percent": None,
                    "details": data
                }
            
            return {
                "success": True,
                "ready": is_editor and editor_ready and not data.get("cargando", False),
                "loading": data.get("cargando", True),
                "is_template_screen": is_templates,
                "loading_message": data.get("mensaje_carga"),
                "loading_percent": data.get("porcentaje_carga"),
                "details": data
            }
        
        return {"success": False, "ready": False, "error": result.get("error")}
    
    async def plan_drag_drop(self, page: Page, estilo: str = "clasico") -> dict:
        """
        Analiza el editor y planifica las acciones de drag & drop.
        Retorna una lista de acciones: que foto arrastrar a que slot.
        Aplica reglas profesionales de diseño de fotolibros.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport["width"] if viewport else 1920
        h = viewport["height"] if viewport else 1080
        
        prompt = f"""Eres un diseñador profesional de fotolibros. Analiza este editor ({w}x{h} pixeles).

ESTILO DEL LIBRO: {estilo.upper()}

================================================================================
REGLAS CRITICAS DE DISEÑO (OBLIGATORIAS):
================================================================================

1. ZONA DEL LOMO (CENTRO DE DOBLE PAGINA):
   - El libro se abre por el centro, creando una "union" o "lomo"
   - NUNCA colocar rostros, caras o texto importante en el centro exacto
   - Si hay un slot que cruza el centro, la foto debe tener fondo/paisaje en esa zona
   - El lomo "come" ~10mm de cada lado de la union
   - El lomo es la franja central entre las lineas punteadas del editor

2. MARGENES DE SEGURIDAD:
   - Dejar minimo 5mm de sangrado en todos los bordes externos
   - No poner elementos importantes a menos de 10mm del borde (se pueden cortar en encuadernacion)
   - Dejar margenes generosos (espacio en blanco) para evitar cortes

3. FOTOS A DOBLE PAGINA (CRITICO):
   - Solo usar para PAISAJES amplios (cielos, playas, montañas, arquitectura sin personas)
   - NUNCA usar si hay personas que quedarian cortadas por el lomo
   - Si se usa doble pagina con personas: DESPLAZAR el motivo principal (personas/caras) 
     hacia el LADO IZQUIERDO o DERECHO, dejando fondo neutro en el centro
   - El contenido importante debe estar en los tercios laterales, NO en el centro
   - Estirar el contenedor de foto de extremo a extremo

4. JERARQUIA DE FOTOS:
   - PORTADA/TAPA: La mejor foto, impactante, bien iluminada (zona derecha del lienzo es la portada)
   - CONTRAPORTADA: Zona izquierda del lienzo de tapa
   - PAGINAS PRINCIPALES: Fotos destacadas, 1 por pagina
   - COLLAGES: Fotos secundarias o de detalle

5. STICKERS Y ADORNOS (segun estilo):
   - sin_diseno/minimalista: NO usar stickers, solo fotos
   - clasico: Stickers sutiles en esquinas (marcos, lineas finas)
   - divertido: Stickers coloridos (estrellas, globos) - NUNCA tapar rostros
   - premium: Adornos elegantes (dorados, florales, sofisticados)

6. HERRAMIENTAS CONTEXTUALES DE FOTO (Oficial FDF):
   - LUPA: En herramientas contextuales, permite AGRANDAR la imagen dentro del marco
   - MANITO: Aparece cuando tenés la foto seleccionada, permite DESPLAZAR la imagen
   - Uso combinado: Primero LUPA para agrandar, luego MANITO para mover el contenido
   - Esto permite ajustar qué parte de la foto se ve sin cambiar el tamaño del marco

7. PROCEDIMIENTO OFICIAL FDF PARA FOTOS A DOBLE PÁGINA CON PERSONAS:
   - 1) Seleccionar la foto
   - 2) Usar la LUPA para agrandar la imagen
   - 3) Usar la MANITO para desplazar y ubicar la parte principal LEJOS del lomo
   - El centro del libro "come" un poquito donde se unen las hojas

================================================================================
TAREA: Planifica el DRAG & DROP de fotos
================================================================================

1. Identifica las MINIATURAS de fotos en el panel lateral (generalmente izquierda)
2. Identifica los SLOTS/ESPACIOS en el canvas central (area de trabajo)
3. Analiza cada foto: tiene rostros? es paisaje? es grupal? orientacion?
4. Asigna fotos a slots siguiendo las reglas de diseño
5. Si un slot cruza el lomo y la foto tiene personas, indica que hay que DESPLAZAR el motivo

Responde en JSON:
{{
    "fotos_disponibles": [
        {{
            "id": 0, 
            "x": centro_x, 
            "y": centro_y, 
            "tiene_rostros": true/false,
            "es_paisaje": true/false,
            "es_grupal": true/false,
            "orientacion": "horizontal|vertical|cuadrada",
            "calidad": "alta|media|baja",
            "descripcion": "que se ve en la foto"
        }}
    ],
    "slots_disponibles": [
        {{
            "id": 0, 
            "x": centro_x, 
            "y": centro_y, 
            "width": ancho, 
            "height": alto, 
            "vacio": true/false,
            "cruza_lomo": true/false,
            "es_principal": true/false,
            "es_doble_pagina": true/false
        }}
    ],
    "plan_drag_drop": [
        {{
            "foto_id": 0,
            "foto_x": x_origen,
            "foto_y": y_origen,
            "slot_id": 0,
            "slot_x": x_destino,
            "slot_y": y_destino,
            "razon": "por que esta foto va en este slot",
            "requiere_ajuste_pan": true/false,
            "direccion_pan": "izquierda|derecha|ninguna",
            "advertencia": "si hay alguna advertencia de diseño"
        }}
    ],
    "pagina_actual": "tapa|interior|contraportada",
    "zona_tapa": {{
        "portada": "derecha del canvas",
        "contraportada": "izquierda del canvas",
        "lomo": "franja central entre lineas punteadas"
    }},
    "estado_canvas": "vacio|parcial|lleno",
    "recomendaciones": ["lista de sugerencias de diseño"],
    "advertencias_lomo": ["fotos que podrian tener problemas con el lomo"],
    "ajustes_pan_requeridos": [
        {{
            "slot_id": 0,
            "foto_id": 0,
            "motivo": "rostros en centro",
            "direccion_desplazamiento": "izquierda|derecha",
            "descripcion": "desplazar personas hacia la derecha para evitar el lomo"
        }}
    ]
}}

IMPORTANTE: 
- Coordenadas en pixeles desde esquina superior izquierda
- NO colocar fotos con rostros en slots que crucen el lomo SIN ajuste de pan
- Si se coloca foto con personas en doble pagina, SIEMPRE indicar que hay que desplazar el motivo
- Priorizar fotos de mejor calidad para slots principales (portada, paginas destacadas)
- En la TAPA: la zona DERECHA es la portada, la zona IZQUIERDA es la contraportada"""

        result = await self._call_vision(prompt, screenshot_b64, max_tokens=2000)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "photos": data.get("fotos_disponibles", []),
                "slots": data.get("slots_disponibles", []),
                "actions": data.get("plan_drag_drop", []),
                "page_type": data.get("pagina_actual", "interior"),
                "canvas_state": data.get("estado_canvas", "vacio"),
                "recommendations": data.get("recomendaciones", []),
                "spine_warnings": data.get("advertencias_lomo", [])
            }
        
        return {"success": False, "error": result.get("error"), "raw": result.get("raw")}
    
    async def get_precise_coordinates(self, page: Page, element_description: str) -> dict:
        """
        Obtiene coordenadas PRECISAS de un elemento para hacer click o drag.
        Mas preciso que find_element.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport["width"] if viewport else 1920
        h = viewport["height"] if viewport else 1080
        
        prompt = f"""Analiza esta captura ({w}x{h} pixeles).

TAREA: Encuentra las coordenadas EXACTAS del centro de: "{element_description}"

Necesito coordenadas PRECISAS para hacer click o drag programaticamente.

Responde SOLO en JSON:
{{
    "encontrado": true/false,
    "x": coordenada_x_exacta_del_centro,
    "y": coordenada_y_exacta_del_centro,
    "confianza": 0.0-1.0
}}

Si hay multiples elementos que coinciden, da las coordenadas del PRIMERO visible."""

        result = await self._call_vision(prompt, screenshot_b64, max_tokens=300)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            if data.get("encontrado") and data.get("x") is not None and data.get("y") is not None:
                return {
                    "success": True,
                    "x": int(data["x"]),
                    "y": int(data["y"]),
                    "confidence": data.get("confianza", 0.5)
                }
        
        return {"success": False, "error": "No encontrado"}
    
    async def suggest_stickers_and_text(self, page: Page, estilo: str, tipo_pagina: str = "interior") -> dict:
        """
        Sugiere stickers, adornos y textos para la pagina segun el estilo.
        
        Args:
            page: Pagina de Playwright
            estilo: Estilo del libro (sin_diseno, minimalista, clasico, divertido, premium)
            tipo_pagina: Tipo de pagina (tapa, interior, contraportada)
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        # Reglas de stickers por estilo
        reglas_stickers = {
            "sin_diseno": "NO agregar ningun sticker ni adorno. Solo las fotos.",
            "solo_fotos": "NO agregar ningun sticker ni adorno. Solo las fotos.",
            "minimalista": "Maximo 1 elemento decorativo muy sutil (linea fina o marco simple). Nada recargado.",
            "clasico": "Stickers elegantes: marcos dorados, esquinas decorativas, lineas sutiles, adornos florales pequenos. Maximo 2-3 por pagina.",
            "divertido": "Stickers coloridos: estrellas, corazones, globos, confeti, emojis. Pueden ser abundantes pero NO tapar rostros. Maximo 4-5 por pagina.",
            "premium": "Adornos sofisticados: elementos dorados o plateados, marcos elegantes con filigrana, flores estilizadas. Maximo 2-3 por pagina."
        }
        
        regla = reglas_stickers.get(estilo.lower(), reglas_stickers["clasico"])
        
        prompt = f"""Analiza esta pagina del editor de fotolibros.

ESTILO DEL LIBRO: {estilo.upper()}
TIPO DE PAGINA: {tipo_pagina}

REGLA DE STICKERS PARA ESTE ESTILO:
{regla}

TAREA: Sugiere donde colocar stickers/adornos y textos en esta pagina.

REGLAS GENERALES:
1. NUNCA tapar rostros con stickers
2. Colocar adornos en esquinas o espacios vacios
3. Mantener coherencia de estilo
4. Los textos deben tener buen contraste
5. No sobrecargar la pagina

Para TAPA:
- Sugerir posicion para titulo principal
- Adornos en esquinas si el estilo lo permite

Para INTERIOR:
- Pies de foto si hay espacio
- Adornos decorativos en esquinas vacias
- Posible titulo de seccion si es primera pagina de un momento

Responde en JSON:
{{
    "agregar_stickers": true/false,
    "stickers_sugeridos": [
        {{
            "tipo": "marco|estrella|corazon|flor|linea|esquina",
            "x": posicion_x,
            "y": posicion_y,
            "descripcion": "descripcion del sticker"
        }}
    ],
    "agregar_texto": true/false,
    "textos_sugeridos": [
        {{
            "tipo": "titulo|pie_foto|fecha|cita",
            "x": posicion_x,
            "y": posicion_y,
            "contenido_sugerido": "ejemplo de texto",
            "tamano": "grande|mediano|pequeno"
        }}
    ],
    "espacios_vacios": [
        {{"x": x, "y": y, "width": w, "height": h}}
    ],
    "advertencias": ["lista de cosas a evitar"]
}}"""

        result = await self._call_vision(prompt, screenshot_b64, max_tokens=1500)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "add_stickers": data.get("agregar_stickers", False),
                "stickers": data.get("stickers_sugeridos", []),
                "add_text": data.get("agregar_texto", False),
                "texts": data.get("textos_sugeridos", []),
                "empty_spaces": data.get("espacios_vacios", []),
                "warnings": data.get("advertencias", [])
            }
        
        return {"success": False, "error": result.get("error")}
    
    async def verify_design_rules(self, page: Page) -> dict:
        """
        Verifica que el diseño actual cumpla con las reglas profesionales.
        Detecta problemas como rostros en el lomo, margenes inseguros, etc.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        prompt = """Analiza esta pagina de fotolibro y verifica si cumple las reglas de diseño profesional.

REGLAS A VERIFICAR:

1. LOMO/CENTRO: ¿Hay rostros o texto importante en el centro de la doble pagina?
2. MARGENES: ¿Hay elementos muy cerca de los bordes que podrian cortarse?
3. RESOLUCION: ¿Alguna foto se ve pixelada o borrosa?
4. BALANCE: ¿La composicion esta equilibrada?
5. LEGIBILIDAD: ¿Los textos son legibles? ¿Tienen buen contraste?
6. STICKERS: ¿Los stickers tapan algo importante?

Responde en JSON:
{
    "cumple_reglas": true/false,
    "puntuacion": 0-100,
    "problemas_criticos": [
        {
            "tipo": "rostro_en_lomo|margen_inseguro|baja_resolucion|sticker_tapa_rostro",
            "descripcion": "descripcion del problema",
            "ubicacion": {"x": x, "y": y},
            "solucion": "como arreglarlo"
        }
    ],
    "advertencias": ["problemas menores"],
    "aspectos_positivos": ["que esta bien"],
    "recomendaciones": ["mejoras sugeridas"]
}"""

        result = await self._call_vision(prompt, screenshot_b64, max_tokens=1200)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "passes_rules": data.get("cumple_reglas", False),
                "score": data.get("puntuacion", 0),
                "critical_issues": data.get("problemas_criticos", []),
                "warnings": data.get("advertencias", []),
                "positives": data.get("aspectos_positivos", []),
                "recommendations": data.get("recomendaciones", [])
            }
        
        return {"success": False, "error": result.get("error")}
    
    async def analyze_double_page_photo(self, page: Page, photo_info: dict = {}) -> dict:
        """
        Analiza si una foto es apropiada para doble pagina y como ajustarla.
        
        REGLA CRITICA: Si la foto tiene personas/rostros y se usa en doble pagina,
        el motivo principal debe desplazarse hacia un lado para evitar el lomo.
        
        Args:
            page: Pagina de Playwright
            photo_info: Info de la foto (opcional, con descripcion previa)
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        prompt = """Analiza esta foto en el editor de fotolibros.

CONTEXTO: Esta foto podria usarse a DOBLE PAGINA (cruzando el lomo central).

TAREA: Determina si es apropiada para doble pagina y como ajustarla.

REGLAS PARA DOBLE PAGINA:
1. IDEAL: Paisajes amplios sin personas en el centro (cielos, playas, montañas)
2. ACEPTABLE: Grupos de personas SI el motivo principal puede desplazarse a un lado
3. PROHIBIDO: Rostros/caras que quedarian cortados por el lomo central

Si hay personas en la foto:
- Indicar hacia donde desplazar el motivo (usar Herramienta Mano)
- El centro del libro "come" ~20mm total, no debe haber rostros ahi
- Desplazar personas hacia izquierda o derecha segun composicion

Responde en JSON:
{
    "apta_doble_pagina": true/false,
    "tipo_contenido": "paisaje|personas|mixto|objeto",
    "tiene_rostros": true/false,
    "rostros_en_centro": true/false,
    "requiere_ajuste": true/false,
    "ajuste_recomendado": {
        "accion": "desplazar_izquierda|desplazar_derecha|zoom_out|ninguno",
        "motivo": "explicacion del ajuste",
        "intensidad": "leve|moderado|fuerte"
    },
    "zona_segura_lomo": {
        "descripcion": "que hay actualmente en la zona del lomo",
        "es_seguro": true/false
    },
    "alternativa": "si no es apta, que hacer en su lugar",
    "confianza": 0.0-1.0
}"""
        
        result = await self._call_vision(prompt, screenshot_b64, max_tokens=1000)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "suitable_for_double": data.get("apta_doble_pagina", False),
                "content_type": data.get("tipo_contenido", "mixto"),
                "has_faces": data.get("tiene_rostros", False),
                "faces_in_center": data.get("rostros_en_centro", False),
                "needs_adjustment": data.get("requiere_ajuste", False),
                "adjustment": data.get("ajuste_recomendado", {}),
                "spine_zone": data.get("zona_segura_lomo", {}),
                "alternative": data.get("alternativa"),
                "confidence": data.get("confianza", 0.5)
            }
        
        return {"success": False, "error": result.get("error")}
    
    async def plan_spine_text(self, page: Page, text: str, book_thickness: str = "normal") -> dict:
        """
        Planifica la colocacion de texto en el LOMO del libro (texto vertical rotado 90 grados).
        
        El lomo es la franja central entre las lineas punteadas en la vista de Tapa/Contratapa.
        El texto debe rotarse 90 grados para leerse cuando el libro esta en un estante.
        
        Args:
            page: Pagina de Playwright
            text: Texto a colocar en el lomo
            book_thickness: Grosor del libro (fino|normal|grueso) - afecta el ancho disponible
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        prompt = f"""Analiza esta vista de TAPA del editor de fotolibros.

TAREA: Planificar la colocacion del texto "{text}" en el LOMO del libro.

ANATOMIA DE LA TAPA:
- CONTRATAPA: Zona IZQUIERDA del canvas
- LOMO: Franja CENTRAL entre las lineas punteadas verticales
- PORTADA: Zona DERECHA del canvas

EL LOMO:
- Es la franja estrecha entre las dos lineas punteadas verticales
- El texto debe escribirse VERTICALMENTE (rotado 90 grados)
- Lectura de abajo hacia arriba cuando el libro esta en el estante
- Grosor del libro: {book_thickness}

PASOS PARA COLOCAR TEXTO EN EL LOMO:
1. Insertar cuadro de texto (herramienta Texto)
2. Escribir el texto
3. Usar el TIRADOR CIRCULAR sobre la caja de texto para rotar 90 grados
4. Centrar manualmente entre las lineas punteadas
5. Ajustar tamaño de fuente segun el ancho del lomo

Responde en JSON:
{{
    "lomo_detectado": true/false,
    "lomo_coordenadas": {{
        "x_izquierda": x1,
        "x_derecha": x2,
        "y_superior": y1,
        "y_inferior": y2,
        "ancho_px": ancho,
        "centro_x": x_centro
    }},
    "texto_cabe": true/false,
    "fuente_recomendada": {{
        "tamano": numero_px,
        "familia": "serif|sans-serif|script",
        "peso": "normal|bold"
    }},
    "posicion_texto": {{
        "x": centro_x_del_lomo,
        "y": centro_y_del_lomo,
        "rotacion": 90
    }},
    "instrucciones": [
        "paso 1...",
        "paso 2..."
    ],
    "advertencias": ["si el texto es muy largo, etc"]
}}"""
        
        result = await self._call_vision(prompt, screenshot_b64, max_tokens=1000)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "spine_detected": data.get("lomo_detectado", False),
                "spine_coords": data.get("lomo_coordenadas", {}),
                "text_fits": data.get("texto_cabe", True),
                "recommended_font": data.get("fuente_recomendada", {}),
                "text_position": data.get("posicion_texto", {}),
                "instructions": data.get("instrucciones", []),
                "warnings": data.get("advertencias", [])
            }
        
        return {"success": False, "error": result.get("error")}
    
    async def detect_cover_zones(self, page: Page) -> dict:
        """
        Detecta las zonas de la vista de Tapa: Contratapa, Lomo, Portada.
        Util para saber donde colocar elementos en la portada vs contratapa.
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport["width"] if viewport else 1920
        h = viewport["height"] if viewport else 1080
        
        prompt = f"""Analiza esta vista del editor de fotolibros ({w}x{h} pixeles).

TAREA: Detectar las ZONAS de la vista de TAPA del libro.

ESTRUCTURA DE LA TAPA (de izquierda a derecha):
1. CONTRATAPA (Back Cover): Zona izquierda - es la parte trasera del libro
2. LOMO (Spine): Franja central estrecha entre lineas punteadas - se ve en el estante
3. PORTADA (Front Cover): Zona derecha - es la cara principal del libro

IMPORTANTE:
- Las lineas punteadas verticales delimitan el lomo
- La portada es lo primero que ve el cliente
- La contratapa puede tener info adicional, codigo QR, etc.

Responde en JSON:
{{
    "es_vista_tapa": true/false,
    "zonas": {{
        "contratapa": {{
            "x_inicio": x1,
            "x_fin": x2,
            "y_inicio": y1,
            "y_fin": y2,
            "ancho": w,
            "alto": h
        }},
        "lomo": {{
            "x_inicio": x1,
            "x_fin": x2,
            "y_inicio": y1,
            "y_fin": y2,
            "ancho": w,
            "centro_x": cx
        }},
        "portada": {{
            "x_inicio": x1,
            "x_fin": x2,
            "y_inicio": y1,
            "y_fin": y2,
            "ancho": w,
            "alto": h
        }}
    }},
    "lineas_punteadas_visibles": true/false,
    "elementos_actuales": {{
        "en_portada": ["descripcion de elementos"],
        "en_lomo": ["descripcion de elementos"],
        "en_contratapa": ["descripcion de elementos"]
    }},
    "recomendaciones": ["sugerencias de diseño"]
}}"""
        
        result = await self._call_vision(prompt, screenshot_b64, max_tokens=1200)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "is_cover_view": data.get("es_vista_tapa", False),
                "zones": data.get("zonas", {}),
                "dotted_lines_visible": data.get("lineas_punteadas_visibles", False),
                "current_elements": data.get("elementos_actuales", {}),
                "recommendations": data.get("recomendaciones", [])
            }
        
        return {"success": False, "error": result.get("error")}
    
    async def detect_page_navigator(self, page: Page) -> dict:
        """
        Detecta el navegador de páginas del editor FDF.
        
        El navegador de páginas está generalmente en la parte INFERIOR del editor
        y muestra miniaturas de todas las páginas del libro para poder navegar.
        
        Returns:
            dict con info de páginas: total, actual, miniaturas con coordenadas
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        viewport = page.viewport_size
        w = viewport["width"] if viewport else 1920
        h = viewport["height"] if viewport else 1080
        
        prompt = f"""Analiza este editor de fotolibros ({w}x{h} pixeles).

TAREA: Detectar el NAVEGADOR DE PÁGINAS del libro.

El navegador de páginas suele estar en la parte INFERIOR del editor y muestra:
- Miniaturas pequeñas de cada página/spread del libro
- La página actual puede estar resaltada o con borde
- Permite navegar entre páginas haciendo click

ELEMENTOS A BUSCAR:
1. Fila horizontal de miniaturas en la parte inferior
2. Cada miniatura representa una página o spread (doble página)
3. Texto como "Contratapa-Tapa", "Páginas 2-3", etc. debajo de cada miniatura
4. Indicadores de página actual (borde, fondo destacado, etc.)

IMPORTANTE:
- En FDF, "Contratapa-Tapa" es la primera vista (portada del libro)
- Las páginas interiores se muestran como spreads (2 páginas a la vez)
- Un libro de 24 páginas tiene ~12 spreads + tapas

Responde en JSON:
{{
    "navegador_encontrado": true/false,
    "posicion_navegador": {{
        "y_inicio": coordenada_y_donde_comienza,
        "altura": altura_aproximada
    }},
    "total_miniaturas": numero,
    "pagina_actual_index": indice_0_based_de_miniatura_activa,
    "miniaturas": [
        {{
            "index": 0,
            "x": centro_x,
            "y": centro_y,
            "width": ancho,
            "height": alto,
            "label": "texto_debajo_si_visible",
            "es_activa": true/false
        }}
    ],
    "total_paginas_libro": numero_total_de_paginas_del_libro,
    "tipo_vista": "spreads|paginas_individuales",
    "descripcion": "descripcion de lo que ves"
}}

IMPORTANTE: Coordenadas en pixeles desde esquina superior izquierda."""
        
        result = await self._call_vision(prompt, screenshot_b64, max_tokens=1500)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "navigator_found": data.get("navegador_encontrado", False),
                "navigator_position": data.get("posicion_navegador", {}),
                "total_thumbnails": data.get("total_miniaturas", 0),
                "current_index": data.get("pagina_actual_index", 0),
                "thumbnails": data.get("miniaturas", []),
                "total_pages": data.get("total_paginas_libro", 0),
                "view_type": data.get("tipo_vista", "spreads"),
                "description": data.get("descripcion", "")
            }
        
        return {"success": False, "error": result.get("error"), "raw": result.get("raw")}
    
    async def suggest_photo_pan_adjustment(self, page: Page, target_direction: str = "auto") -> dict:
        """
        Sugiere como ajustar el PAN (desplazamiento) de una foto dentro de su marco.
        
        Esto es util cuando:
        - Una foto con personas esta en un slot que cruza el lomo
        - Queremos centrar mejor un motivo dentro del marco
        - Necesitamos evitar que algo importante quede cortado
        
        Args:
            page: Pagina de Playwright  
            target_direction: Direccion del ajuste (auto|izquierda|derecha|arriba|abajo)
        """
        screenshot = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot).decode("utf-8")
        
        prompt = f"""Analiza esta foto en el editor de fotolibros.

CONTEXTO: La foto esta colocada en un contenedor/marco y puede necesitar ajuste de posicion.

HERRAMIENTAS DISPONIBLES:
1. Herramienta Mano: Permite MOVER la imagen DENTRO de su marco (pan/desplazamiento)
2. Control de Zoom: Slider para ampliar/reducir la foto dentro del marco

TAREA: Determinar si la foto necesita ajuste de pan y en que direccion.

DIRECCION OBJETIVO: {target_direction}

CASOS COMUNES:
- Foto cruza el lomo y tiene rostros en el centro -> desplazar rostros hacia un lado
- Motivo principal muy al borde -> centrar mejor
- Mucho espacio vacio en un lado -> ajustar composicion

Responde en JSON:
{{
    "necesita_ajuste": true/false,
    "foto_seleccionada": true/false,
    "ajuste_pan": {{
        "direccion": "izquierda|derecha|arriba|abajo|ninguna",
        "intensidad_px": numero_aproximado_de_pixeles,
        "motivo": "razon del ajuste"
    }},
    "ajuste_zoom": {{
        "necesita": true/false,
        "direccion": "ampliar|reducir|ninguno",
        "motivo": "razon"
    }},
    "herramienta_mano": {{
        "posicion_actual": {{"x": x, "y": y}},
        "posicion_objetivo": {{"x": x, "y": y}}
    }},
    "instrucciones": [
        "1. Click en la foto para seleccionarla",
        "2. Activar Herramienta Mano",
        "3. Arrastrar hacia X direccion",
        "etc."
    ],
    "resultado_esperado": "descripcion de como quedara"
}}"""
        
        result = await self._call_vision(prompt, screenshot_b64, max_tokens=1000)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "needs_adjustment": data.get("necesita_ajuste", False),
                "photo_selected": data.get("foto_seleccionada", False),
                "pan_adjustment": data.get("ajuste_pan", {}),
                "zoom_adjustment": data.get("ajuste_zoom", {}),
                "hand_tool": data.get("herramienta_mano", {}),
                "instructions": data.get("instrucciones", []),
                "expected_result": data.get("resultado_esperado", "")
            }
        
        return {"success": False, "error": result.get("error")}
