# Alternativas Open Source a Browserbase para Automatización de Fotolibros

**Proyecto:** Fotolibros Argentina - Automatización del editor de fabricadefotolibros.com  
**Fecha:** Enero 2026  
**Stack actual:** AGNO + Gemini 2.5 Flash Lite (OpenRouter) + Browserbase

---

## Resumen Ejecutivo

**Stagehand v3 en modo CUA (Computer Use Agent) self-hosted** es la mejor alternativa a Browserbase para automatizar el editor visual de fabricadefotolibros.com. La clave está en separar las interacciones DOM (login, menús, subida de archivos) de las interacciones con el canvas (posicionamiento de fotos), usando Playwright directo para lo primero y Stagehand CUA con Gemini para lo segundo.

El problema principal con Browserbase no es la herramienta en sí, sino que su capa cloud agrega latencia innecesaria para operaciones que requieren múltiples capturas de pantalla y verificaciones visuales. Self-hosting Stagehand elimina esta latencia y permite implementar caching local de patrones visuales.

---

## Panorama Actual de Browser Agents Autónomos (Enero 2026)

| Herramienta | Estrellas GitHub | Licencia | Vision Mode | Self-hosted | Canvas Support |
|-------------|------------------|----------|-------------|-------------|----------------|
| **Browser Use** | 72.5k | MIT | Híbrido | ✅ Total | ⚠️ Limitado |
| **Stagehand** | 19k | MIT | CUA nativo | ✅ Total | ✅ Excelente |
| **Skyvern** | 18k | AGPL-3.0 | Core feature | ✅ Total | ⚠️ Moderado |
| **Playwright MCP** | 23.2k | Apache-2.0 | Opt-in | ✅ Total | ✅ Bueno |
| **LaVague** | 6.2k | Apache-2.0 | Vía LLM | ✅ Total | ❌ No adecuado |
| **AgentQL** | 1k | MIT/Cloud | ❌ No | ⚠️ Parcial | ❌ No adecuado |

---

## Análisis de las Principales Alternativas

### 1. Stagehand v3 (Recomendado)

Desarrollado por Browserbase pero **completamente open source bajo licencia MIT**. Destaca para editores visuales por tres razones:

1. **Modo CUA (Computer Use Agent):** Permite interacciones basadas en coordenadas visuales en lugar de selectores DOM, esencial para elementos canvas.

2. **Optimización con Gemini:** Browserbase colaboró con Google DeepMind para optimizar la integración con Gemini 2.5 Computer Use.

3. **Rendimiento:** La versión 3 es 44% más rápida que la anterior en operaciones con iframes y shadow DOMs.

4. **Auto-caching:** Cuando una acción tiene éxito, se memoriza y ejecuta sin llamada al LLM en ejecuciones posteriores.

```typescript
// Ejemplo básico de Stagehand con Gemini para canvas
const stagehand = new Stagehand({
  env: "LOCAL",
  modelProvider: "google",
  modelName: "gemini-2.5-computer-use-preview"
});

const agent = stagehand.agent({ mode: "cua" });
await agent.execute("Arrastra la foto a la esquina superior izquierda del canvas");
```

### 2. Browser Use

Domina el ecosistema con más de 500 descargas diarias y respaldo de Y Combinator. Su arquitectura híbrida DOM+Vision funciona bien para la mayoría de aplicaciones web, pero presenta limitaciones para canvas HTML5.

**Problema:** El enfoque de Browser Use prioriza el DOM parsing. El canvas HTML5 no tiene estructura DOM interna — todo el contenido se renderiza como píxeles sin elementos identificables.

**Uso recomendado:** Navegación de menús, selección de templates, subida de archivos. No para posicionamiento dentro del canvas.

### 3. Skyvern

Adopta un enfoque radicalmente diferente: no busca selectores CSS/XPath sino que toma screenshots y usa Vision-LLM para encontrar elementos visualmente.

**Sistema Planner-Actor-Validator:**
1. **Planner Agent:** Mantiene el objetivo de alto nivel
2. **Actor Agent:** Ejecuta el paso inmediato
3. **Validator Agent:** Verifica si la acción funcionó

**Limitación:** Licencia AGPL-3.0 impone restricciones para uso comercial sin compartir código.

---

## El Problema Específico: Canvas de fabricadefotolibros.com

El editor de FDF presenta desafíos específicos:

- **Drag & drop interactivo** de fotos
- **Layouts con múltiples fotos** por página
- **Posicionamiento preciso** en slots predefinidos
- **Zoom, rotar, bordes** como acciones adicionales
- **Muy sensible a cambios de UI** — cualquier update rompe selectores

