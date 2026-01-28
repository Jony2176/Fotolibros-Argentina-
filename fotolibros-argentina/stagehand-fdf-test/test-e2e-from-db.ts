/**
 * Test E2E con Stagehand v3 - Fotos desde BD
 * ===========================================
 * 
 * Usa Stagehand v3 con act() para automatizacion del browser.
 * 
 * Arquitectura:
 * - SQLite: Lee fotos del pedido desde la BD
 * - Stagehand act(): Acciones con lenguaje natural
 * - Stagehand extract(): Analisis visual del estado
 * - Playwright: Upload de archivos (operacion de bajo nivel)
 * 
 * Uso:
 *   npx tsx test-e2e-from-db.ts              # Usa el ultimo pedido con fotos
 *   npx tsx test-e2e-from-db.ts <pedido_id>  # Usa un pedido especifico
 */

import { Stagehand } from "@browserbasehq/stagehand";
import * as fs from 'fs';
import * as path from 'path';
import {
  checkDatabase,
  getPedido,
  getPhotosFromDB,
  getLastPedidoWithPhotos,
  Pedido
} from './db-reader';

// =====================================================
// CONFIGURACION
// =====================================================

// LLM Provider: "gemini" | "ollama" | "openrouter"
const LLM_PROVIDER = process.env.LLM_PROVIDER || "openrouter";

const LLM_CONFIGS: Record<string, { modelName: string; apiKey?: string; baseURL?: string }> = {
  gemini: {
    modelName: "google/gemini-2.0-flash",
    apiKey: process.env.GEMINI_API_KEY,
  },
  ollama: {
    modelName: "ollama/llava",
    baseURL: "http://localhost:11434/v1",
  },
  openrouter: {
    modelName: "openai/gpt-4o-mini",
    apiKey: process.env.OPENROUTER_API_KEY || "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",
    baseURL: "https://openrouter.ai/api/v1"
  }
};

const CONFIG = {
  fdf: {
    email: process.env.FDF_EMAIL || "revelacionesocultas72@gmail.com",
    password: process.env.FDF_PASSWORD || "Jony.2176",
    loginUrl: "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
  },
  llm: LLM_CONFIGS[LLM_PROVIDER] || LLM_CONFIGS.openrouter,
  browser: {
    headless: false,
    viewport: { width: 1400, height: 900 },
    chromePath: "C:/Program Files/Google/Chrome/Application/chrome.exe"
  },
  screenshotDir: path.resolve(__dirname, 'screenshots')
};

// =====================================================
// UTILIDADES
// =====================================================

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function log(step: string, message: string, data?: any) {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`[${timestamp}] [${step}] ${message}`);
  if (data) {
    console.log(`    ${JSON.stringify(data, null, 2).replace(/\n/g, "\n    ")}`);
  }
}

async function takeScreenshot(page: any, name: string) {
  if (!fs.existsSync(CONFIG.screenshotDir)) {
    fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
  }
  const filepath = path.join(CONFIG.screenshotDir, `${name}.png`);
  await page.screenshot({ path: filepath, fullPage: false });
  log("SCREENSHOT", `Guardado: ${name}.png`);
}

// =====================================================
// TEST PRINCIPAL
// =====================================================

