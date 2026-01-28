"""
Design Intelligence - Inteligencia de Diseño para Fotolibros
=============================================================
Combina las reglas de diseño del proyecto con Gemini Vision para
tomar decisiones inteligentes sobre el layout del fotolibro.

Reglas de diseño basadas en:
- config/design_templates.py (templates predefinidos)
- services/fdf_toolkit/fdf_layouts.py (coordenadas de slots)
- agents/orquestador.py (reglas del negocio)

TEMPLATES DE FDF Y SUS TEMÁTICAS:
- Vacío: Sin diseño, para diseño manual
- Solo Fotos: Minimalista, solo fotos sin decoraciones
- Flores (Marga, Beatriz, Ana, Lidia, Mirtha, Carmen): Bodas, Quinceañeras, Aniversarios
- Crafti: Scrapbook, Manualidades, Creativo
- Definición Papá: Día del Padre
- Short Stories: Minimalista con texto, Viajes
- Papá Oso: Infantil, Día del Padre
- Así Fue: Infantil, Cumpleaños de niños
- Acuarela Travel (A, B, C): Viajes, Vacaciones
- Cariño (Leone, Elefante, Volpe): Bebés, Infantil
- Collage: General, Eventos
- Color Block: Moderno, Corporativo
- Memories: Recuerdos, General
"""

import base64
import httpx
import json
import re
from typing import Optional, List, Dict
from dataclasses import dataclass
from enum import Enum


# Importar templates existentes
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.design_templates import (
    DESIGN_TEMPLATES, 
    DesignTemplate, 
    LayoutPagina,
    get_template,
    calcular_paginas_necesarias
)
from services.fdf_toolkit.fdf_layouts import FDF_LAYOUTS, get_slot_info


# =============================================================
# REGLAS DE DISEÑO (del orquestador)
# =============================================================

REGLAS_DISENO = """
REGLAS DE DISEÑO DE FOTOLIBROS PROFESIONALES:

================================================================================
1. ZONAS DE SEGURIDAD Y LOMO (CRITICO - EVITA FALLAS DE IMPRESION)
================================================================================
   - MARGEN EXTERIOR: Dejar minimo 5mm de sangrado en todos los bordes
   - ZONA SEGURA: No colocar elementos importantes a menos de 10mm del borde
   - LOMO/UNION CENTRAL: 
     * NUNCA colocar rostros, texto o elementos importantes en el centro de doble pagina
     * El lomo "come" aproximadamente 5-10mm de cada lado de la union
     * Si una foto cruza el lomo, asegurar que NO haya rostros ni texto en esa zona
     * Preferir que el lomo caiga en zonas de fondo o areas sin detalle importante
   - FOTOS A DOBLE PAGINA:
     * Solo usar para paisajes horizontales amplios (cielos, playas, montanas)
     * NUNCA usar doble pagina si hay personas/rostros que quedarian cortados
     * El contenido importante debe estar en los tercios laterales, no en el centro

2. RESOLUCION DE IMAGENES:
   - Ideal: >170 DPI para impresion HP Indigo de alta calidad
   - Minimo aceptable: 150 DPI
   - Si una foto tiene baja resolucion:
     * NO usarla a pagina completa
     * Preferir slots pequenos o collages
     * Agregar marco/borde para disimular

3. ORIENTACION Y NARRATIVA:
   - Fotos HORIZONTALES (paisaje): Layouts apaisados, pueden ir a doble pagina
   - Fotos VERTICALES (retrato): Layouts verticales, NUNCA a doble pagina
   - Fotos CUADRADAS: Flexibles, funcionan en cualquier layout
   - Mantener orden temporal/cronologico cuando sea posible
   - Agrupar fotos tematicamente (mismo evento, mismo lugar)

================================================================================
4. STICKERS Y ADORNOS (segun estilo)
================================================================================
   ESTILO SIN_DISENO/MINIMALISTA:
   - NO usar stickers ni adornos
   - Maximo: lineas finas o marcos simples
   
   ESTILO CLASICO:
   - Stickers sutiles: marcos dorados, esquinas decorativas, lineas elegantes
   - Adornos florales pequenos en esquinas
   - Evitar exceso - menos es mas
   
   ESTILO DIVERTIDO:
   - Stickers coloridos: estrellas, corazones, globos, confeti
   - Marcos decorativos con formas
   - Emojis y elementos ludicos
   - Se permite abundancia pero sin tapar las fotos
   
   ESTILO PREMIUM:
   - Adornos dorados o plateados
   - Marcos elegantes con filigrana
   - Elementos florales sofisticados
   - Tipografia decorativa
   
   REGLAS GENERALES DE STICKERS:
   - NUNCA tapar rostros o elementos importantes de las fotos
   - Colocar en esquinas o espacios vacios
   - Mantener coherencia de estilo en todo el libro
   - No sobrecargar - maximo 2-3 stickers por pagina

================================================================================
5. TITULOS Y TEXTOS
================================================================================
   PORTADA/TAPA:
   - Titulo principal: Nombre del evento o dedicatoria
   - Ubicacion: Centro o tercio inferior (nunca muy arriba por el corte)
   - Fuente legible, tamano grande (minimo 24pt)
   
   PAGINAS INTERIORES:
   - Titulos de seccion: Para separar momentos (ej: "La Ceremonia", "La Fiesta")
   - Fechas: Pueden ir en esquina inferior
   - Pies de foto: Breves, debajo de las fotos
   - Citas/frases: En paginas con espacio negativo
   
   REGLAS DE TEXTO:
   - NUNCA poner texto sobre rostros
   - Asegurar contraste suficiente (texto claro sobre fondo oscuro o viceversa)
   - Si el fondo es una foto, usar caja de texto con fondo semitransparente
   - No poner texto critico cerca del lomo
   - Tamano minimo legible: 10pt para cuerpo, 8pt para pies de foto

================================================================================
6. DISTRIBUCION DE FOTOS Y NARRATIVA
================================================================================
   PORTADA:
   - La MEJOR foto del evento (impactante, bien iluminada, emocional)
   - O foto grupal principal si es evento social
   
   PRIMERAS PAGINAS (1-4):
   - Fotos de establecimiento (lugar, decoracion, ambiente)
   - Foto grupal principal
   
   PAGINAS CENTRALES:
   - Desarrollo cronologico del evento
   - Alternar entre fotos grandes (protagonistas) y collages (complementarias)
   - Fotos de detalle van en collages, nunca solas
   
   ULTIMAS PAGINAS:
   - Fotos de cierre (despedidas, final del evento)
   - Puede incluir collage resumen
   - Pagina final: Dedicatoria o agradecimiento
   
   EVITAR:
   - Fotos repetitivas consecutivas (misma pose, mismo angulo)
   - Demasiadas fotos del mismo momento
   - Fotos borrosas o mal iluminadas (descartar o minimizar)

================================================================================
7. LAYOUTS RECOMENDADOS POR CANTIDAD DE FOTOS
================================================================================
   1 FOTO POR PAGINA: Foto destacada, bodas, premium
   2 FOTOS POR PAGINA: Clasico, equilibrado
   3 FOTOS POR PAGINA: Dinamico, collage asimetrico
   4+ FOTOS POR PAGINA: Collage, eventos con muchas fotos
   
   DOBLE PAGINA (spread): Solo para panoramicas sin rostros en el centro
"""