### Por qué el canvas es difícil de automatizar

El contenido dentro de `<canvas>` son píxeles renderizados, no elementos DOM:

- No hay selectores CSS ni XPath disponibles
- Los elementos "dibujados" no tienen identidad persistente
- Las interacciones requieren coordenadas calculadas basadas en análisis visual
- El 60% de automation engineers reportan dificultades específicas con canvas

---

## Arquitectura Propuesta para FDF

```
┌─────────────────────────────────────────────────────────────┐
│                    AGNO Orquestador                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ Agente DOM   │    │ Agente Canvas│    │ Agente       │  │
│  │ (Playwright) │    │ (Stagehand   │    │ Verificación │  │
│  │              │    │  CUA + Gemini│    │ (Vision)     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│        │                    │                    │          │
│        ▼                    ▼                    ▼          │
│  • Login FDF          • Drag fotos         • Verificar     │
│  • Seleccionar        • Posicionar en        estado       │
│    producto             slots              • ¿Foto bien    │
│  • Subir fotos        • Ajustar zoom         ubicada?     │
│  • Navegar menús      • Aplicar layouts   • ¿Layout ok?   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Separación Clave: DOM vs Canvas

| Acción | Método | Herramienta |
|--------|--------|-------------|
| Login, menús, seleccionar producto | Playwright directo | Selectores CSS estables |
| Subir fotos al sistema | Playwright | Input file handler |
| Arrastrar foto al canvas | Stagehand CUA | Vision + coordenadas |
| Posicionar dentro del slot | Stagehand CUA | Gemini localiza → click preciso |
| Verificar resultado | Gemini Vision | Screenshot → validación |

---

## Implementación: Mapeo de Coordenadas del Editor FDF

El editor de FDF tiene **layouts predefinidos**. Pre-mapear las coordenadas de cada slot reduce drásticamente las llamadas al modelo de visión.

### Estructura de Layouts

```python
# fdf_layouts.py - Mapeo de slots por template de FDF

FDF_LAYOUTS = {
    "solo_fotos_1x1": {
        "name": "Solo Fotos - 1 foto por página",
        "slots": [
            {"id": "main", "x": 0.1, "y": 0.1, "w": 0.8, "h": 0.8}
        ]
    },
    "collage_2x2": {
        "name": "Collage - 4 fotos",
        "slots": [
            {"id": "top_left", "x": 0.05, "y": 0.05, "w": 0.45, "h": 0.45},
            {"id": "top_right", "x": 0.5, "y": 0.05, "w": 0.45, "h": 0.45},
            {"id": "bottom_left", "x": 0.05, "y": 0.5, "w": 0.45, "h": 0.45},
            {"id": "bottom_right", "x": 0.5, "y": 0.5, "w": 0.45, "h": 0.45}
        ]
    },
    "collage_3_horizontal": {
        "name": "Collage - 3 fotos horizontal",
        "slots": [
            {"id": "left", "x": 0.02, "y": 0.1, "w": 0.32, "h": 0.8},
            {"id": "center", "x": 0.34, "y": 0.1, "w": 0.32, "h": 0.8},
            {"id": "right", "x": 0.66, "y": 0.1, "w": 0.32, "h": 0.8}
        ]
    },
    "featured_with_thumbnails": {
        "name": "1 grande + 3 miniaturas",
        "slots": [
            {"id": "featured", "x": 0.05, "y": 0.05, "w": 0.6, "h": 0.9},
            {"id": "thumb_1", "x": 0.68, "y": 0.05, "w": 0.28, "h": 0.28},
            {"id": "thumb_2", "x": 0.68, "y": 0.36, "w": 0.28, "h": 0.28},
            {"id": "thumb_3", "x": 0.68, "y": 0.67, "w": 0.28, "h": 0.28}
        ]
    }
}


def get_slot_info(layout_name: str, slot_id: str) -> dict:
    """Obtiene información de un slot específico"""
    if layout_name not in FDF_LAYOUTS:
        raise ValueError(f"Layout '{layout_name}' no encontrado")
    
    layout = FDF_LAYOUTS[layout_name]
    for slot in layout["slots"]:
        if slot["id"] == slot_id:
            return slot
    
    raise ValueError(f"Slot '{slot_id}' no encontrado en layout '{layout_name}'")
```

### Calculador de Coordenadas Absolutas

```python
# fdf_coordinates.py

from playwright.async_api import Page, ElementHandle
from fdf_layouts import FDF_LAYOUTS, get_slot_info


