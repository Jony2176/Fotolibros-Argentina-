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
import base64

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
            "[OK] 'El día que supimos que venías'",
            "[OK] 'La risa que lo cambió todo'",
            "[OK] 'Cuando el mundo se detuvo'",
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
        print(f"\n[FOTO] Analizando foto {idx + 1}/{len(photo_paths)}: {os.path.basename(photo_path)}")
        
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
            # Convertir imagen a base64 data URL
            with open(photo_path, 'rb') as f:
                img_data = base64.b64encode(f.read()).decode('utf-8')
                # Detectar tipo MIME
                ext = os.path.splitext(photo_path)[1].lower()
                mime_types = {
                    '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                    '.png': 'image/png', '.gif': 'image/gif',
                    '.webp': 'image/webp'
                }
                mime_type = mime_types.get(ext, 'image/jpeg')
                data_url = f"data:{mime_type};base64,{img_data}"
            
            response = agent.run(
                input=prompt,
                images=[Image(url=data_url)]
            )
            
            # Parsear JSON response
            analysis = json.loads(response.content)
            analysis["filepath"] = photo_path
            analysis["filename"] = os.path.basename(photo_path)
            
            analyses.append(analysis)
            
            print(f"   [OK] Emoción: {analysis['emotion']} ({analysis['intensity']}/10)")
            print(f"   [OK] Calidad: {analysis['composition_quality']}/10")
            print(f"   [OK] Título: \"{analysis['suggested_caption']}\"")
            
        except Exception as e:
            print(f"   [ERROR] Error: {e}")
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