@dataclass
class FotoAnalizada:
    """Información de una foto analizada"""
    index: int
    orientacion: str  # "horizontal", "vertical", "cuadrada"
    tiene_rostros: bool
    es_paisaje: bool
    es_grupal: bool
    calidad_estimada: str  # "alta", "media", "baja"
    mejor_para: List[str]  # ["portada", "pagina_completa", "collage", etc]


@dataclass 
class PlanDePagina:
    """Plan de diseño para una página"""
    numero_pagina: int
    layout: str  # ID del layout de FDF_LAYOUTS
    fotos_asignadas: List[int]  # Índices de fotos
    slots_usados: List[str]  # IDs de slots
    notas: str


class DesignIntelligence:
    """
    Motor de inteligencia de diseño.
    Usa Gemini Vision para analizar fotos y aplicar reglas de diseño.
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
    
    async def _call_vision(self, prompt: str, images_b64: List[str] = None, max_tokens: int = 2000) -> dict:
        """Llama a Gemini con texto y opcionalmente imágenes"""
        
        content = [{"type": "text", "text": prompt}]
        
        if images_b64:
            for img_b64 in images_b64:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                })
        
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
                        "messages": [{"role": "user", "content": content}],
                        "max_tokens": max_tokens,
                        "temperature": 0.2
                    },
                    timeout=60.0
                )
                
                result = response.json()
                
                if "error" in result:
                    return {"success": False, "error": str(result["error"])}
                
                if "choices" not in result:
                    return {"success": False, "error": "No choices in response"}
                
                text = result["choices"][0]["message"]["content"]
                
                # Intentar extraer JSON
                json_match = re.search(r'\{[\s\S]*\}', text)
                if json_match:
                    try:
                        data = json.loads(json_match.group())
                        return {"success": True, "data": data, "raw": text}
                    except:
                        pass
                
                # Intentar extraer array JSON
                array_match = re.search(r'\[[\s\S]*\]', text)
                if array_match:
                    try:
                        data = json.loads(array_match.group())
                        return {"success": True, "data": data, "raw": text}
                    except:
                        pass
                
                return {"success": True, "data": None, "raw": text}
                
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    def get_template_info(self, estilo: str) -> dict:
        """Obtiene información del template de diseño"""
        template = get_template(estilo)
        if not template:
            template = get_template("clasico")
        
        return {
            "id": template.id,
            "nombre": template.nombre,
            "fotos_por_pagina": template.interior.fotos_por_pagina,
            "layout_default": template.interior.layout_default.value,
            "con_fondo": template.interior.con_fondo,
            "con_bordes": template.interior.con_bordes_foto,
            "con_sombras": template.interior.con_sombras,
            "ideal_para": template.ideal_para,
            "tapa_con_titulo": template.tapa.con_titulo,
            "tapa_con_foto": template.tapa.con_foto_portada
        }
    
    def get_layout_info(self, layout_name: str) -> dict:
        """Obtiene información de un layout"""
        if layout_name in FDF_LAYOUTS:
            layout = FDF_LAYOUTS[layout_name]
            return {
                "name": layout["name"],
                "slots": layout["slots"],
                "num_slots": len(layout["slots"])
            }
        return None
    
    def get_available_layouts(self) -> List[dict]:
        """Lista todos los layouts disponibles"""
        layouts = []
        for key, layout in FDF_LAYOUTS.items():
            layouts.append({
                "id": key,
                "name": layout["name"],
                "num_fotos": len(layout["slots"])
            })
        return layouts
    
    async def analizar_foto(self, foto_path: str) -> FotoAnalizada:
        """
        Analiza una foto individual para determinar su mejor uso.
        """
        # Leer y codificar la imagen
        with open(foto_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")
        
        prompt = f"""Analiza esta foto para un fotolibro profesional.

{REGLAS_DISENO}

Responde en JSON:
{{
    "orientacion": "horizontal|vertical|cuadrada",
    "tiene_rostros": true/false,
    "cantidad_personas": numero,
    "es_paisaje": true/false,
    "es_grupal": true/false (mas de 3 personas),
    "tipo_contenido": "retrato|paisaje|evento|detalle|objeto",
    "calidad_estimada": "alta|media|baja",
    "mejor_para": ["portada", "pagina_completa", "collage", "miniatura"],
    "evitar": ["lomo", "bordes", etc - donde NO poner esta foto],
    "notas": "observaciones importantes"
}}"""

        result = await self._call_vision(prompt, [img_b64])
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return FotoAnalizada(
                index=0,
                orientacion=data.get("orientacion", "horizontal"),
                tiene_rostros=data.get("tiene_rostros", False),
                es_paisaje=data.get("es_paisaje", False),
                es_grupal=data.get("es_grupal", False),
                calidad_estimada=data.get("calidad_estimada", "media"),
                mejor_para=data.get("mejor_para", ["collage"])
            )
        
        # Default si falla el análisis
        return FotoAnalizada(
            index=0,
            orientacion="horizontal",
            tiene_rostros=False,
            es_paisaje=False,
            es_grupal=False,
            calidad_estimada="media",
            mejor_para=["collage"]
        )
    
    async def analizar_fotos_batch(self, foto_paths: List[str], max_analizar: int = 10) -> List[FotoAnalizada]:
        """
        Analiza múltiples fotos (hasta max_analizar para no gastar mucho).
        """
        fotos_analizadas = []
        
        for i, path in enumerate(foto_paths[:max_analizar]):
            try:
                foto = await self.analizar_foto(path)
                foto.index = i
                fotos_analizadas.append(foto)
                print(f"[Design] Foto {i+1}/{min(len(foto_paths), max_analizar)} analizada: {foto.orientacion}, mejor para: {foto.mejor_para}")
            except Exception as e:
                print(f"[Design] Error analizando foto {i}: {e}")
                # Agregar con valores default
                fotos_analizadas.append(FotoAnalizada(
                    index=i,
                    orientacion="horizontal",
                    tiene_rostros=False,
                    es_paisaje=False,
                    es_grupal=False,
                    calidad_estimada="media",
                    mejor_para=["collage"]
                ))
        
        return fotos_analizadas
    
    async def generar_plan_diseno(
        self,
        fotos_analizadas: List[FotoAnalizada],
        estilo: str,
        num_paginas: int,
        titulo: str = None,
        evento_detectado: str = None
    ) -> List[PlanDePagina]:
        """
        Genera un plan completo de diseño para el fotolibro.
        """
        template_info = self.get_template_info(estilo)
        layouts_disponibles = self.get_available_layouts()
        
        # Preparar descripción de fotos
        fotos_desc = "\n".join([
            f"- Foto {f.index}: {f.orientacion}, {'con rostros' if f.tiene_rostros else 'sin rostros'}, "
            f"{'grupal' if f.es_grupal else 'individual/paisaje'}, calidad {f.calidad_estimada}, "
            f"mejor para: {', '.join(f.mejor_para)}"
            for f in fotos_analizadas
        ])
        
        layouts_desc = "\n".join([
            f"- {l['id']}: {l['name']} ({l['num_fotos']} fotos)"
            for l in layouts_disponibles
        ])
        
        prompt = f"""Eres un diseñador profesional de fotolibros.