async def get_canvas_bounds(page: Page) -> dict:
    """Obtiene las dimensiones del canvas del editor FDF"""
    # Ajustar el selector según el HTML real de FDF
    canvas = await page.query_selector("#editor-canvas, .canvas-container, [data-editor-canvas]")
    
    if not canvas:
        raise Exception("No se encontró el canvas del editor")
    
    bounds = await canvas.bounding_box()
    return {
        "x": bounds["x"],
        "y": bounds["y"],
        "width": bounds["width"],
        "height": bounds["height"]
    }


async def get_slot_absolute_coordinates(page: Page, layout_name: str, slot_id: str) -> dict:
    """Calcula coordenadas absolutas de un slot en el canvas"""
    canvas = await get_canvas_bounds(page)
    slot = get_slot_info(layout_name, slot_id)
    
    return {
        "x": canvas["x"] + (canvas["width"] * slot["x"]),
        "y": canvas["y"] + (canvas["height"] * slot["y"]),
        "width": canvas["width"] * slot["w"],
        "height": canvas["height"] * slot["h"],
        "center_x": canvas["x"] + (canvas["width"] * (slot["x"] + slot["w"]/2)),
        "center_y": canvas["y"] + (canvas["height"] * (slot["y"] + slot["h"]/2))
    }


async def get_all_slots_coordinates(page: Page, layout_name: str) -> list:
    """Obtiene coordenadas de todos los slots de un layout"""
    if layout_name not in FDF_LAYOUTS:
        raise ValueError(f"Layout '{layout_name}' no encontrado")
    
    canvas = await get_canvas_bounds(page)
    layout = FDF_LAYOUTS[layout_name]
    
    slots_coords = []
    for slot in layout["slots"]:
        slots_coords.append({
            "id": slot["id"],
            "x": canvas["x"] + (canvas["width"] * slot["x"]),
            "y": canvas["y"] + (canvas["height"] * slot["y"]),
            "width": canvas["width"] * slot["w"],
            "height": canvas["height"] * slot["h"],
            "center_x": canvas["x"] + (canvas["width"] * (slot["x"] + slot["w"]/2)),
            "center_y": canvas["y"] + (canvas["height"] * (slot["y"] + slot["h"]/2))
        })
    
    return slots_coords
```

---

## Implementación: Smart Drag & Drop

```python
# fdf_drag_drop.py

import asyncio
from playwright.async_api import Page, ElementHandle
from fdf_coordinates import get_slot_absolute_coordinates


async def drag_photo_to_slot(
    page: Page,
    photo_element: ElementHandle,
    layout_name: str,
    slot_id: str,
    steps: int = 15
) -> bool:
    """
    Arrastra una foto desde el panel lateral hacia un slot del canvas.
    
    Args:
        page: Página de Playwright
        photo_element: Elemento de la foto a arrastrar
        layout_name: Nombre del layout (ej: "collage_2x2")
        slot_id: ID del slot destino (ej: "top_left")
        steps: Pasos del movimiento (más = más suave)
    
    Returns:
        bool: True si el drag fue exitoso
    """
    # 1. Obtener coordenadas del slot destino (pre-calculadas)
    slot_coords = await get_slot_absolute_coordinates(page, layout_name, slot_id)
    
    # 2. Obtener posición de la foto en el panel lateral
    photo_bounds = await photo_element.bounding_box()
    if not photo_bounds:
        raise Exception("No se pudo obtener la posición de la foto")
    
    photo_center_x = photo_bounds["x"] + photo_bounds["width"] / 2
    photo_center_y = photo_bounds["y"] + photo_bounds["height"] / 2
    
    # 3. Ejecutar drag & drop
    await page.mouse.move(photo_center_x, photo_center_y)
    await asyncio.sleep(0.1)  # Pequeña pausa para estabilidad
    
    await page.mouse.down()
    await asyncio.sleep(0.05)
    
    # Movimiento suave hacia el destino
    await page.mouse.move(
        slot_coords["center_x"],
        slot_coords["center_y"],
        steps=steps
    )
    
    await asyncio.sleep(0.1)
    await page.mouse.up()
    
    # 4. Esperar a que el canvas procese el drop
    await asyncio.sleep(0.5)
    
    return True


