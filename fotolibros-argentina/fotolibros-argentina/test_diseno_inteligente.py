"""
Test de Diseño Inteligente de Fotolibros
=========================================
Prueba el flujo completo:
1. Navegación DOM (Playwright) - rápido
2. Análisis visual (Gemini) - inteligente
3. Diseño basado en reglas profesionales
"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_flujo_completo():
    """Test del flujo completo con diseño inteligente"""
    
    print("=" * 70)
    print("TEST: Flujo Completo con Diseño Inteligente")
    print("=" * 70)
    
    # Verificar credenciales
    api_key = os.getenv("OPENROUTER_API_KEY")
    fdf_email = os.getenv("GRAFICA_EMAIL")
    fdf_password = os.getenv("GRAFICA_PASSWORD")
    
    print(f"\nCredenciales:")
    print(f"  API Key: {api_key[:20]}..." if api_key else "  API Key: FALTA")
    print(f"  Email: {fdf_email}")
    print(f"  Modelo: google/gemini-2.0-flash-001")
    
    if not all([api_key, fdf_email, fdf_password]):
        print("\nERROR: Faltan credenciales en .env")
        return
    
    # Importar módulos
    print("\n[1] Importando módulos...")
    from services.fdf_stagehand import FDFStagehandToolkit, VisionDesigner, DesignIntelligence
    from config.design_templates import DESIGN_TEMPLATES, get_template
    
    # Mostrar templates disponibles
    print("\n[2] Templates de diseño disponibles:")
    for tid, template in DESIGN_TEMPLATES.items():
        print(f"    - {tid}: {template.nombre} ({template.interior.fotos_por_pagina} fotos/pág)")
    
    # Crear toolkit
    print("\n[3] Creando toolkit híbrido...")
    toolkit = FDFStagehandToolkit(
        model_api_key=api_key,
        fdf_email=fdf_email,
        fdf_password=fdf_password,
        model_name="google/gemini-2.0-flash-001",
        headless=False
    )
    
    # Crear diseñador inteligente
    designer = DesignIntelligence(
        api_key=api_key,
        model="google/gemini-2.0-flash-001"
    )
    
    # Crear vision para análisis del editor
    vision = VisionDesigner(
        api_key=api_key,
        model="google/gemini-2.0-flash-001"
    )
    
    try:
        # =============================================
        # FASE 1: Navegación DOM (rápido)
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 1: Navegación DOM (Playwright)")
        print("=" * 70)
        
        result = await toolkit.full_flow_to_editor(product_search="21x21")
        
        if not result.get("success"):
            print("\nERROR: No se pudo llegar al editor")
            for step in result.get("results", {}).get("steps", []):
                print(f"  - {step['step']}: {step['result'].get('success')}")
            return
        
        print("\n[OK] Llegamos al editor!")
        
        # =============================================
        # FASE 2: Análisis Visual del Editor (Gemini)
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 2: Análisis Visual del Editor (Gemini Vision)")
        print("=" * 70)
        
        await asyncio.sleep(3)  # Esperar que cargue el editor
        
        print("\n[4] Analizando estado del editor...")
        analysis = await vision.analyze_editor(toolkit.page)
        
        if analysis.get("success"):
            info = analysis.get("analysis", {})
            print(f"    Tipo de página: {info.get('tipo_pagina', 'desconocido')}")
            print(f"    Editor visible: {info.get('editor_visible', False)}")
            if info.get("canvas"):
                canvas = info["canvas"]
                print(f"    Canvas: {canvas.get('width', '?')}x{canvas.get('height', '?')} en ({canvas.get('x', '?')}, {canvas.get('y', '?')})")
            if info.get("panel_fotos"):
                panel = info["panel_fotos"]
                print(f"    Panel fotos: {panel.get('posicion', '?')}, {panel.get('fotos_count', 0)} fotos")
            print(f"    Siguiente acción: {info.get('siguiente_accion', 'N/A')}")
        else:
            print(f"    Error: {analysis.get('error')}")
        
        # =============================================
        # FASE 3: Buscar Slots para Fotos
        # =============================================
        print("\n[5] Buscando slots para fotos...")
        slots_result = await vision.find_photo_slots(toolkit.page)
        
        if slots_result.get("success"):
            slots = slots_result.get("slots", [])
            print(f"    Slots encontrados: {len(slots)}")
            for slot in slots[:5]:
                print(f"      - {slot.get('id', '?')}: ({slot.get('x', 0):.0f}, {slot.get('y', 0):.0f}) "
                      f"{'VACIO' if slot.get('vacio') else 'con foto'}")
        else:
            print(f"    No se encontraron slots: {slots_result.get('error', 'desconocido')}")
        
        # =============================================
        # FASE 4: Info del Template de Diseño
        # =============================================
        print("\n" + "=" * 70)
        print("FASE 3: Reglas de Diseño")
        print("=" * 70)
        
        estilo = "clasico"
        template_info = designer.get_template_info(estilo)
        print(f"\n[6] Template seleccionado: {template_info['nombre']}")
        print(f"    Fotos por página: {template_info['fotos_por_pagina']}")
        print(f"    Layout default: {template_info['layout_default']}")
        print(f"    Ideal para: {', '.join(template_info['ideal_para'])}")
        
        layouts = designer.get_available_layouts()
        print(f"\n[7] Layouts disponibles:")
        for layout in layouts:
            print(f"    - {layout['id']}: {layout['name']} ({layout['num_fotos']} fotos)")
        
        # =============================================
        # Screenshot para debug
        # =============================================
        print("\n[8] Guardando screenshot...")
        await toolkit.take_screenshot("editor_analizado.png")
        print("    Guardado: editor_analizado.png")
        
        # Mantener abierto
        print("\n" + "=" * 70)
        print("PRUEBA COMPLETADA")
        print("=" * 70)
        print("\nNavegador abierto por 30 segundos para inspección...")
        print("Revisa: editor_analizado.png")
        
        await asyncio.sleep(30)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nCerrando navegador...")
        await toolkit.close()
        print("Cerrado.")


async def test_solo_diseno():
    """Test solo del módulo de diseño (sin navegador)"""
    
    print("=" * 70)
    print("TEST: Módulo de Diseño Inteligente (sin navegador)")
    print("=" * 70)
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    from services.fdf_stagehand import DesignIntelligence
    
    designer = DesignIntelligence(
        api_key=api_key,
        model="google/gemini-2.0-flash-001"
    )
    
    # Mostrar info de templates
    print("\n[1] Templates disponibles:")
    for estilo in ["minimalista", "clasico", "divertido", "premium"]:
        info = designer.get_template_info(estilo)
        print(f"\n  {estilo.upper()}:")
        print(f"    - Fotos/página: {info['fotos_por_pagina']}")
        print(f"    - Layout: {info['layout_default']}")
        print(f"    - Con fondo: {info['con_fondo']}")
        print(f"    - Ideal para: {', '.join(info['ideal_para'][:3])}")
    
    # Mostrar layouts
    print("\n[2] Layouts de FDF disponibles:")
    layouts = designer.get_available_layouts()
    for layout in layouts:
        print(f"    - {layout['id']}: {layout['num_fotos']} fotos")
    
    print("\n[OK] Módulo de diseño funcionando correctamente")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--solo-diseno":
        asyncio.run(test_solo_diseno())
    else:
        asyncio.run(test_flujo_completo())
