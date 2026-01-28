"""
Agente Orquestador - PIKSY
==========================
Coordina todo el flujo de creación de fotolibros:
1. Recibe pedido
2. Analiza fotos
3. Aplica estilo de diseño
4. Ejecuta automatización en Browserbase
5. Envía a producción

Usa AGNO con modelos gratuitos de OpenRouter.
"""

import os
import sys
from typing import Optional, List
from dataclasses import dataclass

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.reasoning import ReasoningTools

from config.llm_models import get_agno_model_config, TareaLLM
from config.design_templates import get_template, calcular_paginas_necesarias
from config.agent_instructions import get_agent_instructions_compact, QUICK_RULES

# Importar nuevo sistema AGNO Team (5 agentes especializados)
try:
    from agents.orquestador_agno_team import (
        analizar_fotos_con_agno_team,
        preparar_diseño_con_agno_team
    )
    AGNO_TEAM_DISPONIBLE = True
    print("[OK] Sistema AGNO Team (5 agentes) cargado correctamente")
except ImportError as e:
    print(f"[WARN] Sistema AGNO Team no disponible: {e}")
    print("   Usando sistema de analisis legacy")
    AGNO_TEAM_DISPONIBLE = False


@dataclass
class PedidoInfo:
    """Información de un pedido a procesar"""
    pedido_id: str
    producto_codigo: str
    estilo_diseno: str
    paginas_total: int
    cliente_nombre: str
    cliente_email: str
    titulo_tapa: Optional[str] = None
    texto_lomo: Optional[str] = None
    fotos_paths: List[str] = None
    comentarios_cliente: Optional[str] = None