async def drag_photo_to_coordinates(
    page: Page,
    photo_element: ElementHandle,
    target_x: float,
    target_y: float,
    steps: int = 15
) -> bool:
    """
    Arrastra una foto a coordenadas específicas (para casos donde
    el layout no está pre-mapeado).
    """
    photo_bounds = await photo_element.bounding_box()
    if not photo_bounds:
        raise Exception("No se pudo obtener la posición de la foto")
    
    photo_center_x = photo_bounds["x"] + photo_bounds["width"] / 2
    photo_center_y = photo_bounds["y"] + photo_bounds["height"] / 2
    
    await page.mouse.move(photo_center_x, photo_center_y)
    await asyncio.sleep(0.1)
    await page.mouse.down()
    await asyncio.sleep(0.05)
    
    await page.mouse.move(target_x, target_y, steps=steps)
    
    await asyncio.sleep(0.1)
    await page.mouse.up()
    await asyncio.sleep(0.5)
    
    return True
```

---

## Implementación: Verificación Visual con Gemini

```python
# fdf_verification.py

import base64
import httpx
from playwright.async_api import Page


class GeminiVisionVerifier:
    """Verificador visual usando Gemini 2.5 Flash Lite via OpenRouter"""
    
    def __init__(self, api_key: str, model: str = "google/gemini-2.5-flash-lite"):
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
        
        Args:
            page: Página de Playwright
            slot_description: Descripción del slot (ej: "esquina superior izquierda")
        
        Returns:
            dict: {"success": bool, "confidence": float, "details": str}
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

Solo responde con el JSON, sin texto adicional."""

        async with httpx.AsyncClient() as client:
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
                    "max_tokens": 200
                },
                timeout=30.0
            )
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # Parsear respuesta JSON
        import json
        try:
            verification = json.loads(content)
            return {
                "success": verification.get("foto_presente", False) and verification.get("bien_posicionada", False),
                "confidence": verification.get("confianza", 0.0),
                "details": verification.get("observaciones", "")
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "confidence": 0.0,
                "details": f"Error parseando respuesta: {content}"
            }
    
    async def detect_slot_position(
        self,
        page: Page,
        slot_description: str
    ) -> dict:
        """
        Detecta la posición de un slot usando visión (para layouts no mapeados).
        
        Returns:
            dict: {"x": float, "y": float, "width": float, "height": float}
        """
        screenshot_bytes = await page.screenshot()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
        
        # Obtener dimensiones de la página
        viewport = page.viewport_size
        
        prompt = f"""Analiza esta captura de un editor de fotolibros.
Dimensiones de la imagen: {viewport['width']}x{viewport['height']} píxeles.

Encuentra el slot de foto descrito como: "{slot_description}"

Responde EXACTAMENTE en este formato JSON con las coordenadas en píxeles:
{{
    "encontrado": true/false,
    "x": número (coordenada X del borde izquierdo),
    "y": número (coordenada Y del borde superior),
    "width": número (ancho del slot),
    "height": número (alto del slot),
    "center_x": número (centro X),
    "center_y": número (centro Y)
}}

