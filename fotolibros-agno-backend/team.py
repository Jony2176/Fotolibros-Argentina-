"""
AGNO Team - Equipo de Agentes Coordinados
Coordina los 5 agentes especializados para crear fotolibros artísticos
"""

from agno.team import Team
from dotenv import load_dotenv
import os

# Importar funciones de creación de agentes
from agents.photo_analyzer import create_photo_analyzer
from agents.motif_detector import create_motif_detector
from agents.chronology_specialist import create_chronology_specialist
from agents.story_generator import create_story_generator
from agents.design_curator import create_design_curator

load_dotenv()


def create_fotolibro_team():
    """
    Crea el equipo coordinado de agentes para fotolibros artísticos
    
    El equipo trabaja en 5 fases secuenciales:
    1. PhotoAnalyzer: Analiza cada foto (emoción, composición, contenido)
    2. MotifDetector: Detecta tipo de evento (17 motivos)
    3. ChronologySpecialist: Ordena cronológicamente
    4. StoryGenerator: Genera textos emotivos
    5. DesignCurator: Toma decisiones de diseño
    """
    
    # Crear los 5 agentes especializados
    photo_analyzer = create_photo_analyzer()
    motif_detector = create_motif_detector()
    chronology_specialist = create_chronology_specialist()
    story_generator = create_story_generator()
    design_curator = create_design_curator()
    
    # Crear team coordinado
    team = Team(
        name="FotolibroArtisticoTeam",
        description="Equipo de agentes especializados que crea fotolibros artísticos con alma y emoción",
        mode="coordinate",  # Modo coordinado: un líder coordina las 5 fases
        members=[
            photo_analyzer,
            motif_detector,
            chronology_specialist,
            story_generator,
            design_curator
        ],
        instructions=[
            "Este equipo crea fotolibros artísticos PROFUNDAMENTE emotivos",
            "NO son productos genéricos, son OBRAS DE ARTE personalizadas",
            "",
            "FLUJO DE TRABAJO (5 FASES SECUENCIALES):",
            "",
            "FASE 1 - ANÁLISIS DE FOTOS (PhotoAnalyzer):",
            "  - Analiza CADA foto con Vision AI",
            "  - Detecta: emoción, composición, contenido, importancia",
            "  - Genera títulos emotivos sugeridos",
            "  - Output: análisis completo por foto",
            "",
            "FASE 2 - DETECCIÓN DE MOTIVO (MotifDetector):",
            "  - Analiza conjunto completo de fotos",
            "  - Detecta motivo específico (17 opciones)",
            "  - Carga configuración de diseño del motivo",
            "  - Output: motivo + confidence + design_config",
            "",
            "FASE 3 - ORDENAMIENTO CRONOLÓGICO (ChronologySpecialist):",
            "  - Detecta tipo de cronología (embarazo/viaje/evento/generic)",
            "  - Ordena fotos cronológicamente",
            "  - Identifica hitos clave",
            "  - Output: fotos ordenadas + metadata temporal",
            "",
            "FASE 4 - GENERACIÓN DE TEXTOS (StoryGenerator):",
            "  - Usa fotos YA ORDENADAS cronológicamente",
            "  - Genera textos PROFUNDAMENTE emotivos:",
            "    * Título de tapa (poderoso, específico)",
            "    * Dedicatoria personalizada (hace llorar)",
            "    * Leyendas por foto (momentos, NO descripciones)",
            "    * Capítulos narrativos",
            "    * Texto de contratapa (cierre emotivo)",
            "  - Output: narrativa completa del fotolibro",
            "",
            "FASE 5 - CURACIÓN DE DISEÑO (DesignCurator):",
            "  - Toma decisiones artísticas como diseñador profesional",
            "  - Selecciona template óptimo",
            "  - Planifica layout (hero/collage/respiro)",
            "  - Define paleta de colores",
            "  - Selecciona decoraciones",
            "  - Output: blueprint completo del diseño",
            "",
            "RESULTADO FINAL:",
            "  - JSON con configuración completa del fotolibro",
            "  - Listo para ejecutar en Stagehand + FDF",
            "",
            "PRINCIPIOS CLAVE:",
            "  - Calidad > Cantidad (mejor 20 fotos bien diseñadas que 100 mediocres)",
            "  - Textos emotivos > Descripciones genéricas",
            "  - Orden cronológico lógico > Orden alfabético",
            "  - Diseño artístico > Template por defecto",
            "  - Objetivo: HACER LLORAR de emoción al cliente"
        ],
        markdown=False
    )
    
    return team


