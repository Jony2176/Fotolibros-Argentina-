"""
Visualizador de Configuración AGNO Team
========================================
Muestra el diseño del fotolibro generado por AGNO Team sin ejecutar FDF

Uso:
    python visualizar_agno_config.py <pedido_id>
    
Ejemplo:
    python visualizar_agno_config.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
"""

import sys
import os
import json
from typing import Dict, Any


def print_header(title: str, char: str = "="):
    """Imprime un header bonito"""
    print(f"\n{char * 70}")
    print(f"  {title}")
    print(f"{char * 70}\n")


def visualizar_tapa(story: Dict):
    """Visualiza diseño de tapa"""
    print_header("TAPA DEL FOTOLIBRO", "=")
    
    print(f"  Titulo:     {story['cover']['title']}")
    print(f"  Subtitulo:  {story['cover']['subtitle']}")
    print(f"  Autor:      {story['cover']['author_line']}")


def visualizar_dedicatoria(story: Dict):
    """Visualiza dedicatoria"""
    print_header("DEDICATORIA (Pagina 1)", "=")
    
    print(f"  Para: {story['dedication']['recipient']}\n")
    print(f"  \"{story['dedication']['text']}\"")


def visualizar_capitulos(story: Dict, photos: list):
    """Visualiza estructura de capítulos"""
    print_header("ESTRUCTURA DEL FOTOLIBRO", "=")
    
    print(f"  Total de capitulos: {len(story['chapters'])}")
    print(f"  Total de fotos: {len(photos)}\n")
    
    page_num = 2  # Después de dedicatoria
    
    for i, chapter in enumerate(story['chapters'], 1):
        print(f"\n  [{'-' * 64}]")
        print(f"  CAPITULO {i}: \"{chapter['title']}\"")
        print(f"  [{'-' * 64}]")
        print(f"    Tono emocional: {chapter['emotional_tone']}")
        print(f"    Intro: \"{chapter['chapter_intro']}\"")
        print(f"    Pagina de apertura: {page_num}")
        page_num += 1
        
        print(f"\n    Fotos en este capitulo ({len(chapter['photo_indices'])} fotos):")
        
        for photo_idx in chapter['photo_indices']:
            if photo_idx <= len(photos):
                foto = photos[photo_idx - 1]
                
                # Buscar leyenda
                caption = next(
                    (c['caption'] for c in story['photo_captions'] if c['photo_index'] == photo_idx),
                    foto.get('suggested_caption', 'Sin leyenda')
                )
                
                emotion = foto.get('emotion', 'neutral')
                importance = foto.get('importance', 5)
                filename = foto.get('filename', 'unknown')
                
                print(f"\n      Pagina {page_num}:")
                print(f"        Foto {photo_idx}: {filename}")
                print(f"        Emocion: {emotion} | Importancia: {importance}/10")
                print(f"        Leyenda: \"{caption}\"")
                
                page_num += 1
    
    return page_num


def visualizar_contratapa(story: Dict):
    """Visualiza contratapa"""
    print_header("CONTRATAPA", "=")
    
    print(f"  Texto:\n  \"{story['back_cover']['text']}\"\n")
    print(f"  Frase de cierre:\n  \"{story['back_cover']['closing_quote']}\"")
    
    if 'epilogue' in story and story['epilogue']:
        print(f"\n  Epilogo:\n  \"{story['epilogue']}\"")