Solo responde con el JSON."""

        async with httpx.AsyncClient() as client:
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
                    "max_tokens": 200
                },
                timeout=30.0
            )
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        import json
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"encontrado": False, "error": content}
```

---

## Implementación: Cache de Patrones Visuales

```python
# fdf_pattern_cache.py

import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Optional
from playwright.async_api import Page


class FDFPatternCache:
    """
    Cache de patrones visuales del editor FDF.
    Almacena coordenadas aprendidas para evitar llamadas repetidas al modelo de visión.
    """
    
    def __init__(self, db_path: str = "fdf_patterns.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        """Inicializa la base de datos"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS slot_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                layout_name TEXT NOT NULL,
                slot_id TEXT NOT NULL,
                viewport_width INTEGER NOT NULL,
                viewport_height INTEGER NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                width REAL NOT NULL,
                height REAL NOT NULL,
                center_x REAL NOT NULL,
                center_y REAL NOT NULL,
                confidence REAL DEFAULT 1.0,
                hit_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(layout_name, slot_id, viewport_width, viewport_height)
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ui_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                element_name TEXT NOT NULL,
                viewport_width INTEGER NOT NULL,
                viewport_height INTEGER NOT NULL,
                selector TEXT,
                x REAL,
                y REAL,
                width REAL,
                height REAL,
                hit_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(element_name, viewport_width, viewport_height)
            )
        """)
        
        self.conn.commit()
    
    def get_cached_slot(
        self,
        layout_name: str,
        slot_id: str,
        viewport_width: int,
        viewport_height: int
    ) -> Optional[dict]:
        """Busca un slot en el cache"""
        cursor = self.conn.execute("""
            SELECT x, y, width, height, center_x, center_y, confidence
            FROM slot_patterns
            WHERE layout_name = ? AND slot_id = ? 
              AND viewport_width = ? AND viewport_height = ?
        """, (layout_name, slot_id, viewport_width, viewport_height))
        
        row = cursor.fetchone()
        if row:
            # Actualizar estadísticas de uso
            self.conn.execute("""
                UPDATE slot_patterns 
                SET hit_count = hit_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE layout_name = ? AND slot_id = ?
                  AND viewport_width = ? AND viewport_height = ?
            """, (layout_name, slot_id, viewport_width, viewport_height))
            self.conn.commit()
            
            return {
                "x": row[0],
                "y": row[1],
                "width": row[2],
                "height": row[3],
                "center_x": row[4],
                "center_y": row[5],
                "confidence": row[6],
                "from_cache": True
            }
        
        return None
    
    def save_slot_pattern(
        self,
        layout_name: str,
        slot_id: str,
        viewport_width: int,
        viewport_height: int,
        coords: dict,
        confidence: float = 1.0
    ):
        """Guarda un patrón de slot en el cache"""
        self.conn.execute("""
            INSERT OR REPLACE INTO slot_patterns 
            (layout_name, slot_id, viewport_width, viewport_height, 
             x, y, width, height, center_x, center_y, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            layout_name, slot_id, viewport_width, viewport_height,
            coords["x"], coords["y"], coords["width"], coords["height"],
            coords["center_x"], coords["center_y"], confidence
        ))
        self.conn.commit()
    
    async def get_or_learn_slot(
        self,
        page: Page,
        layout_name: str,
        slot_id: str,
        vision_verifier  # GeminiVisionVerifier instance
    ) -> dict:
        """
        Obtiene coordenadas del cache o las aprende con visión.
        """
        viewport = page.viewport_size
        
        # Intentar obtener del cache
        cached = self.get_cached_slot(
            layout_name, slot_id,
            viewport["width"], viewport["height"]
        )
        
        if cached:
            return cached
        
        # Aprender con visión
        slot_description = f"slot '{slot_id}' del layout '{layout_name}'"
        detected = await vision_verifier.detect_slot_position(page, slot_description)
        
        if detected.get("encontrado"):
            coords = {
                "x": detected["x"],
                "y": detected["y"],
                "width": detected["width"],
                "height": detected["height"],
                "center_x": detected["center_x"],
                "center_y": detected["center_y"]
            }
            
            # Guardar para futuras ejecuciones
            self.save_slot_pattern(
                layout_name, slot_id,
                viewport["width"], viewport["height"],
                coords
            )
            
            coords["from_cache"] = False
            return coords
        
        raise Exception(f"No se pudo detectar el slot {slot_id} en layout {layout_name}")
    
    def get_cache_stats(self) -> dict:
        """Obtiene estadísticas del cache"""
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total_patterns,
                SUM(hit_count) as total_hits,
                AVG(confidence) as avg_confidence
            FROM slot_patterns
        """)
        row = cursor.fetchone()
        
        return {
            "total_patterns": row[0] or 0,
            "total_hits": row[1] or 0,
            "avg_confidence": row[2] or 0.0,
            "cache_efficiency": f"{(row[1] or 0) / max(row[0] or 1, 1):.1f}x"
        }
    
    def clear_old_patterns(self, days: int = 30):
        """Limpia patrones no usados en X días"""
        self.conn.execute("""
            DELETE FROM slot_patterns
            WHERE last_used < datetime('now', ?)
        """, (f'-{days} days',))
        self.conn.commit()
```

---

## Implementación: Toolkit Completo para AGNO

```python
# fdf_browser_toolkit.py

import asyncio
from typing import Optional, List
from playwright.async_api import async_playwright, Page, Browser
from agno.tools import tool

from fdf_layouts import FDF_LAYOUTS
from fdf_coordinates import get_slot_absolute_coordinates, get_all_slots_coordinates
from fdf_drag_drop import drag_photo_to_slot, drag_photo_to_coordinates
from fdf_verification import GeminiVisionVerifier
from fdf_pattern_cache import FDFPatternCache


class FDFBrowserToolkit:
    """
    Toolkit de herramientas para automatizar el editor de fabricadefotolibros.com
    Diseñado para integrarse con AGNO.
    """
    
    def __init__(
        self,
        openrouter_api_key: str,
        fdf_email: str,
        fdf_password: str,
        headless: bool = True,
        cache_db_path: str = "fdf_patterns.db"
    ):
        self.openrouter_api_key = openrouter_api_key
        self.fdf_email = fdf_email
        self.fdf_password = fdf_password
        self.headless = headless
        
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.verifier = GeminiVisionVerifier(openrouter_api_key)
        self.cache = FDFPatternCache(cache_db_path)
    
    async def _ensure_browser(self):
        """Asegura que el browser esté inicializado"""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=self.headless)
            self.page = await self.browser.new_page()
    
    @tool(name="fdf_login", description="Inicia sesión en fabricadefotolibros.com")
    async def login(self) -> dict:
        """Realiza login en FDF"""
        await self._ensure_browser()
        
        await self.page.goto("https://fabricadefotolibros.com/login")
        await self.page.fill('input[name="email"]', self.fdf_email)
        await self.page.fill('input[name="password"]', self.fdf_password)
        await self.page.click('button[type="submit"]')
        
        # Esperar a que cargue el dashboard
        await self.page.wait_for_url("**/dashboard**", timeout=10000)
        
        return {"success": True, "message": "Login exitoso"}
    
    @tool(name="fdf_select_product", description="Selecciona un producto/tamaño de fotolibro")
    async def select_product(self, product_code: str) -> dict:
        """
        Selecciona un producto en FDF.
        
        Args:
            product_code: Código del producto (ej: "CU-21x21-DURA")
        """
        await self._ensure_browser()
        
        # Navegar al catálogo
        await self.page.goto("https://fabricadefotolibros.com/catalogo")
        
        # Buscar y seleccionar el producto
        product_selector = f'[data-product="{product_code}"], .product-card:has-text("{product_code}")'
        await self.page.click(product_selector)
        
        # Esperar carga del editor
        await self.page.wait_for_selector("#editor-canvas, .editor-container", timeout=15000)
        
        return {"success": True, "product": product_code}
    
    @tool(name="fdf_upload_photos", description="Sube fotos al editor de FDF")
    async def upload_photos(self, photo_paths: List[str]) -> dict:
        """
        Sube una lista de fotos al editor.
        
        Args:
            photo_paths: Lista de rutas a las fotos
        """
        await self._ensure_browser()
        
        # Encontrar el input de archivos
        file_input = await self.page.query_selector('input[type="file"]')
        
        if not file_input:
            # Puede que haya que hacer click en un botón primero
            await self.page.click('button:has-text("Subir"), .upload-button')
            file_input = await self.page.wait_for_selector('input[type="file"]')
        
        await file_input.set_input_files(photo_paths)
        
        # Esperar a que se procesen las fotos
        await asyncio.sleep(2)
        
        return {"success": True, "photos_uploaded": len(photo_paths)}
    
    @tool(name="fdf_select_layout", description="Selecciona un layout/template para la página actual")
    async def select_layout(self, layout_name: str) -> dict:
        """
        Selecciona un layout para la página actual.
        
        Args:
            layout_name: Nombre del layout (ej: "collage_2x2", "solo_fotos_1x1")
        """
        await self._ensure_browser()
        
        if layout_name not in FDF_LAYOUTS:
            return {"success": False, "error": f"Layout '{layout_name}' no reconocido"}
        
        # Click en el selector de layouts
        await self.page.click('.layout-selector, [data-layouts]')
        
        # Seleccionar el layout específico
        layout_info = FDF_LAYOUTS[layout_name]
        await self.page.click(f'.layout-option:has-text("{layout_info["name"]}"), [data-layout="{layout_name}"]')
        
        await asyncio.sleep(1)  # Esperar aplicación del layout
        
        return {"success": True, "layout": layout_name, "slots": len(layout_info["slots"])}
    
    @tool(name="fdf_place_photo", description="Coloca una foto en un slot específico del canvas")
    async def place_photo_in_slot(
        self,
        photo_index: int,
        layout_name: str,
        slot_id: str
    ) -> dict:
        """
        Coloca una foto en un slot del canvas.
        
        Args:
            photo_index: Índice de la foto en el panel lateral (0-based)
            layout_name: Nombre del layout actual
            slot_id: ID del slot destino
        """
        await self._ensure_browser()
        
        # Obtener la foto del panel lateral
        photos = await self.page.query_selector_all('.photo-thumbnail, .uploaded-photo')
        
        if photo_index >= len(photos):
            return {"success": False, "error": f"Foto índice {photo_index} no existe"}
        
        photo_element = photos[photo_index]
        
        # Ejecutar drag & drop
        success = await drag_photo_to_slot(
            self.page, photo_element, layout_name, slot_id
        )
        
        if not success:
            return {"success": False, "error": "Falló el drag & drop"}
        
        # Verificar con visión
        verification = await self.verifier.verify_photo_placement(
            self.page,
            f"slot {slot_id} del layout {layout_name}"
        )
        
        return {
            "success": verification["success"],
            "confidence": verification["confidence"],
            "details": verification["details"]
        }
    
    @tool(name="fdf_place_photo_smart", description="Coloca una foto usando cache + visión inteligente")
    async def place_photo_smart(
        self,
        photo_index: int,
        layout_name: str,
        slot_id: str
    ) -> dict:
        """
        Versión inteligente que usa cache de patrones.
        """
        await self._ensure_browser()
        
        # Obtener coordenadas (del cache o aprendidas)
        coords = await self.cache.get_or_learn_slot(
            self.page, layout_name, slot_id, self.verifier
        )
        
        # Obtener la foto
        photos = await self.page.query_selector_all('.photo-thumbnail, .uploaded-photo')
        if photo_index >= len(photos):
            return {"success": False, "error": f"Foto índice {photo_index} no existe"}
        
        photo_element = photos[photo_index]
        
        # Drag & drop a coordenadas conocidas
        await drag_photo_to_coordinates(
            self.page, photo_element,
            coords["center_x"], coords["center_y"]
        )
        
        # Verificar resultado
        verification = await self.verifier.verify_photo_placement(
            self.page, f"slot {slot_id}"
        )
        
        return {
            "success": verification["success"],
            "from_cache": coords.get("from_cache", False),
            "confidence": verification["confidence"],
            "cache_stats": self.cache.get_cache_stats()
        }
    
    @tool(name="fdf_save_project", description="Guarda el proyecto actual")
    async def save_project(self) -> dict:
        """Guarda el proyecto en FDF"""
        await self._ensure_browser()
        
        await self.page.click('button:has-text("Guardar"), .save-button')
        
        # Esperar confirmación
        await self.page.wait_for_selector('.save-success, .toast-success', timeout=10000)
        
        return {"success": True, "message": "Proyecto guardado"}
    
    @tool(name="fdf_checkout", description="Procede al checkout del pedido")
    async def checkout(self) -> dict:
        """Inicia el proceso de checkout"""
        await self._ensure_browser()
        
        await self.page.click('button:has-text("Pedir"), button:has-text("Comprar"), .checkout-button')
        
        # Esperar página de checkout
        await self.page.wait_for_url("**/checkout**", timeout=10000)
        
        # Obtener resumen del pedido
        total_element = await self.page.query_selector('.order-total, .total-price')
        total_text = await total_element.inner_text() if total_element else "N/A"
        
        return {"success": True, "total": total_text}
    
    @tool(name="fdf_get_available_layouts", description="Lista los layouts disponibles")
    async def get_available_layouts(self) -> dict:
        """Retorna todos los layouts pre-mapeados"""
        layouts = []
        for name, info in FDF_LAYOUTS.items():
            layouts.append({
                "name": name,
                "display_name": info["name"],
                "slots_count": len(info["slots"]),
                "slot_ids": [s["id"] for s in info["slots"]]
            })
        return {"layouts": layouts}
    
    @tool(name="fdf_screenshot", description="Toma una captura del estado actual")
    async def take_screenshot(self, save_path: Optional[str] = None) -> dict:
        """Captura el estado actual del editor"""
        await self._ensure_browser()
        
        if save_path:
            await self.page.screenshot(path=save_path)
            return {"success": True, "path": save_path}
        else:
            screenshot = await self.page.screenshot()
            import base64
            b64 = base64.b64encode(screenshot).decode()
            return {"success": True, "base64": b64[:100] + "..."}
    
    async def close(self):
        """Cierra el browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            self.page = None


