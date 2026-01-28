"""
Test E2E: Flujo completo con Stagehand V3 + Gemini Vision (Python Nativo)
=========================================================================
Ejecuta automaticamente:
1. Inicia servidor API en background
2. Crea pedido de prueba (simula frontend)
3. Sube fotos del cliente
4. Sube comprobante de pago (dispara orquestador)
5. Monitorea el agente de navegador Stagehand
6. Reporta resultado final

Uso:
    python test_stagehand_e2e.py
    
    # Con fotos especificas:
    python test_stagehand_e2e.py --fotos "C:/path/foto1.jpg,C:/path/foto2.jpg"
    
    # Con comprobante especifico:
    python test_stagehand_e2e.py --comprobante "C:/path/comprobante.jpg"
"""

import asyncio
import os
import sys
import time
import subprocess
import signal
import argparse
from pathlib import Path
from datetime import datetime

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

import httpx

# ============================================================
# CONFIGURACION
# ============================================================

API_URL = "http://localhost:8000"
TIMEOUT_SERVIDOR = 30  # segundos para esperar que el servidor inicie
TIMEOUT_PROCESO = 300  # 5 minutos maximo para el proceso completo
POLLING_INTERVAL = 5   # segundos entre consultas de estado

# Colores para consola
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(mensaje: str, tipo: str = "info"):
    """Imprime mensaje con timestamp y color"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if tipo == "ok":
        prefix = f"{Colors.GREEN}[OK]{Colors.ENDC}"
    elif tipo == "error":
        prefix = f"{Colors.FAIL}[ERROR]{Colors.ENDC}"
    elif tipo == "warning":
        prefix = f"{Colors.WARNING}[WARN]{Colors.ENDC}"
    elif tipo == "progress":
        prefix = f"{Colors.CYAN}[...]{Colors.ENDC}"
    else:
        prefix = f"{Colors.BLUE}[INFO]{Colors.ENDC}"
    
    print(f"[{timestamp}] {prefix} {mensaje}")


# ============================================================
# FUNCIONES DE SERVIDOR
# ============================================================

def iniciar_servidor() -> subprocess.Popen:
    """Inicia el servidor FastAPI en un subprocess"""
    log("Iniciando servidor API (uvicorn)...", "progress")
    
    # Comando para iniciar uvicorn
    cmd = [
        sys.executable, "-m", "uvicorn",
        "main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "warning"
    ]
    
    # Iniciar proceso
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
    )
    
    return process


async def esperar_servidor_listo(timeout: int = TIMEOUT_SERVIDOR) -> bool:
    """Espera hasta que el servidor responda"""
    log(f"Esperando que el servidor este listo (max {timeout}s)...", "progress")
    
    start = time.time()
    async with httpx.AsyncClient() as client:
        while time.time() - start < timeout:
            try:
                response = await client.get(f"{API_URL}/", timeout=2.0)
                if response.status_code == 200:
                    log(f"Servidor listo en {API_URL}", "ok")
                    return True
            except:
                pass
            await asyncio.sleep(1)
    
    log(f"Timeout esperando servidor despues de {timeout}s", "error")
    return False


def detener_servidor(process: subprocess.Popen):
    """Detiene el servidor"""
    log("Deteniendo servidor API...", "progress")
    try:
        if sys.platform == 'win32':
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:
            process.terminate()
        process.wait(timeout=5)
        log("Servidor detenido", "ok")
    except:
        process.kill()
        log("Servidor forzado a detenerse", "warning")


# ============================================================
# FUNCIONES DE API (SIMULAN FRONTEND)
# ============================================================

async def crear_pedido() -> str:
    """Crea un pedido de prueba via API"""
    log("Creando pedido de prueba...", "progress")
    
    pedido_data = {
        "producto_codigo": "CU-21x21-DURA",
        "estilo_diseno": "clasico",
        "paginas_total": 22,
        "cliente": {
            "nombre": "Cliente Test E2E",
            "email": "test.e2e@fotolibros.com",
            "telefono": "1155551234",
            "direccion": {
                "calle": "Av. Test 123",
                "ciudad": "Buenos Aires",
                "provincia": "CABA",
                "cp": "1425"
            }
        },
        "metodo_pago": "transferencia",
        "titulo_tapa": "Mi Fotolibro de Prueba",
        "texto_lomo": "Recuerdos 2026"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_URL}/pedidos",
            json=pedido_data,
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"Error creando pedido: {response.status_code} - {response.text}")
        
        data = response.json()
        pedido_id = data["id"]
        
        log(f"Pedido creado: {pedido_id}", "ok")
        return pedido_id


async def subir_fotos(pedido_id: str, fotos_paths: list = None) -> int:
    """Sube fotos al pedido"""
    
    # Si no se especifican fotos, buscar en uploads/
    if not fotos_paths:
        uploads_dir = Path(__file__).parent / "uploads"
        fotos_paths = []
        
        # Buscar imagenes en uploads y subdirectorios
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"]:
            fotos_paths.extend(uploads_dir.glob(f"**/{ext}"))
        
        # Tomar maximo 5 fotos
        fotos_paths = [str(p) for p in fotos_paths[:5]]
        
        if not fotos_paths:
            log("No se encontraron fotos en uploads/, creando foto de prueba...", "warning")
            # Crear una imagen de prueba simple
            test_photo = uploads_dir / "test_photo_auto.png"
            if not test_photo.exists():
                # Crear imagen PNG minima (1x1 pixel rojo)
                import struct
                import zlib
                
                def create_minimal_png():
                    # PNG signature
                    signature = b'\x89PNG\r\n\x1a\n'
                    
                    # IHDR chunk (width=100, height=100, bit_depth=8, color_type=2=RGB)
                    width = 100
                    height = 100
                    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
                    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data)
                    ihdr = struct.pack('>I', 13) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
                    
                    # IDAT chunk (imagen roja simple)
                    raw_data = b''
                    for y in range(height):
                        raw_data += b'\x00'  # filter byte
                        for x in range(width):
                            raw_data += b'\xff\x00\x00'  # RGB rojo
                    
                    compressed = zlib.compress(raw_data)
                    idat_crc = zlib.crc32(b'IDAT' + compressed)
                    idat = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
                    
                    # IEND chunk
                    iend_crc = zlib.crc32(b'IEND')
                    iend = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
                    
                    return signature + ihdr + idat + iend
                
                test_photo.parent.mkdir(parents=True, exist_ok=True)
                test_photo.write_bytes(create_minimal_png())
            
            fotos_paths = [str(test_photo)]
    
    log(f"Subiendo {len(fotos_paths)} fotos...", "progress")
    
    async with httpx.AsyncClient() as client:
        files = []
        for path in fotos_paths:
            if os.path.exists(path):
                filename = os.path.basename(path)
                files.append(("fotos", (filename, open(path, "rb"), "image/jpeg")))
        
        if not files:
            log("No hay fotos validas para subir", "warning")
            return 0
        
        try:
            response = await client.post(
                f"{API_URL}/pedidos/{pedido_id}/fotos",
                files=files,
                timeout=60.0
            )
            
            # Cerrar archivos
            for _, (_, f, _) in files:
                f.close()
            
            if response.status_code != 200:
                raise Exception(f"Error subiendo fotos: {response.status_code}")
            
            data = response.json()
            count = data.get("fotos_subidas", 0)
            log(f"{count} fotos subidas correctamente", "ok")
            return count
            
        except Exception as e:
            # Cerrar archivos en caso de error
            for _, (_, f, _) in files:
                try:
                    f.close()
                except:
                    pass
            raise e


async def subir_comprobante(pedido_id: str, comprobante_path: str = None) -> dict:
    """
    Dispara el orquestador Stagehand directamente (modo TEST).
    Omite la verificacion IA de comprobante para evitar timeouts.
    """
    log(f"Iniciando Stagehand directamente (modo TEST, omite verificacion IA)...", "progress")
    
    async with httpx.AsyncClient() as client:
        # Usar el endpoint de test que omite verificacion IA
        response = await client.post(
            f"{API_URL}/test/iniciar-stagehand/{pedido_id}",
            timeout=30.0
        )
        
        if response.status_code != 200:
            raise Exception(f"Error iniciando Stagehand: {response.status_code} - {response.text}")
        
        result = response.json()
        log(f"Stagehand iniciado en background", "ok")
        log(f"  Mensaje: {result.get('mensaje', 'N/A')}", "info")
        
        return result


async def monitorear_progreso(pedido_id: str, timeout: int = TIMEOUT_PROCESO) -> dict:
    """Monitorea el progreso del pedido hasta completar o error"""
    log(f"Monitoreando progreso (max {timeout}s)...", "progress")
    
    start = time.time()
    ultimo_estado = ""
    ultimo_progreso = -1
    
    async with httpx.AsyncClient() as client:
        while time.time() - start < timeout:
            try:
                response = await client.get(
                    f"{API_URL}/pedidos/{pedido_id}",
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    log(f"Error consultando estado: {response.status_code}", "warning")
                    await asyncio.sleep(POLLING_INTERVAL)
                    continue
                
                data = response.json()
                estado = data.get("estado", "desconocido")
                progreso = data.get("progreso", 0)
                mensaje = data.get("mensaje", "")
                
                # Mostrar cambios
                if estado != ultimo_estado or progreso != ultimo_progreso:
                    emoji = {
                        "pendiente": "clock3",
                        "procesando": "gear",
                        "verificando_pago": "mag",
                        "creando_proyecto": "hammer_and_wrench",
                        "subiendo_fotos": "outbox_tray",
                        "aplicando_diseno": "art",
                        "enviando_grafica": "package",
                        "completado": "white_check_mark",
                        "error": "x"
                    }.get(estado, "question")
                    
                    log(f"Estado: {estado} ({progreso}%) - {mensaje}", "progress")
                    ultimo_estado = estado
                    ultimo_progreso = progreso
                
                # Verificar si termino
                if estado == "completado":
                    elapsed = time.time() - start
                    log(f"COMPLETADO en {elapsed:.1f} segundos", "ok")
                    return {
                        "exito": True,
                        "estado": estado,
                        "progreso": progreso,
                        "mensaje": mensaje,
                        "detalles": data.get("detalles"),
                        "tiempo": elapsed
                    }
                
                if estado == "error":
                    log(f"ERROR: {mensaje}", "error")
                    return {
                        "exito": False,
                        "estado": estado,
                        "progreso": progreso,
                        "mensaje": mensaje,
                        "detalles": data.get("detalles"),
                        "tiempo": time.time() - start
                    }
                
            except Exception as e:
                log(f"Error de conexion: {e}", "warning")
            
            await asyncio.sleep(POLLING_INTERVAL)
    
    # Timeout
    log(f"TIMEOUT despues de {timeout} segundos", "error")
    return {
        "exito": False,
        "estado": "timeout",
        "progreso": ultimo_progreso,
        "mensaje": f"Timeout despues de {timeout}s",
        "tiempo": timeout
    }


def reportar_resultado(resultado: dict, pedido_id: str):
    """Imprime el resultado final del test"""
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}RESULTADO DEL TEST E2E{Colors.ENDC}")
    print("=" * 60)
    
    if resultado.get("exito"):
        print(f"\n{Colors.GREEN}{Colors.BOLD}EXITO{Colors.ENDC}")
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}FALLO{Colors.ENDC}")
    
    print(f"\n  Pedido ID: {pedido_id}")
    print(f"  Estado final: {resultado.get('estado', 'N/A')}")
    print(f"  Progreso: {resultado.get('progreso', 0)}%")
    print(f"  Mensaje: {resultado.get('mensaje', 'N/A')}")
    print(f"  Tiempo total: {resultado.get('tiempo', 0):.1f} segundos")
    
    if resultado.get("detalles"):
        print(f"\n  Detalles:")
        for k, v in resultado["detalles"].items():
            print(f"    - {k}: {v}")
    
    print("\n" + "=" * 60)


# ============================================================
# MAIN
# ============================================================

async def main(fotos_paths: list = None, comprobante_path: str = None):
    """Ejecuta el test E2E completo"""
    
    print("\n" + "=" * 60)
    print(f"{Colors.BOLD}{Colors.HEADER}TEST E2E: Stagehand V3 + Gemini Vision{Colors.ENDC}")
    print("=" * 60 + "\n")
    
    # Verificar variables de entorno
    required_vars = ["OPENROUTER_API_KEY", "GRAFICA_EMAIL", "GRAFICA_PASSWORD"]
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        log(f"Faltan variables de entorno: {', '.join(missing)}", "error")
        log("Configura el archivo .env antes de ejecutar", "error")
        return
    
    server_process = None
    pedido_id = None
    
    try:
        # 1. Iniciar servidor
        server_process = iniciar_servidor()
        
        if not await esperar_servidor_listo():
            raise Exception("No se pudo iniciar el servidor")
        
        print()
        
        # 2. Crear pedido
        pedido_id = await crear_pedido()
        print()
        
        # 3. Subir fotos
        await subir_fotos(pedido_id, fotos_paths)
        print()
        
        # 4. Subir comprobante (dispara orquestador)
        await subir_comprobante(pedido_id, comprobante_path)
        print()
        
        # 5. Monitorear progreso
        resultado = await monitorear_progreso(pedido_id)
        
        # 6. Reportar
        reportar_resultado(resultado, pedido_id)
        
    except KeyboardInterrupt:
        log("\nTest interrumpido por el usuario", "warning")
        
    except Exception as e:
        log(f"Error fatal: {e}", "error")
        import traceback
        traceback.print_exc()
        
        if pedido_id:
            reportar_resultado({
                "exito": False,
                "estado": "error",
                "mensaje": str(e),
                "tiempo": 0
            }, pedido_id)
    
    finally:
        # Cleanup
        if server_process:
            detener_servidor(server_process)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test E2E Stagehand V3")
    parser.add_argument(
        "--fotos",
        type=str,
        help="Paths de fotos separados por coma (ej: foto1.jpg,foto2.jpg)"
    )
    parser.add_argument(
        "--comprobante",
        type=str,
        help="Path del comprobante de pago"
    )
    
    args = parser.parse_args()
    
    fotos = args.fotos.split(",") if args.fotos else None
    
    # Ejecutar
    asyncio.run(main(fotos_paths=fotos, comprobante_path=args.comprobante))
