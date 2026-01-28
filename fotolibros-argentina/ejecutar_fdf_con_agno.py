"""
Ejecutor FDF con AGNO Team
===========================
Toma el resultado de AGNO Team (agno_config_*.json) y lo ejecuta en FDF (Fábrica de Fotolibros)

Flujo:
1. Lee agno_config_a309ddfc.json
2. Carga fotos en orden cronológico
3. Aplica template según motivo
4. Agrega textos emotivos (título, dedicatoria, leyendas)
5. Diseña páginas según curación de DesignCurator
6. Genera el fotolibro final

Uso:
    python ejecutar_fdf_con_agno.py <pedido_id>
    
Ejemplo:
    python ejecutar_fdf_con_agno.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
"""

import asyncio
import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Agregar path del backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "fotolibros-argentina"))

from services.fdf_stagehand.fdf_stagehand_driver import FDFStagehandToolkit

load_dotenv()

# Configuración
FDF_EMAIL = os.getenv("FDF_EMAIL")
FDF_PASSWORD = os.getenv("FDF_PASSWORD")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class AGNOFDFExecutor:
    """
    Executor que toma resultados de AGNO Team y los ejecuta en FDF
    """
    
    def __init__(self, pedido_id: str):
        self.pedido_id = pedido_id
        self.config_path = f"fotolibros-argentina/data/agno_config_{pedido_id[:8]}.json"
        self.config = None
        
    def load_agno_config(self):
        """Carga configuración generada por AGNO Team"""
        print(f"\n[1/7] Cargando configuracion AGNO Team...")
        print(f"      Archivo: {self.config_path}")
        
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"No se encontro {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        print(f"      [OK] Configuracion cargada")
        print(f"      Motivo: {self.config['motif']['motif']}")
        print(f"      Titulo: \"{self.config['story']['cover']['title']}\"")
        print(f"      Fotos: {len(self.config['photos'])}")
        print(f"      Capitulos: {len(self.config['story']['chapters'])}")
        
        return self.config
    
    async def ejecutar_en_fdf(self):
        """Ejecuta el diseño en FDF usando Stagehand + Playwright"""
        
        print(f"\n[2/7] Inicializando toolkit FDF...")
        
        # Crear toolkit hibrido (Playwright + Stagehand + Vision)
        toolkit = FDFStagehandToolkit(
            model_api_key=GEMINI_API_KEY,
            fdf_email=FDF_EMAIL,
            fdf_password=FDF_PASSWORD,
            headless=False,  # Ver el navegador
            use_stagehand=True
        )
        
        try:
            # ========================================
            # FASE 1: INICIALIZAR NAVEGADOR
            # ========================================
            print(f"\n[3/7] Iniciando navegador...")
            await toolkit.initialize()
            print(f"      [OK] Navegador listo")
            
            # ========================================
            # FASE 2: LOGIN EN FDF
            # ========================================
            print(f"\n[4/7] Iniciando sesion en FDF...")
            print(f"      Usuario: {FDF_EMAIL}")
            
            await toolkit.login()
            print(f"      [OK] Sesion iniciada")
            
            # ========================================
            # FASE 3: CREAR PROYECTO NUEVO
            # ========================================
            print(f"\n[5/7] Creando proyecto nuevo...")
            
            # Mapear template AGNO → FDF
            template_mapping = {
                "Moderno": "moderno",
                "Moderno - Geometrico": "moderno",
                "Romantico - Flores": "romantico",
                "Romantico - Delicado": "romantico",
                "Clasico - Vintage": "clasico",
                "Clasico - Calido": "clasico",
                "Divertido - Infantil": "divertido",
                "Natural - Suave": "natural"
            }
            
            template_agno = self.config['design']['template_choice']['primary']
            template_fdf = template_mapping.get(template_agno, "clasico")
            
            print(f"      Template AGNO: {template_agno}")
            print(f"      Template FDF: {template_fdf}")
            
            # Crear proyecto (tamaño 20x20cm, 40 páginas)
            proyecto_id = await toolkit.crear_proyecto(
                titulo=self.config['story']['cover']['title'],
                template=template_fdf,
                size="20x20",
                pages=40
            )
            
            print(f"      [OK] Proyecto creado: {proyecto_id}")
            
            # ========================================
            # FASE 4: SUBIR FOTOS EN ORDEN CRONOLOGICO
            # ========================================
            print(f"\n[6/7] Subiendo {len(self.config['photos'])} fotos en orden cronologico...")
            
            fotos_ordenadas = self.config['chronology']['ordered_photos']
            
            for i, foto in enumerate(fotos_ordenadas, 1):
                filepath = foto['filepath']
                # Convertir path relativo a absoluto
                abs_path = os.path.join(
                    os.path.dirname(__file__),
                    "fotolibros-argentina",
                    filepath
                )
                
                if not os.path.exists(abs_path):
                    print(f"      [WARN] Foto no encontrada: {filepath}")
                    continue
                
                print(f"      [{i}/{len(fotos_ordenadas)}] Subiendo: {foto['filename']}")
                await toolkit.upload_photo(abs_path)
            
            print(f"      [OK] Todas las fotos subidas")
            
            # ========================================
            # FASE 5: DISEÑAR PAGINAS CON AGNO TEAM
            # ========================================
            print(f"\n[7/7] Disenando fotolibro con configuracion AGNO...")
            
            # Configurar textos de tapa
            story = self.config['story']
            
            print(f"\n      === TEXTOS DE TAPA ===")
            print(f"      Titulo: \"{story['cover']['title']}\"")
            print(f"      Subtitulo: \"{story['cover']['subtitle']}\"")
            print(f"      Autor: \"{story['cover']['author_line']}\"")
            
            await toolkit.set_cover_text(
                title=story['cover']['title'],
                subtitle=story['cover']['subtitle'],
                author=story['cover']['author_line']
            )
            
            # Configurar dedicatoria (página 1)
            print(f"\n      === DEDICATORIA ===")
            print(f"      Para: {story['dedication']['recipient']}")
            print(f"      Texto: {story['dedication']['text'][:80]}...")
            
            await toolkit.set_page_text(
                page_num=1,
                text=story['dedication']['text']
            )
            
            # Diseñar capítulos
            print(f"\n      === CAPITULOS ===")
            
            page_num = 2  # Empezar después de dedicatoria
            
            for i, chapter in enumerate(story['chapters'], 1):
                print(f"\n      Capitulo {i}: \"{chapter['title']}\"")
                print(f"         Tono: {chapter['emotional_tone']}")
                print(f"         Fotos: {len(chapter['photo_indices'])}")
                
                # Página de apertura del capítulo
                await toolkit.set_page_text(
                    page_num=page_num,
                    text=f"{chapter['title']}\n\n{chapter['chapter_intro']}"
                )
                page_num += 1
                
                # Agregar fotos del capítulo
                for photo_idx in chapter['photo_indices']:
                    if photo_idx <= len(fotos_ordenadas):
                        foto = fotos_ordenadas[photo_idx - 1]
                        
                        # Buscar leyenda
                        caption = next(
                            (c['caption'] for c in story['photo_captions'] if c['photo_index'] == photo_idx),
                            foto.get('suggested_caption', '')
                        )
                        
                        print(f"         - Foto {photo_idx}: \"{caption[:50]}...\"")
                        
                        # Agregar foto a página
                        await toolkit.add_photo_to_page(
                            page_num=page_num,
                            photo_index=photo_idx - 1,  # 0-indexed
                            caption=caption
                        )
                        
                        page_num += 1
            
            # Contratapa
            print(f"\n      === CONTRATAPA ===")
            print(f"      Texto: {story['back_cover']['text'][:80]}...")
            
            await toolkit.set_back_cover_text(
                text=story['back_cover']['text'],
                quote=story['back_cover']['closing_quote']
            )
            
            print(f"\n[OK] ===================================")
            print(f"[OK] FOTOLIBRO COMPLETADO EXITOSAMENTE")
            print(f"[OK] ===================================")
            print(f"\n      Titulo: \"{story['cover']['title']}\"")
            print(f"      Paginas disenadas: {page_num}")
            print(f"      Fotos incluidas: {len(fotos_ordenadas)}")
            print(f"      Capitulos: {len(story['chapters'])}")
            print(f"\n      El fotolibro esta listo para revision en el navegador.")
            print(f"      Revisa el diseno y descargalo desde FDF.")
            
            # Mantener navegador abierto para revisión
            print(f"\n      Presiona ENTER para cerrar el navegador...")
            input()
            
        finally:
            await toolkit.close()


