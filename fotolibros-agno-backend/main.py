"""
Main Entry Point - Sistema AGNO de Fotolibros Artísticos
Punto de entrada principal del sistema
"""

import sys
import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Agregar directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from team import process_fotolibro

load_dotenv()


def main():
    """Punto de entrada principal"""
    
    parser = argparse.ArgumentParser(
        description="Sistema AGNO de Fotolibros Artísticos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:

  # Procesar fotos de un directorio
  python main.py --photos-dir ./mis_fotos --client "Ana y Carlos" --output config.json

  # Procesar con hint de motivo
  python main.py --photos-dir ./embarazo --client "María" --hint pregnancy

  # Procesar fotos específicas
  python main.py --photos foto1.jpg foto2.jpg foto3.jpg --client "Juan" --output config.json
        """
    )
    
    # Argumentos
    parser.add_argument(
        '--photos-dir',
        type=str,
        help='Directorio con fotos a procesar'
    )
    
    parser.add_argument(
        '--photos',
        nargs='+',
        help='Lista de rutas de fotos específicas'
    )
    
    parser.add_argument(
        '--client',
        type=str,
        required=True,
        help='Nombre del cliente (ej: "Ana y Carlos")'
    )
    
    parser.add_argument(
        '--recipient',
        type=str,
        help='Destinatario del fotolibro (ej: "Nuestro bebé", "Para mamá")'
    )
    
    parser.add_argument(
        '--hint',
        type=str,
        choices=[
            'wedding', 'travel', 'pregnancy', 'baby-shower', 'baby-first-year',
            'birthday-child', 'birthday-teen', 'mothers-day', 'fathers-day',
            'anniversary-couple', 'family', 'pet', 'generic'
        ],
        help='Hint del tipo de evento (opcional)'
    )
    
    parser.add_argument(
        '--year',
        type=str,
        help='Año del evento (ej: "2024")'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data/fotolibro_config.json',
        help='Ruta del archivo de salida (default: data/fotolibro_config.json)'
    )
    
    args = parser.parse_args()
    
    # Validar que se especificó fotos
    if not args.photos_dir and not args.photos:
        parser.error("Debe especificar --photos-dir o --photos")
    
    # Recolectar fotos
    photo_paths = []
    
    if args.photos_dir:
        photos_dir = Path(args.photos_dir)
        if not photos_dir.exists():
            print(f"❌ Error: El directorio {photos_dir} no existe")
            sys.exit(1)
        
        # Buscar imágenes en el directorio
        extensions = {'.jpg', '.jpeg', '.png', '.webp', '.heic'}
        for ext in extensions:
            photo_paths.extend(list(photos_dir.glob(f'*{ext}')))
            photo_paths.extend(list(photos_dir.glob(f'*{ext.upper()}')))
        
        photo_paths = [str(p.absolute()) for p in photo_paths]
    
    if args.photos:
        for photo in args.photos:
            photo_path = Path(photo)
            if not photo_path.exists():
                print(f"⚠️  Advertencia: {photo} no existe, omitiendo")
                continue
            photo_paths.append(str(photo_path.absolute()))
    
    if not photo_paths:
        print("❌ Error: No se encontraron fotos para procesar")
        sys.exit(1)
    
    print(f"📸 Encontradas {len(photo_paths)} fotos")
    
    # Preparar contexto del cliente
    client_context = {
        "client_name": args.client
    }
    
    if args.recipient:
        client_context["recipient_name"] = args.recipient
    
    if args.hint:
        client_context["hint"] = args.hint
    
    if args.year:
        client_context["year"] = args.year
    
    # Crear directorio de salida si no existe
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Procesar fotolibro
    try:
        config = process_fotolibro(
            photo_paths,
            client_context,
            str(output_path)
        )
        
        if config.get('success') == False:
            print(f"\n❌ Error: {config.get('error')}")
            sys.exit(1)
        
        print(f"\n✅ ÉXITO: Fotolibro procesado correctamente")
        print(f"   Configuración guardada en: {output_path}")
        print(f"\n📋 Siguiente paso:")
        print(f"   Ejecutar Stagehand para crear en FDF:")
        print(f"   cd ../stagehand-fdf-test")
        print(f"   npm run execute-from-json -- {output_path}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
