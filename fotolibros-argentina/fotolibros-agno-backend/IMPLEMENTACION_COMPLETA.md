# 🎨 Sistema AGNO Team + Stagehand - Implementación Completa

## ✅ ESTADO ACTUAL

He creado la estructura base del proyecto. Ahora necesitas completar la instalación y crear los archivos de código.

## 📂 Estructura Creada

```
fotolibros-agno-backend/
├── .env                    ← Configurado con tu API key
├── .env.example            ← Template para otros desarrolladores
├── requirements.txt        ← Dependencias Python
├── agents/                 ← Agentes especializados (a crear)
├── data/                   ← Base de datos y outputs
└── IMPLEMENTACION_COMPLETA.md  ← Este archivo
```

---

## 🚀 PASO 1: Instalación

### 1.1 Crear entorno virtual

```bash
cd C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-agno-backend

# Crear entorno virtual
python -m venv .venv

# Activar (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install agno python-dotenv pillow
```

---

## 📝 PASO 2: Crear Agentes Especializados

Crea los siguientes archivos en la carpeta `agents/`:

### agents/photo_analyzer.py

```python
"""
PhotoAnalyzer Agent - Análisis Emocional de Fotos
Usa Vision AI para detectar emociones, composición y contenido
"""

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.media import Image
from dotenv import load_dotenv
import os
import json

load_dotenv()

def create_photo_analyzer():
    """Crea agente especializado en análisis de fotos"""
    
    return Agent(
        name="PhotoAnalyzer",
        role="Experto en análisis emocional y compositivo de fotografías",
        model=OpenRouter(
            id=os.getenv("MODEL_ID", "openai/gpt-4o-mini"),
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        ),
        instructions=[
            "Eres un experto en análisis emocional de fotografías",
            "Analiza cada foto para detectar:",
            "1. Emoción dominante (alegría, amor, nostalgia, paz, emoción)",
            "2. Intensidad emocional (1-10)",
            "3. Calidad compositiva (1-10) según regla de tercios, iluminación, balance",
            "4. Contenido: cantidad de personas, caras visibles, sujeto principal",
            "5. Importancia narrativa (1-10): ¿Es una foto clave o complementaria?",
            "6. Título emotivo sugerido (NO descripciones, sino MOMENTOS)",
            "",
            "EJEMPLOS DE BUENOS TÍTULOS:",
            "✓ 'El día que supimos que venías'",
            "✓ 'La risa que lo cambió todo'",
            "✓ 'Cuando el mundo se detuvo'",
            "",
            "EJEMPLOS DE MALOS TÍTULOS:",
            "✗ 'Foto en la playa'",
            "✗ 'Mamá y bebé'",
            "✗ 'Cumpleaños'",
            "",
            "Retorna SIEMPRE un objeto JSON válido con todos los campos"
        ],
        markdown=False,
    )


def analyze_photo_batch(photo_paths: list[str], client_name: str = "Cliente") -> dict:
    """
    Analiza un batch de fotos usando el agente PhotoAnalyzer
    
    Args:
        photo_paths: Lista de rutas absolutas a las fotos
        client_name: Nombre del cliente (para contexto)
    
    Returns:
        dict con análisis de cada foto
    """
    agent = create_photo_analyzer()
    
    analyses = []
    
    for idx, photo_path in enumerate(photo_paths):
        print(f"\n📸 Analizando foto {idx + 1}/{len(photo_paths)}: {os.path.basename(photo_path)}")
        
        # Preparar prompt con imagen
        prompt = f"""Analiza esta fotografía para {client_name}.

Retorna un JSON con el siguiente formato EXACTO:
{{
  "emotion": "string (alegría|amor|nostalgia|paz|emoción|aventura)",
  "intensity": number (1-10),
  "composition_quality": number (1-10),
  "people_count": number,
  "has_faces": boolean,
  "main_subject": "string (retrato|paisaje|grupo|objeto|mascota)",
  "importance": number (1-10),
  "suggested_caption": "string (título emotivo, NO descripción)"
}}

Foto: {os.path.basename(photo_path)}
"""
        
        try:
            response = agent.run(
                message=prompt,
                images=[Image(url=f"file://{photo_path}")]
            )
            
            # Parsear JSON response
            analysis = json.loads(response.content)
            analysis["filepath"] = photo_path
            analysis["filename"] = os.path.basename(photo_path)
            
            analyses.append(analysis)
            
            print(f"   ✓ Emoción: {analysis['emotion']} ({analysis['intensity']}/10)")
            print(f"   ✓ Calidad: {analysis['composition_quality']}/10")
            print(f"   ✓ Título: \"{analysis['suggested_caption']}\"")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            # Fallback
            analyses.append({
                "filepath": photo_path,
                "filename": os.path.basename(photo_path),
                "emotion": "neutral",
                "intensity": 5,
                "composition_quality": 5,
                "people_count": 0,
                "has_faces": False,
                "main_subject": "unknown",
                "importance": 5,
                "suggested_caption": os.path.basename(photo_path)
            })
    
    return {
        "photos": analyses,
        "total": len(analyses),
        "client_name": client_name
    }
```

### agents/motif_detector.py

```python
"""
MotifDetector Agent - Detecta el tipo de evento/motivo del fotolibro
17 motivos posibles: boda, viaje, embarazo, baby shower, etc.
"""

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
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
        response = agent.run(message=prompt)
        result = json.loads(response.content)
        
        # Agregar configuración de diseño
        motif_code = result.get("motif", "generic")
        design_config = MOTIF_CONFIGS.get(motif_code, MOTIF_CONFIGS["generic"])
        
        result["design_config"] = design_config
        
        print(f"\n🎯 Motivo detectado: {motif_code} ({result['confidence']}%)")
        print(f"   Evidencia: {result['evidence']}")
        print(f"   Template: {design_config['template']}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error detectando motivo: {e}")
        return {
            "motif": "generic",
            "confidence": 0,
            "evidence": "Error en detección",
            "design_config": MOTIF_CONFIGS["generic"]
        }
```

---

## CONTINÚA...

El archivo es demasiado largo. He creado la estructura base y los 2 primeros agentes.

**Para continuar:**

1. ¿Quieres que cree el resto de los archivos (3 agentes más + team + main)?
2. ¿O prefieres que te dé el código para que lo copies manualmente?
3. ¿O creo un repositorio Git con todo el código completo?

El sistema completo incluiría:
- ✅ PhotoAnalyzer (creado arriba)
- ✅ MotifDetector (creado arriba)
- ⏳ ChronologySpecialist
- ⏳ StoryGenerator
- ⏳ DesignCurator
- ⏳ FotolibroTeam (coordina todos)
- ⏳ main.py (punto de entrada)
- ⏳ Executor en TypeScript para Stagehand

**¿Cómo prefieres continuar?**