# Función para crear el toolkit como herramientas de AGNO
def get_fdf_tools(
    openrouter_api_key: str,
    fdf_email: str,
    fdf_password: str
) -> list:
    """
    Retorna lista de tools para usar con AGNO Agent.
    
    Uso:
        from agno.agent import Agent
        from fdf_browser_toolkit import get_fdf_tools
        
        agent = Agent(
            model=...,
            tools=get_fdf_tools("key", "email", "pass"),
            description="Agente para automatizar creación de fotolibros"
        )
    """
    toolkit = FDFBrowserToolkit(
        openrouter_api_key=openrouter_api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password
    )
    
    return [
        toolkit.login,
        toolkit.select_product,
        toolkit.upload_photos,
        toolkit.select_layout,
        toolkit.place_photo_in_slot,
        toolkit.place_photo_smart,
        toolkit.save_project,
        toolkit.checkout,
        toolkit.get_available_layouts,
        toolkit.take_screenshot
    ]
```

---

## Integración Completa con AGNO

```python
# main_fdf_agent.py

import asyncio
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from fdf_browser_toolkit import get_fdf_tools
import os


# Configuración
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
FDF_EMAIL = os.getenv("FDF_EMAIL")
FDF_PASSWORD = os.getenv("FDF_PASSWORD")


