"""
Test rápido de integración AGNO Team
Verifica que el sistema esté cargado correctamente
"""

import sys
import os

# Agregar path del backend
sys.path.insert(0, r"C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-argentina")

print("="*70)
print("  TEST DE INTEGRACIÓN AGNO TEAM")
print("="*70)

# Test 1: Verificar imports del backend
print("\n📦 Test 1: Verificando imports del backend...")
try:
    from agents import orquestador
    print("   ✅ orquestador.py importado correctamente")
except Exception as e:
    print(f"   ❌ Error importando orquestador: {e}")
    sys.exit(1)

# Test 2: Verificar que AGNO Team está disponible
print("\n🎨 Test 2: Verificando disponibilidad de AGNO Team...")
try:
    from agents.orquestador import AGNO_TEAM_DISPONIBLE
    if AGNO_TEAM_DISPONIBLE:
        print("   ✅ Sistema AGNO Team DISPONIBLE")
    else:
        print("   ⚠️  Sistema AGNO Team NO disponible (usando fallback)")
except Exception as e:
    print(f"   ❌ Error verificando AGNO Team: {e}")

# Test 3: Verificar imports del módulo AGNO Team
if AGNO_TEAM_DISPONIBLE:
    print("\n📚 Test 3: Verificando módulos AGNO Team...")
    try:
        from agents.orquestador_agno_team import (
            analizar_fotos_con_agno_team,
            preparar_diseño_con_agno_team,
            AGNOTeamProcessor
        )
        print("   ✅ Módulo orquestador_agno_team importado")
        print("   ✅ Funciones disponibles:")
        print("      - analizar_fotos_con_agno_team")
        print("      - preparar_diseño_con_agno_team")
        print("      - AGNOTeamProcessor")
    except Exception as e:
        print(f"   ❌ Error importando módulo AGNO Team: {e}")
        import traceback
        traceback.print_exc()

# Test 4: Verificar dependencias críticas
print("\n🔧 Test 4: Verificando dependencias críticas...")
try:
    import agno
    print(f"   ✅ AGNO instalado (v{agno.__version__})")
except:
    print("   ❌ AGNO no instalado")

try:
    from PIL import Image
    print("   ✅ Pillow instalado (para Vision AI)")
except:
    print("   ❌ Pillow no instalado")

try:
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        print(f"   ✅ OPENROUTER_API_KEY configurada ({api_key[:20]}...)")
    else:
        print("   ⚠️  OPENROUTER_API_KEY no encontrada en .env")
except:
    print("   ❌ python-dotenv no instalado")

# Test 5: Verificar que el backend AGNO existe
print("\n📁 Test 5: Verificando estructura de archivos...")
agno_backend_path = r"C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-agno-backend"
if os.path.exists(agno_backend_path):
    print(f"   ✅ Backend AGNO encontrado: {agno_backend_path}")
    
    agents_path = os.path.join(agno_backend_path, "agents")
    if os.path.exists(agents_path):
        print("   ✅ Directorio agents/ existe")
        
        agent_files = [
            "photo_analyzer.py",
            "motif_detector.py",
            "chronology_specialist.py",
            "story_generator.py",
            "design_curator.py"
        ]
        
        for agent_file in agent_files:
            path = os.path.join(agents_path, agent_file)
            if os.path.exists(path):
                print(f"      ✅ {agent_file}")
            else:
                print(f"      ❌ {agent_file} NO ENCONTRADO")
    else:
        print("   ❌ Directorio agents/ no existe")
else:
    print(f"   ❌ Backend AGNO no encontrado: {agno_backend_path}")

print("\n" + "="*70)
if AGNO_TEAM_DISPONIBLE:
    print("  ✅ SISTEMA LISTO PARA USAR AGNO TEAM")
else:
    print("  ⚠️  SISTEMA USARÁ FALLBACK (sistema legacy)")
print("="*70)
print()
