"""
Test de Seleccion de Categorias y Templates en FDF
===================================================
Prueba el nuevo flujo:
1. Login
2. Navegar a producto
3. Subir fotos
4. Seleccionar CATEGORIA del menu lateral
5. Seleccionar TEMPLATE dentro de esa categoria
6. Llegar al editor
"""

import asyncio
import os
import glob
from dotenv import load_dotenv

load_dotenv()


async def test_categorias_templates():
    """Test de seleccion de categorias y templates"""
    
    print("=" * 70)
    print("TEST: Seleccion de Categorias y Templates")
    print("=" * 70)
    
    # Verificar credenciales
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("ERROR: Faltan credenciales en .env")
        return
    
    # Buscar fotos de prueba
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    test_photos = []
    
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        test_photos.extend(glob.glob(os.path.join(uploads_dir, "**", ext), recursive=True))
    
    test_photos = [p for p in test_photos if "comprobante" not in p.lower()][:3]
    
    print(f"\nFotos de prueba: {len(test_photos)}")
    
    if not test_photos:
        print("ERROR: No hay fotos de prueba")
        return
    
    # Importar toolkit
    from services.fdf_stagehand import FDFStagehandToolkit
    from services.fdf_stagehand.design_intelligence import DesignIntelligence
    
    toolkit = FDFStagehandToolkit(
        model_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=False
    )
    
    designer = DesignIntelligence(api_key=api_key)
    
    try:
        # =============================================
        # FASE 1: Login y navegacion hasta templates
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 1: Login y Navegacion")
        print("=" * 70)
        
        print("\n[1] Login...")
        await toolkit.login()
        await toolkit.apply_zoom(0.5)
        
        print("\n[2] Navegando a Fotolibros...")
        await toolkit.navigate_to_fotolibros()
        await asyncio.sleep(1)
        
        print("\n[3] Seleccionando producto 21x21...")
        await toolkit.select_product_by_text("21x21")
        await asyncio.sleep(2)
        
        print("\n[4] Creando proyecto...")
        await toolkit.click_create_project("Test Categorias")
        await asyncio.sleep(2)
        
        print("\n[5] Seleccionando fuente de fotos...")
        await toolkit.select_photo_source("computadora")
        await asyncio.sleep(1)
        
        print("\n[6] Subiendo fotos...")
        await toolkit.upload_photos(test_photos)
        
        print("\n[7] Clickeando Continuar...")
        await toolkit.click_continue()
        await asyncio.sleep(3)
        
        # Aplicar zoom para ver todo
        await toolkit.apply_zoom(0.5)
        await toolkit.scroll_page("top")
        await toolkit.take_screenshot("cat_01_pantalla_templates.png")
        
        # =============================================
        # FASE 2: Probar diferentes estilos/categorias
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 2: Probar Estilos y Categorias")
        print("=" * 70)
        
        # Lista de estilos a probar
        estilos_test = [
            ("sin_diseno", "Libro en blanco"),
            ("clasico", "Bodas/Flores"),
            ("divertido", "Cumpleanos"),
            ("minimalista", "Solo Fotos"),
        ]
        
        for estilo, descripcion in estilos_test:
            print(f"\n--- Probando estilo: {estilo} ({descripcion}) ---")
            
            # Obtener categoria y template
            cat_info = designer.obtener_categoria_fdf(estilo)
            template_info = designer.seleccionar_template_fdf(estilo)
            
            print(f"    Categoria FDF: {cat_info['categoria_fdf']}")
            print(f"    Templates sugeridos: {cat_info['templates_sugeridos']}")
            print(f"    Template a usar: {template_info['template_fdf']}")
            print(f"    Es solo fotos: {cat_info.get('es_solo_fotos', False)}")
            
            # Scroll al top antes de cada prueba
            await toolkit.scroll_page("top")
            await asyncio.sleep(0.5)
        
        # =============================================
        # FASE 3: SELECCION INTELIGENTE HIBRIDA
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 3: Seleccion INTELIGENTE de Template (Hibrida)")
        print("=" * 70)
        
        # Probar con estilo "clasico"
        estilo_elegido = "clasico"
        
        print(f"\n[8] Estilo elegido por cliente: {estilo_elegido}")
        print("    Iniciando seleccion inteligente...")
        print("    1. Categoria: hardcodeada (rapido)")
        print("    2. Template: LLM Vision (inteligente)")
        
        # Capturar screenshot antes
        await toolkit.take_screenshot("cat_02_antes_seleccion.png")
        
        # USAR SELECCION INTELIGENTE
        print(f"\n[9] Ejecutando select_template_intelligent()...")
        resultado = await toolkit.select_template_intelligent(
            estilo_cliente=estilo_elegido,
            fotos_paths=test_photos,  # Pasar fotos del cliente
            designer=designer
        )
        
        print(f"\n[10] Resultado de seleccion inteligente:")
        print(f"     Success: {resultado.get('success')}")
        print(f"     Template elegido: {resultado.get('template_elegido')}")
        print(f"     Categoria usada: {resultado.get('categoria')}")
        print(f"     Razonamiento: {resultado.get('razonamiento')}")
        print(f"     Confianza: {resultado.get('confianza')}")
        print(f"     Alternativa: {resultado.get('alternativa')}")
        print(f"     Templates visibles: {resultado.get('templates_visibles', [])[:5]}...")
        
        await asyncio.sleep(1)
        await toolkit.take_screenshot("cat_04_template_seleccionado.png")
        
        # =============================================
        # FASE 4: Modo de relleno y editor
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 4: Modo de Relleno y Editor")
        print("=" * 70)
        
        print("\n[11] Seleccionando modo manual...")
        await toolkit.click_fill_mode("manual")
        await asyncio.sleep(3)
        
        await toolkit.take_screenshot("cat_05_editor.png")
        
        # Verificar estado final
        page_info = await toolkit.get_page_info()
        print(f"\n[12] Estado final:")
        print(f"     URL: {page_info.get('url')}")
        print(f"     Tipo: {page_info.get('page_type')}")
        
        # =============================================
        # FASE 5: Probar con estilo "sin_diseno"
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 5: Probar Sin Diseno (Libro en Blanco)")
        print("=" * 70)
        
        # Mostrar que configuracion se usaria para sin_diseno
        sin_diseno_cat = designer.obtener_categoria_fdf("sin_diseno")
        sin_diseno_template = designer.seleccionar_template_fdf("sin_diseno")
        
        print(f"\n[INFO] Configuracion para 'sin_diseno':")
        print(f"       Categoria: {sin_diseno_cat['categoria_fdf']}")
        print(f"       Template: {sin_diseno_template['template_fdf']}")
        print(f"       Es solo fotos: {sin_diseno_cat.get('es_solo_fotos', False)}")
        print(f"       Descripcion: {sin_diseno_template['descripcion']}")
        
        # =============================================
        # Resultado final
        # =============================================
        print("\n" + "=" * 70)
        print("RESULTADO FINAL")
        print("=" * 70)
        
        print("\nScreenshots guardados:")
        print("  - cat_01_pantalla_templates.png")
        print("  - cat_02_antes_categoria.png")
        print("  - cat_03_despues_categoria.png")
        print("  - cat_04_template_seleccionado.png")
        print("  - cat_05_editor.png")
        
        print("\nNavegador abierto 60 segundos para inspeccion...")
        await asyncio.sleep(60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        await toolkit.take_screenshot("cat_error.png")
    
    finally:
        print("\nCerrando navegador...")
        await toolkit.close()


if __name__ == "__main__":
    asyncio.run(test_categorias_templates())
