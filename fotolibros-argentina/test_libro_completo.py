#!/usr/bin/env python3
"""
Test E2E Completo: Libro Divertido con TODOS los elementos
============================================================
Este test crea un fotolibro completo con:
- Template divertido (Asi Fue o similar colorido)
- 24 paginas
- Fotos en todas las paginas
- Titulo en portada
- Texto en lomo
- Stickers/adornos segun el estilo
- Pies de foto

El test llega hasta el CHECKOUT pero NO confirma el pago.

Uso:
    python test_libro_completo.py
    python test_libro_completo.py --estilo clasico
    python test_libro_completo.py --paginas 30
"""

import asyncio
import os
import sys
import glob
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.fdf_stagehand import FDFStagehandToolkit
from services.fdf_stagehand.design_intelligence import DesignIntelligence


async def test_libro_completo(
    estilo: str = "divertido",
    num_paginas: int = 24,
    titulo_libro: str = "Mi Libro Divertido",
    headless: bool = False,
    max_spreads: int = None  # None = todos, o especificar limite para test rapido
):
    """
    Test E2E completo de creacion de fotolibro.
    
    Args:
        estilo: Estilo del libro (divertido, clasico, minimalista, premium)
        num_paginas: Numero de paginas del libro
        titulo_libro: Titulo para el libro
        headless: Si True, ejecuta sin mostrar el navegador
        max_spreads: Limite de spreads a disenar (None = todos)
    """
    
    # Obtener credenciales
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("ERROR: Faltan credenciales en .env")
        print("Necesitas: OPENROUTER_API_KEY, GRAFICA_EMAIL, GRAFICA_PASSWORD")
        return False
    
    # Buscar fotos de prueba
    uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")
    test_photos = []
    for ext in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]:
        test_photos.extend(glob.glob(os.path.join(uploads_dir, "**", ext), recursive=True))
    
    # Filtrar comprobantes y archivos de sistema
    test_photos = [
        p for p in test_photos 
        if "comprobante" not in p.lower() 
        and "thumb" not in p.lower()
        and not os.path.basename(p).startswith(".")
    ]
    
    if len(test_photos) < 5:
        print(f"ERROR: Se necesitan al menos 5 fotos en {uploads_dir}")
        print(f"Encontradas: {len(test_photos)}")
        return False
    
    # LIMITAR A MAXIMO 12 FOTOS para evitar tiempos de carga excesivos
    MAX_PHOTOS = 12
    if len(test_photos) > MAX_PHOTOS:
        print(f"[INFO] Limitando de {len(test_photos)} a {MAX_PHOTOS} fotos")
        test_photos = test_photos[:MAX_PHOTOS]
    
    print("=" * 70)
    print("TEST E2E COMPLETO - LIBRO DIVERTIDO")
    print("=" * 70)
    print(f"Estilo: {estilo}")
    print(f"Paginas: {num_paginas}")
    print(f"Titulo: {titulo_libro}")
    print(f"Fotos disponibles: {len(test_photos)}")
    print(f"Max spreads a disenar: {max_spreads or 'todos'}")
    print("=" * 70)
    
    # Inicializar toolkit
    toolkit = FDFStagehandToolkit(
        model_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=headless
    )
    
    designer = DesignIntelligence(api_key=api_key)
    
    results = {
        "success": False,
        "steps": [],
        "screenshots": [],
        "errors": [],
        "start_time": datetime.now().isoformat()
    }
    
    try:
        # =====================================================
        # PASO 1: Login
        # =====================================================
        print("\n[PASO 1] Login...")
        login_result = await toolkit.login()
        results["steps"].append({"step": "login", "success": login_result.get("success")})
        
        if not login_result.get("success"):
            raise Exception(f"Login fallido: {login_result.get('error')}")
        
        # =====================================================
        # PASO 2: Navegar a "Para Profesionales (sin logo de FDF)"
        # =====================================================
        # IMPORTANTE: Como RESELLERS debemos clickear la categoría 
        # "Para Profesionales (sin logo de FDF)" en la pantalla principal
        # para que los fotolibros NO tengan el logo de FDF
        print("\n[PASO 2] Navegando a 'Para Profesionales (sin logo de FDF)'...")
        nav_result = await toolkit.navigate_to_fotolibros(for_professionals=True)
        results["steps"].append({"step": "navigate_professionals", "success": nav_result.get("success")})
        
        print("[PASO 2.1] Seleccionando producto 21x21...")
        await toolkit.select_product_by_text("21x21")
        
        print(f"[PASO 2.2] Creando proyecto '{titulo_libro}' con {num_paginas} paginas...")
        await toolkit.click_create_project(titulo_libro, pages=num_paginas)
        results["steps"].append({"step": "create_project", "success": True})
        
        # =====================================================
        # PASO 3: Subir fotos
        # =====================================================
        print(f"\n[PASO 3] Subiendo {len(test_photos)} fotos...")
        await toolkit.select_photo_source("computadora")
        upload_result = await toolkit.upload_photos(test_photos)
        results["steps"].append({
            "step": "upload_photos", 
            "success": upload_result.get("success"),
            "photos_uploaded": upload_result.get("fotos_subidas", 0)
        })
        
        print("[PASO 3.1] Continuando al siguiente paso...")
        await toolkit.click_continue()
        await asyncio.sleep(2)
        
        # =====================================================
        # PASO 4: Seleccionar template segun estilo
        # =====================================================
        print(f"\n[PASO 4] Seleccionando template (estilo: {estilo})...")
        template_result = await toolkit.select_template_intelligent(
            estilo_cliente=estilo,
            fotos_paths=test_photos[:3],
            designer=designer
        )
        
        template_elegido = template_result.get("template_elegido", "Desconocido")
        print(f"[PASO 4] Template elegido: {template_elegido}")
        results["steps"].append({
            "step": "select_template", 
            "success": template_result.get("success"),
            "template": template_elegido,
            "confianza": template_result.get("confianza", 0)
        })
        
        # =====================================================
        # PASO 5: Entrar al editor
        # =====================================================
        print("\n[PASO 5] Entrando al editor...")
        await toolkit.click_fill_mode("manual")
        
        print("[PASO 5.1] Esperando que el editor cargue...")
        editor_ready = await toolkit.wait_for_editor_ready(timeout=90)
        results["steps"].append({
            "step": "enter_editor", 
            "success": editor_ready.get("success")
        })
        
        if not editor_ready.get("success"):
            raise Exception("El editor no cargo correctamente")
        
        print("[PASO 5] Editor listo!")
        await toolkit.take_screenshot("01_editor_listo.png")
        results["screenshots"].append("01_editor_listo.png")
        
        # =====================================================
        # PASO 6: Obtener info de paginas
        # =====================================================
        print("\n[PASO 6] Obteniendo info de paginas...")
        pages_info = await toolkit.get_book_pages_info()
        total_thumbnails = pages_info.get("total_thumbnails", 0)
        page_thumbnails = pages_info.get("page_thumbnails", [])
        
        print(f"[PASO 6] Total miniaturas/spreads: {total_thumbnails}")
        print(f"[PASO 6] Total paginas del libro: {pages_info.get('total_pages', num_paginas)}")
        
        # Determinar cuantos spreads disenar
        spreads_to_design = total_thumbnails if total_thumbnails > 0 else 13  # 24 pags = ~13 spreads
        if max_spreads:
            spreads_to_design = min(spreads_to_design, max_spreads)
        
        # =====================================================
        # PASO 7: Disenar PORTADA (Contratapa-Tapa)
        # =====================================================
        print("\n[PASO 7] Disenando PORTADA (Contratapa-Tapa)...")
        
        # Navegar a la primera miniatura (Tapa)
        if page_thumbnails and len(page_thumbnails) > 0:
            tapa_thumb = page_thumbnails[0]
            if tapa_thumb.get("x") and tapa_thumb.get("y"):
                await toolkit.page.mouse.click(tapa_thumb["x"], tapa_thumb["y"])
                await asyncio.sleep(2)
                print("[PASO 7] Navegado a vista Tapa")
        
        # 7.1 Colocar foto principal en portada
        print("[PASO 7.1] Colocando foto principal...")
        fill_result = await toolkit.auto_fill_page_with_vision(max_photos=2)
        print(f"[PASO 7.1] Fotos colocadas: {fill_result.get('photos_placed', 0)}")
        
        # 7.2 Agregar titulo en portada
        print(f"[PASO 7.2] Agregando titulo: '{titulo_libro}'...")
        title_result = await toolkit.add_cover_title(titulo_libro)
        results["steps"].append({
            "step": "add_cover_title",
            "success": title_result.get("success")
        })
        
        # 7.3 Agregar stickers decorativos (solo para estilo divertido)
        if estilo.lower() in ["divertido", "premium"]:
            print("[PASO 7.3] Agregando stickers decorativos...")
            
            # Estrella en esquina superior derecha
            sticker1 = await toolkit.add_sticker("estrella", x=1100, y=150)
            
            # Corazon en esquina inferior
            sticker2 = await toolkit.add_sticker("corazon", x=1150, y=500)
            
            results["steps"].append({
                "step": "add_stickers_cover",
                "stickers_added": 2
            })
        
        # 7.4 Agregar texto en lomo
        print(f"[PASO 7.4] Agregando texto en lomo: '{titulo_libro}'...")
        spine_result = await toolkit.add_spine_text(titulo_libro)
        results["steps"].append({
            "step": "add_spine_text",
            "success": spine_result.get("success")
        })
        
        await toolkit.take_screenshot("02_portada_completa.png")
        results["screenshots"].append("02_portada_completa.png")
        
        # =====================================================
        # PASO 8: Disenar paginas interiores
        # =====================================================
        print(f"\n[PASO 8] Disenando {spreads_to_design - 1} spreads interiores...")
        
        spreads_designed = 0
        photos_placed_total = 0
        stickers_added = 0
        captions_added = 0
        
        for spread_idx in range(1, spreads_to_design):
            print(f"\n[PASO 8.{spread_idx}] Disenando spread {spread_idx + 1}/{spreads_to_design}...")
            
            try:
                # Navegar al spread
                if page_thumbnails and spread_idx < len(page_thumbnails):
                    thumb = page_thumbnails[spread_idx]
                    if thumb.get("x") and thumb.get("y"):
                        await toolkit.page.mouse.click(thumb["x"], thumb["y"])
                        await asyncio.sleep(2)
                        print(f"  - Navegado a: {thumb.get('label', f'Spread {spread_idx + 1}')}")
                else:
                    # Usar navegacion secuencial
                    await toolkit.next_page()
                    await asyncio.sleep(1.5)
                
                # Auto-fill con fotos
                fill_result = await toolkit.auto_fill_page_with_vision(max_photos=3)
                photos_placed = fill_result.get("photos_placed", 0)
                photos_placed_total += photos_placed
                print(f"  - Fotos colocadas: {photos_placed}")
                
                # Agregar sticker cada 3 spreads (para estilo divertido)
                if estilo.lower() == "divertido" and spread_idx % 3 == 0:
                    sticker_types = ["estrella", "corazon", "globo", "flor"]
                    sticker_type = sticker_types[spread_idx % len(sticker_types)]
                    
                    sticker_result = await toolkit.add_sticker(sticker_type)
                    if sticker_result.get("success"):
                        stickers_added += 1
                        print(f"  - Sticker agregado: {sticker_type}")
                
                # Agregar pie de foto cada 4 spreads
                if spread_idx % 4 == 0:
                    caption_text = f"Recuerdo {spread_idx}"
                    caption_result = await toolkit.add_photo_caption(caption_text)
                    if caption_result.get("success"):
                        captions_added += 1
                        print(f"  - Pie de foto: '{caption_text}'")
                
                spreads_designed += 1
                
                # Tomar screenshot cada 4 spreads
                if spread_idx % 4 == 0 or spread_idx == spreads_to_design - 1:
                    screenshot_name = f"spread_{spread_idx + 1:02d}.png"
                    await toolkit.take_screenshot(screenshot_name)
                    results["screenshots"].append(screenshot_name)
                
            except Exception as e:
                print(f"  - ERROR en spread {spread_idx + 1}: {e}")
                results["errors"].append({
                    "spread": spread_idx + 1,
                    "error": str(e)
                })
                # Continuar con el siguiente spread
                continue
        
        print(f"\n[PASO 8] Resumen de diseno:")
        print(f"  - Spreads disenados: {spreads_designed}")
        print(f"  - Total fotos colocadas: {photos_placed_total}")
        print(f"  - Stickers agregados: {stickers_added}")
        print(f"  - Pies de foto: {captions_added}")
        
        results["steps"].append({
            "step": "design_interior_pages",
            "spreads_designed": spreads_designed,
            "photos_placed": photos_placed_total,
            "stickers_added": stickers_added,
            "captions_added": captions_added
        })
        
        # =====================================================
        # PASO 9: Guardar proyecto
        # =====================================================
        print("\n[PASO 9] Guardando proyecto...")
        save_result = await toolkit.save_project()
        results["steps"].append({
            "step": "save_project",
            "success": save_result.get("success")
        })
        
        if save_result.get("success"):
            print("[PASO 9] Proyecto guardado exitosamente")
        else:
            print(f"[PASO 9] ADVERTENCIA: {save_result.get('error', 'No se pudo guardar')}")
        
        await asyncio.sleep(2)
        
        # =====================================================
        # PASO 10: Ir al checkout (SIN CONFIRMAR PAGO)
        # =====================================================
        print("\n[PASO 10] Navegando al checkout...")
        print("[PASO 10] NOTA: NO se confirmara el pago")
        
        checkout_result = await toolkit.go_to_checkout()
        results["steps"].append({
            "step": "go_to_checkout",
            "success": checkout_result.get("success")
        })
        
        await asyncio.sleep(3)
        
        # Tomar screenshot del checkout
        await toolkit.take_screenshot("checkout_final.png")
        results["screenshots"].append("checkout_final.png")
        
        # Verificar que estamos en checkout
        page_info = await toolkit.get_page_info()
        url = page_info.get("url", "").lower()
        
        in_checkout = any(word in url for word in ["checkout", "carrito", "cart", "pedir", "comprar"])
        
        if in_checkout:
            print("[PASO 10] Llegamos al checkout exitosamente!")
            print("[PASO 10] NO se confirmo el pago (como solicitado)")
        else:
            print(f"[PASO 10] ADVERTENCIA: URL actual: {page_info.get('url')}")
            print("[PASO 10] Puede que no estemos en la pantalla de checkout")
        
        # =====================================================
        # RESUMEN FINAL
        # =====================================================
        print("\n" + "=" * 70)
        print("RESUMEN DEL TEST")
        print("=" * 70)
        print(f"Estilo: {estilo}")
        print(f"Template usado: {template_elegido}")
        print(f"Paginas: {num_paginas}")
        print(f"Spreads disenados: {spreads_designed}")
        print(f"Fotos colocadas: {photos_placed_total}")
        print(f"Stickers agregados: {stickers_added}")
        print(f"Pies de foto: {captions_added}")
        print(f"Screenshots guardados: {len(results['screenshots'])}")
        print(f"Errores: {len(results['errors'])}")
        print(f"En checkout: {'SI' if in_checkout else 'NO'}")
        print("=" * 70)
        
        results["success"] = True
        results["in_checkout"] = in_checkout
        results["end_time"] = datetime.now().isoformat()
        
        # Mantener browser abierto para verificacion manual
        print("\n[INFO] Browser abierto por 30 segundos para verificacion...")
        print("[INFO] Puedes verificar el diseno manualmente")
        await asyncio.sleep(30)
        
        return results
        
    except Exception as e:
        print(f"\n[ERROR] Error en el test: {e}")
        import traceback
        traceback.print_exc()
        
        results["errors"].append({"general": str(e)})
        results["end_time"] = datetime.now().isoformat()
        
        # Tomar screenshot del error
        try:
            await toolkit.take_screenshot("error_final.png")
            results["screenshots"].append("error_final.png")
        except:
            pass
        
        return results
        
    finally:
        print("\n[CLEANUP] Cerrando browser...")
        await toolkit.close()