{REGLAS_DISENO}

CONTEXTO DEL PROYECTO:
- Estilo: {estilo} ({template_info['nombre']})
- Fotos por página recomendadas: {template_info['fotos_por_pagina']}
- Título: {titulo or 'Sin título'}
- Evento: {evento_detectado or 'General'}
- Total de páginas disponibles: {num_paginas}
- Total de fotos: {len(fotos_analizadas)}

FOTOS DISPONIBLES:
{fotos_desc}

LAYOUTS DISPONIBLES:
{layouts_desc}

TAREA: Genera un plan de diseño para las primeras 10 páginas.

Para cada página, decide:
1. Qué layout usar (de los disponibles)
2. Qué fotos asignar a cada slot
3. Notas especiales de posicionamiento

Responde en JSON:
{{
    "portada": {{
        "foto_index": numero,
        "titulo_sugerido": "texto",
        "notas": "observaciones"
    }},
    "paginas": [
        {{
            "numero": 1,
            "layout": "id_del_layout",
            "fotos": [indices de fotos],
            "notas": "por qué este layout y estas fotos"
        }}
    ],
    "resumen": "explicación general del diseño elegido"
}}

IMPORTANTE: 
- La mejor foto SIEMPRE en portada
- Respetar las reglas de márgenes y lomo
- Variar layouts para que no sea monótono
- Fotos grupales en layouts simples (1-2 fotos)
- Fotos de detalle/paisaje pueden ir en collages"""

        result = await self._call_vision(prompt)
        
        if not result.get("success") or not result.get("data"):
            # Plan por defecto si falla
            return self._generar_plan_default(fotos_analizadas, estilo, num_paginas)
        
        data = result["data"]
        plan = []
        
        # Convertir respuesta a PlanDePagina
        for pag in data.get("paginas", []):
            plan.append(PlanDePagina(
                numero_pagina=pag.get("numero", len(plan) + 1),
                layout=pag.get("layout", "solo_fotos_1x1"),
                fotos_asignadas=pag.get("fotos", []),
                slots_usados=[],  # Se llenará durante la ejecución
                notas=pag.get("notas", "")
            ))
        
        return plan
    
    def _generar_plan_default(
        self,
        fotos: List[FotoAnalizada],
        estilo: str,
        num_paginas: int
    ) -> List[PlanDePagina]:
        """Genera un plan básico si el LLM falla"""
        template = get_template(estilo)
        fotos_por_pag = template.interior.fotos_por_pagina if template else 2
        
        plan = []
        foto_idx = 0
        
        for pag_num in range(1, min(num_paginas + 1, 11)):  # Máximo 10 páginas
            if foto_idx >= len(fotos):
                break
            
            # Elegir layout según fotos por página
            if fotos_por_pag == 1:
                layout = "solo_fotos_1x1"
                fotos_pag = [foto_idx]
                foto_idx += 1
            elif fotos_por_pag == 2:
                layout = "clasico"
                fotos_pag = [foto_idx]
                foto_idx += 1
            else:
                layout = "collage_2x2"
                fotos_pag = list(range(foto_idx, min(foto_idx + 4, len(fotos))))
                foto_idx += len(fotos_pag)
            
            plan.append(PlanDePagina(
                numero_pagina=pag_num,
                layout=layout,
                fotos_asignadas=fotos_pag,
                slots_usados=[],
                notas="Plan automático"
            ))
        
        return plan
    
    async def decidir_siguiente_accion(
        self,
        screenshot_b64: str,
        contexto: dict
    ) -> dict:
        """
        Dado el estado actual del editor, decide la siguiente acción.
        """
        prompt = f"""Eres un agente de automatización de fotolibros.

CONTEXTO ACTUAL:
- Paso actual: {contexto.get('paso_actual', 'desconocido')}
- Fotos subidas: {contexto.get('fotos_subidas', 0)}
- Página actual: {contexto.get('pagina_actual', 1)}
- Layout aplicado: {contexto.get('layout_actual', 'ninguno')}

{REGLAS_DISENO}

Analiza el screenshot y decide la siguiente acción.

Responde en JSON:
{{
    "accion": "click|drag|escribir|esperar|completado",
    "elemento": "descripcion del elemento",
    "coordenadas": {{"x": numero, "y": numero}},
    "valor": "texto si es escribir",
    "razon": "por qué esta acción",
    "siguiente_paso": "qué hacer después"
}}"""

        result = await self._call_vision(prompt, [screenshot_b64])
        
        if result.get("success") and result.get("data"):
            return result["data"]
        
        return {"accion": "esperar", "razon": "No se pudo determinar acción"}
    
    async def detectar_tematica_fotos(self, foto_paths: List[str], max_fotos: int = 5) -> dict:
        """
        Analiza las fotos para detectar la temática y recomendar un template de FDF.
        
        Returns:
            dict con:
            - tematica: str (boda, viaje, bebe, cumpleaños, etc.)
            - template_recomendado: str (nombre del template de FDF)
            - confianza: float (0-1)
            - razon: str
        """
        # Codificar algunas fotos para análisis
        images_b64 = []
        for path in foto_paths[:max_fotos]:
            try:
                with open(path, "rb") as f:
                    images_b64.append(base64.b64encode(f.read()).decode("utf-8"))
            except:
                continue
        
        if not images_b64:
            return {
                "tematica": "general",
                "template_recomendado": "Vacío",
                "confianza": 0.5,
                "razon": "No se pudieron analizar las fotos"
            }
        
        prompt = """Analiza estas fotos para determinar la TEMÁTICA del fotolibro.

