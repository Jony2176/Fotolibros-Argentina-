/**
 * Test Stagehand TypeScript + OpenRouter para FDF
 * VERSIÓN 2: Enfocado en llegar al editor y probar drag & drop
 * 
 * Ejecutar: npx tsx test-fdf-editor.ts
 */

import { Stagehand } from "@browserbasehq/stagehand";

// Credenciales desde .env del proyecto principal
const OPENROUTER_API_KEY = "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";
const FDF_EMAIL = "revelacionesocultas72@gmail.com";
const FDF_PASSWORD = "Jony.2176";
const FDF_URL = "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com";

async function main() {
  console.log("=".repeat(60));
  console.log("TEST v2: Stagehand TypeScript + OpenRouter + FDF EDITOR");
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
      executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
    },
  });

  try {
    console.log("\n[1] Inicializando Stagehand...");
    await stagehand.init();
    console.log("    OK - Browser iniciado");

    const page = stagehand.context.pages()[0];
    if (!page) {
      throw new Error("No page available in context");
    }

    // =====================================================
    // PASO 1: Navegar a FDF
    // =====================================================
    console.log("\n[2] Navegando a FDF...");
    await page.goto(FDF_URL);
    await sleep(5000);
    console.log("    OK - Pagina cargada");

    // =====================================================
    // PASO 2: Login
    // =====================================================
    console.log("\n[3] Haciendo login...");
    await stagehand.act(`type '${FDF_EMAIL}' in the email field`);
    await sleep(500);
    await stagehand.act(`type '${FDF_PASSWORD}' in the password field`);
    await sleep(500);
    await stagehand.act("click the INGRESAR button");
    await sleep(5000);
    console.log("    OK - Login completado");

    // =====================================================
    // PASO 3: Verificar si hay proyectos existentes
    // =====================================================
    console.log("\n[4] Buscando proyectos existentes...");
    
    // Intentar encontrar un proyecto existente para editar
    try {
      // Buscar sección "Mis proyectos" o similar
      await stagehand.act("click on 'Mis pedidos' or 'Mis proyectos' if visible");
      await sleep(3000);
      
      // Ver si hay proyectos para editar
      const projectState = await stagehand.extract({
        instruction: "check if there are any existing projects that can be edited",
        schema: {
          type: "object",
          properties: {
            hasProjects: { type: "boolean", description: "Are there existing projects?" },
            projectNames: { type: "array", items: { type: "string" }, description: "Names of projects" },
          },
        },
      });
      console.log("    Estado proyectos:", JSON.stringify(projectState, null, 2));
      
      if (projectState.hasProjects) {
        console.log("    Intentando editar proyecto existente...");
        await stagehand.act("click on 'Editar' button of the first project");
        await sleep(5000);
      }
    } catch (e) {
      console.log("    No se encontraron proyectos existentes, creando nuevo...");
    }

    // =====================================================
    // PASO 4: Crear nuevo proyecto (si no hay existentes)
    // =====================================================
    console.log("\n[5] Creando nuevo proyecto 21x21...");
    
    // Ir a crear nuevo
    await stagehand.act("click on 'Nuevo pedido' or the button to create a new project");
    await sleep(2000);
    
    // Seleccionar Fotolibros
    await stagehand.act("click on 'Fotolibros' category");
    await sleep(2000);
    
    // Seleccionar fotolibro 21x21
    await stagehand.act("click on the product '21x21' or 'Fotolibro 21x21'");
    await sleep(3000);
    
    // Hacer click en "Crear Proyecto" para entrar al editor
    await stagehand.act("click on 'Crear Proyecto' button");
    await sleep(5000);
    
    console.log("    OK - En la pantalla del editor");

    // =====================================================
    // PASO 5: Verificar si estamos en el editor real
    // =====================================================
    console.log("\n[6] Verificando estado del editor...");
    
    const editorState = await stagehand.extract({
      instruction: "Analyze if we are in the photo editor. Look for: photo panels, canvas/page area, photo thumbnails, empty slots for photos",
      schema: {
        type: "object",
        properties: {
          isInEditor: { type: "boolean", description: "Are we in the photo editor view?" },
          hasPhotoPanel: { type: "boolean", description: "Is there a panel with photo thumbnails?" },
          hasCanvas: { type: "boolean", description: "Is there a canvas or page editing area?" },
          hasEmptySlots: { type: "boolean", description: "Are there empty photo slots?" },
          currentView: { type: "string", description: "Description of current view" },
        },
      },
    });
    
    console.log("    Estado del editor:", JSON.stringify(editorState, null, 2));

    // =====================================================
    // PASO 6: Si estamos en el editor, intentar subir fotos
    // =====================================================
    if (editorState.isInEditor || editorState.hasCanvas) {
      console.log("\n[7] Subiendo fotos...");
      
      // Buscar botón para agregar fotos
      await stagehand.act("click on the button to add photos, 'Agregar fotos', or '+' icon in the photos panel");
      await sleep(2000);
      
      // Seleccionar desde computadora
      await stagehand.act("click on 'Desde computadora' or 'Upload from computer'");
      await sleep(2000);
      
      console.log("    ⚠️  PAUSA: Selecciona fotos manualmente en el diálogo del sistema");
      console.log("    Tienes 30 segundos...");
      await sleep(30000);
      
      // =====================================================
      // PASO 7: Probar drag & drop con métodos alternativos
      // =====================================================
      console.log("\n[8] Probando métodos de drag & drop...");
      
      // Método 1: Click en foto para seleccionar, luego click en slot
      console.log("\n    Método 1: Click-select pattern...");
      try {
        await stagehand.act("click on the first photo thumbnail in the left panel to select it");
        await sleep(1000);
        await stagehand.act("click on the first empty photo slot in the canvas/page area");
        await sleep(2000);
      } catch (e) {
        console.log(`    Error: ${e}`);
      }
      
      // Método 2: Usar el page de Playwright directamente para drag
      console.log("\n    Método 2: Playwright drag nativo...");
      try {
        // Obtener posiciones de elementos usando extract
        const positions = await stagehand.extract({
          instruction: "Get the positions of the first photo thumbnail and the first empty slot",
          schema: {
            type: "object",
            properties: {
              photoSelector: { type: "string", description: "CSS selector or description of first photo" },
              slotSelector: { type: "string", description: "CSS selector or description of first empty slot" },
            },
          },
        });
        console.log("    Posiciones:", JSON.stringify(positions, null, 2));
        
        // Intentar drag usando page.locator directamente
        if (positions.photoSelector && positions.slotSelector) {
          // Usar dragAndDrop de Playwright directamente
          const photoLoc = page.locator('.photo-thumbnail').first();
          const slotLoc = page.locator('.photo-slot-empty').first();
          
          if (await photoLoc.count() > 0 && await slotLoc.count() > 0) {
            await photoLoc.dragTo(slotLoc);
            console.log("    Drag ejecutado con Playwright");
          }
        }
      } catch (e) {
        console.log(`    Error: ${e}`);
      }
      
      // Método 3: Dispatch de eventos HTML5
      console.log("\n    Método 3: HTML5 DataTransfer events...");
      try {
        await page.evaluate(() => {
          // Buscar foto source y slot target
          const photo = document.querySelector('.photo-thumbnail, [draggable="true"], img[src*="thumb"]') as HTMLElement;
          const slot = document.querySelector('.photo-slot, .empty-slot, [data-drop]') as HTMLElement;
          
          if (!photo || !slot) {
            console.log('No se encontraron elementos para drag');
            return false;
          }
          
          // Crear DataTransfer
          const dataTransfer = new DataTransfer();
          
          // Dispatch dragstart en la foto
          const dragStart = new DragEvent('dragstart', {
            bubbles: true,
            cancelable: true,
            dataTransfer
          });
          photo.dispatchEvent(dragStart);
          
          // Dispatch dragover en el slot
          const dragOver = new DragEvent('dragover', {
            bubbles: true,
            cancelable: true,
            dataTransfer
          });
          slot.dispatchEvent(dragOver);
          
          // Dispatch drop en el slot
          const drop = new DragEvent('drop', {
            bubbles: true,
            cancelable: true,
            dataTransfer
          });
          slot.dispatchEvent(drop);
          
          // Dispatch dragend en la foto
          const dragEnd = new DragEvent('dragend', {
            bubbles: true,
            cancelable: true,
            dataTransfer
          });
          photo.dispatchEvent(dragEnd);
          
          return true;
        });
        console.log("    Eventos HTML5 dispatched");
      } catch (e) {
        console.log(`    Error: ${e}`);
      }
    } else {
      console.log("\n[7] No estamos en el editor real. Estado actual:");
      console.log("    " + editorState.currentView);
    }

    // =====================================================
    // VERIFICACIÓN FINAL
    // =====================================================
    console.log("\n[9] Verificando resultado final...");
    
    const finalState = await stagehand.extract({
      instruction: "Check how many photos have been placed on the canvas/page",
      schema: {
        type: "object",
        properties: {
          photosPlaced: { type: "number", description: "Number of photos placed on canvas" },
          emptySlots: { type: "number", description: "Number of remaining empty slots" },
          pageDescription: { type: "string", description: "Description of current page state" },
        },
      },
    });
    
    console.log("    Estado final:", JSON.stringify(finalState, null, 2));

    // Mantener browser abierto para inspección
    console.log("\n[10] Browser abierto para inspección manual...");
    console.log("     Presiona Ctrl+C para cerrar");
    
    await sleep(120000);

  } catch (error) {
    console.error("\nERROR:", error);
    console.log("\nBrowser abierto para debug. Presiona Ctrl+C para cerrar.");
    await sleep(120000);
  } finally {
    await stagehand.close();
    console.log("\nBrowser cerrado");
  }
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

main().catch(console.error);