def main():
    parser = argparse.ArgumentParser(description="Test E2E completo de fotolibro")
    parser.add_argument("--estilo", default="divertido", 
                       choices=["divertido", "clasico", "minimalista", "premium"],
                       help="Estilo del libro")
    parser.add_argument("--paginas", type=int, default=24,
                       help="Numero de paginas")
    parser.add_argument("--titulo", default="Mi Libro Divertido",
                       help="Titulo del libro")
    parser.add_argument("--headless", action="store_true",
                       help="Ejecutar sin mostrar navegador")
    parser.add_argument("--max-spreads", type=int, default=None,
                       help="Limite de spreads a disenar (para test rapido)")
    parser.add_argument("--rapido", action="store_true",
                       help="Test rapido: solo 3 spreads")
    
    args = parser.parse_args()
    
    # Si es test rapido, limitar spreads
    max_spreads = args.max_spreads
    if args.rapido:
        max_spreads = 3
        print("[INFO] Modo rapido: solo se disenaran 3 spreads")
    
    # Ejecutar test
    results = asyncio.run(test_libro_completo(
        estilo=args.estilo,
        num_paginas=args.paginas,
        titulo_libro=args.titulo,
        headless=args.headless,
        max_spreads=max_spreads
    ))
    
    # Imprimir resultado final
    if results and results.get("success"):
        print("\n" + "=" * 70)
        print("TEST COMPLETADO EXITOSAMENTE")
        print("=" * 70)
        return 0
    else:
        print("\n" + "=" * 70)
        print("TEST FALLIDO")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
