"""
Orquestador AGNO Team - Integración con los 5 Agentes Especializados
=====================================================================
Integra el nuevo sistema AGNO Team (5 agentes) con el backend existente.

Este módulo reemplaza la lógica de análisis y diseño del orquestador original
con el sistema de 5 agentes especializados:
1. PhotoAnalyzer - Análisis emocional con Vision AI
2. MotifDetector - Detección de 17 motivos específicos  
3. ChronologySpecialist - Ordenamiento cronológico inteligente
4. StoryGenerator - Generación de textos emotivos
5. DesignCurator - Curación artística de diseño
"""

import os
import sys
from typing import Dict, List, Optional

# Agregar path del backend AGNO
AGNO_BACKEND_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "fotolibros-agno-backend"
)

# Asegurarse de que el path existe
if not os.path.exists(AGNO_BACKEND_PATH):
    # Intentar path alternativo
    AGNO_BACKEND_PATH = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        "..", "..", "fotolibros-agno-backend"
    ))

sys.path.insert(0, AGNO_BACKEND_PATH)

# Agregar también el path de agents dentro del backend AGNO
agents_path = os.path.join(AGNO_BACKEND_PATH, "agents")
if os.path.exists(agents_path):
    sys.path.insert(0, agents_path)


class AGNOTeamProcessor:
    """
    Procesador que usa el sistema AGNO Team de 5 agentes especializados
    """
    
    def __init__(self):
        """Inicializa el procesador AGNO Team"""
        self.logs = []
    
    def log(self, mensaje: str, nivel: str = "info"):
        """Log helper"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{nivel.upper()}] {mensaje}"
        self.logs.append(log_entry)
        print(log_entry)
    
    async def procesar_con_agno_team(
        self,
        fotos_paths: List[str],
        cliente_nombre: str,
        motif_hint: Optional[str] = None,
        recipient: Optional[str] = None
    ) -> Dict:
        """
        Procesa fotos usando el sistema AGNO Team completo
        
        Args:
            fotos_paths: Lista de rutas a las fotos
            cliente_nombre: Nombre del cliente
            motif_hint: Hint opcional del motivo (wedding, pregnancy, etc.)
            recipient: Destinatario opcional del fotolibro
        
        Returns:
            dict con toda la configuración del fotolibro
        """
        self.log("[AGNO] Iniciando procesamiento con AGNO Team (5 agentes)")
        
        try:
            # Importar funciones del backend AGNO
            # Los imports son directos porque ya agregamos agents_path al sys.path
            from photo_analyzer import analyze_photo_batch
            from motif_detector import detect_event_motif
            from chronology_specialist import detect_chronology_type
            from story_generator import generate_photobook_story
            from design_curator import curate_design
            
            # Preparar contexto del cliente
            client_context = {
                "client_name": cliente_nombre,
                "hint": motif_hint,
                "recipient_name": recipient
            }
            
            # ========================================
            # FASE 1: ANÁLISIS DE FOTOS
            # ========================================
            self.log(f"[FOTO] FASE 1/5: Analizando {len(fotos_paths)} fotos con Vision AI...")
            
            photo_analyses = analyze_photo_batch(fotos_paths, cliente_nombre)
            
            self.log(f"   [OK] {photo_analyses['total']} fotos analizadas")
            
            # ========================================
            # FASE 2: DETECCIÓN DE MOTIVO
            # ========================================
            self.log("[MOTIF] FASE 2/5: Detectando motivo del fotolibro...")
            
            motif_info = detect_event_motif(
                photo_analyses['photos'],
                motif_hint
            )
            
            self.log(f"   [OK] Motivo: {motif_info['motif']} ({motif_info['confidence']}%)")
            self.log(f"   [OK] Template sugerido: {motif_info['design_config']['template']}")
            
            # ========================================
            # FASE 3: ORDENAMIENTO CRONOLÓGICO
            # ========================================
            self.log("[CHRONO] FASE 3/5: Ordenando fotos cronológicamente...")
            
            chronology_info = detect_chronology_type(
                photo_analyses['photos'],
                motif_info['motif']
            )
            
            self.log(f"   [OK] Tipo cronológico: {chronology_info['chronology_type']}")
            self.log(f"   [OK] Fotos reordenadas: {len(chronology_info['ordered_photos'])}")
            
            if chronology_info.get('key_moments'):
                self.log(f"   [OK] Hitos detectados: {len(chronology_info['key_moments'])}")
            
            # ========================================
            # FASE 4: GENERACIÓN DE TEXTOS EMOTIVOS
            # ========================================
            self.log("[STORY] FASE 4/5: Generando textos emotivos...")
            
            story_info = generate_photobook_story(
                chronology_info['ordered_photos'],
                motif_info,
                chronology_info,
                client_context
            )
            
            if story_info['success']:
                self.log(f"   [OK] Titulo: \"{story_info['story']['cover']['title']}\"")
                self.log(f"   [OK] Capitulos: {len(story_info['story'].get('chapters', []))}")
                self.log(f"   [OK] Leyendas: {len(story_info['story'].get('photo_captions', []))}")
            else:
                self.log(f"   [WARN]  Narrativa con fallback: {story_info.get('error', 'Error desconocido')}")
            
            # ========================================
            # FASE 5: CURACIÓN DE DISEÑO
            # ========================================
            self.log("[AGNO] FASE 5/5: Curando diseño artístico...")
            
            design_info = curate_design(
                chronology_info['ordered_photos'],
                motif_info,
                story_info,
                chronology_info
            )
            
            if design_info['success']:
                self.log(f"   [OK] Template final: {design_info['design']['template_choice']['primary']}")
                self.log(f"   [OK] Paginas hero: {len(design_info['design']['layout_strategy'].get('hero_pages', []))}")
                self.log(f"   [OK] Estilo tipografico: {design_info['design']['typography']['font_style']}")
            else:
                self.log(f"   [WARN]  Diseño con fallback: {design_info.get('error', 'Error desconocido')}")
            
            # ========================================
            # RESULTADO FINAL
            # ========================================
            self.log("[OK] Procesamiento AGNO Team completado exitosamente")
            
            return {
                "success": True,
                "photos": chronology_info['ordered_photos'],
                "motif": motif_info,
                "chronology": chronology_info,
                "story": story_info['story'],
                "design": design_info['design'],
                "logs": self.logs
            }
            
        except Exception as e:
            self.log(f"[ERROR] Error en procesamiento AGNO Team: {e}", "error")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "logs": self.logs
            }


async def analizar_fotos_con_agno_team(
    fotos_paths: List[str],
    cliente_nombre: str,
    motif_hint: Optional[str] = None
) -> Dict:
    """
    Función wrapper para usar desde el orquestador original
    
    Reemplaza la función analizar_fotos() del orquestador
    con el sistema AGNO Team completo
    
    Returns:
        dict compatible con el formato esperado por el orquestador
    """
    processor = AGNOTeamProcessor()
    
    result = await processor.procesar_con_agno_team(
        fotos_paths,
        cliente_nombre,
        motif_hint
    )
    
    if not result['success']:
        return {
            "evento_detectado": "generic",
            "mejores_para_portada": [0],
            "confianza": 0,
            "error": result.get('error', 'Error desconocido')
        }
    
    # Adaptar formato al esperado por el orquestador
    motif = result['motif']['motif']
    
    # Mapear motivos AGNO a eventos del orquestador
    motif_mapping = {
        "wedding": "boda",
        "travel": "viaje",
        "pregnancy": "embarazo",
        "baby-shower": "baby_shower",
        "baby-first-year": "bebe",
        "birthday-child": "cumpleaños",
        "mothers-day": "dia_madre",
        "fathers-day": "dia_padre",
        "family": "familia",
        "pet": "mascota",
        "generic": "otro"
    }
    
    evento = motif_mapping.get(motif, "otro")
    
    # Identificar mejores fotos para portada (las de mayor importancia)
    photos = result['photos']
    fotos_con_importancia = [
        (i, p.get('importance', 5))
        for i, p in enumerate(photos)
    ]
    fotos_ordenadas = sorted(fotos_con_importancia, key=lambda x: x[1], reverse=True)
    mejores_indices = [idx for idx, _ in fotos_ordenadas[:3]]
    
    return {
        "evento_detectado": evento,
        "mejores_para_portada": mejores_indices,
        "confianza": result['motif']['confidence'] / 100,  # Convertir a 0-1
        
        # Datos adicionales del sistema AGNO
        "agno_result": result,
        "motif_original": motif,
        "titulo_sugerido": result['story']['cover']['title'],
        "template_sugerido": result['design']['template_choice']['primary'],
        "fotos_ordenadas": photos,  # Fotos YA en orden cronológico
    }


async def preparar_diseño_con_agno_team(
    pedido_info: Dict,
    analisis_agno: Dict
) -> Dict:
    """
    Función wrapper para preparar diseño usando resultados de AGNO Team
    
    Reemplaza la función preparar_diseño() del orquestador
    
    Returns:
        dict compatible con el formato esperado por el orquestador
    """
    if 'agno_result' not in analisis_agno:
        # Fallback si no hay resultado AGNO
        return {
            "template_id": "clasico",
            "titulo_tapa": pedido_info.get('titulo_tapa', 'Mi Fotolibro'),
            "texto_lomo": pedido_info.get('texto_lomo', ''),
            "fotos_ordenadas": [],
        }
    
    agno_result = analisis_agno['agno_result']
    story = agno_result['story']
    design = agno_result['design']
    
    # Mapear template AGNO a templates de FDF
    template_mapping = {
        "Romántico - Flores": "romantico",
        "Romántico - Delicado": "romantico",
        "Romántico - Elegante": "romantico",
        "Moderno - Geométrico": "moderno",
        "Moderno": "moderno",
        "Clásico - Vintage": "clasico",
        "Clásico - Cálido": "clasico",
        "Divertido - Infantil": "divertido",
        "Divertido - Colorful": "divertido",
        "Natural - Suave": "natural",
    }
    
    template_agno = design['template_choice']['primary']
    template_fdf = template_mapping.get(template_agno, "clasico")
    
    return {
        "template_id": template_fdf,
        "titulo_tapa": story['cover']['title'],
        "texto_lomo": story['cover'].get('author_line', pedido_info.get('texto_lomo', '')),
        "fotos_ordenadas": agno_result['photos'],  # Fotos en orden cronológico
        
        # Metadatos adicionales para el executor
        "dedicatoria": story['dedication']['text'],
        "capítulos": story.get('chapters', []),
        "leyendas": story.get('photo_captions', []),
        "texto_contratapa": story['back_cover']['text'],
        "paleta_colores": design['color_scheme'],
        "decoraciones": design['decorations'],
    }


if __name__ == "__main__":
    print("Orquestador AGNO Team - Módulo de integración")
    print("Uso: import desde orquestador.py principal")