async function main() {
  console.log("=".repeat(70));
  console.log("  TEST E2E - Stagehand v3 + Fotos desde BD");
  console.log("=".repeat(70));
  
  // Verificar BD
  const dbCheck = checkDatabase();
  if (!dbCheck.ok) {
    console.error(`\n[ERROR] ${dbCheck.message}`);
    process.exit(1);
  }
  console.log(`\n[OK] ${dbCheck.message}`);
  
  // Obtener pedido
  let pedido: Pedido;
  let photoPaths: string[];
  
  const pedidoIdArg = process.argv[2];
  
  if (pedidoIdArg) {
    const p = getPedido(pedidoIdArg);
    if (!p) {
      console.error(`\n[ERROR] Pedido no encontrado: ${pedidoIdArg}`);
      process.exit(1);
    }
    pedido = p;
    photoPaths = getPhotosFromDB(pedidoIdArg);
  } else {
    const last = getLastPedidoWithPhotos();
    if (!last) {
      console.error("\n[ERROR] No hay pedidos con fotos. Ejecuta: npx tsx test-setup.ts");
      process.exit(1);
    }
    pedido = last.pedido;
    photoPaths = last.photos;
  }
  
  console.log(`\n[PEDIDO] ID: ${pedido.id}`);
  console.log(`  Producto: ${pedido.producto_codigo}`);
  console.log(`  Estilo: ${pedido.estilo_diseno}`);
  console.log(`  Titulo: ${pedido.titulo_tapa || 'Sin titulo'}`);
  console.log(`  Fotos: ${photoPaths.length}`);
  
  if (photoPaths.length === 0) {
    console.error("\n[ERROR] El pedido no tiene fotos");
    process.exit(1);
  }
  
  console.log("\n" + "-".repeat(70));
  log("INIT", `Iniciando Stagehand LOCAL con ${LLM_PROVIDER}...`);
  log("INIT", `Modelo: ${CONFIG.llm.modelName}`);
  
  // Construir config del modelo
  const modelConfig: any = { modelName: CONFIG.llm.modelName };
  if (CONFIG.llm.apiKey) modelConfig.apiKey = CONFIG.llm.apiKey;
  if (CONFIG.llm.baseURL) modelConfig.baseURL = CONFIG.llm.baseURL;
  
  const stagehand = new Stagehand({
    env: "LOCAL",
    model: modelConfig,
    localBrowserLaunchOptions: {
      headless: CONFIG.browser.headless,
      viewport: CONFIG.browser.viewport,
      executablePath: CONFIG.browser.chromePath,
    },
  });
  
  const projectTitle = pedido.titulo_tapa || `E2E_${Date.now()}`;
  
  try {
    await stagehand.init();
    log("INIT", "Stagehand inicializado");
    
    const page = stagehand.context.pages()[0];
    if (!page) throw new Error("No page available");
    
    // =====================================================
    // FASE 1: Login
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 1: Login");
    console.log("=".repeat(70));
    
    log("NAV", "Navegando a FDF...");
    await page.goto(CONFIG.fdf.loginUrl);
    await sleep(4000);
    await takeScreenshot(page, "01_login_page");
    
    log("LOGIN", "Llenando formulario con Playwright directo...");
    // Usar Playwright directo para login (más confiable que act())
    await page.locator('#email_log').fill(CONFIG.fdf.email);
    await sleep(500);
    await page.locator('#clave_log').fill(CONFIG.fdf.password);
    await sleep(500);
    await page.locator('#bt_log').click();
    
    log("LOGIN", "Esperando carga...");
    await sleep(6000);
    await takeScreenshot(page, "02_logged_in");
    
    // =====================================================
    // FASE 2: Navegacion
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 2: Navegacion");
    console.log("=".repeat(70));
    
    log("NAV", "Buscando version profesional...");
    try {
      await stagehand.act("click on 'Para Profesionales' or 'sin logo de FDF'");
      await sleep(2000);
    } catch {
      log("NAV", "Opcion profesional no encontrada, continuando...");
    }
    
    log("NAV", "Clickeando Fotolibros...");
    await stagehand.act("click on 'Fotolibros' category");
    await sleep(2000);
    
    log("NAV", "Seleccionando producto 21x21...");
    await stagehand.act("click on the product with '21x21' or '21 x 21'");
    await sleep(2000);
    await takeScreenshot(page, "03_product_selected");
    
    // =====================================================
    // FASE 3: Crear Proyecto
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 3: Crear Proyecto");
    console.log("=".repeat(70));
    
    log("PROJECT", `Escribiendo titulo: ${projectTitle}`);
    await sleep(1500);
    await stagehand.act(`type '${projectTitle}' in the title input field`);
    await sleep(500);
    
    log("PROJECT", "Clickeando Crear Proyecto...");
    await stagehand.act("click the 'Crear Proyecto' button");
    await sleep(4000);
    await takeScreenshot(page, "04_project_created");
    
    // =====================================================
    // FASE 4: Subir Fotos
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 4: Subir Fotos");
    console.log("=".repeat(70));
    
    log("UPLOAD", "Seleccionando fuente de fotos...");
    await sleep(2000);
    
    try {
      await stagehand.act("click on 'Desde computador' option");
    } catch {
      await stagehand.act("click on the computer upload option");
    }
    await sleep(2000);
    
    log("UPLOAD", `Subiendo ${photoPaths.length} fotos...`);
    const fileInput = page.locator("input[type='file']").first();
    if (await fileInput.count() > 0) {
      await fileInput.setInputFiles(photoPaths);
      const waitTime = Math.min(5000 + photoPaths.length * 2500, 30000);
      log("UPLOAD", `Esperando ${waitTime / 1000}s...`);
      await sleep(waitTime);
    }
    await takeScreenshot(page, "05_photos_uploaded");
    
    log("NAV", "Clickeando Continuar...");
    await stagehand.act("click the 'Continuar' button");
    await sleep(3000);
    
    // =====================================================
    // FASE 5: Seleccionar Template CON DISEÑO
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 5: Seleccionar Template");
    console.log("=".repeat(70));
    
    await takeScreenshot(page, "06_templates");
    
    log("TEMPLATE", `Buscando template para estilo: ${pedido.estilo_diseno}`);
    
    // Mapeo de estilos a tipos de templates
    const templateGuide: Record<string, string> = {
      "minimalista": "a clean and simple template with minimal decorations, NOT 'Vacio'",
      "clasico": "an elegant or classic design template",
      "moderno": "a modern design template",
      "infantil": "a fun or child-friendly template",
      "romantico": "a romantic or wedding-style template",
      "viajes": "a travel or adventure themed template"
    };
    
    const templateDescription = templateGuide[pedido.estilo_diseno] || "a designed template with visual elements, NOT blank or 'Vacio'";
    
    log("TEMPLATE", `Buscando: ${templateDescription}`);
    
    // Usar extract para analizar templates disponibles
    const templateAnalysis = await stagehand.extract({
      instruction: `Look at the template selection screen. 
        Find templates that have designs, graphics, or decorative elements.
        Exclude 'Vacio' or blank templates.
        List 3-5 template names that match "${pedido.estilo_diseno}" style.`,
      schema: {
        type: "object",
        properties: {
          availableTemplates: { 
            type: "array", 
            items: { type: "string" },
            description: "Names of designed templates (not Vacio)" 
          },
          recommended: { 
            type: "string", 
            description: "Best template for the style" 
          }
        }
      }
    });
    
    log("TEMPLATE", "Templates encontrados:", templateAnalysis);
    
    const templateToSelect = templateAnalysis.recommended || "the first template with designs";
    
    log("TEMPLATE", `Seleccionando: ${templateToSelect}`);
    await stagehand.act(`click on the template named "${templateToSelect}" or a similar designed template. Do NOT click on 'Vacio' or blank templates`);
    await sleep(2000);
    await takeScreenshot(page, "07_template_selected");
    
    // =====================================================
    // FASE 6: Seleccionar RELLENO FOTOS SMART
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 6: Seleccionar Relleno Fotos Smart");
    console.log("=".repeat(70));
    
    log("FILL", "Scrolleando para ver opciones de relleno...");
    await stagehand.act("scroll down to the bottom to see the fill mode buttons");
    await sleep(1500);
    await takeScreenshot(page, "08_fill_options");
    
    log("FILL", "Clickeando 'Relleno fotos smart'...");
    // Hay 3 opciones: Manual, Rápido, Smart
    // Smart es la mejor porque coloca fotos de forma inteligente
    await stagehand.act("click on the 'Relleno fotos smart' button (the third option for automatic smart photo placement)");
    
    await sleep(3000);
    await takeScreenshot(page, "09_after_smart_click");
    
    // Manejar modal de configuración que puede aparecer
    log("FILL", "Buscando modal de configuración...");
    try {
      // El modal tiene opciones como "Caras, Colores y Dimensiones", "Colores y Dimensiones", "Dimensiones"
      // Seleccionar la primera opción (más completa)
      await stagehand.act("click on 'Caras, Colores y Dimensiones' or the first option in the modal");
      await sleep(2000);
      log("FILL", "Modal de configuración manejado");
    } catch {
      log("FILL", "No se encontró modal (o ya se procesó)");
    }
    
    log("FILL", "Esperando procesamiento automático de Smart Fill...");
    await sleep(15000);  // Smart fill necesita tiempo para colocar fotos
    await takeScreenshot(page, "10_smart_fill_processing");
    
    // =====================================================
    // FASE 7: Verificar Editor
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 7: Verificar Editor");
    console.log("=".repeat(70));
    
    await sleep(5000);
    await takeScreenshot(page, "11_editor_loaded");
    
    log("VERIFY", "Analizando estado...");
    const analysis = await stagehand.extract({
      instruction: "Analyze the editor: count photos on canvas, empty slots, and rate quality 0-100",
      schema: {
        type: "object",
        properties: {
          photosOnCanvas: { type: "number" },
          emptySlots: { type: "number" },
          qualityScore: { type: "number" },
          isInEditor: { type: "boolean" }
        }
      }
    });
    
    log("VERIFY", "Estado:", analysis);
    
    // =====================================================
    // RESULTADO FINAL
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  RESULTADO");
    console.log("=".repeat(70));
    
    const success = (analysis.photosOnCanvas || 0) > 0;
    
    console.log(`
  Pedido:          ${pedido.id.slice(0, 8)}...
  Producto:        ${pedido.producto_codigo}
  
  Fotos subidas:   ${photoPaths.length}
  Fotos en canvas: ${analysis.photosOnCanvas || 0}
  Puntuacion:      ${analysis.qualityScore || 0}/100
  
  LLM:             ${LLM_PROVIDER} (${CONFIG.llm.modelName})
  Costo:           ${LLM_PROVIDER === 'ollama' ? 'GRATIS' : 'Pago por uso'}
  
  Estado:          ${success ? 'EXITO' : 'REVISAR'}
  Screenshots:     ${CONFIG.screenshotDir}
`);
    
    log("INFO", "Browser abierto 60s para inspeccion. Ctrl+C para cerrar.");
    await sleep(60000);
    
  } catch (error) {
    console.error("\n[ERROR]", error);
    try {
      const p = stagehand.context.pages()[0];
      if (p) await takeScreenshot(p, "error_state");
    } catch {}
    await sleep(30000);
  } finally {
    await stagehand.close();
    console.log("\nBrowser cerrado.");
  }
}

main().catch(console.error);