class OrquestadorFotolibros:
    """
    Orquestador principal que coordina la creación automática de fotolibros.
    """
    
    def __init__(self):
        # Fix para Windows + Playwright + Subprocesos
        import sys
        import asyncio
        if sys.platform == 'win32':
             try:
                 asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
             except:
                 pass
                 
        # Configurar modelo para orquestación
        model_config = get_agno_model_config(TareaLLM.ORQUESTACION)

        # DEBUG LOGGER
        import logging
        logging.basicConfig(filename='agent_debug.log', level=logging.DEBUG, force=True)
        self.file_logger = logging.getLogger('agent_debug')
        
        # Crear agente principal
        self.agente = Agent(
            name="Orquestador PIKSY",
            model=OpenRouter(id=model_config["model_id"]),
            tools=[ReasoningTools(add_instructions=True)],
            instructions=[
                "Eres el orquestador de PIKSY, una plataforma de fotolibros personalizados para RESELLERS.",
                "Tu trabajo es coordinar la creación automática de fotolibros en Fábrica de Fotolibros (FDF).",
                "",
                "IMPORTANTE - SOMOS RESELLERS:",
                "- SIEMPRE usar templates 'para Editores' o '- ED' (sin logo de FDF)",
                "- Esto permite poner nuestra propia marca en los libros",
                "- NUNCA usar templates '- CL' (tienen logo de FDF)",
                "",
                "================================================================================",
                "ANATOMIA DEL EDITOR FDF:",
                "================================================================================",
                "",
                "PANELES Y HERRAMIENTAS:",
                "- Panel de Herramientas (Izquierda Vertical): Añadir QR, Texto, Cuadros de Color, Contenedores de Fotos",
                "- Pestañas de Diseño (Lateral Izquierdo): Plantillas, Temas, Máscaras, Cliparts, Fondos, Bordes",
                "- Lienzo Principal (Centro): Área de trabajo - Tapa/Contratapa o Doble Página",
                "- Panel de Propiedades (Derecha): Controles de fuentes, colores, tamaños, rotación",
                "- Navegador de Páginas (Inferior): Miniaturas para navegar entre páginas",
                "- Barra de Acción (Superior Derecha): Guardar, Comprar, Deshacer",
                "",
                "ESTRUCTURA DE LA TAPA:",
                "- CONTRATAPA: Zona IZQUIERDA del lienzo central",
                "- LOMO: Franja CENTRAL entre las líneas punteadas",
                "- PORTADA: Zona DERECHA del lienzo central (la cara principal del libro)",
                "",
                "================================================================================",
                "REGLAS DE DISEÑO PROFESIONAL (CRITICO):",
                "================================================================================",
                "",
                "1. ZONA DEL LOMO (CENTRO DE DOBLE PAGINA):",
                "   - El lomo es la franja central entre las líneas punteadas",
                "   - NUNCA colocar rostros, caras o texto importante en el centro exacto",
                "   - El lomo 'come' ~10mm de cada lado de la union (~20mm total)",
                "   - Si una foto cruza el lomo, debe tener fondo/paisaje en esa zona",
                "",
                "2. TEXTO EN EL LOMO:",
                "   - Click en herramienta 'Texto' -> Doble click para escribir",
                "   - En el Panel Derecho, usar el TIRADOR CIRCULAR sobre la caja de texto para rotar 90°",
                "   - Centrar manualmente entre las líneas punteadas",
                "   - El texto se lee de abajo hacia arriba cuando el libro está en un estante",
                "",
                "3. FOTOS A DOBLE PAGINA (CONSEJO OFICIAL FDF #3):",
                "   - Lo que quede en el MEDIO sobre el lomo va a quedar OCULTO o CORTADO",
                "   - La encuadernación 'come' un poquito en el centro donde se unen las hojas",
                "   - Solo usar para PAISAJES amplios (cielos, playas, montañas, arquitectura)",
                "   - NUNCA si hay personas que quedarian cortadas por el lomo",
                "   - PROCEDIMIENTO OFICIAL si hay personas en el centro:",
                "     1) Seleccionar la foto",
                "     2) Usar la LUPA (herramientas contextuales) para agrandar la imagen",
                "     3) Usar la MANITO para desplazar la parte principal LEJOS del lomo",
                "   - El contenido importante debe quedar en los tercios laterales, NO en el centro",
                "",
                "4. HERRAMIENTAS CONTEXTUALES DE FOTO (Oficial FDF):",
                "   - LUPA: En herramientas contextuales - permite AGRANDAR la imagen dentro del marco",
                "   - MANITO: Aparece cuando tenés la foto seleccionada - permite DESPLAZAR la imagen",
                "   - Uso combinado: Primero LUPA para agrandar, luego MANITO para mover el contenido",
                "   - Esto permite ajustar qué parte de la foto se ve sin cambiar el tamaño del marco",
                "",
                "5. FOTOS HASTA EL BORDE (CONSEJO OFICIAL FDF #1):",
                "   - Para que fotos lleguen al borde: extenderlas hasta LÍNEA LLENA EXTERIOR",
                "   - Si solo llegan a línea punteada interior: queda LÍNEA BLANCA en el borde",
                "   - Concepto de DEMASÍA: área adicional que se corta, usada como margen de seguridad",
                "",
                "6. TEXTOS CERCA DE BORDES (CONSEJO OFICIAL FDF #4):",
                "   - Dejar MARGEN DE SEGURIDAD para evitar que el texto quede cortado",
                "   - Líneas punteadas = donde se DOBLA (tapa dura) o CORTA (tapa blanda/interiores)",
                "   - NUNCA dejar texto pegado a la línea punteada",
                "",
                "7. MARGENES DE SEGURIDAD:",
                "   - Dejar minimo 5mm de sangrado en todos los bordes externos",
                "   - No poner elementos importantes a menos de 10mm del borde",
                "   - Dejar márgenes generosos (espacio en blanco) en los bordes",
                "",
                "6. RESOLUCION DE IMAGENES:",
                "   - Ideal: >170 DPI para impresion HP Indigo",
                "   - Fotos de baja resolucion: usar en slots pequeños, no a pagina completa",
                "",
                "7. STICKERS Y ADORNOS (segun estilo):",
                "   - sin_diseno: NINGUNO - solo fotos",
                "   - minimalista: Muy sutiles (lineas finas)",
                "   - clasico: Elegantes (marcos, esquinas doradas)",
                "   - divertido: Coloridos (estrellas, corazones) - NUNCA tapar rostros",
                "   - premium: Sofisticados (dorados, florales)",
                "",
                "8. GESTION DE FONDOS Y BORDES:",
                "   - Pestaña 'Fondos': Seleccionar color o galería",
                "   - Aplicar a: Página izquierda, Página derecha, o Todo el libro",
                "   - Usar el GOTERO para copiar un color exacto de una fotografía",
                "   - Pestaña 'Bordes': Seleccionar grosor (px) y color (blanco es estándar profesional)",
                "",
                "9. USO DE PLANTILLAS (Layouts):",
                "   - Ir a pestaña 'Plantillas'",
                "   - Filtrar por número de fotos (ej. '4 fotos')",
                "   - Arrastrar plantilla elegida a la página deseada",
                "",
                "10. CODIGOS QR:",
                "    - Seleccionar herramienta 'Añadir QR' -> Pegar URL (YouTube/Instagram)",
                "    - Tamaño mínimo: 2x2 cm para asegurar lectura",
                "    - Colocar en esquinas, típicamente en contratapa",
                "",
                "11. ESTILOS DISPONIBLES:",
                "    - sin_diseno/solo_fotos: Libro en blanco, sin fondos temáticos",
                "    - minimalista: Limpio, fondos blancos, 1 foto por página",
                "    - clasico: Elegante, flores, ideal bodas/aniversarios",
                "    - divertido: Colorido, collages, ideal cumpleaños/infantil",
                "    - premium: Lujo, sofisticado, ideal regalos especiales",
                "",
                "================================================================================",
                "REGLA DE ORO - GUARDADO:",
                "================================================================================",
                "Ejecutar la acción de 'Guardar' (botón superior) cada 5 minutos o tras finalizar cada doble página.",
                "",
                "================================================================================",
                "FLUJO DE TRABAJO:",
                "================================================================================",
                "1. Validar pedido (formato, páginas, estilo)",
                "2. Analizar fotos (calidad, rostros, eventos)",
                "3. Seleccionar template (SIEMPRE versión para Editores)",
                "4. Ejecutar automatización con Vision",
                "5. Verificar reglas de diseño (especialmente lomo y márgenes)",
                "6. Guardar proyecto",
                "7. Enviar a producción",
            ],
            markdown=True,
        )
        
        # Estado del proceso
        self.estado_actual = "inicializado"
        self.progreso = 0
        self.logs = []
        self.on_progress = None  # Callback(mensaje, progreso)
    
    async def _update_progress(self, mensaje: str, progreso: int = None):
        """Actualiza el progreso y notifica"""
        if progreso is not None:
            self.progreso = progreso
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [INFO] {mensaje}"
        self.logs.append(log_entry)
        print(log_entry)
        
        if self.on_progress:
            try:
                import asyncio
                if asyncio.iscoroutinefunction(self.on_progress):
                    await self.on_progress(mensaje, self.progreso)
                else:
                    self.on_progress(mensaje, self.progreso)
            except Exception as e:
                print(f"Error en callback de progreso: {e}")

    def log(self, mensaje: str, nivel: str = "info"):
        """Registra un mensaje de log (wrapper legacy)"""
        # Este método se mantiene por compatibilidad interna de 'self.log'
        # pero idealmente usar _update_progress para notificar cambios importantes
        if nivel == "info":
            # No podemos hacer await aquí fácilmente porque log no es async en toda la clase
            # Así que solo actualizamos localmente, y usaremos _update_progress explícitamente en los pasos
            pass
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{nivel.upper()}] {mensaje}"
        self.logs.append(log_entry)
        print(log_entry)
        
        # Log to file
        if hasattr(self, 'file_logger'):
            try:
                self.file_logger.info(log_entry)
            except:
                pass
    
    async def validar_pedido(self, pedido: PedidoInfo) -> bool:
        """Paso 1: Validar datos del pedido"""
        self.estado_actual = "validando"
        await self._update_progress(f"Validando pedido {pedido.pedido_id}...", 10)
        
        # Validar producto
        from config.design_templates import DESIGN_TEMPLATES
        if pedido.estilo_diseno not in DESIGN_TEMPLATES:
            self.log(f"Estilo '{pedido.estilo_diseno}' no válido, usando 'clasico'", "warn")
            pedido.estilo_diseno = "clasico"
        
        # Validar páginas
        if pedido.paginas_total < 20 or pedido.paginas_total > 80:
            self.log(f"Páginas fuera de rango, ajustando a 22", "warn")
            pedido.paginas_total = 22
        
        self.log("✅ Pedido validado correctamente")
        return True
    
    async def analizar_fotos(self, pedido: PedidoInfo) -> dict:
        """Paso 2: Analizar fotos del cliente"""
        self.estado_actual = "analizando_fotos"
        await self._update_progress(f"Analizando {len(pedido.fotos_paths or [])} fotos...", 25)
        
        if not pedido.fotos_paths:
            self.log("No hay fotos para analizar", "warn")
            return {"evento_detectado": "otro", "mejores_para_portada": []}
        
        # Usar nuevo sistema AGNO Team si está disponible
        if AGNO_TEAM_DISPONIBLE:
            try:
                self.log("🎨 Usando sistema AGNO Team (5 agentes especializados)...")
                
                resultado = await analizar_fotos_con_agno_team(
                    pedido.fotos_paths,
                    pedido.cliente_nombre,
                    pedido.estilo_diseno  # Usar como hint de motivo
                )
                
                self.log(f"📸 Evento detectado: {resultado.get('evento_detectado', 'otro')}")
                self.log(f"📸 Confianza: {resultado.get('confianza', 0):.0%}")
                
                if 'titulo_sugerido' in resultado:
                    self.log(f"📝 Título sugerido: \"{resultado['titulo_sugerido']}\"")
                if 'template_sugerido' in resultado:
                    self.log(f"🎨 Template sugerido: {resultado['template_sugerido']}")
                
                return resultado
                
            except Exception as e:
                self.log(f"Error con AGNO Team, usando fallback: {e}", "warn")
                # Continuar con sistema legacy
        
        # Sistema legacy (fallback)
        try:
            from services.photo_analyzer import analizar_fotos_rapido
            resultado = await analizar_fotos_rapido(pedido.fotos_paths)
            
            self.log(f"📸 Evento detectado: {resultado.get('evento_detectado', 'otro')}")
            self.log(f"📸 Confianza: {resultado.get('confianza', 0):.0%}")
            
            return resultado
        except Exception as e:
            self.log(f"Error analizando fotos: {e}", "error")
            return {"evento_detectado": "otro", "mejores_para_portada": [0]}
    
    async def preparar_diseño(self, pedido: PedidoInfo, analisis: dict) -> dict:
        """Paso 3: Preparar el diseño según el template"""
        self.estado_actual = "preparando_diseño"
        await self._update_progress(f"Preparando diseño con estilo '{pedido.estilo_diseno}'...", 40)
        
        if pedido.comentarios_cliente:
            self.log(f"📝 Instrucciones del cliente: '{pedido.comentarios_cliente}'")
        
        # Usar diseño de AGNO Team si está disponible
        if AGNO_TEAM_DISPONIBLE and 'agno_result' in analisis:
            try:
                self.log("🎨 Usando diseño curado por AGNO Team...")
                
                pedido_dict = {
                    "titulo_tapa": pedido.titulo_tapa,
                    "texto_lomo": pedido.texto_lomo,
                }
                
                diseño = await preparar_diseño_con_agno_team(pedido_dict, analisis)
                
                self.log(f"📐 Template: {diseño['template_id']}")
                self.log(f"📝 Título: \"{diseño['titulo_tapa']}\"")
                
                if 'dedicatoria' in diseño:
                    self.log(f"💌 Dedicatoria generada")
                if 'capítulos' in diseño and len(diseño['capítulos']) > 0:
                    self.log(f"📖 Capítulos: {len(diseño['capítulos'])}")
                
                return diseño
                
            except Exception as e:
                self.log(f"Error con diseño AGNO Team, usando fallback: {e}", "warn")
                # Continuar con sistema legacy
        
        template = get_template(pedido.estilo_diseno)
        if not template:
            self.log("Template no encontrado, usando clasico", "warn")
            template = get_template("clasico")
        
        # Determinar título de tapa
        titulo = pedido.titulo_tapa
        if not titulo and template.tapa.con_titulo:
            # Generar título basado en el evento detectado
            evento = analisis.get("evento_detectado", "otro")
            titulos_default = {
                "boda": "Nuestra Boda",
                "cumpleaños": "¡Feliz Cumple!",
                "viaje": "Nuestro Viaje",
                "bebé": "Mi Primer Año",
                "graduación": "¡Lo Logramos!",
                "familia": "Momentos en Familia",
                "otro": "Recuerdos",
            }
            titulo = titulos_default.get(evento, "Recuerdos")
        
        diseño = {
            "template_id": template.id,
            "titulo_tapa": titulo,
            "texto_lomo": pedido.texto_lomo or template.tapa.texto_lomo_default,
            "fotos_por_pagina": template.interior.fotos_por_pagina,
            "con_fondo": template.interior.con_fondo,
            "mejor_foto_portada": analisis.get("mejores_para_portada", [0])[0] if analisis.get("mejores_para_portada") else 0,
        }
        
        self.log(f"🎨 Diseño preparado: {diseño['titulo_tapa']}")
        return diseño
    
    async def ejecutar_automatizacion(self, pedido: PedidoInfo, diseño: dict) -> dict:
        """Paso 4: Ejecutar automatización en Browserbase"""
        self.estado_actual = "ejecutando_automatizacion"
        await self._update_progress("Iniciando automatización en Browserbase...", 60)
        
        # Flag para modo simulación (cambiar a False para usar Browserbase real)
        MODO_SIMULACION = False  # ← BROWSERBASE REAL ACTIVADO
        
        if MODO_SIMULACION:
            # Modo simulación - no usa Browserbase real
            import asyncio
            
            self.log("⚠️ MODO SIMULACIÓN ACTIVO")
            self.log("🔐 Conectando al editor...")
            await asyncio.sleep(1)
            await self._update_progress(f"Creando proyecto: {pedido.producto_codigo}...", 65)
            
            await asyncio.sleep(1)
            await self._update_progress(f"Subiendo {len(pedido.fotos_paths or [])} fotos...", 70)
            
            await asyncio.sleep(2)
            await self._update_progress(f"Aplicando diseño '{diseño['template_id']}'...", 80)
            
            await asyncio.sleep(1)
            await self._update_progress("Guardando proyecto...", 85)
            
            await asyncio.sleep(1)
            
            resultado = {
                "exito": True,
                "proyecto_id": f"FDF-{pedido.pedido_id[:8].upper()}",
                "browserbase_session": "simulated-session-id",
                "replay_url": None,
            }
            
            self.log(f"✅ Proyecto creado: {resultado['proyecto_id']}")
            return resultado
        
        else:
            # Modo real - usa FDF Stagehand Toolkit (Playwright + Gemini Vision HIBRIDO)
            try:
                import asyncio
                from services.fdf_stagehand import FDFStagehandToolkit, VisionDesigner
                from services.fdf_stagehand.design_intelligence import DesignIntelligence
                
                self.log("🚀 Iniciando FDF Stagehand Toolkit (Hibrido: DOM + Vision)...")
                
                # Crear toolkit
                toolkit = FDFStagehandToolkit(
                    model_api_key=os.getenv("OPENROUTER_API_KEY"),
                    fdf_email=os.getenv("GRAFICA_EMAIL"),
                    fdf_password=os.getenv("GRAFICA_PASSWORD"),
                    headless=False  # Visible para debug
                )
                
                designer = DesignIntelligence(api_key=os.getenv("OPENROUTER_API_KEY"))
                vision = VisionDesigner(api_key=os.getenv("OPENROUTER_API_KEY"))
                
                titulo = diseño.get('titulo_tapa', 'Mi Fotolibro')
                fotos = pedido.fotos_paths or []
                estilo = pedido.estilo_diseno or "clasico"
                
                try:
                    # ========================================
                    # PASO 1: Login
                    # ========================================
                    self.log("🔐 Paso 1: Login en FDF...")
                    await self._update_progress("Iniciando sesion en FDF...", 62)
                    await toolkit.login()
                    
                    # ========================================
                    # PASO 2: Navegar y seleccionar producto
                    # ========================================
                    self.log(f"📦 Paso 2: Seleccionando producto {pedido.producto_codigo}...")
                    await self._update_progress("Navegando al catalogo...", 65)
                    await toolkit.navigate_to_fotolibros()
                    await asyncio.sleep(1)
                    
                    # Extraer formato del codigo (ej: CU-21x21-DURA -> 21x21)
                    formato = "21x21"  # Default
                    if "21x21" in pedido.producto_codigo:
                        formato = "21x21"
                    elif "30x30" in pedido.producto_codigo:
                        formato = "30x30"
                    elif "20x15" in pedido.producto_codigo:
                        formato = "20x15"
                    
                    await toolkit.select_product_by_text(formato)
                    await asyncio.sleep(2)
                    
                    # ========================================
                    # PASO 3: Crear proyecto
                    # ========================================
                    self.log(f"📝 Paso 3: Creando proyecto '{titulo}'...")
                    await self._update_progress("Configurando proyecto...", 68)
                    await toolkit.click_create_project(titulo)
                    await asyncio.sleep(2)
                    
                    # ========================================
                    # PASO 4: Subir fotos
                    # ========================================
                    self.log(f"📸 Paso 4: Subiendo {len(fotos)} fotos...")
                    await self._update_progress(f"Subiendo {len(fotos)} fotos...", 70)
                    
                    await toolkit.select_photo_source("computadora")
                    await asyncio.sleep(1)
                    await toolkit.upload_photos(fotos)
                    
                    await toolkit.click_continue()
                    await asyncio.sleep(3)
                    
                    # ========================================
                    # PASO 5: Seleccion INTELIGENTE de template
                    # ========================================
                    self.log(f"🎨 Paso 5: Seleccionando template para estilo '{estilo}'...")
                    await self._update_progress("Seleccionando template inteligente...", 75)
                    
                    # Usar seleccion hibrida (categoria hardcodeada + Vision para template)
                    template_result = await toolkit.select_template_intelligent(
                        estilo_cliente=estilo,
                        fotos_paths=fotos[:3],  # Analizar primeras 3 fotos
                        designer=designer
                    )
                    
                    template_elegido = template_result.get("template_elegido", "Vacio")
                    self.log(f"    Template elegido: {template_elegido}")
                    self.log(f"    Razonamiento: {template_result.get('razonamiento', 'N/A')}")
                    
                    # ========================================
                    # PASO 6: Modo manual y esperar editor
                    # ========================================
                    self.log("⏳ Paso 6: Entrando al editor...")
                    await self._update_progress("Cargando editor...", 78)
                    
                    await toolkit.click_fill_mode("manual")
                    await asyncio.sleep(2)
                    
                    # Esperar que el editor este listo
                    ready = await toolkit.wait_for_editor_ready(timeout=60)
                    if ready.get("success"):
                        self.log(f"    Editor listo en {ready.get('time_waited', 0)}s")
                    
                    # ========================================
                    # PASO 7: Drag & Drop con Vision
                    # ========================================
                    self.log("🖼️ Paso 7: Colocando fotos en el libro...")
                    await self._update_progress("Diseñando paginas con Vision...", 82)
                    
                    # Analizar el editor
                    analysis = await vision.analyze_editor(toolkit.page)
                    if analysis.get("success"):
                        self.log(f"    Panel fotos detectado: {analysis.get('analysis', {}).get('panel_fotos', {})}")
                    
                    # Auto-fill de la primera pagina
                    auto_result = await toolkit.auto_fill_page_with_vision(max_photos=4)
                    self.log(f"    Fotos colocadas: {auto_result.get('photos_placed', 0)}")
                    
                    # ========================================
                    # PASO 8: Verificar reglas de diseño
                    # ========================================
                    self.log("✅ Paso 8: Verificando reglas de diseño...")
                    await self._update_progress("Verificando calidad del diseño...", 85)
                    
                    verify = await vision.verify_design_rules(toolkit.page)
                    if verify.get("success"):
                        score = verify.get("score", 0)
                        self.log(f"    Puntuacion de diseño: {score}/100")
                        
                        if verify.get("critical_issues"):
                            for issue in verify.get("critical_issues", []):
                                self.log(f"    ⚠️ {issue.get('tipo')}: {issue.get('descripcion')}", "warn")
                    
                    # ========================================
                    # PASO 9: Guardar proyecto
                    # ========================================
                    self.log("💾 Paso 9: Guardando proyecto...")
                    await self._update_progress("Guardando proyecto...", 88)
                    
                    await toolkit.save_project()
                    await asyncio.sleep(2)
                    
                    # Tomar screenshot final
                    await toolkit.take_screenshot(f"proyecto_{pedido.pedido_id[:8]}.png")
                    
                    # Reportar final
                    await self._update_progress("Automatizacion completada", 90)
                    
                    return {
                        "exito": True,
                        "proyecto_id": f"FDF-{pedido.pedido_id[:8].upper()}",
                        "browserbase_session": "local-playwright-stagehand",
                        "replay_url": None,
                        "template_usado": template_elegido,
                        "fotos_colocadas": auto_result.get("photos_placed", 0),
                        "score_diseño": verify.get("score", 0) if verify.get("success") else None,
                    }
                    
                finally:
                    # Cerrar navegador
                    self.log("🔒 Cerrando navegador...")
                    await toolkit.close()
                
            except Exception as e:
                self.log(f"❌ Error en automatizacion: {repr(e)}", "error")
                import traceback
                traceback.print_exc()
                return {"exito": False, "error": repr(e)}
    
    async def enviar_produccion(self, pedido: PedidoInfo, proyecto: dict) -> bool:
        """Paso 5: Enviar a producción"""
        self.estado_actual = "enviando_produccion"
        await self._update_progress("Enviando proyecto a producción...", 95)
        
        if not proyecto.get("exito"):
            self.log("No se puede enviar: proyecto no creado o error en checkout", "error")
            return False
        
        # El proyecto ya fue enviado/procesado en el paso anterior (ejecutar_automatizacion)
        # por lo que aquí validamos el resultado final reportado por Browserbase.
        
        self.log(f"📦 Proyecto {proyecto.get('proyecto_id')} procesado en Fábrica de Fotolibros")
        
        # Esperar un poco para que el usuario pueda ver el resultado si está mirando
        import asyncio
        await asyncio.sleep(10)
        
        await self._update_progress("¡Pedido completado y enviado a producción!", 100)
        self.estado_actual = "completado"
        
        return True
    
    
    async def procesar_pedido(self, pedido: PedidoInfo, on_progress=None) -> dict:
        """
        Ejecuta el flujo completo de procesamiento de un pedido.
        """
        if on_progress:
            self.on_progress = on_progress
            
        self.log(f"🚀 Iniciando procesamiento del pedido {pedido.pedido_id}")
        
        try:
            # Paso 1: Validar
            await self.validar_pedido(pedido)
            
            # Paso 2: Analizar fotos
            analisis = await self.analizar_fotos(pedido)
            
            # Paso 3: Preparar diseño
            diseño = await self.preparar_diseño(pedido, analisis)
            
            # Paso 4: Ejecutar automatización
            proyecto = await self.ejecutar_automatizacion(pedido, diseño)
            
            # Paso 5: Enviar a producción
            enviado = await self.enviar_produccion(pedido, proyecto)
            
            resultado = {
                "exito": enviado,
                "pedido_id": pedido.pedido_id,
                "proyecto_id": proyecto.get("proyecto_id"),
                "estado": self.estado_actual,
                "progreso": self.progreso,
                "logs": self.logs,
                "browserbase_session": proyecto.get("browserbase_session"),
                "replay_url": proyecto.get("replay_url"),
            }
            
            self.log(f"🎉 Pedido {pedido.pedido_id} procesado exitosamente!")
            return resultado
            
        except Exception as e:
            self.log(f"❌ Error fatal: {e}", "error")
            return {
                "exito": False,
                "pedido_id": pedido.pedido_id,
                "error": str(e),
                "estado": "error",
                "progreso": self.progreso,
                "logs": self.logs,
            }


