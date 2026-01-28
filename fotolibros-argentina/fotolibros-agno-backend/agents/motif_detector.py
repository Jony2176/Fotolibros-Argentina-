"""
MotifDetector Agent - Detecta el tipo de evento/motivo del fotolibro
17 motivos posibles: boda, viaje, embarazo, baby shower, etc.
"""

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.reasoning import ReasoningTools
from dotenv import load_dotenv
import os
import json

load_dotenv()

# Configuraciones de diseño por motivo
MOTIF_CONFIGS = {
    "wedding": {
        "template": "Romántico - Flores",
        "colors": ["#FFFFFF", "#F5E6D3", "#D4AF37"],
        "decorations": ["flores", "corazones", "anillos"],
        "font_style": "elegant"
    },
    "travel": {
        "template": "Moderno - Geométrico",
        "colors": ["#4A90E2", "#50E3C2", "#F5A623"],
        "decorations": ["mapas", "brújula", "avión"],
        "font_style": "modern"
    },
    "pregnancy": {
        "template": "Romántico - Delicado",
        "colors": ["#F8E8E8", "#E8D5D5", "#D5C2C2"],
        "decorations": ["flores-delicadas", "corazones-sutiles"],
        "font_style": "elegant"
    },
    "baby-shower": {
        "template": "Divertido - Infantil",
        "colors": ["#A8E6CF", "#FFD3B6", "#FFAAA5"],
        "decorations": ["ositos", "chupetes", "nubes"],
        "font_style": "playful"
    },
    "baby-first-year": {
        "template": "Natural - Suave",
        "colors": ["#FFF8DC", "#F0E68C", "#FFE4B5"],
        "decorations": ["ositos", "nubes", "estrellas"],
        "font_style": "handwritten"
    },
    "birthday-child": {
        "template": "Divertido - Colorful",
        "colors": ["#FF6B6B", "#4ECDC4", "#FFE66D"],
        "decorations": ["globos", "confetti", "estrellas"],
        "font_style": "playful"
    },
    "mothers-day": {
        "template": "Romántico - Flores",
        "colors": ["#FFC0CB", "#FFB6C1", "#DDA0DD"],
        "decorations": ["flores", "corazones", "mariposas"],
        "font_style": "handwritten"
    },
    "fathers-day": {
        "template": "Clásico - Vintage",
        "colors": ["#2C3E50", "#34495E", "#7F8C8D"],
        "decorations": ["marcos-clasicos"],
        "font_style": "modern"
    },
    "anniversary-couple": {
        "template": "Romántico - Elegante",
        "colors": ["#8B0000", "#FFD700", "#FFFFFF"],
        "decorations": ["corazones", "flores"],
        "font_style": "elegant"
    },
    "family": {
        "template": "Clásico - Cálido",
        "colors": ["#8B4513", "#CD853F", "#DEB887"],
        "decorations": ["marcos-familiares", "corazones"],
        "font_style": "handwritten"
    },
    "pet": {
        "template": "Divertido - Natural",
        "colors": ["#8B4513", "#DEB887", "#F4A460"],
        "decorations": ["huellas", "huesos"],
        "font_style": "playful"
    },
    "generic": {
        "template": "Moderno",
        "colors": ["#FFFFFF", "#E0E0E0", "#9E9E9E"],
        "decorations": [],
        "font_style": "modern"
    }
}


def create_motif_detector():
    """Crea agente detector de motivos"""
    
    motif_list = ", ".join(MOTIF_CONFIGS.keys())
    
    return Agent(
        name="MotifDetector",
        role="Experto en detectar el tipo de evento/motivo de fotolibros",
        model=OpenRouter(
            id=os.getenv("MODEL_ID", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        ),
        tools=[ReasoningTools()],
        instructions=[
            "Eres un experto en identificar el tipo de evento basándote en análisis de fotos",
            f"Motivos posibles: {motif_list}",
            "",
            "Analiza el conjunto de fotos para detectar:",
            "- wedding: Bodas/casamientos (novia, ceremonia, anillos, fiesta)",
            "- travel: Viajes (múltiples lugares, landmarks, turismo)",
            "- pregnancy: Embarazo (barriga creciendo, ecografías, maternity)",
            "- baby-shower: Baby shower (decoraciones, juegos, regalos para bebé)",
            "- baby-first-year: Primer año del bebé (recién nacido a 12 meses)",
            "- birthday-child: Cumpleaños infantil (menores 12 años, juegos, torta)",
            "- mothers-day: Día de la madre (madre con hijos, familia)",
            "- fathers-day: Día del padre (padre con hijos)",
            "- anniversary-couple: Aniversario de pareja (momentos románticos)",
            "- family: Familia general (multi-generacional, reuniones)",
            "- pet: Mascotas (perros, gatos como sujeto principal)",
            "- generic: Sin motivo específico detectado",
            "",
            "Retorna JSON con:",
            "- motif: el código del motivo detectado",
            "- confidence: porcentaje de confianza (0-100)",
            "- evidence: por qué detectaste este motivo",
            "",
            "Sé MUY específico. Usa generic solo si realmente no está claro."
        ],
        markdown=False,
    )


def detect_event_motif(photo_analyses: list[dict], client_hint: str = None) -> dict:
    """
    Detecta el motivo del fotolibro basándose en análisis de fotos
    
    Args:
        photo_analyses: Lista de análisis de fotos del PhotoAnalyzer
        client_hint: Hint opcional del cliente sobre el tipo de evento
    
    Returns:
        dict con motivo detectado y configuración de diseño
    """
    agent = create_motif_detector()
    
    # Preparar resumen de fotos
    photo_summary = "\n".join([
        f"- Foto {i+1}: {p['emotion']}, {p['main_subject']}, personas: {p['people_count']}, caption: \"{p['suggested_caption']}\""
        for i, p in enumerate(photo_analyses[:10])  # Primeras 10 para no saturar
    ])
    
    prompt = f"""Analiza estas fotos y detecta el motivo del fotolibro.

Cliente hint: {client_hint or "No especificado"}

Fotos ({len(photo_analyses)} total):
{photo_summary}

Retorna JSON con formato EXACTO:
{{
  "motif": "string (código del motivo)",
  "confidence": number (0-100),
  "evidence": "string (por qué detectaste este motivo)"
}}
"""
    
    try:
        response = agent.run(input=prompt)
        result = json.loads(response.content)
        
        # Agregar configuración de diseño
        motif_code = result.get("motif", "generic")
        design_config = MOTIF_CONFIGS.get(motif_code, MOTIF_CONFIGS["generic"])
        
        result["design_config"] = design_config
        
        print(f"\n[MOTIF] Motivo detectado: {motif_code} ({result['confidence']}%)")
        print(f"   Evidencia: {result['evidence']}")
        print(f"   Template: {design_config['template']}")
        
        return result
        
    except Exception as e:
        print(f"[ERROR] Error detectando motivo: {e}")
        return {
            "motif": "generic",
            "confidence": 0,
            "evidence": "Error en detección",
            "design_config": MOTIF_CONFIGS["generic"]
        }