TEMPLATES DISPONIBLES EN FDF (Fábrica de Fotolibros):
- Vacío: Sin diseño, para diseño manual libre
- Solo Fotos: Minimalista, solo fotos sin decoraciones
- Flores (Marga, Beatriz, Ana, Lidia, Mirtha, Carmen): Elegante con flores, ideal para BODAS, Quinceañeras, Aniversarios
- Crafti: Estilo scrapbook con texturas de papel, ideal para proyectos creativos
- Definición Papá: Especial para DÍA DEL PADRE
- Short Stories: Minimalista con espacio para texto, ideal para VIAJES con historias
- Papá Oso: Infantil tierno, ideal para DÍA DEL PADRE con niños
- Así Fue: Infantil colorido, ideal para CUMPLEAÑOS de niños
- Acuarela Travel (A, B, C): Ilustraciones de viaje en acuarela, ideal para VACACIONES
- Cariño Leone/Elefante/Volpe: Tierno con animales, ideal para BEBÉS
- Collage: Múltiples fotos por página, ideal para EVENTOS con muchas fotos
- Color Block: Moderno y limpio, ideal para CORPORATIVO o portfolios
- Memories: Estilo recuerdos, ideal para uso GENERAL

IMPORTANTE: 
- Siempre recomendar la versión "para Editores" del template (no incluye logo FDF)
- Analiza: personas, lugares, eventos, objetos, colores dominantes, emociones

