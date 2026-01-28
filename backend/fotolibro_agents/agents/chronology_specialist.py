"""
ChronologySpecialist Agent - Ordenamiento Cronológico Inteligente
Detecta si es embarazo/viaje/evento y ordena fotos cronológicamente
"""

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
import os
import json

load_dotenv()


def create_chronology_specialist():
    """Crea agente especializado en ordenamiento cronológico"""
    
    return Agent(
        name="ChronologySpecialist",
        role="Experto en detectar y ordenar fotos cronológicamente según su contexto",
        model=OpenRouter(
            id=os.getenv("MODEL_ID", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        ),
        tools=[ReasoningTools()],
        instructions=[
            "Eres un experto en detectar contextos temporales en fotografías",
            "Tu misión: ordenar fotos cronológicamente según su tipo",
            "",
            "TIPOS DE ORDENAMIENTO:",
            "",
            "1. EMBARAZO:",
            "   - Detecta progresión de barriga (semana 8 → 40)",
            "   - Identifica hitos: ecografías, baby shower, parto",
            "   - Ordena por semanas estimadas del embarazo",
            "   - Busca: misma mujer, barriga creciendo, ecografías, newborn",
            "",
            "2. VIAJE:",
            "   - Detecta múltiples ubicaciones geográficas",
            "   - Identifica ruta lógica (París → Roma → Barcelona)",
            "   - Ordena según itinerario del viaje",
            "   - Busca: diferentes ciudades, landmarks, cambios de escenario",
            "",
            "3. EVENTO (boda, cumpleaños, graduación):",
            "   - Detecta fases del evento (preparación → ceremonia → fiesta)",
            "   - Ordena según timeline del día",
            "   - Busca: misma locación, misma ropa, progresión de iluminación",
            "",
            "4. PRIMER AÑO BEBÉ:",
            "   - Detecta progresión de edad (recién nacido → 12 meses)",
            "   - Ordena por crecimiento del bebé",
            "   - Busca: mismo bebé, cambios de tamaño, hitos (gatear, caminar)",
            "",
            "5. GENÉRICO:",
            "   - No hay progresión temporal clara",
            "   - Ordenar por importancia narrativa",
            "",
            "PROCESO:",
            "1. Analiza el conjunto completo de fotos",
            "2. Detecta tipo de progresión temporal",
            "3. Identifica hitos clave",
            "4. Ordena cronológicamente",
            "5. Asigna metadata temporal (semanas, fechas relativas, fases)",
            "",
            "Retorna JSON con:",
            "- chronology_type: pregnancy|travel|event|baby-first-year|generic",
            "- confidence: 0-100",
            "- ordered_indices: lista de índices en orden cronológico",
            "- temporal_metadata: información específica del tipo",
            "- key_moments: hitos importantes identificados"
        ],
        markdown=False,
    )


def detect_chronology_type(photo_analyses: list[dict], motif_hint: str = None) -> dict:
    """
    Detecta el tipo de cronología y ordena fotos inteligentemente
    
    Args:
        photo_analyses: Lista de análisis de fotos del PhotoAnalyzer
        motif_hint: Hint del motivo detectado (opcional)
    
    Returns:
        dict con tipo de cronología, fotos ordenadas y metadata temporal
    """
    agent = create_chronology_specialist()
    
    # Preparar resumen de fotos (primeras 15 para no saturar)
    photo_summary = "\n".join([
        f"- Foto {i}: {p['emotion']}, {p['main_subject']}, personas: {p['people_count']}, "
        f"caption: \"{p['suggested_caption']}\", archivo: {p['filename']}"
        for i, p in enumerate(photo_analyses[:15])
    ])
    
    prompt = f"""Analiza este conjunto de fotos y determina el mejor ordenamiento cronológico.

Motivo detectado: {motif_hint or "No especificado"}

Fotos ({len(photo_analyses)} total):
{photo_summary}

Determina:
1. ¿Qué tipo de progresión temporal tiene este álbum?
2. ¿Cuál es el orden cronológico correcto?
3. ¿Qué hitos clave hay en la historia?

Retorna JSON con formato EXACTO:
{{
  "chronology_type": "pregnancy|travel|event|baby-first-year|generic",
  "confidence": number (0-100),
  "evidence": "string (por qué detectaste este tipo)",
  "ordered_indices": [array de números - índices en orden cronológico],
  "temporal_metadata": {{
    // Para embarazo:
    "weeks": [8, 12, 16, 20, ...],
    "milestones": ["Primera ecografía", "Baby shower", "Parto"],
    
    // Para viaje:
    "route": ["Madrid", "Barcelona", "Valencia"],
    "locations_per_photo": ["Madrid", "Madrid", "Barcelona", ...],
    
    // Para evento:
    "phases": ["Preparación", "Ceremonia", "Fiesta", "Despedida"],
    "phase_per_photo": ["Preparación", "Preparación", "Ceremonia", ...],
    
    // Para baby-first-year:
    "ages": ["Recién nacido", "1 mes", "2 meses", ...],
    "milestones": ["Primer sonrisa", "Primer diente", "Gatear"]
  }},
  "key_moments": [
    "string (descripción del hito)",
    "otro hito"
  ]
}}

IMPORTANTE: 
- ordered_indices debe contener TODOS los índices del 0 al {len(photo_analyses) - 1}
- Cada índice debe aparecer UNA sola vez
- El orden debe ser cronológico según el tipo detectado
"""
    
    try:
        response = agent.run(input=prompt)
        result = json.loads(response.content)
        
        chronology_type = result.get("chronology_type", "generic")
        confidence = result.get("confidence", 0)
        
        print(f"\n[CHRONO] Tipo de cronología detectado: {chronology_type} ({confidence}%)")
        print(f"   Evidencia: {result.get('evidence', 'N/A')}")
        
        # Validar que ordered_indices tiene todos los índices
        ordered_indices = result.get("ordered_indices", list(range(len(photo_analyses))))
        if len(ordered_indices) != len(photo_analyses):
            print(f"   [WARN]  Advertencia: Faltan índices, usando orden original")
            ordered_indices = list(range(len(photo_analyses)))
        
        # Reordenar fotos según los índices
        ordered_photos = [photo_analyses[i] for i in ordered_indices]
        
        # Agregar metadata temporal a cada foto
        temporal_metadata = result.get("temporal_metadata", {})
        for i, photo in enumerate(ordered_photos):
            if chronology_type == "pregnancy" and "weeks" in temporal_metadata:
                photo["week"] = temporal_metadata["weeks"][i] if i < len(temporal_metadata["weeks"]) else None
            elif chronology_type == "travel" and "locations_per_photo" in temporal_metadata:
                photo["location"] = temporal_metadata["locations_per_photo"][i] if i < len(temporal_metadata["locations_per_photo"]) else None
            elif chronology_type == "event" and "phase_per_photo" in temporal_metadata:
                photo["event_phase"] = temporal_metadata["phase_per_photo"][i] if i < len(temporal_metadata["phase_per_photo"]) else None
            elif chronology_type == "baby-first-year" and "ages" in temporal_metadata:
                photo["age"] = temporal_metadata["ages"][i] if i < len(temporal_metadata["ages"]) else None
        
        # Mostrar hitos clave
        key_moments = result.get("key_moments", [])
        if key_moments:
            print(f"\n   [HITO] Hitos clave identificados:")
            for moment in key_moments[:5]:  # Primeros 5
                print(f"      - {moment}")
        
        # Mostrar primeras 5 fotos en orden cronológico
        print(f"\n   [FOTO] Primeras 5 fotos en orden cronológico:")
        for i, photo in enumerate(ordered_photos[:5]):
            extra_info = ""
            if chronology_type == "pregnancy" and "week" in photo:
                extra_info = f" (Semana ~{photo['week']})"
            elif chronology_type == "travel" and "location" in photo:
                extra_info = f" ({photo['location']})"
            elif chronology_type == "event" and "event_phase" in photo:
                extra_info = f" ({photo['event_phase']})"
            elif chronology_type == "baby-first-year" and "age" in photo:
                extra_info = f" ({photo['age']})"
            
            print(f"      {i+1}. {photo['filename']}{extra_info}")
        
        return {
            "chronology_type": chronology_type,
            "confidence": confidence,
            "evidence": result.get("evidence", ""),
            "ordered_photos": ordered_photos,
            "temporal_metadata": temporal_metadata,
            "key_moments": key_moments,
            "original_indices": ordered_indices
        }
        
    except Exception as e:
        print(f"[ERROR] Error detectando cronología: {e}")
        # Fallback: mantener orden original
        return {
            "chronology_type": "generic",
            "confidence": 0,
            "evidence": f"Error en detección: {str(e)}",
            "ordered_photos": photo_analyses,
            "temporal_metadata": {},
            "key_moments": [],
            "original_indices": list(range(len(photo_analyses)))
        }


def order_by_pregnancy_weeks(photo_analyses: list[dict]) -> dict:
    """
    Ordenamiento especializado para álbumes de embarazo
    (Función auxiliar para casos específicos)
    """
    agent = create_chronology_specialist()
    
    photo_summary = "\n".join([
        f"- Foto {i}: {p['filename']}, {p['main_subject']}, personas: {p['people_count']}"
        for i, p in enumerate(photo_analyses)
    ])
    
    prompt = f"""Estas fotos son de un EMBARAZO. Ordénalas cronológicamente por semanas.

Fotos:
{photo_summary}

Analiza:
- Tamaño de barriga (flat → pequeña → grande → muy grande)
- Ecografías (semanas tempranas)
- Fotos de newborn/parto (semana 40+)
- Baby shower (típicamente semanas 30-35)

Retorna JSON:
{{
  "ordered_indices": [índices del 0 al {len(photo_analyses)-1} en orden cronológico],
  "weeks": [semana estimada para cada foto en el nuevo orden],
  "milestones": ["Primera ecografía semana 12", "Baby shower semana 32", "Parto semana 40"]
}}
"""
    
    try:
        response = agent.run(input=prompt)
        result = json.loads(response.content)
        
        ordered_indices = result.get("ordered_indices", list(range(len(photo_analyses))))
        ordered_photos = [photo_analyses[i] for i in ordered_indices]
        
        # Agregar semanas a cada foto
        weeks = result.get("weeks", [])
        for i, photo in enumerate(ordered_photos):
            photo["week"] = weeks[i] if i < len(weeks) else None
        
        return {
            "ordered_photos": ordered_photos,
            "weeks": weeks,
            "milestones": result.get("milestones", [])
        }
        
    except Exception as e:
        print(f"[ERROR] Error en ordenamiento de embarazo: {e}")
        return {
            "ordered_photos": photo_analyses,
            "weeks": [],
            "milestones": []
        }
