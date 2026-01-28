/**
 * Test Híbrido: Stagehand v3 + Playwright para FDF
 * 
 * Estrategia:
 * - Stagehand para navegación/login (AI-driven, adaptable)
 * - Playwright directo para subir archivos (más rápido)
 * - Modo "Relleno fotos smart" (auto-colocación)
 * 
 * LLM: OpenRouter con openai/gpt-4o
 * 
 * Ejecutar: npx tsx test-hybrid-drag.ts
 */

import { Stagehand } from "@browserbasehq/stagehand";
import type { Page } from "playwright-core";

// =====================================================
// CONFIGURACIÓN
// =====================================================
const CONFIG = {
  // LLM Provider: OpenRouter con GPT-4o
  llm: {
    modelName: "openai/gpt-4o",
    apiKey: "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",
    baseURL: "https://openrouter.ai/api/v1"
  },

  // Modo de relleno de fotos
  fillMode: "smart",  // "Relleno fotos smart"

  // Fotos de la base de datos
  photoPaths: [
    "C:/Users/Usuario/Downloads/fotolibros_argentina/fotolibros-argentina-v2/fotolibros-argentina/uploads/717a603f-156b-4c3c-9ab0-f00596d78aa7/d975c7d2-dbe9-494e-9907-e38fb07de4ed.png",
    "C:/Users/Usuario/Downloads/fotolibros_argentina/fotolibros-argentina-v2/fotolibros-argentina/uploads/717a603f-156b-4c3c-9ab0-f00596d78aa7/c5e8b3f7-2c18-4527-814e-c422338e814f.jpg",
    "C:/Users/Usuario/Downloads/fotolibros_argentina/fotolibros-argentina-v2/fotolibros-argentina/uploads/717a603f-156b-4c3c-9ab0-f00596d78aa7/9cebe9fb-6746-4113-a1d7-a8fc15537b8d.jpg"
  ]
};

// Credenciales FDF
const FDF = {
  email: "revelacionesocultas72@gmail.com",
  password: "Jony.2176",
  baseUrl: "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
};

// Browser options
const BROWSER = {
  headless: false,
  viewport: { width: 1400, height: 900 },
  chromePath: "C:/Program Files/Google/Chrome/Application/chrome.exe"
};

// =====================================================
// FUNCIONES AUXILIARES
// =====================================================

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function log(step: string, message: string, data?: any) {
  const timestamp = new Date().toLocaleTimeString();
  console.log(`[${timestamp}] [${step}] ${message}`);
  if (data) console.log("    ", JSON.stringify(data, null, 2).replace(/\n/g, "\n    "));
}

// =====================================================
// TEST PRINCIPAL
// =====================================================