Responde en JSON:
{
    "tematica": "boda|viaje|bebe|cumpleaños|dia_padre|quince|corporativo|general",
    "descripcion_fotos": "breve descripción de lo que ves en las fotos",
    "template_recomendado": "nombre exacto del template de FDF",
    "alternativas": ["template2", "template3"],
    "confianza": 0.0-1.0,
    "razon": "por qué este template es el mejor"
}"""
        
        result = await self._call_vision(prompt, images_b64)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "tematica": data.get("tematica", "general"),
                "descripcion": data.get("descripcion_fotos", ""),
                "template_recomendado": data.get("template_recomendado", "Vacío"),
                "alternativas": data.get("alternativas", []),
                "confianza": data.get("confianza", 0.5),
                "razon": data.get("razon", "")
            }
        
        return {
            "tematica": "general",
            "template_recomendado": "Vacío",
            "confianza": 0.3,
            "razon": "Error al analizar fotos, usando template por defecto"
        }
    
    def seleccionar_template_fdf(self, estilo_diseno: str, evento_detectado: str = None) -> dict:
        """
        Selecciona el template de FDF basado en el estilo elegido por el cliente en el frontend.
        
        IMPORTANTE: Siempre usar versión "para Editores" (sin logo FDF, permite logo propio)
        
        TEMPLATES DISPONIBLES EN FDF (según screenshot):
        ================================================
        Fila 1: Vacío, Flores Marga, Flores Beatriz, Flores Ana, Flores Lidia, Flores Mirtha, 
                Flores Carmen, Crafti, Definición Papá, Short Stories, Papá Oso
        Fila 2: Así Fue, Acuarela Travel C, Acuarela Travel B, Acuarela Travel A, 
                Cariño Leone, Cariño Elefante, Cariño Volpe, Collage v1, Collage v2, 
                Color Block, Color Block v2
        Fila 3: (más templates de viajes, love, etc.)
        
        Args:
            estilo_diseno: str - Estilo elegido en el frontend:
                - "minimalista": Limpio y moderno, 1 foto por página
                - "clasico": Elegante y atemporal, 2 fotos por página  
                - "divertido": Colorido y alegre, 3+ fotos por página
                - "premium": Lujo y sofisticación, 1 foto por página
            evento_detectado: str opcional - Evento detectado en las fotos
        
        Returns:
            dict con configuración completa del template
        """
        
        # ================================================================
        # MAPEO OFICIAL: Estilos del Frontend → Templates + Config de FDF
        # NOTA: Siempre usar versión "para Editores" 
        # ================================================================
        MAPEO_ESTILOS_FDF = {
            # ============================================================
            # SIN DISEÑO / SOLO FOTOS - Libro en blanco sin fondos temáticos
            # Usar para: clientes que quieren solo fotos, sin decoraciones
            # ============================================================
            "sin_diseno": {
                "template_fdf": "Vacío",  # Template completamente en blanco
                "alternativas": [],
                "fotos_por_pagina": 1,
                "descripcion": "Libro en blanco - SOLO FOTOS sin fondos ni decoraciones",
                "usar_categoria": "Vacío",  # Categoría específica en menú lateral
                "config_fdf": {
                    "fondo_paginas": "#FFFFFF",  # Blanco puro
                    "con_margenes": True,
                    "margen_grande": True,
                    "con_bordes_foto": False,
                    "con_sombras": False,
                    "fuente_textos": "Montserrat",
                    "color_textos": "#333333",
                    "layout_preferido": "1_foto_centrada",
                    "sin_fondos_tematicos": True  # Flag importante
                }
            },
            "solo_fotos": {
                "template_fdf": "Vacío",  # Alias de sin_diseno
                "alternativas": [],
                "fotos_por_pagina": 1,
                "descripcion": "Libro en blanco - SOLO FOTOS sin fondos ni decoraciones",
                "usar_categoria": "Vacío",
                "config_fdf": {
                    "fondo_paginas": "#FFFFFF",
                    "con_margenes": True,
                    "margen_grande": True,
                    "con_bordes_foto": False,
                    "con_sombras": False,
                    "fuente_textos": "Montserrat",
                    "color_textos": "#333333",
                    "layout_preferido": "1_foto_centrada",
                    "sin_fondos_tematicos": True
                }
            },
            # ============================================================
            # MINIMALISTA - Limpio pero puede tener fondos sutiles
            # ============================================================
            "minimalista": {
                "template_fdf": "Vacío",
                "alternativas": ["Short Stories", "Color Block"],
                "fotos_por_pagina": 1,
                "descripcion": "Diseño limpio sin decoraciones, las fotos son protagonistas",
                "usar_categoria": "Solo Fotos",  # Categoría en menú lateral
                # Configuración de diseño en FDF
                "config_fdf": {
                    "fondo_paginas": "#FFFFFF",  # Blanco puro
                    "con_margenes": True,
                    "margen_grande": True,  # Márgenes amplios
                    "con_bordes_foto": False,
                    "con_sombras": False,
                    "fuente_textos": "Montserrat",
                    "color_textos": "#333333",
                    "layout_preferido": "1_foto_centrada"
                }
            },
            "clasico": {
                "template_fdf": "Flores Ana",
                "alternativas": ["Flores Marga", "Flores Beatriz", "Flores Lidia"],
                "fotos_por_pagina": 2,
                "descripcion": "Elegante con detalles florales sutiles, ideal para bodas",
                "config_fdf": {
                    "fondo_paginas": "#FAF9F6",  # Crema suave
                    "con_margenes": True,
                    "margen_grande": False,
                    "con_bordes_foto": False,
                    "con_sombras": True,
                    "fuente_textos": "Playfair Display",  # Serif elegante
                    "color_textos": "#1a365d",  # Azul oscuro
                    "layout_preferido": "2_fotos_horizontal"
                }
            },
            "divertido": {
                "template_fdf": "Así Fue",
                "alternativas": ["Crafti", "Collage v1", "Color Block v2"],
                "fotos_por_pagina": 3,
                "descripcion": "Colorido y alegre, perfecto para cumpleaños y fiestas",
                "config_fdf": {
                    "fondo_paginas": "#FFF9E6",  # Amarillo suave
                    "con_margenes": True,
                    "margen_grande": False,
                    "con_bordes_foto": True,
                    "color_borde": "#FFFFFF",
                    "con_sombras": True,
                    "fuente_textos": "Fredoka One",  # Divertida redondeada
                    "color_textos": "#ed8936",  # Naranja
                    "layout_preferido": "collage_3_fotos"
                }
            },
            "premium": {
                "template_fdf": "Flores Marga",
                "alternativas": ["Flores Mirtha", "Flores Carmen"],
                "fotos_por_pagina": 1,
                "descripcion": "Máxima elegancia con detalles florales premium",
                "config_fdf": {
                    "fondo_paginas": "#F5F5F0",  # Marfil
                    "con_margenes": True,
                    "margen_grande": True,
                    "con_bordes_foto": True,
                    "color_borde": "#C9A227",  # Dorado
                    "con_sombras": True,
                    "fuente_textos": "Cormorant Garamond",  # Serif premium
                    "color_textos": "#2d3748",  # Gris oscuro
                    "layout_preferido": "1_foto_con_marco"
                }
            }
        }
        
        # ================================================================
        # MAPEO POR EVENTO DETECTADO (sobrescribe el estilo si aplica)
        # ================================================================
        MAPEO_EVENTOS_FDF = {
            # Bodas y eventos formales → Flores elegantes
            "boda": {"template": "Flores Marga", "config": MAPEO_ESTILOS_FDF["premium"]["config_fdf"]},
            "casamiento": {"template": "Flores Marga", "config": MAPEO_ESTILOS_FDF["premium"]["config_fdf"]},
            "aniversario": {"template": "Flores Lidia", "config": MAPEO_ESTILOS_FDF["clasico"]["config_fdf"]},
            
            # Quinceañeras → Flores románticas
            "quince": {"template": "Flores Beatriz", "config": MAPEO_ESTILOS_FDF["premium"]["config_fdf"]},
            "quinceañera": {"template": "Flores Beatriz", "config": MAPEO_ESTILOS_FDF["premium"]["config_fdf"]},
            
            # Viajes → Acuarela Travel
            "viaje": {"template": "Acuarela Travel A", "config": MAPEO_ESTILOS_FDF["minimalista"]["config_fdf"]},
            "vacaciones": {"template": "Acuarela Travel B", "config": MAPEO_ESTILOS_FDF["minimalista"]["config_fdf"]},
            
            # Bebés → Cariño (animales tiernos)
            "bebe": {"template": "Cariño Elefante", "config": MAPEO_ESTILOS_FDF["divertido"]["config_fdf"]},
            "bebé": {"template": "Cariño Elefante", "config": MAPEO_ESTILOS_FDF["divertido"]["config_fdf"]},
            "nacimiento": {"template": "Cariño Leone", "config": MAPEO_ESTILOS_FDF["divertido"]["config_fdf"]},
            
            # Cumpleaños infantil → Así Fue (colorido)
            "cumpleaños": {"template": "Así Fue", "config": MAPEO_ESTILOS_FDF["divertido"]["config_fdf"]},
            "cumple": {"template": "Así Fue", "config": MAPEO_ESTILOS_FDF["divertido"]["config_fdf"]},
            "infantil": {"template": "Así Fue", "config": MAPEO_ESTILOS_FDF["divertido"]["config_fdf"]},
            
            # Día del padre
            "dia_padre": {"template": "Definición Papá", "config": MAPEO_ESTILOS_FDF["clasico"]["config_fdf"]},
            "padre": {"template": "Papá Oso", "config": MAPEO_ESTILOS_FDF["divertido"]["config_fdf"]},
            
            # Corporativo
            "corporativo": {"template": "Color Block", "config": MAPEO_ESTILOS_FDF["minimalista"]["config_fdf"]},
            "empresa": {"template": "Color Block", "config": MAPEO_ESTILOS_FDF["minimalista"]["config_fdf"]},
        }
        
        # Normalizar estilo
        estilo = estilo_diseno.lower().strip() if estilo_diseno else "clasico"
        
        # Si hay evento detectado, puede sobrescribir
        if evento_detectado:
            evento = evento_detectado.lower().strip()
            if evento in MAPEO_EVENTOS_FDF:
                evento_config = MAPEO_EVENTOS_FDF[evento]
                return {
                    "template_fdf": evento_config["template"],
                    "es_version_editores": True,
                    "fotos_por_pagina": MAPEO_ESTILOS_FDF.get(estilo, MAPEO_ESTILOS_FDF["clasico"])["fotos_por_pagina"],
                    "config_fdf": evento_config["config"],
                    "descripcion": f"Template optimizado para: {evento}",
                    "motivo": f"evento_detectado:{evento}",
                    "alternativas": []
                }
        
        # Usar mapeo por estilo del frontend
        if estilo in MAPEO_ESTILOS_FDF:
            config = MAPEO_ESTILOS_FDF[estilo]
            return {
                "template_fdf": config["template_fdf"],
                "es_version_editores": True,
                "fotos_por_pagina": config["fotos_por_pagina"],
                "config_fdf": config["config_fdf"],
                "alternativas": config["alternativas"],
                "descripcion": config["descripcion"],
                "motivo": f"estilo_frontend:{estilo}"
            }
        
        # Default: Vacío (máxima flexibilidad)
        return {
            "template_fdf": "Vacío",
            "es_version_editores": True,
            "fotos_por_pagina": 1,
            "config_fdf": MAPEO_ESTILOS_FDF["minimalista"]["config_fdf"],
            "descripcion": "Template por defecto - diseño manual",
            "motivo": "default",
            "alternativas": []
        }
    
    def obtener_categoria_fdf(self, estilo_diseno: str, evento_detectado: str = None) -> dict:
        """
        Determina la CATEGORÍA del menú lateral de FDF para filtrar templates.
        
        CATEGORÍAS DISPONIBLES EN FDF (menú lateral izquierdo):
        ========================================================
        - TODOS: Muestra todos los templates
        - Anuarios: Templates para anuarios escolares
        - Vacío: Template en blanco sin diseño
        - Solo Fotos: Templates minimalistas, solo fotos
        - Colecciones: Templates de colecciones especiales
        - Viajes: Templates con tema de viajes/vacaciones
        - Infantil: Templates para bebés y niños
        - Bodas: Templates elegantes para bodas
        - Quince: Templates para quinceañeras
        - Cumple y Aniversario: Templates para cumpleaños/aniversarios
        - San Valentín: Templates románticos
        - Egresados: Templates para graduaciones
        - Comunión: Templates para comuniones
        - Día del Padre: Templates especiales día del padre
        - Día de la Madre: Templates especiales día de la madre
        
        Args:
            estilo_diseno: str - Estilo elegido en frontend (minimalista, clasico, divertido, premium)
            evento_detectado: str opcional - Evento detectado en las fotos
            
        Returns:
            dict con:
            - categoria_fdf: str - Categoría a seleccionar en menú lateral
            - templates_sugeridos: List[str] - Templates recomendados dentro de esa categoría
            - filtrar_por_categoria: bool - Si se debe filtrar primero por categoría
        """
        
        # ================================================================
        # MAPEO: Eventos detectados → Categorías FDF
        # ================================================================
        MAPEO_EVENTO_CATEGORIA = {
            # Bodas y eventos formales
            "boda": {"categoria": "Bodas", "templates": ["Flores Marga", "Flores Beatriz", "Flores Ana"]},
            "casamiento": {"categoria": "Bodas", "templates": ["Flores Marga", "Flores Beatriz"]},
            "civil": {"categoria": "Bodas", "templates": ["Flores Lidia", "Flores Mirtha"]},
            "matrimonio": {"categoria": "Bodas", "templates": ["Flores Marga", "Flores Ana"]},
            "aniversario": {"categoria": "Cumple y Aniversario", "templates": ["Flores Lidia", "Collage v1"]},
            
            # Quinceañeras
            "quince": {"categoria": "Quince", "templates": ["Flores Beatriz", "Flores Ana", "Flores Lidia"]},
            "quinceañera": {"categoria": "Quince", "templates": ["Flores Beatriz", "Flores Ana"]},
            "15": {"categoria": "Quince", "templates": ["Flores Beatriz", "Flores Ana"]},
            
            # Viajes y vacaciones
            "viaje": {"categoria": "Viajes", "templates": ["Acuarela Travel A", "Acuarela Travel B", "Short Stories"]},
            "vacaciones": {"categoria": "Viajes", "templates": ["Acuarela Travel B", "Acuarela Travel C"]},
            "europa": {"categoria": "Viajes", "templates": ["Acuarela Travel A", "Short Stories"]},
            "playa": {"categoria": "Viajes", "templates": ["Acuarela Travel C", "Acuarela Travel B"]},
            
            # Bebés e infantil
            "bebe": {"categoria": "Infantil", "templates": ["Cariño Elefante", "Cariño Leone", "Cariño Volpe"]},
            "bebé": {"categoria": "Infantil", "templates": ["Cariño Elefante", "Cariño Leone"]},
            "nacimiento": {"categoria": "Infantil", "templates": ["Cariño Leone", "Cariño Elefante"]},
            "baby_shower": {"categoria": "Infantil", "templates": ["Cariño Volpe", "Cariño Elefante"]},
            "infantil": {"categoria": "Infantil", "templates": ["Así Fue", "Cariño Leone", "Crafti"]},
            
            # Cumpleaños
            "cumpleaños": {"categoria": "Cumple y Aniversario", "templates": ["Así Fue", "Collage v1", "Crafti"]},
            "cumple": {"categoria": "Cumple y Aniversario", "templates": ["Así Fue", "Collage v1"]},
            "fiesta": {"categoria": "Cumple y Aniversario", "templates": ["Collage v1", "Collage v2", "Así Fue"]},
            
            # Día del Padre/Madre
            "dia_padre": {"categoria": "Día del Padre", "templates": ["Definición Papá", "Papá Oso"]},
            "padre": {"categoria": "Día del Padre", "templates": ["Papá Oso", "Definición Papá"]},
            "dia_madre": {"categoria": "Día de la Madre", "templates": ["Flores Marga", "Flores Ana"]},
            "madre": {"categoria": "Día de la Madre", "templates": ["Flores Beatriz", "Flores Lidia"]},
            
            # Graduaciones
            "graduacion": {"categoria": "Egresados", "templates": ["Short Stories", "Collage v1"]},
            "egresados": {"categoria": "Egresados", "templates": ["Short Stories", "Color Block"]},
            
            # San Valentín
            "san_valentin": {"categoria": "San Valentín", "templates": ["Flores Marga", "Flores Beatriz"]},
            "amor": {"categoria": "San Valentín", "templates": ["Flores Ana", "Flores Lidia"]},
            "pareja": {"categoria": "San Valentín", "templates": ["Flores Marga", "Short Stories"]},
            
            # Comunión
            "comunion": {"categoria": "Comunión", "templates": ["Flores Lidia", "Flores Ana"]},
            "primera_comunion": {"categoria": "Comunión", "templates": ["Flores Beatriz", "Flores Mirtha"]},
            
            # Corporativo
            "corporativo": {"categoria": "Solo Fotos", "templates": ["Vacío", "Color Block", "Short Stories"]},
            "empresa": {"categoria": "Solo Fotos", "templates": ["Color Block", "Color Block v2"]},
            "portfolio": {"categoria": "Solo Fotos", "templates": ["Vacío", "Short Stories"]},
        }
        
        # ================================================================
        # MAPEO: Estilos del frontend → Categorías FDF
        # ================================================================
        MAPEO_ESTILO_CATEGORIA = {
            # SIN DISEÑO - Libro completamente en blanco
            "sin_diseno": {
                "categoria": "Vacío",  # Ir directo a la categoría Vacío
                "templates": ["Vacío"],
                "filtrar": True,
                "es_solo_fotos": True  # Flag para indicar que NO queremos fondos
            },
            "solo_fotos": {
                "categoria": "Vacío",  # Alias
                "templates": ["Vacío"],
                "filtrar": True,
                "es_solo_fotos": True
            },
            "minimalista": {
                "categoria": "TODOS",  # Mostrar todos para elegir el más apropiado
                "templates": ["Short Stories", "Color Block", "Memories", "Collage v1"],
                "filtrar": False  # No filtrar, dejar que Vision elija de todos
            },
            "clasico": {
                "categoria": "TODOS",  # Mostrar todos para más opciones
                "templates": ["Flores Ana", "Flores Marga", "Flores Beatriz", "Flores Lidia", "Memories"],
                "filtrar": False  # No filtrar, dejar que Vision elija
            },
            "divertido": {
                "categoria": "TODOS",  # Mostrar todos para más opciones coloridas
                "templates": ["Así Fue", "Collage v1", "Collage v2", "Crafti", "Color Block v2"],
                "filtrar": False
            },
            "premium": {
                "categoria": "TODOS",  # Mostrar todos para elegir el más elegante
                "templates": ["Flores Marga", "Flores Mirtha", "Flores Carmen", "Flores Ana"],
                "filtrar": False
            }
        }
        
        # Prioridad: evento_detectado > estilo_diseno
        if evento_detectado:
            evento = evento_detectado.lower().strip()
            if evento in MAPEO_EVENTO_CATEGORIA:
                config = MAPEO_EVENTO_CATEGORIA[evento]
                return {
                    "categoria_fdf": config["categoria"],
                    "templates_sugeridos": config["templates"],
                    "filtrar_por_categoria": True,
                    "motivo": f"evento_detectado:{evento}"
                }
        
        # Usar mapeo por estilo
        estilo = estilo_diseno.lower().strip() if estilo_diseno else "clasico"
        if estilo in MAPEO_ESTILO_CATEGORIA:
            config = MAPEO_ESTILO_CATEGORIA[estilo]
            return {
                "categoria_fdf": config["categoria"],
                "templates_sugeridos": config["templates"],
                "filtrar_por_categoria": config["filtrar"],
                "es_solo_fotos": config.get("es_solo_fotos", False),  # True = libro en blanco sin fondos
                "motivo": f"estilo_frontend:{estilo}"
            }
        
        # Default: mostrar TODOS
        return {
            "categoria_fdf": "TODOS",
            "templates_sugeridos": ["Vacío"],
            "filtrar_por_categoria": False,
            "es_solo_fotos": False,
            "motivo": "default"
        }
    
    async def seleccionar_template_con_vision(
        self,
        screenshot_b64: str,
        estilo_cliente: str,
        fotos_b64: List[str] = None,
        descripcion_fotos: str = None
    ) -> dict:
        """
        SELECCION HIBRIDA DE TEMPLATE:
        Usa Gemini Vision para elegir el mejor template de los visibles en pantalla.
        
        Este metodo se llama DESPUES de filtrar por categoria.
        El LLM ve los templates disponibles y elige el mas apropiado.
        
        Args:
            screenshot_b64: Screenshot de la pantalla de templates (ya filtrada por categoria)
            estilo_cliente: Estilo elegido por el cliente (minimalista, clasico, divertido, premium, sin_diseno)
            fotos_b64: Lista opcional de fotos del cliente codificadas en base64 (max 3)
            descripcion_fotos: Descripcion textual de las fotos si no se envian imagenes
            
        Returns:
            dict con:
            - template_elegido: str - Nombre exacto del template a clickear
            - razonamiento: str - Por que se eligio este template
            - confianza: float - 0.0 a 1.0
            - alternativa: str - Template alternativo si el primero falla
        """
        
        # Descripcion de estilos para el LLM
        DESCRIPCION_ESTILOS = {
            "sin_diseno": "SOLO FOTOS - El cliente quiere un libro completamente en blanco, sin fondos, sin decoraciones, sin tematicas. Las fotos deben ser las unicas protagonistas. Elegir 'Vacio' o el template mas limpio posible.",
            "solo_fotos": "SOLO FOTOS - Igual que sin_diseno. Libro en blanco, sin fondos tematicos.",
            "minimalista": "MINIMALISTA - Diseño limpio y moderno. Fondos blancos o muy sutiles. Sin decoraciones recargadas. Las fotos son protagonistas. Ideal: Short Stories, Color Block, o templates con fondos solidos claros.",
            "clasico": "CLASICO/ELEGANTE - Diseño atemporal y sofisticado. Puede tener fondos sutiles, marcos elegantes, tipografias serif. Ideal para bodas, aniversarios. Templates con flores, marcos dorados, o estilos wedding.",
            "divertido": "DIVERTIDO/FESTIVO - Diseño colorido y alegre. Puede tener ilustraciones, colores vibrantes, elementos ludicos. Ideal para cumpleaños, fiestas infantiles. Templates con colores, stickers, o estilos playful.",
            "premium": "PREMIUM/LUJO - Maxima elegancia y sofisticacion. Fondos oscuros o dorados, tipografias premium, mucho espacio negativo. Para regalos especiales, quinceañeras, eventos corporativos de alto nivel."
        }
        
        estilo_desc = DESCRIPCION_ESTILOS.get(estilo_cliente.lower(), DESCRIPCION_ESTILOS["clasico"])
        
        # Construir contexto de fotos
        fotos_context = ""
        if descripcion_fotos:
            fotos_context = f"\n\nDESCRIPCION DE LAS FOTOS DEL CLIENTE:\n{descripcion_fotos}"
        elif fotos_b64:
            fotos_context = "\n\nSe adjuntan algunas fotos del cliente para que consideres su contenido al elegir el template."
        
        # Determinar si el cliente quiere diseño o no
        quiere_diseno = estilo_cliente.lower() not in ["sin_diseno", "solo_fotos"]
        
        instruccion_diseno = ""
        if quiere_diseno:
            instruccion_diseno = f"""