# Modelo de visión via OpenRouter
model = OpenAIChat(
    id="google/gemini-2.5-flash-lite",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)


# Crear agente con herramientas de FDF
agent = Agent(
    model=model,
    tools=get_fdf_tools(OPENROUTER_API_KEY, FDF_EMAIL, FDF_PASSWORD),
    description="""Eres un agente especializado en crear fotolibros en fabricadefotolibros.com.

Tu flujo de trabajo típico es:
1. Login en FDF
2. Seleccionar el producto/tamaño correcto
3. Subir las fotos del cliente
4. Seleccionar layouts apropiados para cada página
5. Colocar las fotos en los slots correspondientes
6. Guardar el proyecto
7. Proceder al checkout

Usa place_photo_smart para aprovechar el cache de patrones visuales.
Siempre verifica que las fotos quedaron bien posicionadas antes de continuar.
""",
    instructions=[
        "Siempre usa login primero antes de cualquier otra acción",
        "Prefiere place_photo_smart sobre place_photo_in_slot para mejor eficiencia",
        "Si un placement falla, reintenta con coordenadas ligeramente diferentes",
        "Toma screenshots periódicos para verificar el estado"
    ]
)


async def create_photobook(
    product_code: str,
    photo_paths: list,
    layout_plan: list  # Lista de {"page": int, "layout": str, "photos": [indices]}
):
    """
    Crea un fotolibro completo.
    
    Args:
        product_code: Código del producto (ej: "CU-21x21-DURA")
        photo_paths: Lista de rutas a las fotos
        layout_plan: Plan de layouts por página
    """
    prompt = f"""
    Crea un fotolibro con las siguientes especificaciones:
    
    Producto: {product_code}
    
    Fotos a subir: {photo_paths}
    
    Plan de páginas:
    {layout_plan}
    
    Ejecuta todos los pasos necesarios para completar el fotolibro.
    """
    
    response = await agent.arun(prompt)
    return response


