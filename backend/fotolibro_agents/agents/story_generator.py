"""
StoryGenerator Agent - Generación de Textos Emotivos
Crea narrativa completa del fotolibro: títulos, dedicatorias, leyendas
"""

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from dotenv import load_dotenv
import os
import json

load_dotenv()


def create_story_generator():
    """Crea agente especializado en generación de textos emotivos"""
    
    return Agent(
        name="StoryGenerator",
        role="Escritor creativo especializado en narrativas emocionales para fotolibros",
        model=OpenRouter(
            id=os.getenv("MODEL_ID", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        ),
        instructions=[
            "Eres un escritor creativo que crea textos PROFUNDAMENTE emotivos",
            "Tu objetivo: hacer que el cliente LLORE de emoción al leer el fotolibro",
            "",
            "PRINCIPIOS FUNDAMENTALES:",
            "",
            "1. NUNCA uses descripciones genéricas",
            "   ✗ MAL: 'Fotolibro 2024', 'Vacaciones', 'Foto en la playa'",
            "   [OK] BIEN: 'Nueve Meses de Amor', 'La risa que lo cambió todo'",
            "",
            "2. Escribe MOMENTOS, no descripciones",
            "   ✗ MAL: 'Mamá y bebé en el hospital'",
            "   [OK] BIEN: 'El momento en que el mundo se detuvo y comenzaste a respirar'",
            "",
            "3. Usa lenguaje EMOCIONAL y POÉTICO",
            "   ✗ MAL: 'Viaje a Europa'",
            "   [OK] BIEN: 'Tres semanas de libertad donde descubrimos que el mundo es infinito'",
            "",
            "4. PERSONALIZA según el contexto",
            "   - Usa nombres del cliente",
            "   - Menciona hitos específicos detectados",
            "   - Habla al corazón, no a la cabeza",
            "",
            "TEXTOS QUE DEBES GENERAR:",
            "",
            "1. TÍTULO DE TAPA:",
            "   - Corto (2-6 palabras)",
            "   - Poderoso y específico",
            "   - Ejemplos: 'Nueve Meses de Amor', 'Nuestro Día Especial', 'Mi Primer Año'",
            "",
            "2. SUBTÍTULO:",
            "   - Complementa el título",
            "   - Más emotivo",
            "   - Ejemplos: 'Ana y Carlos - 2024', 'Cuando el tiempo se detuvo'",
            "",
            "3. DEDICATORIA (2-3 frases):",
            "   - Debe tocar el corazón",
            "   - Personalizada al motivo",
            "   - Ejemplos:",
            "     * Embarazo: 'Para nuestro bebé, cada día de espera fue un paso más cerca de ti...'",
            "     * Boda: 'El día que prometimos amarnos para siempre, sin saber que cada mañana nos amaríamos más'",
            "     * Viaje: 'Perderse juntos para encontrarse a sí mismos'",
            "",
            "4. LEYENDAS POR FOTO:",
            "   - UNA frase emotiva por foto",
            "   - Captura el MOMENTO, no lo que se ve",
            "   - Ejemplos:",
            "     * 'La risa que hizo que todo valiera la pena'",
            "     * 'Cuando supimos que venías en camino'",
            "     * 'El abrazo que necesitábamos sin saberlo'",
            "",
            "5. TEXTO DE CONTRATAPA:",
            "   - Cierre emocional (2-3 frases)",
            "   - Con gratitud y mirada al futuro",
            "   - Ejemplos:",
            "     * 'Cada foto es un recuerdo, cada recuerdo es un tesoro. Gracias por ser parte de nuestra historia'",
            "     * 'El tiempo pasa, las fotos quedan, pero el amor se multiplica infinitamente'",
            "",
            "6. EPÍLOGO (opcional):",
            "   - Frase final inspiradora",
            "   - Cierra con esperanza",
            "",
            "CAPÍTULOS NARRATIVOS:",
            "- Divide el fotolibro en 2-4 capítulos según el motivo",
            "- Cada capítulo tiene título emotivo",
            "- Ejemplos:",
            "  * Embarazo: 'Los Primeros Pasos' → 'La Espera' → 'Llegada al Mundo'",
            "  * Viaje: Por ciudades ('París, la Ciudad Luz' → 'Roma, Donde Vive la Historia')",
            "  * Boda: 'Preparación' → 'El Sí que Cambió Todo' → 'Bailando Hacia el Futuro'",
            "",
            "Retorna JSON con TODOS los textos generados"
        ],
        markdown=False,
    )


def generate_photobook_story(
    ordered_photos: list[dict],
    motif_info: dict,
    chronology_info: dict,
    client_context: dict
) -> dict:
    """
    Genera la narrativa completa del fotolibro
    
    Args:
        ordered_photos: Lista de fotos YA ORDENADAS cronológicamente
        motif_info: Información del motivo detectado (del MotifDetector)
        chronology_info: Información cronológica (del ChronologySpecialist)
        client_context: {
            "client_name": "Ana y Carlos",
            "recipient_name": "Nuestro bebé" (opcional),
            "year": "2024" (opcional)
        }
    
    Returns:
        dict con historia completa: títulos, dedicatoria, leyendas, etc.
    """
    agent = create_story_generator()
    
    # Extraer información del contexto
    client_name = client_context.get("client_name", "Cliente")
    motif_type = motif_info.get("motif", "generic")
    chronology_type = chronology_info.get("chronology_type", "generic")
    
    # Preparar resumen de fotos (limitar a 20 para no saturar)
    photo_summaries = []
    for i, photo in enumerate(ordered_photos[:20]):
        summary = {
            "index": i + 1,
            "filename": photo["filename"],
            "emotion": photo.get("emotion", "neutral"),
            "suggested_caption": photo.get("suggested_caption", ""),
            "importance": photo.get("importance", 5)
        }
        
        # Agregar metadata temporal si existe
        if chronology_type == "pregnancy" and "week" in photo:
            summary["week"] = photo["week"]
        elif chronology_type == "travel" and "location" in photo:
            summary["location"] = photo["location"]
        elif chronology_type == "event" and "event_phase" in photo:
            summary["phase"] = photo["event_phase"]
        elif chronology_type == "baby-first-year" and "age" in photo:
            summary["age"] = photo["age"]
        
        photo_summaries.append(summary)
    
    # Información de hitos clave
    key_moments = chronology_info.get("key_moments", [])
    key_moments_str = "\n".join([f"   - {moment}" for moment in key_moments[:5]]) if key_moments else "   (No detectados)"
    
    prompt = f"""Crea la NARRATIVA COMPLETA para un fotolibro artístico.

CONTEXTO DEL CLIENTE:
- Cliente: {client_name}
- Motivo detectado: {motif_type}
- Tipo de cronología: {chronology_type}
- Total de fotos: {len(ordered_photos)}

HITOS CLAVE DETECTADOS:
{key_moments_str}

FOTOS (primeras {len(photo_summaries)}, ya ordenadas cronológicamente):
{json.dumps(photo_summaries, indent=2, ensure_ascii=False)}

TU MISIÓN:
Crea textos que HAGAN LLORAR de emoción. No descriptions genéricas, sino MOMENTOS que toquen el alma.

IMPORTANTE:
1. El título de tapa debe ser ESPECÍFICO al motivo (no genérico)
2. La dedicatoria debe ser PERSONALIZADA y emotiva (2-3 frases)
3. Cada foto necesita UNA leyenda emotiva (no descripción)
4. Divide en capítulos narrativos (2-4 capítulos según el tipo)
5. El texto de contratapa debe cerrar con gratitud y esperanza

EJEMPLOS DE BUENOS TEXTOS:

Para EMBARAZO:
- Título: "Nueve Meses de Amor"
- Dedicatoria: "Para nuestro bebé, cada día de espera fue un paso más cerca de ti. Cuando llegaste, entendimos que el amor no tiene límites."
- Leyenda foto: "El día que supimos que venías en camino y el mundo se llenó de luz"

Para VIAJE:
- Título: "Tres Semanas de Libertad"
- Dedicatoria: "Perderse juntos para encontrarse a sí mismos. Cada ciudad fue un capítulo, cada momento una página de esta aventura."
- Leyenda foto: "París nos enseñó que la belleza vive en cada esquina"

Para BODA:
- Título: "Nuestro Día Especial"
- Dedicatoria: "El día que prometimos amarnos para siempre, sin saber que cada mañana nos amaríamos más que la anterior."
- Leyenda foto: "El momento en que dijimos 'sí' y cambiamos nuestras vidas para siempre"

Retorna JSON con formato EXACTO:
{{
  "cover": {{
    "title": "string (2-6 palabras, poderoso, específico)",
    "subtitle": "string (complementa el título)",
    "author_line": "string (ej: 'Ana y Carlos - 2024')"
  }},
  "dedication": {{
    "text": "string (2-3 frases emotivas que hagan llorar)",
    "recipient": "string (ej: 'Para nuestro bebé', 'Para mamá')"
  }},
  "chapters": [
    {{
      "title": "string (título emotivo del capítulo)",
      "emotional_tone": "string (nostálgico|alegre|romántico|esperanzador)",
      "photo_indices": [array de índices de fotos que van en este capítulo],
      "chapter_intro": "string (texto que abre el capítulo, 1 frase)"
    }}
  ],
  "photo_captions": [
    {{
      "photo_index": number,
      "caption": "string (UNA frase emotiva, NO descripción)"
    }}
  ],
  "back_cover": {{
    "text": "string (2-3 frases de cierre emotivo con gratitud)",
    "closing_quote": "string (frase final inspiradora)"
  }},
  "epilogue": "string opcional (mirada al futuro)",
  "overall_theme": "string (crecimiento|amor|aventura|familia|esperanza)"
}}

GENERA LOS TEXTOS MÁS EMOTIVOS POSIBLES:
"""
    
    try:
        print(f"\n[STORY] Generando narrativa emotiva para {motif_type}...")
        
        response = agent.run(input=prompt)
        story = json.loads(response.content)
        
        print(f"\n   [OK] Título: \"{story['cover']['title']}\"")
        print(f"   [OK] Subtítulo: \"{story['cover']['subtitle']}\"")
        print(f"   [OK] Dedicatoria generada: {len(story['dedication']['text'])} caracteres")
        print(f"   [OK] Capítulos: {len(story.get('chapters', []))}")
        print(f"   [OK] Leyendas por foto: {len(story.get('photo_captions', []))}")
        
        # Mostrar primeros capítulos
        if story.get('chapters'):
            print(f"\n   [CAPITULO] Capítulos creados:")
            for i, chapter in enumerate(story['chapters'][:3]):
                print(f"      {i+1}. \"{chapter['title']}\" ({chapter['emotional_tone']})")
        
        # Mostrar primeras leyendas
        if story.get('photo_captions'):
            print(f"\n   [CAPTION] Primeras leyendas:")
            for caption_item in story['photo_captions'][:3]:
                print(f"      Foto {caption_item['photo_index']}: \"{caption_item['caption']}\"")
        
        return {
            "success": True,
            "story": story,
            "motif_type": motif_type,
            "chronology_type": chronology_type
        }
        
    except Exception as e:
        print(f"[ERROR] Error generando narrativa: {e}")
        
        # Fallback con textos genéricos básicos
        return {
            "success": False,
            "error": str(e),
            "story": {
                "cover": {
                    "title": "Nuestros Momentos",
                    "subtitle": "Recuerdos que duran para siempre",
                    "author_line": f"{client_name}"
                },
                "dedication": {
                    "text": "Cada foto cuenta una historia, cada momento es un tesoro.",
                    "recipient": "Para ti"
                },
                "chapters": [],
                "photo_captions": [],
                "back_cover": {
                    "text": "Gracias por estos momentos inolvidables.",
                    "closing_quote": "El tiempo pasa, pero los recuerdos permanecen."
                },
                "overall_theme": "familia"
            }
        }


def generate_captions_for_photos(photos: list[dict], story_context: dict) -> list[dict]:
    """
    Genera leyendas emotivas para fotos que no tienen en la historia principal
    (función auxiliar para completar captions faltantes)
    """
    agent = create_story_generator()
    
    photos_without_captions = [
        {"index": i, "filename": p["filename"], "emotion": p.get("emotion", "neutral")}
        for i, p in enumerate(photos)
        if not p.get("caption")
    ]
    
    if not photos_without_captions:
        return photos
    
    prompt = f"""Genera leyendas EMOTIVAS (NO descripciones) para estas fotos.

Contexto: {story_context.get('motif_type', 'generic')}

Fotos sin leyenda:
{json.dumps(photos_without_captions, indent=2, ensure_ascii=False)}

Para cada foto, retorna UNA frase emotiva que capture el MOMENTO.

Retorna JSON:
{{
  "captions": [
    {{ "index": 0, "caption": "La risa que hizo que todo valiera la pena" }},
    {{ "index": 1, "caption": "Cuando el tiempo se detuvo" }},
    ...
  ]
}}
"""
    
    try:
        response = agent.run(input=prompt)
        result = json.loads(response.content)
        
        # Aplicar captions a las fotos
        for caption_item in result.get("captions", []):
            idx = caption_item["index"]
            if idx < len(photos):
                photos[idx]["caption"] = caption_item["caption"]
        
        return photos
        
    except Exception as e:
        print(f"[WARN]  Error generando captions adicionales: {e}")
        return photos
