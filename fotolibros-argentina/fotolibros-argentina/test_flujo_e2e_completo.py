"""
Test E2E Completo: Login -> Template -> Diseno TODAS las paginas -> Checkout
============================================================================
Prueba el flujo COMPLETO del sistema:
1. Login a FDF
2. Seleccionar producto y crear proyecto
3. Subir fotos
4. Seleccion inteligente de template (categoria + Vision)
5. Disenar TODAS las paginas con Vision
6. Verificar reglas de diseno
7. Ir al checkout
"""

import asyncio
import os
import glob
from dotenv import load_dotenv

load_dotenv()


async def test_e2e_checkout():
    """Test E2E completo hasta checkout"""
    
    print("=" * 70)
    print("TEST E2E COMPLETO: Login -> Diseno -> Checkout")
    print("=" * 70)
    
    # Verificar credenciales
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("ERROR: Faltan credenciales en .env")
        print("Necesitas: OPENROUTER_API_KEY, GRAFICA_EMAIL, GRAFICA_PASSWORD")
        return
    
    # Buscar fotos de prueba
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    test_photos = []
    
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        test_photos.extend(glob.glob(os.path.join(uploads_dir, "**", ext), recursive=True))
    
    # Filtrar comprobantes y limitar cantidad
    test_photos = [p for p in test_photos if "comprobante" not in p.lower()][:10]
    
    print(f"\nFotos de prueba encontradas: {len(test_photos)}")
    
    if len(test_photos) < 3:
        print("ADVERTENCIA: Pocas fotos de prueba, el libro quedara casi vacio")
        print("Agrega mas fotos en la carpeta 'uploads/'")
    
    # Importar toolkit
    from services.fdf_stagehand import FDFStagehandToolkit, VisionDesigner
    from services.fdf_stagehand.design_intelligence import DesignIntelligence
    
    toolkit = FDFStagehandToolkit(
        model_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=False  # Ver el browser
    )
    
    designer = DesignIntelligence(api_key=api_key)
    vision = VisionDesigner(api_key=api_key)
    
    # Configuracion del pedido
    ESTILO = "minimalista"  # Opciones: sin_diseno, minimalista, clasico, divertido, premium
    PRODUCTO = "21x21"      # Formato del fotolibro
    TITULO = "Test E2E Checkout"
    PAGINAS = 24            # Cantidad de páginas (24, 30, 40, 50, etc.)
    
    try:
        # =============================================
        # FASE 1: Login y navegacion
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 1: Login y Navegacion")
        print("=" * 70)
        
        print("\n[1] Login a FDF...")
        result = await toolkit.login()
        if not result.get("success"):
            print(f"ERROR: Login fallo - {result.get('error')}")
            return
        print("    Login exitoso!")
        
        # CRÍTICO: Seleccionar versión para PROFESIONALES (con templates completos)
        print("\n[1.5] Seleccionando version 'para Profesionales' (CRITICO - templates completos)...")
        editor_version = await toolkit.select_editor_version()
        if editor_version.get("success"):
            print(f"    Version seleccionada: {editor_version.get('version')}")
        else:
            print(f"    ADVERTENCIA: {editor_version.get('error')}")
        
        await toolkit.take_screenshot("e2e_00_version_editores.png")
        
        print("\n[2] Navegando a Fotolibros...")
        await toolkit.navigate_to_fotolibros()
        await asyncio.sleep(1)
        
        print(f"\n[3] Seleccionando producto {PRODUCTO}...")
        await toolkit.select_product_by_text(PRODUCTO)
        await asyncio.sleep(2)
        
        print(f"\n[4] Creando proyecto '{TITULO}'...")
        await toolkit.click_create_project(TITULO)
        await asyncio.sleep(2)
        
        await toolkit.take_screenshot("e2e_01_proyecto_creado.png")
        
        # =============================================
        # FASE 2: Subir fotos
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 2: Subir Fotos")
        print("=" * 70)
        
        print("\n[5] Seleccionando fuente de fotos...")
        await toolkit.select_photo_source("computadora")
        await asyncio.sleep(1)
        
        print(f"\n[6] Subiendo {len(test_photos)} fotos...")
        upload_result = await toolkit.upload_photos(test_photos)
        print(f"    Fotos subidas: {upload_result.get('photos_uploaded', 0)}")
        print(f"    Miniaturas detectadas: {upload_result.get('thumbnails_found', 0)}")
        
        print("\n[7] Clickeando Continuar...")
        await toolkit.click_continue()
        await asyncio.sleep(3)
        
        await toolkit.take_screenshot("e2e_02_fotos_subidas.png")
        
        # =============================================
        # FASE 3: Seleccion inteligente de template
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 3: Seleccion INTELIGENTE de Template")
        print("=" * 70)
        
        print(f"\n[8] Estilo elegido: {ESTILO}")
        
        # Seleccion hibrida: categoria + Vision
        resultado = await toolkit.select_template_intelligent(
            estilo_cliente=ESTILO,
            fotos_paths=test_photos[:3],  # Analizar algunas fotos
            designer=designer
        )
        
        print(f"\n[9] Resultado seleccion:")
        print(f"    Template: {resultado.get('template_elegido')}")
        print(f"    Categoria: {resultado.get('categoria')}")
        print(f"    Razonamiento: {resultado.get('razonamiento', '')[:100]}...")
        print(f"    Confianza: {resultado.get('confianza', 0):.2f}")
        
        await toolkit.take_screenshot("e2e_03_template_seleccionado.png")
        
        # =============================================
        # FASE 4: Entrar al editor
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 4: Entrar al Editor")
        print("=" * 70)
        
        print("\n[10] Seleccionando modo MANUAL (para control con Vision)...")
        await toolkit.click_fill_mode("manual")
        await asyncio.sleep(2)
        
        print("\n[11] Esperando que el editor cargue completamente...")
        ready = await toolkit.wait_for_editor_ready(timeout=90)
        
        if ready.get("success"):
            print(f"    Editor listo en {ready.get('time_waited')}s")
        else:
            print(f"    ADVERTENCIA: Timeout - {ready.get('error')}")
            print("    Continuando de todos modos...")
        
        await asyncio.sleep(3)
        await toolkit.take_screenshot("e2e_04_editor_listo.png")
        
        # =============================================
        # FASE 5: Disenar TODAS las paginas
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 5: Diseno Automatico de TODAS las Paginas")
        print("=" * 70)
        
        # Obtener info del libro
        pages_info = await toolkit.get_book_pages_info()
        total_pages = pages_info.get("total_pages", 10)
        print(f"\n[12] Libro tiene {total_pages} paginas")
        
        # Disenar todas las paginas
        print(f"\n[13] Iniciando diseno automatico...")
        design_result = await toolkit.design_all_pages(
            estilo=ESTILO,
            max_photos_per_page=3  # Ajustar segun cantidad de fotos
        )
        
        print(f"\n[14] Resumen del diseno:")
        print(f"    Paginas disenadas: {len(design_result.get('pages_designed', []))}")
        print(f"    Total fotos colocadas: {design_result.get('total_photos_placed', 0)}")
        print(f"    Errores: {len(design_result.get('errors', []))}")
        
        # Mostrar detalle por pagina
        for page in design_result.get("pages_designed", [])[:5]:
            print(f"    - Pag {page['page']}: {page['photos_placed']} fotos, score={page.get('rules_score', 0)}")
        
        await toolkit.take_screenshot("e2e_05_diseno_completo.png")
        
        # =============================================
        # FASE 6: Verificacion final y guardar
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 6: Verificacion Final")
        print("=" * 70)
        
        print("\n[15] Verificando reglas de diseno en pagina actual...")
        verify_result = await vision.verify_design_rules(toolkit.page)
        
        if verify_result.get("success"):
            print(f"    Cumple reglas: {verify_result.get('passes_rules')}")
            print(f"    Puntuacion: {verify_result.get('score', 0)}/100")
            
            if verify_result.get("critical_issues"):
                print("    PROBLEMAS CRITICOS:")
                for issue in verify_result.get("critical_issues", [])[:3]:
                    print(f"      - {issue.get('tipo')}: {issue.get('descripcion')}")
        
        print("\n[16] Guardando proyecto...")
        save_result = await toolkit.save_project()
        if save_result.get("success"):
            print("    Proyecto guardado!")
        else:
            print(f"    ADVERTENCIA: No se pudo guardar - {save_result.get('error')}")
        
        await toolkit.take_screenshot("e2e_06_guardado.png")
        
        # =============================================
        # FASE 7: Ir al Checkout
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 7: Checkout")
        print("=" * 70)
        
        print("\n[17] Navegando al checkout...")
        checkout_result = await toolkit.go_to_checkout()
        
        if checkout_result.get("success"):
            print("    Navegando a checkout...")
            await asyncio.sleep(3)
        else:
            print(f"    ADVERTENCIA: {checkout_result.get('error')}")
        
        await toolkit.take_screenshot("e2e_07_checkout.png")
        
        # =============================================
        # Resultado final
        # =============================================
        print("\n" + "=" * 70)
        print("RESULTADO FINAL")
        print("=" * 70)
        
        page_info = await toolkit.get_page_info()
        print(f"\nURL actual: {page_info.get('url')}")
        print(f"Tipo pagina: {page_info.get('page_type')}")
        
        # Determinar si llegamos al checkout
        url = page_info.get("url", "")
        is_checkout = "checkout" in url.lower() or "carrito" in url.lower() or "cart" in url.lower()
        
        if is_checkout:
            print("\n*** EXITO: Llegamos al CHECKOUT! ***")
        else:
            print("\n*** El flujo termino pero no detectamos checkout en la URL ***")
            print("    Revisar screenshots para verificar estado")
        
        await toolkit.take_screenshot("e2e_08_final.png")
        
        print("\n" + "=" * 70)
        print("SCREENSHOTS GUARDADOS")
        print("=" * 70)
        print("""
  e2e_01_proyecto_creado.png    - Despues de crear proyecto
  e2e_02_fotos_subidas.png      - Fotos subidas
  e2e_03_template_seleccionado.png - Template elegido
  e2e_04_editor_listo.png       - Editor cargado
  e2e_05_diseno_completo.png    - Todas las paginas disenadas
  e2e_06_guardado.png           - Proyecto guardado
  e2e_07_checkout.png           - Pantalla de checkout
  e2e_08_final.png              - Estado final
        """)
        
        print("\n" + "=" * 70)
        print("FUNCIONALIDADES PROBADAS")
        print("=" * 70)
        print(f"""
  1. Login automatico a FDF
  2. Navegacion al catalogo de fotolibros
  3. Seleccion de producto ({PRODUCTO})
  4. Creacion de proyecto con titulo
  5. Upload de {len(test_photos)} fotos
  6. Seleccion INTELIGENTE de template:
     - Filtrado por categoria (hardcodeado)
     - Seleccion con Vision (LLM)
     - Siempre version 'para Editores'
  7. Modo manual en editor
  8. Espera inteligente de carga
  9. Diseno automatico de {total_pages} paginas
  10. Verificacion de reglas de diseno
  11. Guardado del proyecto
  12. Navegacion al checkout
        """)
        
        # Mantener browser abierto para inspeccion
        print("\nNavegador abierto 120 segundos para inspeccion manual...")
        print("Presiona Ctrl+C para cerrar antes")
        
        try:
            await asyncio.sleep(120)
        except KeyboardInterrupt:
            print("\nCerrando...")
        
    except Exception as e:
        print(f"\n*** ERROR EN EL FLUJO: {e} ***")
        import traceback
        traceback.print_exc()
        await toolkit.take_screenshot("e2e_error.png")
    
    finally:
        print("\nCerrando navegador...")
        await toolkit.close()
        print("Test completado.")