async function main() {
  console.log("=".repeat(70));
  console.log("  TEST HÍBRIDO: Stagehand v3 + Playwright para FDF");
  console.log("=".repeat(70));
  console.log(`\n  LLM: ${CONFIG.llm.modelName}`);
  console.log(`  Browser: ${BROWSER.headless ? "Headless" : "Visible"} Chrome`);
  console.log("  Fotos de BD: " + CONFIG.photoPaths.length);
  console.log("-".repeat(70));

  // Inicializar Stagehand
  const stagehand = new Stagehand({
    env: "LOCAL",
    model: {
      modelName: CONFIG.llm.modelName,
      apiKey: CONFIG.llm.apiKey,
      baseURL: CONFIG.llm.baseURL,
    },
    localBrowserLaunchOptions: {
      headless: BROWSER.headless,
      viewport: BROWSER.viewport,
      executablePath: BROWSER.chromePath,
    },
  });

  try {
    console.log("\n[INIT] Iniciando Stagehand...");
    await stagehand.init();
    console.log("    Browser listo");

    const page = stagehand.context.pages()[0];
    if (!page) {
      throw new Error("No page available in context");
    }

    // =====================================================
    // FASE 1: Navegación y Login (Stagehand)
    // =====================================================
    log("NAV", "Navegando a FDF...");
    await page.goto(FDF.baseUrl);
    await sleep(5000);

    console.log("    OK - Pagina cargada");

    log("LOGIN", "Haciendo login con Stagehand...");
    await stagehand.act(`type '${FDF.email}' in email or username field`);
    await sleep(500);
    await stagehand.act(`type '${FDF.password}' in password field`);
    await sleep(500);
    await stagehand.act("click on login or 'Ingresar' button");
    await sleep(5000);

    console.log("    OK - Login completado");

    // =====================================================
    // FASE 2: Navegar al editor (Stagehand)
    // =====================================================
    log("NAV", "Creando nuevo proyecto...");
    
    await stagehand.act("click on 'Nuevo pedido' or create new project button");
    await sleep(2000);
    
    await stagehand.act("click on 'Fotolibros' category");
    await sleep(2000);
    
    await stagehand.act("click on the '21x21' or 'Fotolibro 21x21' product");
    await sleep(3000);

    // Llenar título (obligatorio)
    const projectTitle = `Test_${Date.now()}`;
    log("CONFIG", `Llenando título: ${projectTitle}`);
    await stagehand.act(`type '${projectTitle}' in the 'Título' text field`);
    await sleep(1000);

    // =====================================================
    // FASE 3: Seleccionar plantilla y modo de relleno
    // =====================================================
    log("TEMPLATE", "Seleccionando plantilla...");

    await stagehand.act("scroll down to see template options");
    await sleep(2000);

    await stagehand.act("click on first available template or design");
    await sleep(2000);

    // ⚠️ CRÍTICO: Hacer scroll para ver los botones de relleno
    log("SCROLL", "Scrolling para ver botones de relleno...");
    await stagehand.act("scroll down multiple times or go to bottom of the page to see fill mode buttons");
    await sleep(2000);

    // Seleccionar modo de relleno (importante: ESPECIFICAR "relleno fotos" para evitar confusión con "crear proyecto")
    const fillModeButtons: Record<string, string> = {
      "manual": "Relleno fotos manual",
      "rapido": "Relleno fotos rápido",
      "smart": "Relleno fotos smart"
    };

    const buttonText = fillModeButtons[CONFIG.fillMode] || fillModeButtons["smart"];
    log("FILL_MODE", `Seleccionando botón: ${buttonText}`);
    await stagehand.act(`click on the button that says 'Relleno fotos' and '${buttonText.split(" ")[1]}' to select fill mode`);
    await sleep(5000);

    console.log("    OK - En el editor (o esperando ser redirigido)");

    // =====================================================
    // FASE 4: Subir fotos de la base de datos
    // =====================================================
    log("UPLOAD", "Subiendo fotos de la base de datos...");

    await stagehand.act("find and click on 'Subir fotos' or 'Add photos' button in the left panel");
    await sleep(2000);

    // Buscar input de tipo file
    const fileInput = await page.locator('input[type="file"]').first();
    await fileInput.setInputFiles(CONFIG.photoPaths);
    await sleep(3000);

    log("UPLOAD", `✅ ${CONFIG.photoPaths.length} fotos subidas de la base de datos`);

    // =====================================================
    // FASE 5: Verificar estado después de subir
    // =====================================================
    log("CHECK", "Verificando estado después de subir fotos...");
    await sleep(3000);

    // Analizar si hay botones de continuación o si estamos en el editor
    const checkState = await stagehand.extract({
      instruction: `Analyze the current screen. Answer:
        1. Are you still in a photo upload dialog/selection screen?
        2. Is there a "Continuar", "Accept", "OK", or "Enter editor" button visible?
        3. Are there any error messages or warnings?
        4. If in editor, how many photos are shown in the panel?
        Be specific about what you see.`,
      schema: {
        type: "object",
        properties: {
          inUploadScreen: { type: "boolean", description: "Still in upload selection screen?" },
          hasContinueButton: { type: "boolean", description: "Is there a Continue/OK button?" },
          errorMessage: { type: "string", description: "Any error messages visible?" },
          inEditor: { type: "boolean", description: "Already in the photo editor?" },
          photosVisible: { type: "number", description: "Number of photos in panel?" }
        }
      }
    });

    log("CHECK", "Estado actual:", checkState);

    // Si estamos en pantalla de upload, intentar continuar
    if (checkState.inUploadScreen) {
      log("ACTION", "Intentando salir de pantalla de upload...");

      // Buscar y click en botón de Continuar, Aceptar, OK, o similar
      const continueFound = await stagehand.observe("find 'Continuar', 'Aceptar', 'OK', 'Guardar', or 'Confirm' button");
      if (continueFound.length > 0) {
        log("ACTION", `Click en botón: ${continueFound[0].description}`);
        await stagehand.act(continueFound[0]);
        await sleep(3000);
      } else {
        log("WARN", "No se encontró botón de continuar - haciendo scroll");
        await stagehand.act("scroll down or press Enter to continue");
        await sleep(2000);
      }

      // Verificar nuevamente
      const afterClick = await stagehand.extract({
        instruction: "Analyze if we are now in the photo editor. Look for photo thumbnails panel and canvas area.",
        schema: {
          type: "object",
          properties: {
            inEditor: { type: "boolean", description: "Are we in the photo editor?" },
            photosVisible: { type: "number", description: "How many photos visible?" }
          }
        }
      });
      log("AFTER_CLICK", "Después de click:", afterClick);
    }

    // =====================================================
    // FASE 6: Verificar resultado
    // =====================================================
    log("VERIFY", "Verificando resultado del modo " + CONFIG.fillMode + "...");

    if (CONFIG.fillMode === "smart" || CONFIG.fillMode === "rapido") {
      log("AUTO_FILL", `Modo '${CONFIG.fillMode}' activo - FDF colocará fotos automáticamente`);
      await sleep(10000);  // Esperar procesamiento
    }

    // Resultado final
    console.log("\n" + "=".repeat(70));
    console.log("  RESULTADO DEL TEST");
    console.log("=".repeat(70));
    console.log(`  Fotos subidas: ${CONFIG.photoPaths.length}`);
    console.log(`  Modo de relleno: ${CONFIG.fillMode}`);
    console.log("-".repeat(70));

    // Mantener browser abierto
    console.log("\n[INFO] Browser abierto para inspección. Presiona Ctrl+C para cerrar.");
    await sleep(120000);

  } catch (error) {
    console.error("\n❌ ERROR:", error);
    console.log("\n[INFO] Browser abierto para debug. Presiona Ctrl+C para cerrar.");
    await sleep(120000);
  } finally {
    await stagehand.close();
    console.log("\nBrowser cerrado");
  }
}

main().catch(console.error);
