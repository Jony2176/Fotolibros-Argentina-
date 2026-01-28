"""
Test Hybrid Toolkit
===================
Tests para el enfoque hibrido:
- Pattern Cache (SQLite)
- Stagehand v3 Wrapper
- Metodos hibridos del FDFStagehandToolkit

Ejecutar:
    python test_hybrid_toolkit.py
    python test_hybrid_toolkit.py --full  # Incluye tests con browser
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# ==================================================
# TESTS DE PATTERN CACHE
# ==================================================

def test_pattern_cache():
    """Test del Pattern Cache en memoria"""
    print("\n" + "=" * 60)
    print("TEST: Pattern Cache (SQLite en memoria)")
    print("=" * 60)
    
    from services.fdf_stagehand.pattern_cache import FDFPatternCache
    
    # Crear cache en memoria para testing
    cache = FDFPatternCache(":memory:")
    
    # Test 1: Cache MISS inicial
    print("\n[Test 1] Cache MISS inicial...")
    result = cache.get_cached_slot("collage_2x2", "top_left", 1920, 1080)
    assert result is None, "Deberia ser None (cache vacio)"
    print("  OK - Cache MISS esperado")
    
    # Test 2: Guardar patron
    print("\n[Test 2] Guardar patron de slot...")
    coords = {
        "x": 100,
        "y": 100,
        "width": 400,
        "height": 300,
        "center_x": 300,
        "center_y": 250
    }
    saved = cache.save_slot_pattern("collage_2x2", "top_left", 1920, 1080, coords, confidence=0.95)
    assert saved, "Deberia guardarse correctamente"
    print("  OK - Patron guardado")
    
    # Test 3: Cache HIT
    print("\n[Test 3] Cache HIT...")
    result = cache.get_cached_slot("collage_2x2", "top_left", 1920, 1080)
    assert result is not None, "Deberia retornar el patron"
    assert result["from_cache"] is True, "Deberia indicar que viene del cache"
    assert result["center_x"] == 300, "Coordenadas incorrectas"
    print(f"  OK - Cache HIT: center=({result['center_x']}, {result['center_y']})")
    
    # Test 4: Tolerancia de viewport
    print("\n[Test 4] Tolerancia de viewport...")
    result = cache.get_cached_slot("collage_2x2", "top_left", 1910, 1070, tolerance=50)
    assert result is not None, "Deberia encontrar con tolerancia de 50px"
    print("  OK - Tolerancia funciona (1910x1070 encontro 1920x1080)")
    
    # Test 5: Sin tolerancia suficiente
    result = cache.get_cached_slot("collage_2x2", "top_left", 1800, 900, tolerance=50)
    assert result is None, "No deberia encontrar (fuera de tolerancia)"
    print("  OK - Fuera de tolerancia retorna None")
    
    # Test 6: UI Elements
    print("\n[Test 6] UI Elements cache...")
    ui_coords = {"x": 50, "y": 10, "width": 100, "height": 40}
    cache.save_ui_element("login_button", 1920, 1080, ui_coords, selector="#btn-login")
    result = cache.get_cached_ui_element("login_button", 1920, 1080)
    assert result is not None, "Deberia retornar el elemento UI"
    assert result["selector"] == "#btn-login"
    print("  OK - UI Element guardado y recuperado")
    
    # Test 7: Template Patterns
    print("\n[Test 7] Template Patterns cache...")
    template_coords = {"x": 200, "y": 150, "width": 180, "height": 220}
    cache.save_template_pattern("Clasico ED", 1920, 1080, template_coords, category="fotolibros")
    result = cache.get_cached_template("Clasico ED", 1920, 1080)
    assert result is not None, "Deberia retornar el template"
    assert result["category"] == "fotolibros"
    print("  OK - Template Pattern guardado y recuperado")
    
    # Test 8: Estadisticas
    print("\n[Test 8] Estadisticas del cache...")
    stats = cache.get_cache_stats()
    print(f"  Slots: {stats['slots']['total']} (hits: {stats['slots']['hits']})")
    print(f"  UI Elements: {stats['ui_elements']['total']} (hits: {stats['ui_elements']['hits']})")
    print(f"  Templates: {stats['templates']['total']} (hits: {stats['templates']['hits']})")
    print(f"  Total patrones: {stats['total_patterns']}")
    print(f"  Eficiencia: {stats['cache_efficiency']}")
    assert stats["total_patterns"] == 3, "Deberia haber 3 patrones"
    print("  OK - Estadisticas correctas")
    
    # Test 9: Mark success/failure
    print("\n[Test 9] Mark success/failure...")
    cache.mark_slot_success("collage_2x2", "top_left", 1920, 1080)
    cache.mark_slot_success("collage_2x2", "top_left", 1920, 1080)
    stats = cache.get_cache_stats()
    print(f"  Success rate: {stats['slots']['success_rate']}%")
    print("  OK - Success marcado")
    
    # Test 10: Invalidation
    print("\n[Test 10] Invalidacion de patron...")
    cache.invalidate_slot("collage_2x2", "top_left")
    result = cache.get_cached_slot("collage_2x2", "top_left", 1920, 1080)
    assert result is None, "Patron deberia estar invalidado"
    print("  OK - Patron invalidado correctamente")
    
    # Cleanup
    cache.close()
    
    print("\n" + "-" * 60)
    print("PATTERN CACHE: TODOS LOS TESTS PASARON")
    print("-" * 60)
    return True


# ==================================================
# TESTS DE STAGEHAND WRAPPER (requiere Chrome)
# ==================================================

async def test_stagehand_wrapper():
    """Test del Stagehand Wrapper (requiere Chrome instalado)"""
    print("\n" + "=" * 60)
    print("TEST: Stagehand v3 Wrapper")
    print("=" * 60)
    
    from services.fdf_stagehand.stagehand_wrapper import STAGEHAND_AVAILABLE, FDFStagehandWrapper
    
    if not STAGEHAND_AVAILABLE:
        print("\n[SKIP] Stagehand no esta instalado")
        print("  Instalar con: pip install stagehand")
        return None
    
    # Verificar si hay API key
    api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n[SKIP] No hay API key configurada")
        print("  Configurar OPENROUTER_API_KEY o GOOGLE_API_KEY")
        return None
    
    print("\n[Test 1] Inicializacion del wrapper...")
    try:
        wrapper = FDFStagehandWrapper(
            model_name="google/gemini-2.0-flash-exp",
            headless=True
        )
        print("  OK - Wrapper inicializado")
    except Exception as e:
        print(f"  ERROR - {e}")
        return False
    
    print("\n[Test 2] Inicio de sesion (Chrome local)...")
    try:
        await wrapper.start()
        assert wrapper.is_started, "Deberia estar iniciado"
        print("  OK - Sesion iniciada")
    except Exception as e:
        print(f"  ERROR iniciando sesion: {e}")
        print("  (Asegurate de tener Chrome instalado)")
        return False
    
    print("\n[Test 3] Navegacion a ejemplo...")
    try:
        result = await wrapper.navigate("https://example.com")
        assert result["success"], f"Navegacion fallo: {result.get('error')}"
        print("  OK - Navegacion exitosa")
    except Exception as e:
        print(f"  ERROR - {e}")
    
    print("\n[Test 4] Observe (encontrar elementos)...")
    try:
        result = await wrapper.observe("find all links on the page")
        print(f"  Encontrados: {result.get('count', 0)} elementos")
        if result["success"]:
            print("  OK - Observe funciona")
        else:
            print(f"  Warning: {result.get('error')}")
    except Exception as e:
        print(f"  ERROR - {e}")
    
    print("\n[Test 5] Cierre de sesion...")
    try:
        await wrapper.stop()
        assert not wrapper.is_started, "Deberia estar cerrado"
        print("  OK - Sesion cerrada")
    except Exception as e:
        print(f"  ERROR - {e}")
        return False
    
    print("\n" + "-" * 60)
    print("STAGEHAND WRAPPER: TESTS COMPLETADOS")
    print("-" * 60)
    return True


# ==================================================
# TESTS DE IMPORTS
# ==================================================

def test_imports():
    """Verifica que todos los imports funcionen"""
    print("\n" + "=" * 60)
    print("TEST: Imports del modulo fdf_stagehand")
    print("=" * 60)
    
    errors = []
    
    # Test imports principales
    print("\n[Test] Importando FDFStagehandToolkit...")
    try:
        from services.fdf_stagehand import FDFStagehandToolkit
        print("  OK")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(str(e))
    
    print("\n[Test] Importando get_fdf_stagehand_tools...")
    try:
        from services.fdf_stagehand import get_fdf_stagehand_tools
        print("  OK")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(str(e))
    
    print("\n[Test] Importando FDFPatternCache...")
    try:
        from services.fdf_stagehand import FDFPatternCache, get_pattern_cache
        print("  OK")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(str(e))
    
    print("\n[Test] Importando FDFStagehandWrapper...")
    try:
        from services.fdf_stagehand import FDFStagehandWrapper, FDFStagehandActions, STAGEHAND_AVAILABLE
        print(f"  OK (STAGEHAND_AVAILABLE={STAGEHAND_AVAILABLE})")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(str(e))
    
    print("\n[Test] Importando stagehand_session...")
    try:
        from services.fdf_stagehand import stagehand_session
        print("  OK")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(str(e))
    
    print("\n[Test] Importando VisionDesigner...")
    try:
        from services.fdf_stagehand import VisionDesigner
        print("  OK")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(str(e))
    
    print("\n[Test] Importando DesignIntelligence...")
    try:
        from services.fdf_stagehand import DesignIntelligence
        print("  OK")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(str(e))
    
    print("\n[Test] Importando error_handling...")
    try:
        from services.fdf_stagehand import (
            FDFError, LoginError, NavigationError, UploadError,
            TemplateError, EditorError, VisionError, DragDropError,
            CheckoutError, TimeoutError, retry_async, retry_sync,
            VisionFallback, RecoveryStrategy, SafeOperation, health_check
        )
        print("  OK")
    except Exception as e:
        print(f"  ERROR: {e}")
        errors.append(str(e))
    
    if errors:
        print("\n" + "-" * 60)
        print(f"IMPORTS: {len(errors)} ERRORES")
        print("-" * 60)
        return False
    else:
        print("\n" + "-" * 60)
        print("IMPORTS: TODOS LOS TESTS PASARON")
        print("-" * 60)
        return True


# ==================================================
# TEST DE METODOS HIBRIDOS (sin browser)
# ==================================================

def test_hybrid_methods_existence():
    """Verifica que los metodos hibridos existan en FDFStagehandToolkit"""
    print("\n" + "=" * 60)
    print("TEST: Metodos Hibridos en FDFStagehandToolkit")
    print("=" * 60)
    
    from services.fdf_stagehand import FDFStagehandToolkit
    
    hybrid_methods = [
        "select_template_hybrid",
        "drag_photo_to_slot_hybrid",
        "auto_fill_page_hybrid",
        "execute_with_stagehand",
        "get_stats",
    ]
    
    missing = []
    for method in hybrid_methods:
        if hasattr(FDFStagehandToolkit, method):
            print(f"  OK - {method}() existe")
        else:
            print(f"  MISSING - {method}() no encontrado")
            missing.append(method)
    
    if missing:
        print(f"\n  ADVERTENCIA: {len(missing)} metodos no encontrados")
        print("  (Pueden estar pendientes de implementacion)")
        return False
    
    print("\n" + "-" * 60)
    print("METODOS HIBRIDOS: TODOS PRESENTES")
    print("-" * 60)
    return True


# ==================================================
# MAIN
# ==================================================

async def main():
    """Ejecuta todos los tests"""
    print("\n" + "=" * 70)
    print(" TEST HYBRID TOOLKIT - Fotolibros Argentina")
    print(" " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    full_test = "--full" in sys.argv
    
    results = {}
    
    # Test 1: Imports
    results["imports"] = test_imports()
    
    # Test 2: Pattern Cache
    results["pattern_cache"] = test_pattern_cache()
    
    # Test 3: Metodos hibridos
    results["hybrid_methods"] = test_hybrid_methods_existence()
    
    # Test 4: Stagehand (solo con --full)
    if full_test:
        results["stagehand"] = await test_stagehand_wrapper()
    else:
        print("\n[INFO] Ejecuta con --full para tests de Stagehand con browser")
    
    # Resumen
    print("\n")
    print("=" * 70)
    print(" RESUMEN DE TESTS")
    print("=" * 70)
    
    for test_name, passed in results.items():
        if passed is True:
            status = "PASS"
        elif passed is False:
            status = "FAIL"
        else:
            status = "SKIP"
        print(f"  {test_name:30} {status}")
    
    failed = sum(1 for v in results.values() if v is False)
    if failed > 0:
        print(f"\n  {failed} test(s) fallaron")
        return 1
    else:
        print("\n  Todos los tests pasaron!")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