IMPORTANTE - EL CLIENTE QUIERE UN TEMPLATE CON DISEÑO:
- El estilo "{estilo_cliente}" requiere un template CON elementos decorativos
- NO elegir "Vacio" a menos que sea la UNICA opcion
- Buscar templates que tengan fondos, colores, o elementos que coincidan con el estilo
- Templates recomendados para {estilo_cliente}:
  * minimalista: "Short Stories", "Color Block", "Memories" (fondos limpios pero con diseño)
  * clasico: "Flores Ana", "Flores Marga", "Flores Beatriz" (elegantes con flores)
  * divertido: "Asi Fue", "Crafti", "Collage v1" (coloridos y alegres)
  * premium: "Flores Marga", "Flores Mirtha" (muy elegantes)
"""
        else:
            instruccion_diseno = """
IMPORTANTE - EL CLIENTE QUIERE LIBRO SIN DISEÑO:
- Elegir "Vacio" que es un libro completamente en blanco
- Solo las fotos, sin fondos ni decoraciones
"""
        
        prompt = f"""Eres un diseñador profesional de fotolibros para un RESELLER/REVENDEDOR.

ESTILO ELEGIDO POR EL CLIENTE: {estilo_cliente.upper()}
{estilo_desc}
{fotos_context}
{instruccion_diseno}

