/**
 * Test Stagehand TypeScript + OpenRouter para FDF
 * 
 * Prueba el drag & drop de fotos en el editor de Fabrica de Fotolibros
 * 
 * Ejecutar: npx tsx test-fdf-drag.ts
 */

import { Stagehand } from "@browserbasehq/stagehand";

// Credenciales desde .env del proyecto principal
const OPENROUTER_API_KEY = "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";
const FDF_EMAIL = "revelacionesocultas72@gmail.com";
const FDF_PASSWORD = "Jony.2176";
const FDF_URL = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com";

async function main() {
  console.log("=".repeat(60));
  console.log("TEST: Stagehand TypeScript + OpenRouter + FDF");
  console.log("=".repeat(60));

  // Inicializar Stagehand con OpenRouter
  const stagehand = new Stagehand({
    env: "LOCAL",
    model: {
      modelName: "openai/gpt-4o",
      apiKey: OPENROUTER_API_KEY,
      baseURL: "https://openrouter.ai/api/v1",
    },
    localBrowserLaunchOptions: {
      headless: false,
      viewport: { width: 1400, height: 900 },
      // Chrome path para Windows
      executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
    },
  });

  try {
    console.log("\n[1] Inicializando Stagehand...");
    await stagehand.init();
    console.log("    OK - Browser iniciado");

    // Acceder a la página via context (Stagehand v3)
    const page = stagehand.context.pages()[0];
    if (!page) {
      throw new Error("No page available in context");
    }

    // =====================================================
    // PASO 1: Navegar a FDF
    // =====================================================
    console.log("\n[2] Navegando a FDF...");
    await page.goto(FDF_URL);
    // Esperar un tiempo fijo en lugar de networkidle (FDF tiene muchos recursos)
    await sleep(5000);
    console.log("    OK - Pagina cargada");

    // =====================================================
    // PASO 2: Login
    // =====================================================
    console.log("\n[3] Haciendo login...");
    
    // Escribir email
    await stagehand.act(`type '${FDF_EMAIL}' in the email or username field`);
    await sleep(500);
    
    // Escribir password
    await stagehand.act(`type '${FDF_PASSWORD}' in the password field`);
    await sleep(500);
    
    // Click en login
    await stagehand.act("click the login or 'Ingresar' button");
    await sleep(5000);
    
    console.log("    OK - Login completado");

    // =====================================================
    // PASO 3: Crear nuevo proyecto
    // =====================================================
    console.log("\n[4] Creando nuevo proyecto...");
    
    // Buscar producto
    await stagehand.act("click on 'Nuevo pedido' or 'Crear nuevo' button");
    await sleep(2000);
    
    // Seleccionar fotolibro 21x21
    await stagehand.act("search for or click on '21x21' photobook product");
    await sleep(2000);
    
    // Seleccionar template
    await stagehand.act("click on the first available template or design");
    await sleep(3000);
    
    console.log("    OK - Proyecto creado");

    // =====================================================
    // PASO 4: Subir fotos
    // =====================================================
    console.log("\n[5] Subiendo fotos...");
    
    // Click en agregar fotos
    await stagehand.act("click the button to add photos or 'Agregar fotos'");
    await sleep(2000);
    
    // Seleccionar desde computadora
    await stagehand.act("click 'Desde computadora' or 'From computer' option");
    await sleep(2000);
    
    console.log("    Nota: Se requiere seleccionar fotos manualmente");
    await sleep(5000);  // Tiempo para seleccionar fotos manualmente

    // =====================================================
    // PASO 5: Entrar al editor
    // =====================================================
    console.log("\n[6] Entrando al editor...");
    
    await stagehand.act("click the button to enter the editor or 'Entrar al editor'");
    await sleep(5000);
    
    console.log("    OK - En el editor");

    // =====================================================
    // PASO 6: DRAG & DROP (El momento de la verdad)
    // =====================================================
    console.log("\n[7] Intentando drag & drop...");
    console.log("    Metodo: Stagehand act() con lenguaje natural");
    
    try {
      // Intento 1: Lenguaje natural directo
      console.log("\n    Intento 1: Lenguaje natural...");
      await stagehand.act("drag the first photo from the left panel to the empty slot on the canvas");
      await sleep(2000);
      console.log("    Resultado: Posiblemente exitoso");
    } catch (error) {
      console.log(`    Error: ${error}`);
    }

    try {
      // Intento 2: Mas especifico
      console.log("\n    Intento 2: Instruccion mas especifica...");
      await stagehand.act("drag and drop a photo thumbnail from the photos panel on the left side to the main photo area in the center of the page");
      await sleep(2000);
      console.log("    Resultado: Posiblemente exitoso");
    } catch (error) {
      console.log(`    Error: ${error}`);
    }

    try {
      // Intento 3: Click-based alternative
      console.log("\n    Intento 3: Click en foto y luego en slot...");
      await stagehand.act("click on the first photo in the left panel to select it");
      await sleep(1000);
      await stagehand.act("click on the empty photo slot in the center of the canvas to place the photo");
      await sleep(2000);
      console.log("    Resultado: Posiblemente exitoso");
    } catch (error) {
      console.log(`    Error: ${error}`);
    }

    try {
      // Intento 4: Double-click
      console.log("\n    Intento 4: Doble click en foto...");
      await stagehand.act("double-click on the first photo in the left panel to add it to the canvas");
      await sleep(2000);
      console.log("    Resultado: Posiblemente exitoso");
    } catch (error) {
      console.log(`    Error: ${error}`);
    }

    // =====================================================
    // VERIFICACION
    // =====================================================
    console.log("\n[8] Verificando resultado...");
    
    const pageState = await stagehand.extract({
      instruction: "analyze the current state of the photo editor",
      schema: {
        type: "object",
        properties: {
          photosInPanel: { type: "number", description: "Number of photos visible in the left panel" },
          photosOnCanvas: { type: "number", description: "Number of photos placed on the canvas" },
          emptySlots: { type: "number", description: "Number of empty slots remaining" },
          currentPage: { type: "string", description: "Current page being edited" },
        },
      },
    });
    
    console.log("    Estado del editor:", JSON.stringify(pageState, null, 2));

    // Mantener browser abierto para inspección
    console.log("\n[9] Browser abierto para inspeccion manual...");
    console.log("    Presiona Ctrl+C para cerrar");
    
    // Esperar 60 segundos
    await sleep(60000);

  } catch (error) {
    console.error("\nERROR:", error);
    // Mantener browser abierto en caso de error para debug
    console.log("\nBrowser abierto para debug. Presiona Ctrl+C para cerrar.");
    await sleep(60000);
  } finally {
    await stagehand.close();
    console.log("\nBrowser cerrado");
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

main().catch(console.error);