def visualizar_diseno(design: Dict, motif: Dict):
    """Visualiza decisiones de diseño"""
    print_header("CONFIGURACION DE DISENO", "=")
    
    print(f"  Motivo detectado: {motif['motif']} ({motif['confidence']}% confianza)")
    print(f"  Template elegido: {design['template_choice']['primary']}")
    print(f"  Razon: {design['template_choice']['reasoning']}")
    
    print(f"\n  Paleta de colores:")
    print(f"    Primario:   {design['color_scheme']['primary']}")
    print(f"    Secundario: {design['color_scheme']['secondary']}")
    print(f"    Acento:     {design['color_scheme']['accent']}")
    print(f"    Mood:       {design['color_scheme']['mood']}")
    
    print(f"\n  Tipografia:")
    print(f"    Estilo: {design['typography']['font_style']}")
    print(f"    Razon: {design['typography']['reasoning']}")
    
    print(f"\n  Decoraciones:")
    print(f"    Usar clip-arts: {design['decorations']['use_cliparts']}")
    if design['decorations']['use_cliparts']:
        print(f"    Tipos: {', '.join(design['decorations'].get('clipart_types', []))}")
    print(f"    Estilo: {design['decorations']['style']}")
    
    print(f"\n  Objetivos de calidad:")
    print(f"    Calidad minima/pagina: {design['quality_targets']['minimum_page_quality']}/10")
    print(f"    Impacto emocional:     {design['quality_targets']['emotional_impact']}/10")
    print(f"    Coherencia:            {design['quality_targets']['coherence_score']}/10")


def visualizar_estadisticas(config: Dict):
    """Visualiza estadísticas generales"""
    print_header("ESTADISTICAS GENERALES", "=")
    
    photos = config['chronology']['ordered_photos']
    
    # Contar emociones
    emotions = {}
    for photo in photos:
        emotion = photo.get('emotion', 'neutral')
        emotions[emotion] = emotions.get(emotion, 0) + 1
    
    print(f"  Total de fotos: {len(photos)}")
    print(f"  Distribucion emocional:")
    for emotion, count in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (count / len(photos)) * 100
        print(f"    - {emotion.capitalize()}: {count} fotos ({porcentaje:.1f}%)")
    
    # Promedio de importancia
    importances = [p.get('importance', 5) for p in photos]
    avg_importance = sum(importances) / len(importances) if importances else 0
    print(f"\n  Importancia promedio: {avg_importance:.1f}/10")
    
    # Fotos por capítulo
    print(f"\n  Fotos por capitulo:")
    for i, chapter in enumerate(config['story']['chapters'], 1):
        print(f"    Capitulo {i}: {len(chapter['photo_indices'])} fotos")


def main():
    """Punto de entrada principal"""
    
    print_header("VISUALIZADOR AGNO TEAM", "#")
    
    # Validar argumentos
    if len(sys.argv) < 2:
        print("\n[ERROR] Uso: python visualizar_agno_config.py <pedido_id>")
        print("\nEjemplo:")
        print("  python visualizar_agno_config.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf")
        sys.exit(1)
    
    pedido_id = sys.argv[1]
    
    # Cargar configuración
    config_path = f"fotolibros-argentina/data/agno_config_{pedido_id[:8]}.json"
    
    print(f"\nCargando: {config_path}")
    
    if not os.path.exists(config_path):
        print(f"\n[ERROR] No se encontro el archivo: {config_path}")
        print("\nPrimero ejecuta: python procesar_pedido_agno.py")
        sys.exit(1)
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    print("[OK] Configuracion cargada exitosamente\n")
    
    # Visualizar todas las secciones
    visualizar_tapa(config['story'])
    visualizar_dedicatoria(config['story'])
    
    total_pages = visualizar_capitulos(
        config['story'],
        config['chronology']['ordered_photos']
    )
    
    visualizar_contratapa(config['story'])
    visualizar_diseno(config['design'], config['motif'])
    visualizar_estadisticas(config)
    
    # Resumen final
    print_header("RESUMEN FINAL", "#")
    print(f"  Titulo:          \"{config['story']['cover']['title']}\"")
    print(f"  Motivo:          {config['motif']['motif']}")
    print(f"  Template:        {config['design']['template_choice']['primary']}")
    print(f"  Total paginas:   ~{total_pages}")
    print(f"  Total fotos:     {len(config['chronology']['ordered_photos'])}")
    print(f"  Capitulos:       {len(config['story']['chapters'])}")
    print(f"  Tema general:    {config['story']['overall_theme']}")
    
    print(f"\n  Para ejecutar en FDF:")
    print(f"    python ejecutar_fdf_con_agno.py {pedido_id}")
    
    print("\n" + "#" * 70 + "\n")


if __name__ == "__main__":
    main()