def process_fotolibro(
    photo_paths: list[str],
    client_context: dict,
    output_path: str = None
) -> dict:
    """
    Procesa un fotolibro completo usando el equipo AGNO
    
    Args:
        photo_paths: Lista de rutas absolutas a las fotos
        client_context: {
            "client_name": "Ana y Carlos",
            "recipient_name": "Nuestro bebé" (opcional),
            "hint": "pregnancy" (opcional),
            "year": "2024" (opcional)
        }
        output_path: Ruta donde guardar fotolibro_config.json (opcional)
    
    Returns:
        dict con configuración completa del fotolibro
    """
    
    print("="*80)
    print("  🎨 AGNO TEAM - SISTEMA DE FOTOLIBROS ARTÍSTICOS")
    print("="*80)
    print(f"\n  📸 Procesando {len(photo_paths)} fotos")
    print(f"  👤 Cliente: {client_context.get('client_name', 'Cliente')}")
    if client_context.get('hint'):
        print(f"  💡 Hint: {client_context['hint']}")
    print()
    
    # Importar funciones individuales de cada agente
    from agents.photo_analyzer import analyze_photo_batch
    from agents.motif_detector import detect_event_motif
    from agents.chronology_specialist import detect_chronology_type
    from agents.story_generator import generate_photobook_story
    from agents.design_curator import curate_design
    
    try:
        # FASE 1: Análisis de fotos
        print("\n" + "="*80)
        print("  FASE 1/5: ANÁLISIS EMOCIONAL DE FOTOS")
        print("="*80)
        
        photo_analyses = analyze_photo_batch(
            photo_paths,
            client_context.get('client_name', 'Cliente')
        )
        
        print(f"\n  ✅ Análisis completado: {photo_analyses['total']} fotos procesadas")
        
        # FASE 2: Detección de motivo
        print("\n" + "="*80)
        print("  FASE 2/5: DETECCIÓN DE MOTIVO DEL FOTOLIBRO")
        print("="*80)
        
        motif_info = detect_event_motif(
            photo_analyses['photos'],
            client_context.get('hint')
        )
        
        print(f"\n  ✅ Motivo detectado: {motif_info['motif']} ({motif_info['confidence']}%)")
        
        # FASE 3: Ordenamiento cronológico
        print("\n" + "="*80)
        print("  FASE 3/5: ORDENAMIENTO CRONOLÓGICO INTELIGENTE")
        print("="*80)
        
        chronology_info = detect_chronology_type(
            photo_analyses['photos'],
            motif_info['motif']
        )
        
        print(f"\n  ✅ Cronología: {chronology_info['chronology_type']}")
        print(f"      Fotos reordenadas: {len(chronology_info['ordered_photos'])}")
        
        # FASE 4: Generación de textos emotivos
        print("\n" + "="*80)
        print("  FASE 4/5: GENERACIÓN DE TEXTOS EMOTIVOS")
        print("="*80)
        
        story_info = generate_photobook_story(
            chronology_info['ordered_photos'],
            motif_info,
            chronology_info,
            client_context
        )
        
        if story_info['success']:
            print(f"\n  ✅ Narrativa generada exitosamente")
        else:
            print(f"\n  ⚠️  Narrativa generada con fallback")
        
        # FASE 5: Curación de diseño
        print("\n" + "="*80)
        print("  FASE 5/5: CURACIÓN ARTÍSTICA DE DISEÑO")
        print("="*80)
        
        design_info = curate_design(
            chronology_info['ordered_photos'],
            motif_info,
            story_info,
            chronology_info
        )
        
        if design_info['success']:
            print(f"\n  ✅ Diseño curado exitosamente")
        else:
            print(f"\n  ⚠️  Diseño curado con fallback")
        
        # RESULTADO FINAL
        print("\n" + "="*80)
        print("  ✅ PROCESAMIENTO COMPLETADO")
        print("="*80)
        
        fotolibro_config = {
            "metadata": {
                "client_name": client_context.get('client_name', 'Cliente'),
                "recipient_name": client_context.get('recipient_name'),
                "year": client_context.get('year'),
                "total_photos": len(photo_paths),
                "processed_at": "2025-01-25"  # Timestamp
            },
            "photos": chronology_info['ordered_photos'],
            "motif": {
                "type": motif_info['motif'],
                "confidence": motif_info['confidence'],
                "design_config": motif_info['design_config']
            },
            "chronology": {
                "type": chronology_info['chronology_type'],
                "confidence": chronology_info['confidence'],
                "temporal_metadata": chronology_info.get('temporal_metadata', {}),
                "key_moments": chronology_info.get('key_moments', [])
            },
            "story": story_info['story'],
            "design": design_info['design']
        }
        
        # Guardar a archivo si se especificó ruta
        if output_path:
            import json
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(fotolibro_config, f, indent=2, ensure_ascii=False)
            print(f"\n  💾 Configuración guardada en: {output_path}")
        
        print(f"\n  🎯 RESUMEN:")
        print(f"     - Motivo: {motif_info['motif']}")
        print(f"     - Cronología: {chronology_info['chronology_type']}")
        print(f"     - Título: \"{story_info['story']['cover']['title']}\"")
        print(f"     - Template: {design_info['design']['template_choice']['primary']}")
        print(f"     - Fotos hero: {len(design_info['design']['layout_strategy'].get('hero_pages', []))}")
        print(f"     - Capítulos: {len(story_info['story'].get('chapters', []))}")
        
        print("\n" + "="*80)
        print("  🎨 LISTO PARA EJECUTAR EN STAGEHAND + FDF")
        print("="*80)
        print()
        
        return fotolibro_config
        
    except Exception as e:
        print(f"\n❌ ERROR EN PROCESAMIENTO: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "success": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Ejemplo de uso
    print("AGNO Team para Fotolibros Artísticos")
    print("Uso:")
    print("  from team import process_fotolibro")
    print("  config = process_fotolibro(photo_paths, client_context, 'output.json')")