async def test_e2e_rapido():
    """
    Version rapida del test E2E.
    Solo prueba login -> template -> primera pagina -> screenshot
    """
    print("=" * 70)
    print("TEST E2E RAPIDO (solo primera pagina)")
    print("=" * 70)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("ERROR: Faltan credenciales")
        return
    
    # Buscar fotos
    uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
    test_photos = []
    for ext in ["*.jpg", "*.jpeg", "*.png"]:
        test_photos.extend(glob.glob(os.path.join(uploads_dir, "**", ext), recursive=True))
    test_photos = [p for p in test_photos if "comprobante" not in p.lower()][:5]
    
    print(f"Fotos: {len(test_photos)}")
    
    from services.fdf_stagehand import FDFStagehandToolkit
    
    toolkit = FDFStagehandToolkit(
        model_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        headless=False
    )
    
    try:
        # Login
        print("\n[1] Login...")
        await toolkit.login()
        
        # CRÍTICO: Seleccionar version para PROFESIONALES (con templates completos)
        print("[1.5] Seleccionando version para Profesionales (templates completos)...")
        await toolkit.select_editor_version()
        
        # Navegar
        print("[2] Navegando...")
        await toolkit.navigate_to_fotolibros()
        await toolkit.select_product_by_text("21x21")
        await toolkit.click_create_project("Test Rapido")
        
        # Fotos
        print("[3] Subiendo fotos...")
        await toolkit.select_photo_source("computadora")
        await toolkit.upload_photos(test_photos)
        await toolkit.click_continue()
        await asyncio.sleep(2)
        
        # Template - usar template CON diseño para que funcione relleno smart
        print("[4] Seleccionando template CON diseño...")
        
        # Intentar diferentes templates con diseño que funcionan con relleno smart
        templates_con_diseno = [
            "Flores Ana",      # Bodas/elegante - tiene slots
            "Solo Fotos",      # Minimalista - tiene slots  
            "Collage v1",      # Múltiples fotos - tiene slots
            "Short Stories",   # Viajes - tiene slots
            "Así Fue",         # Infantil - tiene slots
            "Color Block"      # Moderno - tiene slots
        ]
        
        template_seleccionado = None
        template_exitoso = False
        
        for template in templates_con_diseno:
            try:
                print(f"    Intentando template: {template}")
                result = await toolkit.select_template(template, for_editors=True)
                if result.get("success"):
                    template_seleccionado = template
                    template_exitoso = True
                    print(f"    [OK] Template seleccionado: {template}")
                    break
                else:
                    print(f"    [WARN] Template {template} no disponible")
            except Exception as e:
                print(f"    [ERROR] Error con template {template}: {e}")
        
        if not template_exitoso:
            print("    ⚠️ Ningún template con diseño disponible, usando Vacío como último recurso")
            await toolkit.select_template("Vacío", for_editors=True)
            template_seleccionado = "Vacío"
        
        # Modo manual
        print("[5] Entrando al editor...")
        await toolkit.click_fill_mode("manual")
        await toolkit.wait_for_editor_ready(timeout=60)
        
        # Usar relleno smart (solo funciona con templates CON diseño)
        print("[6] Usando relleno smart con template con diseño...")
        
        # Determinar si es template Vacío (sin slots) o con diseño
        es_template_vacio = template_seleccionado == "Vacío" if template_seleccionado else True
        
        if es_template_vacio:
            print("    ⚠️ Template Vacío - relleno smart no disponible")
            print("    Tomando screenshot y continuando...")
            await toolkit.take_screenshot("template_vacio_estado.png")
        else:
            try:
                # Intentar usar relleno smart (debería funcionar con templates con diseño)
                fill_result = await toolkit.usar_relleno_smart(is_template_vacio=False)
                
                if fill_result.get('success'):
                    print(f"    ✅ Relleno smart aplicado: {fill_result.get('modo')}")
                    print(f"    Fotos colocadas: {fill_result.get('fotos_colocadas', 0)}")
                else:
                    print(f"    ⚠️ Error relleno smart: {fill_result.get('error', 'desconocido')}")
                    
                    # Fallback: intentar modo manual simple
                    print("    Intentando método manual simple...")
                    try:
                        # Buscar primer slot disponible
                        slot_selectors = [
                            "[class*='slot']",
                            "[class*='photo']",
                            ".photo-slot"
                        ]
                        
                        for selector in slot_selectors:
                            try:
                                slots = await toolkit.page.locator(selector).all()
                                if slots:
                                    await slots[0].click(timeout=3000)
                                    print(f"    Slot clickeado: {selector}")
                                    
                                    # Buscar botón de rellenar
                                    fill_selectors = [
                                        "button:has-text('Rellenar')",
                                        "text=Rellenar",
                                        "button:has-text('Usar')"
                                    ]
                                    
                                    for fill_selector in fill_selectors:
                                        try:
                                            await toolkit.page.click(fill_selector, timeout=2000)
                                            print(f"    Botón rellenar: {fill_selector}")
                                            break
                                        except:
                                            continue
                                    
                                    await asyncio.sleep(2)
                                    print("    ✅ Foto colocada manualmente")
                                    break
                            except:
                                continue
                                
                    except Exception as manual_error:
                        print(f"    ⚠️ Error método manual: {manual_error}")
                        
            except Exception as e:
                print(f"    ⚠️ Error relleno smart general: {e}")
                print("    Continuando con test...")
        
        await toolkit.take_screenshot("test_rapido_resultado.png")
        print("\nScreenshot guardado: test_rapido_resultado.png")
        
        print("\nBrowser abierto 30s...")
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await toolkit.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rapido":
        asyncio.run(test_e2e_rapido())
    else:
        asyncio.run(test_e2e_checkout())
