"""
Test de Flujo Completo: Login -> Producto -> Subir Fotos -> Editor
==================================================================
"""

import asyncio
import os
import glob
from dotenv import load_dotenv

load_dotenv()


async def test_flujo_hasta_editor():
    """Test completo hasta llegar al editor con fotos cargadas"""
    
    print("=" * 70)
    print("TEST: Flujo Completo hasta Editor con Fotos")
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
    
    # Buscar en subcarpetas de uploads
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        test_photos.extend(glob.glob(os.path.join(uploads_dir, "**", ext), recursive=True))
    
    # Filtrar comprobantes
    test_photos = [p for p in test_photos if "comprobante" not in p.lower()][:5]  # Max 5 fotos
    
    print(f"\nFotos de prueba encontradas: {len(test_photos)}")
    for p in test_photos[:3]:
        print(f"  - {os.path.basename(p)}")
    
    if not test_photos:
        print("ERROR: No hay fotos de prueba en uploads/")
        return
    
    # Importar toolkit
    from services.fdf_stagehand import FDFStagehandToolkit, VisionDesigner
    from services.fdf_stagehand.design_intelligence import DesignIntelligence
    
    toolkit = FDFStagehandToolkit(
        model_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=False
    )
    
    vision = VisionDesigner(api_key=api_key)
    designer = DesignIntelligence(api_key=api_key)
    
    try:
        # =============================================
        # PASO 1: Login
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 1: Login y Navegación")
        print("=" * 70)
        
        print("\n[1] Login...")
        login_result = await toolkit.login()
        print(f"    Resultado: {login_result.get('success')}")
        
        # Aplicar zoom 50% para ver toda la pantalla
        await toolkit.apply_zoom(0.5)
        await toolkit.take_screenshot("01_post_login.png")
        
        # =============================================
        # PASO 2: Navegar a Fotolibros y ver formatos
        # =============================================
        print("\n[2] Navegando a Fotolibros...")
        await toolkit.navigate_to_fotolibros()
        await asyncio.sleep(1)
        
        # Aplicar zoom 50% para ver todos los formatos
        await toolkit.apply_zoom(0.5)
        await toolkit.scroll_page("top")
        await toolkit.take_screenshot("02_formatos_todos.png")
        
        # =============================================
        # PASO 3: Seleccionar producto
        # =============================================
        print("\n[3] Seleccionando producto 21x21...")
        product_result = await toolkit.select_product_by_text("21x21")
        print(f"    Resultado: {product_result}")
        await asyncio.sleep(2)
        
        # Aplicar zoom 50% al modal de configuración
        await toolkit.apply_zoom(0.5)
        await toolkit.take_screenshot("03_modal_config.png")
        
        # =============================================
        # PASO 4: Configurar y crear proyecto
        # =============================================
        print("\n[4] Configurando proyecto...")
        create_result = await toolkit.click_create_project("Test Automatizado")
        print(f"    Resultado: {create_result}")
        
        # =============================================
        # PASO 5: Esperar pantalla de fuente de fotos
        # =============================================
        print("\n[5] Esperando pantalla de selección de fuente...")
        await toolkit.wait_for_editor(timeout=15)
        
        # Aplicar zoom 50%
        await toolkit.apply_zoom(0.5)
        await toolkit.take_screenshot("04_seleccion_fuente.png")
        
        print("[OK] Llegamos a selección de fuente de fotos")
        
        # =============================================
        # PASO 5: Seleccionar fuente y subir fotos
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 2: Subir fotos")
        print("=" * 70)
        
        # Seleccionar "Desde computadora"
        print("\n[5.1] Seleccionando 'Desde computadora'...")
        source_result = await toolkit.select_photo_source("computadora")
        print(f"      Resultado: {source_result}")
        
        await asyncio.sleep(2)
        await toolkit.take_screenshot("paso2_source_selected.png")
        
        # Subir fotos
        print(f"\n[5.2] Subiendo {len(test_photos)} fotos...")
        upload_result = await toolkit.upload_photos(test_photos)
        print(f"      Resultado: {upload_result}")
        
        await toolkit.take_screenshot("paso3_fotos_subidas.png")
        
        # =============================================
        # PASO 6: Continuar al editor
        # =============================================
        print("\n[6] Clickeando Continuar...")
        continue_result = await toolkit.click_continue()
        print(f"    Resultado: {continue_result}")
        
        await asyncio.sleep(3)
        await toolkit.take_screenshot("paso4_post_continuar.png")
        
        # =============================================
        # PASO 7: Pantalla de selección de templates
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 3: Selección de Template según Estilo del Pedido")
        print("=" * 70)
        
        # Aplicar zoom 50% para ver todos los templates
        await toolkit.apply_zoom(0.5)
        await toolkit.scroll_page("top")
        await toolkit.take_screenshot("05_templates_todos.png")
        
        # Ver info de scroll
        scroll_info = await toolkit.get_scroll_info()
        print(f"\n[7.1] Info scroll: {scroll_info.get('info', {})}")
        
        # Simular estilo del pedido (en producción viene del pedido real)
        # Opciones: "minimalista", "clasico", "divertido", "premium"
        estilo_pedido = "clasico"  # Este valor vendría del pedido
        evento_detectado = None  # Opcional: se puede detectar de las fotos
        
        # Usar DesignIntelligence para obtener el template de FDF correcto
        print(f"\n[7.2] Estilo del pedido: {estilo_pedido}")
        
        # NUEVO: Obtener la categoría del menú lateral
        categoria_info = designer.obtener_categoria_fdf(estilo_pedido, evento_detectado)
        categoria_fdf = categoria_info["categoria_fdf"]
        templates_sugeridos = categoria_info["templates_sugeridos"]
        print(f"    Categoría FDF: {categoria_fdf}")
        print(f"    Templates sugeridos: {templates_sugeridos}")
        print(f"    Motivo: {categoria_info['motivo']}")
        
        # Obtener configuración del template
        template_info = designer.seleccionar_template_fdf(estilo_pedido, evento_detectado)
        template_fdf = template_info["template_fdf"]
        print(f"\n    Template FDF seleccionado: {template_fdf}")
        print(f"    Descripción: {template_info['descripcion']}")
        print(f"    Fotos por página: {template_info['fotos_por_pagina']}")
        print(f"    Versión Editores: {template_info['es_version_editores']}")

        # NUEVO FLUJO: Primero filtrar por categoría, luego seleccionar template
        print(f"\n[7.3] Seleccionando categoría '{categoria_fdf}' y template '{template_fdf}'...")
        template_result = await toolkit.select_template(
            template_name=template_fdf, 
            for_editors=True,
            category=categoria_fdf  # Nuevo parámetro para filtrar por categoría
        )
        print(f"    Resultado: {template_result}")
        
        await asyncio.sleep(1)
        await toolkit.take_screenshot("paso5_template_selected.png")
        
        # Clickear "Relleno fotos manual"
        print("\n[7.4] Clickeando 'Relleno fotos manual'...")
        fill_result = await toolkit.click_fill_mode("manual")
        print(f"    Resultado: {fill_result}")
        
        await asyncio.sleep(3)
        await toolkit.take_screenshot("paso6_fill_mode.png")
        
        # =============================================
        # PASO 8: Editor de diseño
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 4: Editor de Diseño")
        print("=" * 70)
        
        # Esperar que cargue el editor
        print("\n[8] Esperando editor de diseño...")
        editor_result = await toolkit.wait_for_editor(timeout=30)
        print(f"    Resultado: {editor_result}")
        
        await toolkit.take_screenshot("paso7_editor.png")
        
        # Analizar con Vision
        print("\n[8] Analizando editor con Gemini Vision...")
        analysis = await vision.analyze_editor(toolkit.page)
        
        if analysis.get("success"):
            info = analysis.get("analysis", {})
            print(f"    Tipo página: {info.get('tipo_pagina')}")
            print(f"    Editor visible: {info.get('editor_visible')}")
            print(f"    Panel fotos: {info.get('panel_fotos')}")
            print(f"    Siguiente acción: {info.get('siguiente_accion')}")
        
        # Buscar slots
        print("\n[9] Buscando slots para fotos...")
        slots_result = await vision.find_photo_slots(toolkit.page)
        if slots_result.get("success"):
            slots = slots_result.get("slots", [])
            print(f"    Slots encontrados: {len(slots)}")
        
        # =============================================
        # Resultado final
        # =============================================
        print("\n" + "=" * 70)
        print("RESULTADO FINAL")
        print("=" * 70)
        
        page_info = await toolkit.get_page_info()
        print(f"URL: {page_info.get('url')}")
        print(f"Tipo: {page_info.get('page_type')}")
        
        await toolkit.take_screenshot("resultado_final.png")
        
        print("\nNavegador abierto 60 segundos para inspección...")
        print("Screenshots guardados: paso1-5, resultado_final.png")
        
        await asyncio.sleep(60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        await toolkit.take_screenshot("error.png")
    
    finally:
        print("\nCerrando navegador...")
        await toolkit.close()


if __name__ == "__main__":
    asyncio.run(test_flujo_hasta_editor())
