"""
DesignCurator Agent - Curación Artística de Diseño
Toma decisiones de diseño como un diseñador profesional
"""

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
import os
import json

load_dotenv()


def create_design_curator():
    """Crea agente especializado en curación artística"""
    
    return Agent(
        name="DesignCurator",
        role="Diseñador gráfico experto en curaduría artística de fotolibros",
        model=OpenRouter(
            id=os.getenv("MODEL_ID", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        ),
        tools=[ReasoningTools()],
        instructions=[
            "Eres un diseñador gráfico profesional especializado en fotolibros artísticos",
            "Tu misión: tomar decisiones de diseño que eleven el fotolibro a OBRA DE ARTE",
            "",
            "PRINCIPIOS DE DISEÑO:",
            "",
            "1. CALIDAD SOBRE CANTIDAD",
            "   - Mejor 20 fotos bien diseñadas que 100 mediocres",
            "   - Cada página debe tener calidad mínima de 8/10",
            "   - Si una foto no aporta, NO la incluyas",
            "",
            "2. RESPIRO VISUAL",
            "   - NO satures cada página con fotos",
            "   - Deja páginas en blanco intencionalmente (respiro)",
            "   - Alterna páginas hero (1 foto grande) con collages",
            "",
            "3. COHERENCIA ARTÍSTICA",
            "   - Template debe reflejar la emoción dominante",
            "   - Paleta de colores consistente en todo el libro",
            "   - Tipografía acorde al mood (elegante/playful/moderno)",
            "",
            "4. JERARQUÍA VISUAL",
            "   - Fotos de alta importancia → páginas hero (full page)",
            "   - Fotos complementarias → collages",
            "   - Momentos clave → máximo destaque",
            "",
            "5. DECORACIONES CON PROPÓSITO",
            "   - Clip-arts solo si aportan al tema (bodas: flores, viajes: mapas)",
            "   - Estilo minimal para fotos artísticas",
            "   - Estilo ornate para eventos formales",
            "",
            "DECISIONES QUE DEBES TOMAR:",
            "",
            "1. SELECCIÓN DE TEMPLATE:",
            "   - Analiza emoción dominante + motivo",
            "   - Elige template que mejor exprese el alma del fotolibro",
            "   - Opciones: Romántico, Moderno, Clásico, Divertido, Natural, Elegante",
            "",
            "2. ESTRATEGIA DE LAYOUT:",
            "   - Identifica fotos para páginas HERO (importancia ≥8)",
            "   - Agrupa fotos complementarias en COLLAGES",
            "   - Planifica RESPIROS (páginas vacías entre secciones)",
            "",
            "3. PALETA DE COLORES:",
            "   - Extrae colores dominantes de las fotos",
            "   - Define primario, secundario, acento",
            "   - Mood: warm/cool/vibrant/muted",
            "",
            "4. TIPOGRAFÍA:",
            "   - Estilo de fuente según emoción:",
            "     * elegant: bodas, aniversarios, graduaciones",
            "     * playful: cumpleaños infantil, mascotas",
            "     * modern: viajes, empresarial",
            "     * handwritten: familia, bebés",
            "",
            "5. DECORACIONES:",
            "   - ¿Usar clip-arts? (solo si aportan)",
            "   - ¿Qué tipo? (flores, corazones, mapas, globos, etc.)",
            "   - Estilo: minimal|ornate|modern",
            "",
            "6. OBJETIVOS DE CALIDAD:",
            "   - Calidad mínima por página: 8/10",
            "   - Impacto emocional objetivo: 9/10",
            "   - Coherencia del diseño: 8/10",
            "",
            "Retorna JSON con TODAS las decisiones de diseño"
        ],
        markdown=False,
    )


def curate_design(
    ordered_photos: list[dict],
    motif_info: dict,
    story_info: dict,
    chronology_info: dict
) -> dict:
    """
    Genera decisiones completas de diseño artístico
    
    Args:
        ordered_photos: Fotos ordenadas cronológicamente
        motif_info: Información del motivo (del MotifDetector)
        story_info: Narrativa generada (del StoryGenerator)
        chronology_info: Info cronológica (del ChronologySpecialist)
    
    Returns:
        dict con decisiones de diseño completas
    """
    agent = create_design_curator()
    
    # Extraer información clave
    motif_type = motif_info.get("motif", "generic")
    design_config = motif_info.get("design_config", {})
    overall_theme = story_info.get("story", {}).get("overall_theme", "familia")
    
    # Analizar perfil emocional del álbum
    emotions = [p.get("emotion", "neutral") for p in ordered_photos]
    emotion_counts = {}
    for emotion in emotions:
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    dominant_emotion = max(emotion_counts, key=emotion_counts.get)
    
    # Calcular importancia promedio
    importances = [p.get("importance", 5) for p in ordered_photos]
    avg_importance = sum(importances) / len(importances) if importances else 5
    
    # Preparar resumen de fotos (primeras 15)
    photo_summaries = []
    for i, photo in enumerate(ordered_photos[:15]):
        summary = {
            "index": i,
            "filename": photo["filename"],
            "emotion": photo.get("emotion", "neutral"),
            "importance": photo.get("importance", 5),
            "composition_quality": photo.get("composition_quality", 5),
            "main_subject": photo.get("main_subject", "unknown")
        }
        photo_summaries.append(summary)
    
    prompt = f"""Cura el DISEÑO ARTÍSTICO completo de este fotolibro.

CONTEXTO:
- Motivo detectado: {motif_type}
- Emoción dominante: {dominant_emotion}
- Tema general: {overall_theme}
- Total de fotos: {len(ordered_photos)}
- Importancia promedio: {avg_importance:.1f}/10

CONFIGURACIÓN SUGERIDA DEL MOTIVO:
- Template sugerido: {design_config.get('template', 'Moderno')}
- Colores sugeridos: {design_config.get('colors', [])}
- Decoraciones sugeridas: {design_config.get('decorations', [])}
- Estilo de fuente: {design_config.get('font_style', 'modern')}

FOTOS (primeras {len(photo_summaries)}):
{json.dumps(photo_summaries, indent=2, ensure_ascii=False)}

TU MISIÓN:
Toma decisiones de diseño que conviertan este fotolibro en una OBRA DE ARTE.

IMPORTANTE:
1. Selecciona el template ÓPTIMO (puede coincidir o no con el sugerido)
2. Planifica layout página por página (hero/collage/respiro)
3. Define paleta de colores coherente
4. Decide decoraciones con propósito (no por defecto)
5. Establece objetivos de calidad altos (mínimo 8/10 por página)

Retorna JSON con formato EXACTO:
{{
  "template_choice": {{
    "primary": "string (nombre del template elegido)",
    "reasoning": "string (por qué elegiste este template)",
    "backup_options": ["template alternativo 1", "template alternativo 2"]
  }},
  "layout_strategy": {{
    "hero_pages": [array de índices de fotos que deben ser full-page],
    "collage_pages": [
      {{ "photos": [índices], "layout": "2-grid|3-grid|4-grid" }}
    ],
    "empty_pages": [índices donde dejar respiro visual],
    "page_assignments": [
      {{
        "page_number": number,
        "photo_indices": [array de índices],
        "layout_type": "hero|collage|empty",
        "reasoning": "por qué esta distribución"
      }}
    ]
  }},
  "color_scheme": {{
    "primary": "color hex (color principal extraído de fotos)",
    "secondary": "color hex (secundario)",
    "accent": "color hex (acento)",
    "mood": "warm|cool|vibrant|muted",
    "reasoning": "por qué esta paleta"
  }},
  "typography": {{
    "font_style": "elegant|playful|modern|handwritten",
    "reasoning": "por qué este estilo",
    "size_hierarchy": {{
      "cover_title": "large|xlarge",
      "chapter_titles": "medium|large",
      "captions": "small|medium"
    }}
  }},
  "decorations": {{
    "use_cliparts": boolean,
    "clipart_types": [array de strings si use_cliparts=true],
    "use_backgrounds": boolean,
    "use_frames": boolean,
    "style": "minimal|ornate|modern",
    "reasoning": "por qué estas decoraciones"
  }},
  "quality_targets": {{
    "minimum_page_quality": number (8-10),
    "emotional_impact": number (8-10),
    "coherence_score": number (8-10)
  }},
  "design_notes": "string (notas adicionales para el diseñador/sistema)"
}}

GENERA LAS MEJORES DECISIONES ARTÍSTICAS:
"""
    
    try:
        print(f"\n[DESIGN] Curando diseño artístico para {motif_type}...")
        
        response = agent.run(input=prompt)
        design = json.loads(response.content)
        
        print(f"\n   [OK] Template: {design['template_choice']['primary']}")
        print(f"      Razón: {design['template_choice']['reasoning']}")
        
        print(f"\n   [OK] Layout:")
        print(f"      Páginas hero: {len(design['layout_strategy'].get('hero_pages', []))}")
        print(f"      Páginas collage: {len(design['layout_strategy'].get('collage_pages', []))}")
        print(f"      Respiros: {len(design['layout_strategy'].get('empty_pages', []))}")
        
        print(f"\n   [OK] Paleta de colores:")
        print(f"      Primario: {design['color_scheme']['primary']}")
        print(f"      Mood: {design['color_scheme']['mood']}")
        
        print(f"\n   [OK] Tipografía: {design['typography']['font_style']}")
        
        print(f"\n   [OK] Decoraciones:")
        print(f"      Clip-arts: {design['decorations']['use_cliparts']}")
        if design['decorations']['use_cliparts']:
            print(f"      Tipos: {', '.join(design['decorations'].get('clipart_types', []))}")
        print(f"      Estilo: {design['decorations']['style']}")
        
        print(f"\n   [OK] Objetivos de calidad:")
        print(f"      Calidad mínima/página: {design['quality_targets']['minimum_page_quality']}/10")
        print(f"      Impacto emocional: {design['quality_targets']['emotional_impact']}/10")
        
        return {
            "success": True,
            "design": design,
            "motif_type": motif_type,
            "dominant_emotion": dominant_emotion
        }
        
    except Exception as e:
        print(f"[ERROR] Error curando diseño: {e}")
        
        # Fallback con decisiones básicas
        return {
            "success": False,
            "error": str(e),
            "design": {
                "template_choice": {
                    "primary": design_config.get("template", "Moderno"),
                    "reasoning": "Fallback por error en curación",
                    "backup_options": ["Clásico", "Natural"]
                },
                "layout_strategy": {
                    "hero_pages": [i for i, p in enumerate(ordered_photos) if p.get("importance", 5) >= 8],
                    "collage_pages": [],
                    "empty_pages": [],
                    "page_assignments": []
                },
                "color_scheme": {
                    "primary": design_config.get("colors", ["#FFFFFF"])[0],
                    "secondary": "#E0E0E0",
                    "accent": "#9E9E9E",
                    "mood": "neutral",
                    "reasoning": "Colores por defecto"
                },
                "typography": {
                    "font_style": design_config.get("font_style", "modern"),
                    "reasoning": "Estilo por defecto del motivo",
                    "size_hierarchy": {
                        "cover_title": "xlarge",
                        "chapter_titles": "large",
                        "captions": "medium"
                    }
                },
                "decorations": {
                    "use_cliparts": len(design_config.get("decorations", [])) > 0,
                    "clipart_types": design_config.get("decorations", []),
                    "use_backgrounds": False,
                    "use_frames": False,
                    "style": "minimal",
                    "reasoning": "Decoraciones básicas del motivo"
                },
                "quality_targets": {
                    "minimum_page_quality": 8,
                    "emotional_impact": 9,
                    "coherence_score": 8
                },
                "design_notes": "Diseño generado con fallback por error"
            }
        }


def suggest_page_layouts(photos: list[dict], design_decisions: dict) -> list[dict]:
    """
    Genera layout sugerido página por página
    (Función auxiliar para planificación detallada)
    """
    hero_indices = set(design_decisions.get("layout_strategy", {}).get("hero_pages", []))
    
    pages = []
    current_page = 1
    photo_idx = 0
    
    while photo_idx < len(photos):
        if photo_idx in hero_indices:
            # Página hero: 1 foto completa
            pages.append({
                "page_number": current_page,
                "layout_type": "hero",
                "photos": [photo_idx],
                "caption": photos[photo_idx].get("caption", "")
            })
            photo_idx += 1
        else:
            # Página collage: 2-4 fotos
            num_photos = min(4, len(photos) - photo_idx)
            page_photos = list(range(photo_idx, photo_idx + num_photos))
            
            pages.append({
                "page_number": current_page,
                "layout_type": "collage",
                "photos": page_photos,
                "layout_grid": f"{num_photos}-grid"
            })
            photo_idx += num_photos
        
        current_page += 1
    
    return pages