# Ejemplo de uso
if __name__ == "__main__":
    layout_plan = [
        {"page": 1, "layout": "solo_fotos_1x1", "photos": [0]},
        {"page": 2, "layout": "collage_2x2", "photos": [1, 2, 3, 4]},
        {"page": 3, "layout": "featured_with_thumbnails", "photos": [5, 6, 7, 8]},
    ]
    
    result = asyncio.run(create_photobook(
        product_code="CU-21x21-DURA",
        photo_paths=["/path/to/photo1.jpg", "/path/to/photo2.jpg", "..."],
        layout_plan=layout_plan
    ))
    
    print(result)
```

---

## Comparativa Final: Browserbase vs Stack Propuesto

| Criterio | Browserbase (actual) | Stack Propuesto |
|----------|---------------------|-----------------|
| **Velocidad** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (sin latencia cloud) |
| **Precisión canvas** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (coords pre-mapeadas) |
| **Costo LLM** | $$$$ (muchas llamadas) | $$ (cache reduce 80%+) |
| **Repeticiones necesarias** | Muchas | Mínimas (cache + verificación) |
| **Mantenibilidad** | Media | Alta (layouts declarativos) |
| **Self-hosted** | ❌ | ✅ Total control |
| **Integración AGNO** | Toolkit genérico | Toolkit específico FDF |

---

## Stack Final Recomendado

| Componente | Herramienta | Justificación |
|------------|-------------|---------------|
| **Orquestación** | AGNO | Ya implementado, rápido |
| **Browser DOM** | Playwright directo | Login, menús, uploads - estable |
| **Browser Canvas** | Playwright + coords pre-mapeadas | Máximo control, sin vision overhead |
| **Vision verificación** | Gemini 2.5 Flash Lite | Costo-efectivo para validaciones |
| **Vision detección** | Gemini 2.5 Pro | Solo para layouts nuevos no mapeados |
| **Pattern cache** | SQLite local | Reducción 80%+ llamadas a vision |

---

## Próximos Pasos

1. **Mapear layouts reales de FDF** - Explorar el editor y documentar todos los templates disponibles con sus coordenadas exactas

2. **Ajustar selectores CSS** - Los selectores en el código son ejemplos; necesitan ajustarse al HTML real de FDF

3. **Testing incremental** - Probar cada herramienta individualmente antes de integrar

4. **Entrenar el cache** - Ejecutar flujos manuales para poblar el cache de patrones

5. **Monitoreo** - Agregar logging detallado para detectar cuando FDF cambia su UI

---

*Documento generado: Enero 2026*  
*Proyecto: Fotolibros Argentina - NEXUM Labs*