async def main():
    """Punto de entrada principal"""
    
    print("=" * 70)
    print("  EJECUTOR FDF CON AGNO TEAM")
    print("=" * 70)
    
    # Validar argumentos
    if len(sys.argv) < 2:
        print("\n[ERROR] Uso: python ejecutar_fdf_con_agno.py <pedido_id>")
        print("\nEjemplo:")
        print("  python ejecutar_fdf_con_agno.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf")
        sys.exit(1)
    
    pedido_id = sys.argv[1]
    
    # Validar credenciales
    if not FDF_EMAIL or not FDF_PASSWORD:
        print("\n[ERROR] Faltan credenciales de FDF")
        print("Configura en .env:")
        print("  FDF_EMAIL=tu_email@ejemplo.com")
        print("  FDF_PASSWORD=tu_password")
        sys.exit(1)
    
    if not GEMINI_API_KEY:
        print("\n[ERROR] Falta GEMINI_API_KEY en .env")
        sys.exit(1)
    
    # Ejecutar
    executor = AGNOFDFExecutor(pedido_id)
    
    try:
        executor.load_agno_config()
        await executor.ejecutar_en_fdf()
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
        print("\nPrimero ejecuta: python procesar_pedido_agno.py")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n[ERROR] Error durante ejecucion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
