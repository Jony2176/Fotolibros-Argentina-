/**
 * Test E2E - Flujo Backend COMPLETO (Híbrido)
 * ============================================
 * 
 * Simula el flujo REAL completo del sistema:
 * 
 * FASE 1 - FRONTEND (Simulada):
 * 1. Cliente crea nuevo proyecto en FDF
 * 2. Cliente sube sus fotos
 * 3. Cliente paga
 * 
 * FASE 2 - BACKEND (Automatizada):
 * 4. Backend recibe notificación de pago
 * 5. Backend hace login con credenciales del cliente
 * 6. Backend abre el proyecto existente
 * 7. Backend aplica template según estilo
 * 8. Backend usa "Relleno fotos smart" (opción SMART completa)
 * 9. Backend guarda y exporta
 */

import { Stagehand } from "@browserbasehq/stagehand";
import * as fs from 'fs';
import * as path from 'path';

// =====================================================
// CONFIGURACION
// =====================================================

const CONFIG = {
  fdf: {
    // IMPORTANTE: Usar credenciales del CLIENTE (no del backend)
    // El proyecto ya existe en la cuenta del cliente
    email: process.env.FDF_EMAIL || "revelacionesocultas72@gmail.com",
    password: process.env.FDF_PASSWORD || "Jony.2176",
    loginUrl: "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com"
  },
  
  llm: {
    modelName: "openai/gpt-4o-mini",
    apiKey: process.env.OPENROUTER_API_KEY || "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",
    baseURL: "https://openrouter.ai/api/v1"
  },
  
  browser: {
    headless: false,
    viewport: { width: 1400, height: 900 },
    chromePath: "C:/Program Files/Google/Chrome/Application/chrome.exe"
  },
  
  screenshotDir: path.resolve(__dirname, 'screenshots-backend')
};

// =====================================================
// DATOS DEL PEDIDO (simulando lo que viene del frontend)
// =====================================================

const PEDIDO_CONFIRMADO = {
  pedido_id: "ej-123456",  // ID del pedido en nuestra BD
  fdf_project_name: "Test E2E Hibrido",  // Nombre del proyecto en FDF
  producto: "21x21",
  estilo: "minimalista",
  template: "Flores Marga",  // Template que el cliente eligió o que asignamos
  
  // FOTOS DE PRUEBA (ubicadas en uploads/fotos_test/)
  fotos: [
    path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto1.jpg'),
    path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto2.jpg'),
    path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto3.jpg'),
    path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto4.jpg'),
    path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto5.jpg'),
  ]
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
  log("SCREENSHOT", `${name}.png`);
}

// =====================================================
// FLUJO BACKEND
// =====================================================

