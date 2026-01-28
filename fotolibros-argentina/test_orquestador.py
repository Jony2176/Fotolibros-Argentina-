"""
Test del Orquestador Actualizado
================================
Prueba el flujo completo del orquestador con el nuevo toolkit hibrido.
"""

import asyncio
import os
import glob
from dotenv import load_dotenv

load_dotenv()


async def test_orquestador():
    """Test del orquestador con el nuevo toolkit"""
    
    print("=" * 70)
    print("TEST: Orquestador con FDF Stagehand Toolkit")
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
    
    test_photos = [p for p in test_photos if "comprobante" not in p.lower()][:5]
    
    print(f"\nFotos de prueba encontradas: {len(test_photos)}")
    
    if len(test_photos) < 2:
        print("ERROR: Necesitas al menos 2 fotos de prueba en uploads/")
        return
    
    # Importar orquestador
    from agents.orquestador import OrquestadorFotolibros, PedidoInfo
    
    # Crear pedido de prueba
    pedido = PedidoInfo(
        pedido_id="test-orq-001",
        producto_codigo="CU-21x21-DURA",
        estilo_diseno="clasico",  # Probar con estilo clasico
        paginas_total=22,
        cliente_nombre="Test Usuario",
        cliente_email="test@test.com",
        titulo_tapa="Recuerdos de Prueba",
        texto_lomo="2024",
        fotos_paths=test_photos,
        comentarios_cliente="Quiero un libro elegante para un aniversario"
    )
    
    print(f"\nPedido de prueba:")
    print(f"  ID: {pedido.pedido_id}")
    print(f"  Producto: {pedido.producto_codigo}")
    print(f"  Estilo: {pedido.estilo_diseno}")
    print(f"  Titulo: {pedido.titulo_tapa}")
    print(f"  Fotos: {len(pedido.fotos_paths)}")
    
    # Callback para ver progreso
    async def on_progress(mensaje, progreso):
        print(f"  [{progreso}%] {mensaje}")
    
    # Crear orquestador y procesar
    print("\n" + "=" * 70)
    print("INICIANDO PROCESAMIENTO")
    print("=" * 70)
    
    orquestador = OrquestadorFotolibros()
    resultado = await orquestador.procesar_pedido(pedido, on_progress=on_progress)
    
    # Mostrar resultado
    print("\n" + "=" * 70)
    print("RESULTADO FINAL")
    print("=" * 70)
    
    print(f"\nExito: {resultado.get('exito')}")
    print(f"Proyecto ID: {resultado.get('proyecto_id')}")
    print(f"Estado: {resultado.get('estado')}")
    print(f"Progreso: {resultado.get('progreso')}%")
    
    if resultado.get('template_usado'):
        print(f"Template usado: {resultado.get('template_usado')}")
    
    if resultado.get('fotos_colocadas'):
        print(f"Fotos colocadas: {resultado.get('fotos_colocadas')}")
    
    if resultado.get('score_diseño'):
        print(f"Score diseño: {resultado.get('score_diseño')}/100")
    
    if resultado.get('error'):
        print(f"Error: {resultado.get('error')}")
    
    print("\n" + "=" * 70)
    print("LOGS DEL PROCESO")
    print("=" * 70)
    
    for log in resultado.get('logs', [])[-20:]:  # Ultimos 20 logs
        print(log)
    
    return resultado


async def test_estilos():
    """Test rapido de diferentes estilos"""
    
    print("=" * 70)
    print("TEST: Diferentes Estilos de Diseño")
    print("=" * 70)
    
    from services.fdf_stagehand.design_intelligence import DesignIntelligence
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    designer = DesignIntelligence(api_key=api_key)
    
    estilos = ["sin_diseno", "minimalista", "clasico", "divertido", "premium"]
    
    print("\nMapeo de estilos a categorias y templates:\n")
    
    for estilo in estilos:
        cat_info = designer.obtener_categoria_fdf(estilo)
        template_info = designer.seleccionar_template_fdf(estilo)
        
        print(f"ESTILO: {estilo.upper()}")
        print(f"  Categoria FDF: {cat_info['categoria_fdf']}")
        print(f"  Templates sugeridos: {cat_info['templates_sugeridos'][:3]}")
        print(f"  Template a usar: {template_info['template_fdf']}")
        print(f"  Es solo fotos: {cat_info.get('es_solo_fotos', False)}")
        print(f"  Version Editores: {template_info['es_version_editores']}")
        print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--estilos":
        asyncio.run(test_estilos())
    else:
        asyncio.run(test_orquestador())
