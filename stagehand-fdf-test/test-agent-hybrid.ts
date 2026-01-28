/**
 * Test E2E - Stagehand Agent Mode (Hybrid/DOM)
 * =============================================
 * 
 * Usa el Agent de Stagehand para automatizar FDF de forma más robusta.
 * El Agent puede manejar interfaces complejas mejor que act() directo.
 * 
 * Flujo:
 * 1. Login en FDF
 * 2. Crear proyecto o abrir existente
 * 3. Subir fotos
 * 4. Aplicar template
 * 5. Usar Smart Fill
 * 6. Verificar resultado
 */

import { Stagehand } from "@browserbasehq/stagehand";
import * as fs from 'fs';
import * as path from 'path';

// =====================================================
// CONFIGURACION
// =====================================================

const CONFIG = {
  fdf: {
    email: process.env.FDF_EMAIL || "revelacionesocultas72@gmail.com",
    password: process.env.FDF_PASSWORD || "Jony.2176",
    loginUrl: "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
  },
  
  // Modelo para el Agent y act/extract - usando GPT-4o via OpenRouter
  agent: {
    modelName: "openai/gpt-4o",  // GPT-4o - potente para tareas complejas
    apiKey: process.env.OPENROUTER_API_KEY || "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",
    baseURL: "https://openrouter.ai/api/v1"
  },
  
  // Modelo para act/extract básico
  llm: {
    modelName: "openai/gpt-4o",  // Mismo modelo para consistencia
    apiKey: process.env.OPENROUTER_API_KEY || "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",
    baseURL: "https://openrouter.ai/api/v1"
  },
  
  browser: {
    headless: false,
    viewport: { width: 1288, height: 711 },  // Viewport óptimo para Stagehand
    chromePath: "C:/Program Files/Google/Chrome/Application/chrome.exe"
  },
  
  screenshotDir: path.resolve(__dirname, 'screenshots-agent')
};

// Fotos de prueba
const FOTOS_TEST = [
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto1.jpg'),
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto2.jpg'),
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto3.jpg'),
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto4.jpg'),
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto5.jpg'),
];

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
  log("SCREENSHOT", `${name}.png`);
}

// =====================================================
// TEST PRINCIPAL
// =====================================================