================================================================================
INSTRUCCIONES PARA ELEGIR EL TEMPLATE:
================================================================================

1. Mira el screenshot de la pantalla de templates de FDF (Fabrica de Fotolibros)

2. ATENCION A LAS VERSIONES:
   - Algunos templates tienen "- CL" (version Cliente, con logo FDF) 
   - Otros tienen "- ED" o "para Editores" (sin logo, para resellers)
   - La version NO es tan importante, lo que importa es el DISEÑO del template

3. PRIORIDAD DE SELECCION:
   a) Primero: Elegir un template que COINCIDA con el estilo "{estilo_cliente}"
   b) Segundo: Si hay version "para Editores" de ese template, mejor
   c) Tercero: Si no hay version ED, elegir la version CL (despues se elige profesionales)

4. REGLA CLAVE: {"NO elegir 'Vacio' - el cliente quiere diseño!" if quiere_diseno else "Elegir 'Vacio' - el cliente NO quiere diseño"}

Responde en JSON:
{{
    "templates_visibles": ["lista de nombres de templates que ves"],
    "template_elegido": "nombre del template a clickear (ej: 'Flores Ana - CL' o 'Short Stories')",
    "es_version_editores": true/false,
    "razonamiento": "por que este template es bueno para el estilo {estilo_cliente}",
    "confianza": 0.0-1.0,
    "alternativa": "segundo mejor template",
    "necesita_scroll": false
}}"""

        # Preparar imagenes
        images = [screenshot_b64]
        if fotos_b64:
            images.extend(fotos_b64[:3])  # Max 3 fotos del cliente
        
        result = await self._call_vision(prompt, images, max_tokens=1500)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            return {
                "success": True,
                "template_elegido": data.get("template_elegido", "Vacío - CL"),
                "templates_visibles": data.get("templates_visibles", []),
                "razonamiento": data.get("razonamiento", ""),
                "confianza": data.get("confianza", 0.5),
                "alternativa": data.get("alternativa", "Vacío - CL")
            }
        
        # Fallback si falla el LLM
        fallback_templates = {
            "sin_diseno": "Vacío - CL",
            "solo_fotos": "Vacío - CL",
            "minimalista": "Vacío - CL",
            "clasico": "Flores Ana - CL",
            "divertido": "Así Fue - CL",
            "premium": "Flores Marga - CL"
        }
        
        return {
            "success": False,
            "template_elegido": fallback_templates.get(estilo_cliente.lower(), "Vacío - CL"),
            "templates_visibles": [],
            "razonamiento": "Fallback - LLM no respondio correctamente",
            "confianza": 0.3,
            "alternativa": "Vacío - CL",
            "error": result.get("error", "Unknown error")
        }
    
    async def analizar_fotos_para_template(self, fotos_paths: List[str], max_fotos: int = 3) -> dict:
        """
        Analiza las fotos del cliente para generar una descripcion
        que ayude a elegir el template adecuado.
        
        Args:
            fotos_paths: Lista de rutas a las fotos
            max_fotos: Maximo de fotos a analizar
            
        Returns:
            dict con descripcion y caracteristicas detectadas
        """
        images_b64 = []
        for path in fotos_paths[:max_fotos]:
            try:
                with open(path, "rb") as f:
                    images_b64.append(base64.b64encode(f.read()).decode("utf-8"))
            except:
                continue
        
        if not images_b64:
            return {
                "success": False,
                "descripcion": "No se pudieron cargar las fotos",
                "tematica": "general"
            }
        
        prompt = """Analiza estas fotos que un cliente quiere incluir en su fotolibro.