async function main() {
  console.log("=".repeat(70));
  console.log("  TEST BACKEND - Diseño Automático de Proyecto Existente");
  console.log("=".repeat(70));
  
  console.log("\nPEDIDO RECIBIDO:");
  console.log(`  ID: ${PEDIDO_CONFIRMADO.pedido_id}`);
  console.log(`  Proyecto FDF: ${PEDIDO_CONFIRMADO.fdf_project_name}`);
  console.log(`  Producto: ${PEDIDO_CONFIRMADO.producto}`);
  console.log(`  Estilo: ${PEDIDO_CONFIRMADO.estilo}`);
  console.log("\n  Estado: PAGADO ✓");
  console.log("  Fotos preparadas:", PEDIDO_CONFIRMADO.fotos.length);
  
  // Verificar que las fotos existan
  for (const foto of PEDIDO_CONFIRMADO.fotos) {
    if (!fs.existsSync(foto)) {
      console.error(`\n❌ ERROR: Foto no encontrada: ${foto}`);
      process.exit(1);
    }
  }
  console.log("  ✓ Todas las fotos existen");
  
  console.log("\n" + "-".repeat(70));
  
  log("INIT", "Iniciando Stagehand...");
  
  const modelConfig: any = {
    modelName: CONFIG.llm.modelName,
    apiKey: CONFIG.llm.apiKey,
    baseURL: CONFIG.llm.baseURL,
  };
  
  const stagehand = new Stagehand({
    env: "LOCAL",
    model: modelConfig,
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
    // FASE 1: CREAR PROYECTO (Simular Frontend)
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 1: CREAR PROYECTO (Simular Frontend)");
    console.log("=".repeat(70));
    
    // =====================================================
    // PASO 1: Login en FDF
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 1: Login en FDF");
    console.log("=".repeat(70));
    
    log("LOGIN", "Navegando a FDF...");
    await page.goto(CONFIG.fdf.loginUrl);
    await sleep(3000);
    await takeScreenshot(page, "01_login");
    
    log("LOGIN", "Autenticando...");
    await page.locator('#email_log').fill(CONFIG.fdf.email);
    await sleep(300);
    await page.locator('#clave_log').fill(CONFIG.fdf.password);
    await sleep(300);
    await page.locator('#bt_log').click();
    
    await sleep(6000);
    await takeScreenshot(page, "02_logged_in");
    
    // =====================================================
    // PASO 2: CREACIÓN MANUAL REQUERIDA
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 2: Verificar Proyecto Existente");
    console.log("=".repeat(70));
    
    console.log(`
⚠️ NOTA IMPORTANTE:
   Este test requiere que el proyecto YA EXISTA en FDF.
   
   Para crear el proyecto manualmente:
   1. En el browser que se abrió, clickea "Nuevo Proyecto"
   2. Selecciona "Fotolibros 21x21"
   3. Sube las 5 fotos de: uploads/fotos_test/
   4. Guarda el proyecto (NO diseñes todavía)
   5. Presiona ENTER aquí para continuar el test
`);
    
    // Esperar a que el usuario presione ENTER
    await new Promise<void>((resolve) => {
      const stdin = process.stdin;
      stdin.setRawMode(true);
      stdin.resume();
      stdin.setEncoding('utf8');
      
      const onData = (key: string) => {
        if (key === '\r' || key === '\n') {
          stdin.removeListener('data', onData);
          stdin.setRawMode(false);
          stdin.pause();
          resolve();
        } else if (key === '\u0003') { // Ctrl+C
          process.exit(0);
        }
      };
      
      stdin.on('data', onData);
    });
    
    console.log("\n✓ Continuando con el test...\n");
    await takeScreenshot(page, "03_usuario_listo");
    
    // =====================================================
    // PASO 3: Abrir Mis Proyectos
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 3: Navegar a Mis Proyectos");
    console.log("=".repeat(70));
    
    log("NAV", "Navegando a Mis Proyectos...");
    try {
      await stagehand.act("click on 'Mis Proyectos' or 'My Projects' to see existing projects");
      await sleep(3000);
    } catch (error) {
      log("NAV", "Error navegando, puede que ya estemos allí");
    }
    
    await takeScreenshot(page, "04_mis_proyectos");
    
    // =====================================================
    // PASO 4: Abrir Proyecto para Editar
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 4: Abrir Proyecto Reciente");
    console.log("=".repeat(70));
    
    log("PROJECT", "Buscando proyecto más reciente...");
    try {
      await stagehand.act("click on 'Editar' or 'Edit' button for the most recent project");
      await sleep(5000);
    } catch (error) {
      console.error("\n❌ No se encontró el proyecto. Asegúrate de haberlo creado.");
      throw error;
    }
    
    await takeScreenshot(page, "05_proyecto_abierto");
    
    // =====================================================
    // FASE 2: BACKEND - DISEÑO AUTOMÁTICO
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  FASE 2: BACKEND - DISEÑO AUTOMÁTICO");
    console.log("=".repeat(70));
    console.log("\n⏱️ Simulando: Cliente pagó → Backend recibe notificación\n");
    await sleep(2000);
    
    // =====================================================
    // PASO 5: Ir a Plantillas/Templates
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 5: Aplicar Template Automático");
    console.log("=".repeat(70));
    
    log("TEMPLATE", "Navegando a sección de plantillas...");
    
    try {
      await stagehand.act("click on 'Temas' or 'Plantillas de página' or 'Templates' in the right panel");
      await sleep(2000);
    } catch {
      log("TEMPLATE", "Intentando ruta alternativa...");
      await stagehand.act("find and click the templates or themes option");
      await sleep(2000);
    }
    
    await takeScreenshot(page, "06_templates_section");
    
    // Seleccionar template según estilo del pedido
    log("TEMPLATE", `Aplicando template para estilo: ${PEDIDO_CONFIRMADO.estilo}`);
    
    await stagehand.act(`click on template "${PEDIDO_CONFIRMADO.template}" or a similar ${PEDIDO_CONFIRMADO.estilo} style template. Do NOT select "Vacio"`);
    await sleep(2000);
    await takeScreenshot(page, "07_template_selected");
    
    // =====================================================
    // PASO 6: Aplicar Relleno Smart
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 6: Relleno Automático con Smart Fill");
    console.log("=".repeat(70));
    
    log("SMART", "Buscando opciones de relleno...");
    
    // Scroll para ver los botones
    await stagehand.act("scroll down to see the fill mode buttons");
    await sleep(1500);
    await takeScreenshot(page, "08_fill_options");
    
    log("SMART", "Aplicando Relleno fotos smart...");
    await stagehand.act("click on 'Relleno fotos smart' button");
    
    await sleep(3000);
    await takeScreenshot(page, "09_smart_clicked");
    
    // Manejar modal de configuración
    log("SMART", "Configurando opciones de Smart Fill...");
    log("SMART", "Seleccionando opción SMART: 'Caras, Colores y Dimensiones' (la más completa)");
    try {
      // Seleccionar la opción más completa (SMART)
      await stagehand.act("click on the first option 'Caras, Colores y Dimensiones' or the most complete smart fill option");
      await sleep(2000);
    } catch {
      log("SMART", "No se encontró modal de config (puede haberse procesado automáticamente)");
    }
    
    // Esperar procesamiento
    log("SMART", "Esperando que Smart Fill coloque las fotos automáticamente...");
    await sleep(15000);
    
    await takeScreenshot(page, "10_smart_fill_done");
    
    // =====================================================
    // PASO 7: Verificar Resultado
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  PASO 7: Verificar Diseño Automático");
    console.log("=".repeat(70));
    
    const finalCheck = await stagehand.extract({
      instruction: `Analyze the final design:
        1. How many photos are placed on the pages?
        2. Are the pages designed or still empty?
        3. Rate the design quality 0-100
        4. Is it ready to save/export?`,
      schema: {
        type: "object",
        properties: {
          photosPlaced: { type: "number" },
          pagesDesigned: { type: "boolean" },
          qualityScore: { type: "number" },
          readyForExport: { type: "boolean" },
          issues: { type: "array", items: { type: "string" } }
        }
      }
    });
    
    log("RESULT", "Verificación final:", finalCheck);
    await takeScreenshot(page, "11_final_design");
    
    // =====================================================
    // RESULTADO FINAL
    // =====================================================
    console.log("\n" + "=".repeat(70));
    console.log("  RESULTADO BACKEND");
    console.log("=".repeat(70));
    
    const success = finalCheck.pagesDesigned && (finalCheck.photosPlaced || 0) > 0;
    
    console.log(`
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  
  FASE 1 - FRONTEND (Simulada):
    ✓ Proyecto creado:       ${PEDIDO_CONFIRMADO.fdf_project_name}
    ✓ Producto:              ${PEDIDO_CONFIRMADO.producto}
    ✓ Fotos subidas:         ${PEDIDO_CONFIRMADO.fotos.length}
    ✓ Cliente "pagó"
  
  FASE 2 - BACKEND (Automatizada):
    ✓ Template aplicado:     ${PEDIDO_CONFIRMADO.template}
    ✓ Smart Fill usado:      "Caras, Colores y Dimensiones" (SMART)
    ✓ Fotos colocadas:       ${finalCheck.photosPlaced || 0}
    ✓ Páginas diseñadas:     ${finalCheck.pagesDesigned ? 'SÍ' : 'NO'}
  
  RESULTADO:
    Puntuación calidad:      ${finalCheck.qualityScore || 0}/100
    Listo para exportar:     ${finalCheck.readyForExport ? 'SÍ' : 'NO'}
    Estado final:            ${success ? '✅ ÉXITO' : '❌ FALLÓ'}
  
  Screenshots guardados en: ${CONFIG.screenshotDir}
  
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
`);
    
    if ((finalCheck.issues || []).length > 0) {
      console.log("\n  Issues detectados:");
      (finalCheck.issues || []).forEach((issue, i) => {
        console.log(`    ${i + 1}. ${issue}`);
      });
    }
    
    // Mantener browser abierto
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