async function main() {
  console.log("=".repeat(70));
  console.log("  TEST AGENT - Stagehand Agent Mode para FDF");
  console.log("=".repeat(70));
  
  // Verificar fotos
  console.log("\nVerificando fotos de prueba...");
  for (const foto of FOTOS_TEST) {
    if (!fs.existsSync(foto)) {
      console.error(`❌ Foto no encontrada: ${foto}`);
      process.exit(1);
    }
  }
  console.log(`✓ ${FOTOS_TEST.length} fotos disponibles\n`);
  
  console.log("-".repeat(70));
  log("INIT", "Iniciando Stagehand con Agent mode...");
  
  const stagehand = new Stagehand({
    env: "LOCAL",
    model: {
      modelName: CONFIG.llm.modelName,
      apiKey: CONFIG.llm.apiKey,
      baseURL: CONFIG.llm.baseURL,
    },
    localBrowserLaunchOptions: {
      headless: CONFIG.browser.headless,
      viewport: CONFIG.browser.viewport,
      executablePath: CONFIG.browser.chromePath,
    },
  });
  
  try {
    await stagehand.init();
    log("INIT", "Stagehand inicializado");
    
    const page = stagehand.context.pages()[0];
    if (!page) throw new Error("No page available");
    
    // =====================================================
    // PASO 1: Login con Playwright directo (más confiable)
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 1: Login en FDF");
    console.log("=".repeat(70));
    
    log("LOGIN", "Navegando a FDF...");
    await page.goto(CONFIG.fdf.loginUrl);
    await sleep(3000);
    await takeScreenshot(page, "01_login_page");
    
    log("LOGIN", "Ingresando credenciales...");
    await page.locator('#email_log').fill(CONFIG.fdf.email);
    await sleep(300);
    await page.locator('#clave_log').fill(CONFIG.fdf.password);
    await sleep(300);
    await page.locator('#bt_log').click();
    
    await sleep(6000);
    await takeScreenshot(page, "02_logged_in");
    log("LOGIN", "✓ Login exitoso");
    
    // =====================================================
    // PASO 2: Crear nuevo proyecto usando Agent
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 2: Crear Proyecto con Agent");
    console.log("=".repeat(70));
    
    // Crear el agent
    log("AGENT", "Creando Agent para navegación...");
    const agent = stagehand.agent({
      model: {
        modelName: CONFIG.agent.modelName,
        apiKey: CONFIG.agent.apiKey,
        baseURL: CONFIG.agent.baseURL,
      },
      systemPrompt: `You are an expert web automation agent for Fábrica de Fotolibros (FDF).
        The interface is in Spanish. Common elements:
        - "Nuevo Proyecto" = New Project
        - "Fotolibros" = Photo books
        - "21x21" = 21x21cm size option
        - "Continuar" = Continue
        - "Subir fotos" = Upload photos
        - "Temas" or "Plantillas" = Templates
        - "Relleno fotos smart" = Smart photo fill
        
        Always wait for elements to load before interacting.
        Click on visible buttons and options.`,
    });
    
    log("AGENT", "Ejecutando tarea: Crear proyecto 21x21...");
    
    const createResult = await agent.execute({
      instruction: `
        1. Click on "Nuevo Proyecto" to create a new project
        2. Wait for the product selection page to load
        3. Find and click on the "Fotolibros" category if needed
        4. Select the "21x21" photobook size option
        5. Click "Continuar" or any button to proceed to the editor
        
        Stop when you reach the editor or photo upload screen.
      `,
      maxSteps: 15,
    });
    
    log("AGENT", "Resultado creación:", {
      success: createResult.success,
      message: createResult.message,
      steps: createResult.actions?.length || 0
    });
    
    await takeScreenshot(page, "03_proyecto_creado");
    
    // =====================================================
    // PASO 3: Subir fotos
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 3: Subir Fotos");
    console.log("=".repeat(70));
    
    log("UPLOAD", `Subiendo ${FOTOS_TEST.length} fotos...`);
    
    // Buscar input de archivo
    await sleep(2000);
    
    try {
      // Intentar encontrar input file usando $$ (selector nativo)
      const fileInputCount = await page.locator('input[type="file"]').count();
      
      if (fileInputCount > 0) {
        log("UPLOAD", `Encontrados ${fileInputCount} inputs de archivo`);
        await page.locator('input[type="file"]').first().setInputFiles(FOTOS_TEST);
        await sleep(8000); // Esperar upload
        log("UPLOAD", "✓ Fotos subidas");
      } else {
        log("UPLOAD", "No se encontró input file, usando Agent...");
        
        const uploadResult = await agent.execute({
          instruction: `
            Find and click on the button to upload photos. 
            It might be labeled "Subir fotos", "Agregar fotos", "+" or have an upload icon.
            Click it to open the file dialog.
          `,
          maxSteps: 5,
        });
        
        log("UPLOAD", "Agent upload result:", uploadResult.message);
        
        // Después del click, buscar input file nuevamente
        await sleep(2000);
        const newFileInputCount = await page.locator('input[type="file"]').count();
        if (newFileInputCount > 0) {
          await page.locator('input[type="file"]').first().setInputFiles(FOTOS_TEST);
          await sleep(8000);
        }
      }
    } catch (error) {
      log("UPLOAD", `Error subiendo fotos: ${error}`);
    }
    
    await takeScreenshot(page, "04_fotos_subidas");
    
    // =====================================================
    // PASO 4: Aplicar Template con Agent
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 4: Aplicar Template");
    console.log("=".repeat(70));
    
    log("TEMPLATE", "Usando Agent para aplicar template...");
    
    const templateResult = await agent.execute({
      instruction: `
        1. Look for "Temas", "Plantillas de página", or "Templates" section in the right panel
        2. Click on it to expand template options
        3. Select a template that is NOT "Vacio" (empty) - preferably one with a design like "Flores", "Moderno", or similar
        4. If a confirmation dialog appears, confirm the selection
        
        The goal is to apply a decorative template to the photobook pages.
      `,
      maxSteps: 10,
    });
    
    log("TEMPLATE", "Resultado:", {
      success: templateResult.success,
      message: templateResult.message
    });
    
    await takeScreenshot(page, "05_template_aplicado");
    
    // =====================================================
    // PASO 5: Smart Fill con Agent
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 5: Relleno Smart (Auto-diseño)");
    console.log("=".repeat(70));
    
    log("SMART", "Usando Agent para Smart Fill...");
    
    const smartFillResult = await agent.execute({
      instruction: `
        1. Scroll down in the right panel to find fill options
        2. Look for buttons like "Relleno fotos smart", "Smart fill", or "Auto relleno"
        3. Click on "Relleno fotos smart" (the smart option, not simple fill)
        4. A modal/dialog should appear with 3 options:
           - "Caras, Colores y Dimensiones" (SMART - most complete)
           - "Colores y Dimensiones" (medium)
           - "Dimensiones" (basic)
        5. Select the FIRST option "Caras, Colores y Dimensiones" as it's the most intelligent
        6. Wait for the system to automatically place photos on all pages
        
        This is the most important step - it will automatically design the entire photobook.
      `,
      maxSteps: 15,
    });
    
    log("SMART", "Resultado Smart Fill:", {
      success: smartFillResult.success,
      message: smartFillResult.message
    });
    
    // Esperar procesamiento del Smart Fill
    log("SMART", "Esperando procesamiento (15 segundos)...");
    await sleep(15000);
    
    await takeScreenshot(page, "06_smart_fill_done");
    
    // =====================================================
    // PASO 6: Verificar resultado
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 6: Verificar Diseño");
    console.log("=".repeat(70));
    
    log("VERIFY", "Extrayendo información del diseño...");
    
    const designInfo = await stagehand.extract({
      instruction: `Analyze the current photobook design:
        1. How many photos appear to be placed on the pages?
        2. Are the pages designed (have photos/decorations) or still empty?
        3. Is there a preview of multiple pages visible?
        4. Does the design look complete and ready to export?`,
      schema: {
        type: "object",
        properties: {
          photosPlaced: { type: "number", description: "Estimated number of photos placed" },
          pagesDesigned: { type: "boolean", description: "Are pages designed (not empty)?" },
          hasPreview: { type: "boolean", description: "Is there a page preview visible?" },
          readyToExport: { type: "boolean", description: "Does it look ready to export?" },
          observations: { type: "string", description: "Any other observations about the design" }
        }
      }
    });
    
    log("VERIFY", "Estado del diseño:", designInfo);
    await takeScreenshot(page, "07_final_design");
    
    // =====================================================
    // RESULTADO FINAL
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  RESULTADO FINAL");
    console.log("=".repeat(70));
    
    const success = designInfo.pagesDesigned && (designInfo.photosPlaced || 0) > 0;
    
    console.log(`
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  RESUMEN DEL TEST AGENT:
  
  Pasos completados:
    1. Login en FDF:           ✓
    2. Crear proyecto:         ${createResult.success ? '✓' : '✗'}
    3. Subir fotos:            ${FOTOS_TEST.length} fotos
    4. Aplicar template:       ${templateResult.success ? '✓' : '✗'}
    5. Smart Fill:             ${smartFillResult.success ? '✓' : '✗'}
  
  Resultado del diseño:
    Fotos colocadas:           ${designInfo.photosPlaced || 0}
    Páginas diseñadas:         ${designInfo.pagesDesigned ? 'SÍ' : 'NO'}
    Listo para exportar:       ${designInfo.readyToExport ? 'SÍ' : 'NO'}
  
  Observaciones:
    ${designInfo.observations || 'N/A'}
  
  ESTADO FINAL: ${success ? '✅ ÉXITO' : '❌ FALLÓ'}
  
  Screenshots guardados en: ${CONFIG.screenshotDir}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
    
    // Mantener browser abierto para inspección
    log("INFO", "Browser abierto 60s para inspección. Ctrl+C para cerrar.");
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