Describe brevemente:
1. Que tipo de evento o tematica representan (boda, viaje, cumpleaños, bebe, familia, etc)
2. El tono general (formal, casual, divertido, emotivo, etc)
3. Colores predominantes
4. Si hay muchas personas, paisajes, objetos, etc

Responde en JSON:
{
    "tematica_principal": "boda|viaje|cumpleaños|bebe|familia|graduacion|otro",
    "tono": "formal|casual|divertido|emotivo|profesional",
    "colores_predominantes": ["color1", "color2"],
    "contenido": "descripcion breve del contenido de las fotos",
    "recomendacion_estilo": "minimalista|clasico|divertido|premium - cual seria el mejor"
}"""

        result = await self._call_vision(prompt, images_b64, max_tokens=800)
        
        if result.get("success") and result.get("data"):
            data = result["data"]
            # Construir descripcion textual
            descripcion = f"Tematica: {data.get('tematica_principal', 'general')}. "
            descripcion += f"Tono: {data.get('tono', 'casual')}. "
            descripcion += f"Contenido: {data.get('contenido', 'fotos variadas')}."
            
            return {
                "success": True,
                "descripcion": descripcion,
                "tematica": data.get("tematica_principal", "general"),
                "tono": data.get("tono", "casual"),
                "colores": data.get("colores_predominantes", []),
                "recomendacion_estilo": data.get("recomendacion_estilo", "clasico"),
                "raw": data
            }
        
        return {
            "success": False,
            "descripcion": "No se pudo analizar las fotos",
            "tematica": "general"
        }