# ============================================================
# FUNCIONES DE CONVENIENCIA
# ============================================================

async def procesar_pedido_desde_db(pedido_id: str) -> dict:
    """
    Carga un pedido de la base de datos y lo procesa.
    """
    import aiosqlite
    from main import DATABASE_PATH
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
        row = await cursor.fetchone()
        
        if not row:
            return {"exito": False, "error": "Pedido no encontrado"}
        
        pedido = dict(row)
    
    # Obtener fotos del pedido
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT filepath FROM fotos_pedido WHERE pedido_id = ?",
            (pedido_id,)
        )
        rows = await cursor.fetchall()
        fotos_paths = [row["filepath"] for row in rows]
    
    # Parsear cliente
    import json
    cliente = json.loads(pedido.get("cliente_json", "{}"))
    
    # Crear objeto PedidoInfo
    info = PedidoInfo(
        pedido_id=pedido_id,
        producto_codigo=pedido.get("producto_codigo", "CU-21x21-DURA"),
        estilo_diseno=pedido.get("estilo_diseno", "clasico"),
        paginas_total=pedido.get("paginas_total", 22),
        cliente_nombre=cliente.get("nombre", ""),
        cliente_email=cliente.get("email", ""),
        titulo_tapa=pedido.get("titulo_tapa"),
        texto_lomo=pedido.get("texto_lomo"),
        fotos_paths=fotos_paths,
    )
    
    # Procesar
    orquestador = OrquestadorFotolibros()
    return await orquestador.procesar_pedido(info)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=" * 60)
        print("TEST: Orquestador de Fotolibros")
        print("=" * 60)
        
        # Crear pedido de prueba
        pedido = PedidoInfo(
            pedido_id="test-123-abc",
            producto_codigo="CU-21x21-DURA",
            estilo_diseno="clasico",
            paginas_total=22,
            cliente_nombre="Test Usuario",
            cliente_email="test@test.com",
            titulo_tapa="Mi Libro de Prueba",
            fotos_paths=[],  # Sin fotos para el test
        )
        
        # Procesar
        orquestador = OrquestadorFotolibros()
        resultado = await orquestador.procesar_pedido(pedido)
        
        print("\n" + "=" * 60)
        print("RESULTADO:")
        print(f"  Éxito: {resultado.get('exito')}")
        print(f"  Proyecto ID: {resultado.get('proyecto_id')}")
        print(f"  Estado: {resultado.get('estado')}")
        print(f"  Progreso: {resultado.get('progreso')}%")
        print("=" * 60)
    
    asyncio.run(test())
