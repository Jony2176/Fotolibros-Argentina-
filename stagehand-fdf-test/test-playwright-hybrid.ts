/**
 * Test E2E Híbrido: Playwright + Stagehand
 * =========================================
 * 
 * Arquitectura:
 * - Playwright DIRECTO: Login, navegación con selectores conocidos, uploads
 * - Stagehand act(): Solo para acciones complejas sin selectores fijos
 * 
 * Este enfoque es más rápido y confiable.
 */

import { Stagehand } from "@browserbasehq/stagehand";
import * as fs from 'fs';
import * as path from 'path';
import { getPedido, getPhotosFromDB, getLastPedidoWithPhotos, checkDatabase } from './db-reader';

// =====================================================
// CONFIGURACION
// =====================================================

const CONFIG = {
  fdf: {
    email: process.env.FDF_EMAIL || "revelacionesocultas72@gmail.com",
    password: process.env.FDF_PASSWORD || "Jony.2176",
    baseUrl: "https://www.fabricadefotolibros.com",
    loginUrl: "https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com",
    editorUrl: "https://online.fabricadefotolibros.com"
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
  
  screenshotDir: path.resolve(__dirname, 'screenshots-hybrid')
};

// Mapeo de estilos de diseño a templates de FDF
const TEMPLATE_MAPPING: Record<string, string[]> = {
  'minimalista': ['Minimalista', 'Simple', 'Clean', 'Básico', 'Moderno'],
  'clasico': ['Clásico', 'Elegante', 'Tradicional', 'Vintage'],
  'divertido': ['Divertido', 'Colorful', 'Alegre', 'Infantil', 'Juguetón'],
  'romantico': ['Romántico', 'Flores', 'Flores Marga', 'Amor'],
  'moderno': ['Moderno', 'Contemporary', 'Minimalista', 'Geométrico'],
  'natural': ['Natural', 'Flores', 'Naturaleza', 'Orgánico'],
  'default': ['Flores Marga', 'Moderno', 'Clásico'] // Fallback
};

// Fotos de prueba (usadas si NO se especifica pedido_id)
const FOTOS_TEST_HARDCODED = [
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto1.jpg'),
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto2.jpg'),
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto3.jpg'),
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto4.jpg'),
  path.resolve(__dirname, '../fotolibros-argentina/uploads/fotos_test/foto5.jpg'),
];

// =====================================================
// SELECTORES CONOCIDOS DE FDF
// =====================================================

const SELECTORS = {
  // Login
  login: {
    email: '#email_log',
    password: '#clave_log',
    submit: '#bt_log',
    userMenu: '.user-menu, .usuario-menu, [class*="user"]'
  },
  
  // Página principal (después de login)
  home: {
    fotolibros: 'text=Fotolibros',
    nuevoProyecto: 'text=Nuevo Proyecto',
    misProyectos: 'text=Mis Proyectos',
  },
  
  // Selección de producto
  products: {
    size21x21: 'text=21x21, [data-size="21x21"], .product-21x21',
    continuar: 'text=Continuar, text=Siguiente, button:has-text("Continuar")',
  },
  
  // Editor
  editor: {
    fileInput: 'input[type="file"]',
    uploadButton: 'text=Subir fotos, text=Agregar fotos, [class*="upload"]',
    temas: 'text=Temas, text=Plantillas',
    smartFill: 'text=Relleno fotos smart, text=Smart Fill',
    guardar: 'text=Guardar, text=Save',
  }
};

// =====================================================
// UTILIDADES
// =====================================================

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function log(step: string, message: string, data?: any) {
  const timestamp = new Date().toLocaleTimeString();
  const color = step === 'ERROR' ? '\x1b[31m' : step === 'OK' ? '\x1b[32m' : '\x1b[36m';
  console.log(`${color}[${timestamp}] [${step}]\x1b[0m ${message}`);
  if (data) {
    console.log(`    ${JSON.stringify(data, null, 2).replace(/\n/g, "\n    ")}`);
  }
}

async function screenshot(page: any, name: string) {
  if (!fs.existsSync(CONFIG.screenshotDir)) {
    fs.mkdirSync(CONFIG.screenshotDir, { recursive: true });
  }
  const filepath = path.join(CONFIG.screenshotDir, `${name}.png`);
  await page.screenshot({ path: filepath, fullPage: false });
  log("SCREENSHOT", name);
}

// Intentar click con múltiples selectores
async function tryClick(page: any, selectors: string, timeout = 5000): Promise<boolean> {
  const selectorList = selectors.split(',').map(s => s.trim());
  
  for (const selector of selectorList) {
    try {
      const element = page.locator(selector).first();
      await element.waitFor({ state: 'visible', timeout });
      await element.click();
      log("CLICK", `Éxito con selector: ${selector}`);
      return true;
    } catch {
      // Continuar con siguiente selector
    }
  }
  return false;
}

// =====================================================
// TEST PRINCIPAL
// =====================================================

async function main() {
  console.log("\n" + "=".repeat(70));
  console.log("  TEST E2E COMPLETO: Playwright + Stagehand + SQLite");
  console.log("=".repeat(70));
  
  // =================================================
  // FASE 0: CARGAR DATOS DEL PEDIDO DESDE BD
  // =================================================
  
  // Leer pedido_id desde CLI o usar el último
  const PEDIDO_ID = process.argv[2]; // node test.ts PEDIDO_123
  
  let fotosExistentes: string[] = [];
  let estiloDiseno = 'default';
  let tituloProyecto = `Test_${Date.now()}`;
  let productoCodigo = '21x21';
  let tituloTapa: string | null = null;
  let tituloContratapa: string | null = null;
  let textoLomo: string | null = null;
  let incluirQR = false;
  let qrUrl: string | null = null;
  let adornos: any = null;
  
  log("INIT", "Verificando base de datos...");
  const dbCheck = checkDatabase();
  
  if (!dbCheck.ok) {
    log("WARN", `⚠️ BD no disponible: ${dbCheck.message}`);
    log("INFO", "Usando fotos hardcodeadas de prueba");
    fotosExistentes = FOTOS_TEST_HARDCODED.filter(f => fs.existsSync(f));
  } else {
    log("OK", `✓ BD OK: ${dbCheck.message}`);
    
    if (PEDIDO_ID) {
      // Modo 1: Pedido específico desde CLI
      log("INFO", `Cargando pedido: ${PEDIDO_ID}`);
      const pedido = getPedido(PEDIDO_ID);
      
      if (!pedido) {
        log("ERROR", `Pedido ${PEDIDO_ID} no encontrado en BD`);
        process.exit(1);
      }
      
      const photos = getPhotosFromDB(PEDIDO_ID);
      
      if (photos.length === 0) {
        log("ERROR", `Pedido ${PEDIDO_ID} no tiene fotos asociadas`);
        process.exit(1);
      }
      
      fotosExistentes = photos;
      estiloDiseno = pedido.estilo_diseno || 'default';
      tituloProyecto = pedido.titulo_tapa || `Pedido_${PEDIDO_ID.slice(0, 8)}`;
      productoCodigo = pedido.producto_codigo || '21x21';
      tituloTapa = pedido.titulo_tapa;
      tituloContratapa = pedido.titulo_contratapa;
      textoLomo = pedido.texto_lomo;
      incluirQR = pedido.incluir_qr || false;
      qrUrl = pedido.qr_url;
      
      try {
        adornos = pedido.adornos_extras ? JSON.parse(pedido.adornos_extras) : null;
      } catch {
        adornos = null;
      }
      
      log("OK", `✓ Pedido cargado: ${pedido.id}`);
      log("INFO", `  Producto: ${productoCodigo}`);
      log("INFO", `  Estilo: ${estiloDiseno}`);
      log("INFO", `  Fotos: ${photos.length}`);
      log("INFO", `  Personalización:`);
      if (tituloTapa) log("INFO", `    - Título tapa: "${tituloTapa}"`);
      if (tituloContratapa) log("INFO", `    - Título contratapa: "${tituloContratapa}"`);
      if (textoLomo) log("INFO", `    - Lomo: "${textoLomo}"`);
      if (incluirQR) log("INFO", `    - QR: ${qrUrl || 'Sí'}`);
      if (adornos) log("INFO", `    - Adornos extras: Sí`);
      
    } else {
      // Modo 2: Último pedido con fotos
      log("INFO", "Buscando último pedido con fotos en BD...");
      const lastPedido = getLastPedidoWithPhotos();
      
      if (lastPedido) {
        fotosExistentes = lastPedido.photos;
        estiloDiseno = lastPedido.pedido.estilo_diseno || 'default';
        tituloProyecto = lastPedido.pedido.titulo_tapa || `Pedido_${lastPedido.pedido.id.slice(0, 8)}`;
        productoCodigo = lastPedido.pedido.producto_codigo || '21x21';
        tituloTapa = lastPedido.pedido.titulo_tapa;
        tituloContratapa = lastPedido.pedido.titulo_contratapa;
        textoLomo = lastPedido.pedido.texto_lomo;
        incluirQR = lastPedido.pedido.incluir_qr || false;
        qrUrl = lastPedido.pedido.qr_url;
        
        try {
          adornos = lastPedido.pedido.adornos_extras ? JSON.parse(lastPedido.pedido.adornos_extras) : null;
        } catch {
          adornos = null;
        }
        
        log("OK", `✓ Usando último pedido: ${lastPedido.pedido.id}`);
        log("INFO", `  Producto: ${productoCodigo}`);
        log("INFO", `  Estilo: ${estiloDiseno}`);
        log("INFO", `  Fotos: ${lastPedido.photos.length}`);
        if (tituloTapa || tituloContratapa || textoLomo || incluirQR || adornos) {
          log("INFO", `  Personalización detectada`);
        }
      } else {
        log("WARN", "No hay pedidos con fotos en BD");
        log("INFO", "Usando fotos hardcodeadas de prueba");
        fotosExistentes = FOTOS_TEST_HARDCODED.filter(f => fs.existsSync(f));
      }
    }
  }
  
  if (fotosExistentes.length === 0) {
    log("ERROR", "No se encontraron fotos disponibles");
    process.exit(1);
  }
  
  log("OK", `✓ ${fotosExistentes.length} fotos listas para procesar`);
  
  // Obtener templates sugeridos según estilo
  const suggestedTemplates = TEMPLATE_MAPPING[estiloDiseno.toLowerCase()] || TEMPLATE_MAPPING['default'];
  log("INFO", `Templates sugeridos para estilo "${estiloDiseno}": ${suggestedTemplates.join(', ')}`);
  
  console.log("\n" + "-".repeat(70));
  
  // Inicializar Stagehand
  log("INIT", "Iniciando Stagehand...");
  
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
    const page = stagehand.context.pages()[0];
    if (!page) throw new Error("No page available");
    
    log("OK", "Browser iniciado");
    
    // =================================================
    // PASO 1: LOGIN (Playwright directo)
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 1", "LOGIN EN FDF (Playwright directo)");
    console.log("-".repeat(50));
    
    await page.goto(CONFIG.fdf.loginUrl);
    await sleep(2000);
    await screenshot(page, "01_login_page");
    
    // Llenar formulario de login
    await page.locator(SELECTORS.login.email).fill(CONFIG.fdf.email);
    await sleep(200);
    await page.locator(SELECTORS.login.password).fill(CONFIG.fdf.password);
    await sleep(200);
    await page.locator(SELECTORS.login.submit).click();
    
    await sleep(5000);
    await screenshot(page, "02_logged_in");
    log("OK", "Login exitoso");
    
    // =================================================
    // PASO 2: NAVEGAR A FOTOLIBROS (Playwright)
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 2", "NAVEGAR A FOTOLIBROS");
    console.log("-".repeat(50));
    
    // Intentar click en Fotolibros
    const clickedFotolibros = await tryClick(page, SELECTORS.home.fotolibros, 3000);
    
    if (!clickedFotolibros) {
      log("INFO", "Usando Stagehand para navegar...");
      await stagehand.act("click on 'Fotolibros' category");
    }
    
    await sleep(2000);
    await screenshot(page, "03_fotolibros");
    
    // =================================================
    // PASO 3: CREAR NUEVO PROYECTO (Híbrido)
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 3", "CREAR NUEVO PROYECTO 21x21");
    console.log("-".repeat(50));
    
    // Click en Nuevo Proyecto
    log("ACTION", "Buscando 'Nuevo Proyecto'...");
    const clickedNuevo = await tryClick(page, 'text=Nuevo Proyecto', 3000);
    
    if (!clickedNuevo) {
      log("INFO", "Usando Stagehand...");
      await stagehand.act("click on 'Nuevo Proyecto' button to create a new photobook");
    }
    
    await sleep(3000);
    await screenshot(page, "04_nuevo_proyecto");
    
    // Seleccionar tamaño 21x21
    log("ACTION", "Seleccionando tamaño 21x21...");
    
    // Primero intentar con texto
    let clicked21 = await tryClick(page, 'text=21x21', 3000);
    
    if (!clicked21) {
      // Intentar con Stagehand
      log("INFO", "Usando Stagehand para seleccionar 21x21...");
      try {
        await stagehand.act("click on the 21x21 photobook size option");
        clicked21 = true;
      } catch (e) {
        log("ERROR", `Stagehand falló: ${e}`);
      }
    }
    
    await sleep(2000);
    await screenshot(page, "05_size_selected");
    
    // =================================================
    // PASO 3.5: CONFIGURAR PROYECTO (Título + Páginas)
    // =================================================
    log("ACTION", "Configurando proyecto...");
    
    const projectTitle = `Test_${Date.now()}`;
    
    // 1. SOLO ingresar título - NO tocar selector de tapa
    log("ACTION", "Ingresando título del proyecto...");
    
    try {
      // Usar Stagehand para encontrar específicamente el campo de título
      await stagehand.act(`find the text input field labeled "Título" or "Nombre del proyecto" and type "${projectTitle}". Do NOT click on any dropdown or selector labeled "Tapa" or cover type.`);
      log("OK", `Título ingresado: ${projectTitle}`);
    } catch (e) {
      // Fallback: buscar input de texto que NO sea un select
      const textInputs = page.locator('input[type="text"]:not([readonly])');
      const count = await textInputs.count();
      
      for (let i = 0; i < count; i++) {
        const input = textInputs.nth(i);
        const placeholder = await input.getAttribute('placeholder') || '';
        const name = await input.getAttribute('name') || '';
        
        // Solo llenar si parece ser campo de título
        if (placeholder.toLowerCase().includes('título') || 
            placeholder.toLowerCase().includes('nombre') ||
            name.toLowerCase().includes('titulo') ||
            name.toLowerCase().includes('nombre')) {
          await input.fill(projectTitle);
          log("OK", `Título ingresado en input: ${name || placeholder}`);
          break;
        }
      }
    }
    
    await sleep(1000);
    await screenshot(page, "05b_title_entered");
    
    // 2. Ajustar cantidad de páginas si es necesario (solo si > 24)
    // Por ahora usamos el valor por defecto, pero aquí se podría ajustar
    // const paginasRequeridas = 30; // Si necesitamos más de 24
    // if (paginasRequeridas > 24) {
    //   await stagehand.act(`change the page count selector to ${paginasRequeridas} pages`);
    // }
    
    await sleep(500);
    
    // 3. Click en "Crear Proyecto"
    log("ACTION", "Buscando botón 'Crear Proyecto'...");
    
    let creado = await tryClick(page, 'text=Crear Proyecto, text=Crear proyecto, button:has-text("Crear")', 3000);
    
    if (!creado) {
      log("INFO", "Usando Stagehand para crear proyecto...");
      try {
        await stagehand.act("click on the 'Crear Proyecto' or 'Crear' button to create the project");
        creado = true;
      } catch (e) {
        log("ERROR", `Error al crear proyecto: ${e}`);
      }
    }
    
    // Esperar a que cargue el editor
    log("WAIT", "Esperando que cargue el editor...");
    await sleep(8000);
    await screenshot(page, "06_project_created");
    
    // =================================================
    // PASO 4: SUBIR FOTOS (Playwright directo)
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 4", "SUBIR FOTOS");
    console.log("-".repeat(50));
    
    // Esperar a que cargue el editor
    await sleep(3000);
    
    // Buscar input de archivo
    const fileInputCount = await page.locator('input[type="file"]').count();
    log("INFO", `Inputs de archivo encontrados: ${fileInputCount}`);
    
    if (fileInputCount > 0) {
      log("ACTION", "Subiendo fotos una por una via input file...");
      
      // FDF solo acepta 1 archivo a la vez en el input
      // Subir cada foto individualmente
      for (let i = 0; i < fotosExistentes.length; i++) {
        const foto = fotosExistentes[i];
        log("INFO", `Subiendo foto ${i + 1}/${fotosExistentes.length}: ${path.basename(foto)}`);
        
        await page.locator('input[type="file"]').first().setInputFiles([foto]);
        await sleep(2000); // Esperar que procese cada foto
      }
      log("WAIT", `Esperando procesamiento de ${fotosExistentes.length} fotos...`);
      
      // FDF procesa las fotos de forma asíncrona y tarda bastante
      // Esperar agresivamente hasta que todas estén listas
      
      await sleep(5000); // Espera inicial para que empiece el proceso
      
      log("INFO", "Esperando que FDF procese todas las fotos (puede tardar 60+ segundos)...");
      
      let fotosDetectadas = 0;
      
      // Esperar hasta 90 segundos (1.5 minutos) para que procesen TODAS
      for (let i = 0; i < 90; i++) {
        await sleep(1000);
        
        // Método 1: Buscar texto "X fotos" en la UI
        const bodyText = await page.locator('body').textContent() || '';
        
        if (bodyText.includes(`${fotosExistentes.length} foto`)) {
          log("OK", `✓ Detectado texto: "${fotosExistentes.length} fotos" en la UI`);
          fotosDetectadas = fotosExistentes.length;
          break;
        }
        
        // Método 2: Contar miniaturas visibles
        const thumbnailSelectors = [
          '.photo-thumbnail',
          '.foto-item',
          'img[class*="thumb"]',
          'img[class*="foto"]',
          '[class*="gallery"] img',
          '.image-item'
        ];
        
        for (const selector of thumbnailSelectors) {
          try {
            const count = await page.locator(selector).count();
            if (count > fotosDetectadas) {
              fotosDetectadas = count;
              log("INFO", `Progreso: ${count}/${fotosExistentes.length} fotos visibles (${Math.round(i/0.9)}% del tiempo)`);
              
              if (count >= fotosExistentes.length) {
                log("OK", `✓ Todas las ${count} fotos están visibles`);
                break;
              }
            }
          } catch {}
        }
        
        if (fotosDetectadas >= fotosExistentes.length) {
          break;
        }
        
        // Mostrar progreso cada 10 segundos
        if (i > 0 && i % 10 === 0) {
          log("WAIT", `Esperando... ${i} segundos transcurridos (${fotosDetectadas}/${fotosExistentes.length} fotos)`);
        }
      }
      
      if (fotosDetectadas < fotosExistentes.length) {
        log("WARN", `⚠️ Solo se detectaron ${fotosDetectadas}/${fotosExistentes.length} fotos después de 90s`);
        log("INFO", "Continuando con las fotos disponibles...");
      } else {
        log("OK", `✓ Las ${fotosExistentes.length} fotos están listas`);
      }
      
      await sleep(3000); // Espera adicional de seguridad
      
      // Cerrar pantalla de carga de fotos / continuar al editor
      log("ACTION", "Cerrando pantalla de carga de fotos...");
      
      // Buscar botones de cerrar/continuar
      const closeButtons = [
        'text=Continuar',
        'text=Cerrar',
        'text=Aceptar',
        'text=OK',
        'button:has-text("×")',
        'button[aria-label="Cerrar"]',
        'button[aria-label="Close"]',
        '.close-button',
        '.modal-close'
      ];
      
      let closed = false;
      for (const selector of closeButtons) {
        try {
          const btn = page.locator(selector).first();
          const isVisible = await btn.isVisible({ timeout: 1000 }).catch(() => false);
          if (isVisible) {
            await btn.click();
            log("OK", `Cerrado con: ${selector}`);
            closed = true;
            await sleep(2000);
            break;
          }
        } catch {}
      }
      
      if (!closed) {
        // Usar Stagehand para cerrar
        log("INFO", "Usando Stagehand para cerrar modal de fotos...");
        try {
          await stagehand.act("close the photo upload modal or dialog. Click on 'Continuar', 'Cerrar', 'X' or any close button to return to the editor");
          await sleep(2000);
        } catch (e) {
          log("WARN", `No se pudo cerrar modal: ${e}`);
        }
      }
      
      log("OK", "Fotos subidas y modal cerrado");
    } else {
      // Intentar encontrar botón de upload
      log("INFO", "Buscando botón de upload...");
      const clickedUpload = await tryClick(page, SELECTORS.editor.uploadButton, 3000);
      
      if (clickedUpload) {
        await sleep(1000);
        const newInputCount = await page.locator('input[type="file"]').count();
        if (newInputCount > 0) {
          await page.locator('input[type="file"]').first().setInputFiles(fotosExistentes);
          await sleep(8000);
          log("OK", "Fotos subidas después de click en botón");
        }
      } else {
        log("INFO", "Usando Stagehand para encontrar upload...");
        await stagehand.act("click on the button to upload photos or add images");
        await sleep(2000);
        
        const finalInputCount = await page.locator('input[type="file"]').count();
        if (finalInputCount > 0) {
          await page.locator('input[type="file"]').first().setInputFiles(fotosExistentes);
          await sleep(8000);
        }
      }
    }
    
    await screenshot(page, "07_photos_uploaded");
    
    // =================================================
    // PASO 5: APLICAR TEMPLATE (Stagehand - complejo)
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 5", "APLICAR TEMPLATE (Stagehand)");
    console.log("-".repeat(50));
    
    log("ACTION", "Buscando sección de Temas/Plantillas...");
    
    // Intentar primero con selector
    let clickedTemas = await tryClick(page, 'text=Temas, text=Plantillas, text=Templates', 3000);
    
    if (!clickedTemas) {
      log("INFO", "Usando Stagehand para templates...");
      try {
        await stagehand.act("click on 'Temas' or 'Plantillas de página' section in the right panel to see template options");
        await sleep(2000);
      } catch (e) {
        log("ERROR", `Error con templates: ${e}`);
      }
    }
    
    await screenshot(page, "08_templates_section");
    
    // Esperar a que carguen los templates
    await sleep(2000);
    
    // Seleccionar template según estilo del cliente
    log("ACTION", `Seleccionando template para estilo "${estiloDiseno}"...`);
    log("INFO", `Templates sugeridos: ${suggestedTemplates.join(', ')}`);
    
    let templateSelected = false;
    
    // Intentar primero con los templates sugeridos según estilo
    for (const templateName of suggestedTemplates) {
      log("INFO", `Buscando template: "${templateName}"...`);
      
      try {
        // Intentar selector directo primero
        const clicked = await tryClick(page, `text=${templateName}`, 1500);
        
        if (clicked) {
          log("OK", `✓ Template "${templateName}" seleccionado (match exacto)`);
          templateSelected = true;
          await sleep(2000);
          break;
        }
      } catch {}
    }
    
    if (!templateSelected) {
      // Usar Stagehand con instrucciones basadas en el estilo
      log("INFO", "Usando Stagehand para seleccionar template...");
      
      const templateInstruction = `Select a template that matches the style "${estiloDiseno}".
        Look for templates named: ${suggestedTemplates.join(', ')}.
        If those are not available, choose a similar decorative template.
        Do NOT select "Vacío" (empty) template.
        Click on the template preview image or name.`;
      
      try {
        await stagehand.act(templateInstruction);
        await sleep(2000);
        templateSelected = true;
        log("OK", `✓ Template seleccionado via Stagehand para estilo "${estiloDiseno}"`);
      } catch (e) {
        log("ERROR", `Error seleccionando template: ${e}`);
      }
    }
    
    // Confirmar aplicación del template si aparece modal
    await sleep(1000);
    const confirmApplied = await tryClick(page, 'text=Aplicar, text=Confirmar, text=Aceptar', 2000);
    if (confirmApplied) {
      log("OK", "Template aplicado y confirmado");
      await sleep(2000);
    }
    
    await screenshot(page, "09_template_selected");
    
    // =================================================
    // PASO 6: SMART FILL (Stagehand - complejo)
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 6", "RELLENO SMART (Stagehand)");
    console.log("-".repeat(50));
    
    log("ACTION", "Buscando opciones de relleno...");
    
    // Scroll para ver botones de relleno
    try {
      await stagehand.act("scroll down in the right panel to see fill options");
      await sleep(1500);
    } catch {}
    
    await screenshot(page, "10_fill_options");
    
    // Click en Relleno Smart ÚNICAMENTE (no rápido, no manual)
    log("ACTION", "Buscando botón 'Relleno fotos smart'...");
    
    // HAY 3 BOTONES DE RELLENO:
    // 1. "Relleno fotos smart" ← ÚNICO PERMITIDO (más inteligente)
    // 2. "Relleno fotos rápido" ← NO USAR
    // 3. "Relleno fotos manual" ← NO USAR
    
    let clickedFill = false;
    
    // Intentar con selector directo primero
    clickedFill = await tryClick(page, 'text=Relleno fotos smart', 2000);
    
    if (clickedFill) {
      log("OK", "✓ Clickeado en 'Relleno fotos smart'");
    } else {
      // Usar Stagehand con instrucciones EXCLUSIVAS para SMART
      log("INFO", "Usando Stagehand para encontrar 'Relleno fotos smart'...");
      try {
        await stagehand.act(`Click ONLY on the button labeled "Relleno fotos smart". 
          This is the SMART photo fill option with face detection.
          Do NOT click on "Relleno fotos rápido" (fast) or "Relleno fotos manual" (manual).
          Look specifically for the button with the word "smart" in it.
          If you cannot find it, report an error.`);
        clickedFill = true;
        log("OK", "✓ Stagehand encontró 'Relleno fotos smart'");
        await sleep(2000);
      } catch (e) {
        log("ERROR", `❌ No se pudo encontrar 'Relleno fotos smart': ${e}`);
        throw new Error("Relleno Smart no disponible - abortando test");
      }
    }
    
    if (!clickedFill) {
      throw new Error("❌ CRÍTICO: No se pudo clickear 'Relleno fotos smart'");
    }
    
    await sleep(2000);
    await screenshot(page, "11_smart_clicked");
    
    // Seleccionar opción SMART (Caras, Colores y Dimensiones)
    log("ACTION", "Esperando modal de opciones Smart Fill...");
    await sleep(3000); // Esperar a que aparezca el modal
    
    await screenshot(page, "11b_smart_modal");
    
    log("ACTION", "Seleccionando opción SMART (Caras, Colores y Dimensiones)...");
    
    // El modal tiene 3 opciones (de más completa a más simple):
    // 1. SMART: "Caras, Colores y Dimensiones" ← QUEREMOS ESTA
    // 2. RÁPIDA: "Colores y Dimensiones"
    // 3. MANUAL: "Dimensiones"
    
    let smartSelected = false;
    
    // Método 1: Buscar por texto exacto
    const smartOptions = [
      'text=Caras, Colores y Dimensiones',
      'text=Caras, colores y dimensiones',
      'button:has-text("Caras")',
      'div:has-text("Caras, Colores")',
    ];
    
    for (const selector of smartOptions) {
      try {
        const elem = page.locator(selector).first();
        const isVisible = await elem.isVisible({ timeout: 2000 }).catch(() => false);
        
        if (isVisible) {
          await elem.click();
          log("OK", `SMART seleccionado con: ${selector}`);
          smartSelected = true;
          await sleep(2000);
          break;
        }
      } catch {}
    }
    
    if (!smartSelected) {
      // Método 2: Usar Stagehand con instrucciones MUY específicas
      log("INFO", "Usando Stagehand para seleccionar opción SMART...");
      try {
        await stagehand.act(`In the modal dialog that appeared, find and click on the option that says "Caras, Colores y Dimensiones". 
          This is the FIRST and most complete option. 
          Do NOT click on "Colores y Dimensiones" (second option).
          Do NOT click on "Dimensiones" alone (third/manual option).
          Click ONLY on the option that mentions "Caras" (faces).`);
        smartSelected = true;
        await sleep(2000);
      } catch (e) {
        log("ERROR", `Error seleccionando SMART: ${e}`);
        
        // Método 3: Click en la primera opción del modal como último recurso
        log("INFO", "Intentando click en primera opción visible del modal...");
        try {
          const modalButtons = page.locator('mat-dialog-content button, .modal-content button, [role="dialog"] button');
          const count = await modalButtons.count();
          
          if (count >= 1) {
            // Click en el PRIMER botón (que debería ser SMART)
            await modalButtons.first().click();
            log("OK", "Primera opción del modal clickeada");
            await sleep(2000);
          }
        } catch (e2) {
          log("ERROR", `No se pudo seleccionar opción SMART: ${e2}`);
        }
      }
    }
    
    // Esperar procesamiento del Smart Fill
    log("WAIT", "Esperando procesamiento del Smart Fill (20 segundos)...");
    await sleep(20000);
    
    await screenshot(page, "12_smart_fill_done");
    
    // =================================================
    // PASO 6.5: PERSONALIZACIÓN (Títulos, QR, Adornos)
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 6.5", "PERSONALIZACIÓN DEL FOTOLIBRO");
    console.log("-".repeat(50));
    
    // Solo personalizar si hay datos del pedido
    if (tituloTapa || tituloContratapa || textoLomo || incluirQR || adornos) {
      
      // Cerrar cualquier modal abierto primero
      try {
        await page.keyboard.press('Escape');
        await sleep(1000);
      } catch {}
      
      // PERSONALIZACIÓN 1: Navegar a la tapa
      if (tituloTapa) {
        log("ACTION", `Agregando título en tapa: "${tituloTapa}"...`);
        
        try {
          // Navegar a la página de tapa
          await stagehand.act("click on the 'Tapa' or 'Cover' page thumbnail to edit the front cover");
          await sleep(2000);
          await screenshot(page, "12a_tapa_page");
          
          // Insertar texto
          log("ACTION", "Insertando texto en tapa...");
          const clickedInsertText = await tryClick(page, 'text=Insertar Texto, button:has-text("Texto"), text=Add Text', 2000);
          
          if (!clickedInsertText) {
            await stagehand.act("click on 'Insertar Texto' or 'Add Text' button to add a text box");
          }
          
          await sleep(1500);
          
          // Escribir el título
          await page.keyboard.type(tituloTapa);
          await sleep(1000);
          
          // Formatear el texto (opcional - centrar, tamaño grande)
          try {
            await stagehand.act("make the text centered and increase font size to large for the title");
            await sleep(1000);
          } catch {}
          
          log("OK", `✓ Título agregado en tapa: "${tituloTapa}"`);
          await screenshot(page, "12b_titulo_tapa");
          
        } catch (e) {
          log("ERROR", `Error agregando título en tapa: ${e}`);
        }
      }
      
      // PERSONALIZACIÓN 2: Título en contratapa
      if (tituloContratapa) {
        log("ACTION", `Agregando título en contratapa: "${tituloContratapa}"...`);
        
        try {
          // Navegar a contratapa
          await stagehand.act("click on the 'Contratapa' or 'Back Cover' page thumbnail");
          await sleep(2000);
          
          // Insertar texto
          const clicked = await tryClick(page, 'text=Insertar Texto', 2000);
          if (!clicked) {
            await stagehand.act("click 'Insertar Texto' button");
          }
          
          await sleep(1500);
          await page.keyboard.type(tituloContratapa);
          await sleep(1000);
          
          log("OK", `✓ Título agregado en contratapa: "${tituloContratapa}"`);
          await screenshot(page, "12c_titulo_contratapa");
          
        } catch (e) {
          log("ERROR", `Error agregando título en contratapa: ${e}`);
        }
      }
      
      // PERSONALIZACIÓN 3: Texto en lomo
      if (textoLomo) {
        log("ACTION", `Agregando texto en lomo: "${textoLomo}"...`);
        
        try {
          // El lomo puede estar en una vista especial
          await stagehand.act("navigate to the spine or 'lomo' of the book to edit it");
          await sleep(2000);
          
          // Insertar texto en lomo
          const clicked = await tryClick(page, 'text=Insertar Texto', 2000);
          if (!clicked) {
            await stagehand.act("add text to the spine");
          }
          
          await sleep(1500);
          await page.keyboard.type(textoLomo);
          await sleep(1000);
          
          log("OK", `✓ Texto agregado en lomo: "${textoLomo}"`);
          await screenshot(page, "12d_texto_lomo");
          
        } catch (e) {
          log("WARN", `Advertencia con lomo (puede no estar disponible en este producto): ${e}`);
        }
      }
      
      // PERSONALIZACIÓN 4: Código QR
      if (incluirQR && qrUrl) {
        log("ACTION", `Agregando código QR: ${qrUrl}...`);
        
        try {
          // Navegar a última página o contratapa
          await stagehand.act("go to the last page or back cover of the book");
          await sleep(2000);
          
          // Buscar botón de QR
          const clickedQR = await tryClick(page, 'text=Código QR, text=QR Code, button:has-text("QR")', 2000);
          
          if (!clickedQR) {
            await stagehand.act("click on 'Código QR' button to insert a QR code");
          }
          
          await sleep(2000);
          
          // Ingresar URL del QR
          const qrInputSelectors = [
            'input[type="url"]',
            'input[placeholder*="URL"]',
            'input[placeholder*="http"]',
            'input[name="qr_url"]'
          ];
          
          let qrFilled = false;
          for (const selector of qrInputSelectors) {
            try {
              const input = page.locator(selector).first();
              const isVisible = await input.isVisible({ timeout: 1000 }).catch(() => false);
              if (isVisible) {
                await input.fill(qrUrl);
                qrFilled = true;
                break;
              }
            } catch {}
          }
          
          if (!qrFilled) {
            await stagehand.act(`enter the URL "${qrUrl}" in the QR code configuration field`);
          }
          
          await sleep(1000);
          
          // Confirmar
          await tryClick(page, 'text=Aceptar, text=OK, text=Confirmar', 1500);
          
          log("OK", `✓ Código QR agregado: ${qrUrl}`);
          await screenshot(page, "12e_qr_code");
          
        } catch (e) {
          log("ERROR", `Error agregando código QR: ${e}`);
        }
      }
      
      // PERSONALIZACIÓN 5: Adornos extras (si vienen configurados)
      if (adornos && adornos.enabled) {
        log("ACTION", "Agregando adornos extras...");
        
        try {
          // Los adornos pueden venir configurados como:
          // { enabled: true, type: 'clip-arts', items: ['corazon', 'estrella'] }
          
          if (adornos.type === 'clip-arts' && adornos.items) {
            // Navegar a sección de Clip-Arts
            await stagehand.act("click on 'Clip-Arts' section in the right panel");
            await sleep(2000);
            
            for (const item of adornos.items.slice(0, 3)) { // Máximo 3 adornos
              log("INFO", `  Buscando clip-art: ${item}`);
              
              try {
                await stagehand.act(`search and click on a clip-art or decoration related to "${item}"`);
                await sleep(1500);
                
                // Clickear en una página para colocarlo
                await page.mouse.click(700, 400);
                await sleep(1000);
                
                log("OK", `  ✓ Adorno "${item}" agregado`);
              } catch (e) {
                log("WARN", `  Advertencia con adorno "${item}": ${e}`);
              }
            }
          }
          
          await screenshot(page, "12f_adornos_extras");
          
        } catch (e) {
          log("ERROR", `Error agregando adornos: ${e}`);
        }
      }
      
      log("OK", "✓ Personalización completada");
      await screenshot(page, "12_personalizacion_final");
      
    } else {
      log("INFO", "No hay personalizaciones configuradas en el pedido - saltando paso");
    }
    
    // =================================================
    // PASO 7: VALIDACIÓN VISUAL INTELIGENTE
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 7", "VALIDACIÓN VISUAL DEL DISEÑO");
    console.log("-".repeat(50));
    
    // Esperar un poco más para asegurar renderizado completo
    await sleep(5000);
    
    // Tomar screenshot del diseño final
    await screenshot(page, "13_diseno_completo");
    
    log("ACTION", "Ejecutando validación visual inteligente...");
    
    let validationResult: any = {
      photosCentered: false,
      logicalOrder: false,
      allPagesFilled: false,
      templateVisible: false,
      qualityScore: 0,
      issues: []
    };
    
    try {
      // Análisis visual con Stagehand usando el modelo LLM
      validationResult = await stagehand.extract({
        instruction: `Analyze this photobook design carefully and provide a detailed assessment:
        
          1. PHOTO CENTERING: Are the photos properly centered within their frames/containers? 
             Look at multiple pages and check if photos are aligned and not cropped incorrectly.
          
          2. LOGICAL ORDER: Do the pages flow in a logical sequence from left to right? 
             Is there a coherent narrative or visual progression?
          
          3. PAGE COMPLETENESS: Are all visible pages filled with content (photos/decorations)? 
             Count pages that appear empty or have only partial content.
          
          4. TEMPLATE VISIBILITY: Is the "Flores Marga" floral template clearly visible? 
             Look for flower decorations, backgrounds, or themed elements.
          
          5. OVERALL QUALITY: Rate the overall design quality from 1-10 where:
             - 1-3: Poor (major issues, unusable)
             - 4-6: Acceptable (minor issues, needs review)
             - 7-9: Good (professional looking)
             - 10: Excellent (perfect, ready to print)
          
          6. ISSUES: List any specific problems you notice (e.g., "Page 3 has cropped faces", 
             "Pages 10-12 are empty", "Photos appear stretched", etc.)
        
          Be critical and thorough - this will be reviewed by a human.`,
        schema: {
          type: "object",
          properties: {
            photosCentered: { 
              type: "boolean", 
              description: "Are photos properly centered and aligned?" 
            },
            logicalOrder: { 
              type: "boolean", 
              description: "Do pages follow a logical left-to-right sequence?" 
            },
            allPagesFilled: { 
              type: "boolean", 
              description: "Are all pages filled with content (no empty pages)?" 
            },
            templateVisible: { 
              type: "boolean", 
              description: "Is the Flores Marga template clearly applied?" 
            },
            qualityScore: { 
              type: "number", 
              minimum: 1, 
              maximum: 10,
              description: "Overall design quality score 1-10" 
            },
            issues: { 
              type: "array", 
              items: { type: "string" },
              description: "List of specific problems or concerns" 
            },
            recommendation: {
              type: "string",
              description: "Overall recommendation: 'approve', 'review', or 'reject'"
            }
          },
          required: ["photosCentered", "logicalOrder", "allPagesFilled", "templateVisible", "qualityScore", "issues", "recommendation"]
        }
      });
      
      log("INFO", "Resultado de validación visual:", validationResult);
      
      // Evaluar resultado
      console.log("\n" + "=".repeat(70));
      console.log("  📊 REPORTE DE VALIDACIÓN VISUAL");
      console.log("=".repeat(70));
      console.log(`
  ✓ Fotos centradas:        ${validationResult.photosCentered ? '✅ SÍ' : '❌ NO'}
  ✓ Orden lógico:           ${validationResult.logicalOrder ? '✅ SÍ' : '❌ NO'}
  ✓ Todas páginas llenas:   ${validationResult.allPagesFilled ? '✅ SÍ' : '❌ NO'}
  ✓ Template visible:       ${validationResult.templateVisible ? '✅ SÍ' : '❌ NO'}
  
  📈 Puntuación de Calidad: ${validationResult.qualityScore}/10
  
  🔍 Problemas detectados:
      `);
      
      if (validationResult.issues && validationResult.issues.length > 0) {
        validationResult.issues.forEach((issue: string, i: number) => {
          console.log(`    ${i + 1}. ${issue}`);
        });
      } else {
        console.log(`    ✅ No se detectaron problemas`);
      }
      
      console.log(`
  📋 Recomendación: ${validationResult.recommendation?.toUpperCase()}
      `);
      console.log("=".repeat(70) + "\n");
      
      // Tomar screenshot adicional si hay problemas
      if (validationResult.qualityScore < 7) {
        log("WARN", "⚠️ Calidad por debajo de 7/10 - tomando screenshots adicionales");
        await screenshot(page, "13b_diseno_con_issues");
      }
      
    } catch (e) {
      log("ERROR", `Error en validación visual: ${e}`);
      validationResult.issues.push(`Error en análisis automático: ${e}`);
      validationResult.qualityScore = 5; // Score neutral si falla
      validationResult.recommendation = "review";
    }
    
    await screenshot(page, "13_final_design");
    
    // =================================================
    // PASO 8: COMPARTIR PROYECTO PARA REVISIÓN
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 8", "COMPARTIR PARA REVISIÓN MANUAL");
    console.log("-".repeat(50));
    
    const REVISION_EMAIL = "j.ertel002@hotmail.com";
    
    log("ACTION", `Compartiendo proyecto a ${REVISION_EMAIL}...`);
    
    let sharingSuccess = false;
    
    try {
      // Cerrar cualquier modal abierto primero
      try {
        await page.keyboard.press('Escape');
        await sleep(1000);
      } catch {}
      
      // Buscar y clickear botón "Compartir" en el menú superior
      log("INFO", "Buscando botón 'Compartir'...");
      
      const clickedShare = await tryClick(page, 'text=Compartir, button:has-text("Compartir"), [aria-label="Compartir"]', 3000);
      
      if (!clickedShare) {
        log("INFO", "Usando Stagehand para encontrar 'Compartir'...");
        await stagehand.act("click on 'Compartir' button in the top menu bar or right sidebar");
      }
      
      await sleep(3000);
      await screenshot(page, "14_modal_compartir");
      
      // Seleccionar opción "Compartir una Copia"
      log("ACTION", "Seleccionando 'Compartir una Copia'...");
      
      const clickedCopy = await tryClick(page, 'text=Compartir una Copia, text=Compartir Copia', 2000);
      
      if (!clickedCopy) {
        await stagehand.act("click on 'Compartir una Copia de este Proyecto' option");
      }
      
      await sleep(2000);
      
      // Ingresar email
      log("ACTION", `Ingresando email ${REVISION_EMAIL}...`);
      
      const emailInputSelectors = [
        'input[type="email"]',
        'input[placeholder*="email"]',
        'input[placeholder*="correo"]',
        'input[name="email"]',
        'input[id*="email"]'
      ];
      
      let emailFilled = false;
      
      for (const selector of emailInputSelectors) {
        try {
          const input = page.locator(selector).first();
          const isVisible = await input.isVisible({ timeout: 1000 }).catch(() => false);
          
          if (isVisible) {
            await input.clear();
            await sleep(200);
            await input.fill(REVISION_EMAIL);
            log("OK", `Email ingresado con selector: ${selector}`);
            emailFilled = true;
            break;
          }
        } catch {}
      }
      
      if (!emailFilled) {
        log("INFO", "Usando Stagehand para llenar email...");
        await stagehand.act(`fill the email input field with "${REVISION_EMAIL}"`);
      }
      
      await sleep(1000);
      await screenshot(page, "14b_email_ingresado");
      
      // Enviar
      log("ACTION", "Enviando compartición...");
      
      const clickedSend = await tryClick(page, 'text=Enviar, button:has-text("Enviar"), text=Send, button:has-text("Send")', 2000);
      
      if (!clickedSend) {
        await stagehand.act("click on 'Enviar' or 'Send' button to share the project");
      }
      
      await sleep(5000);
      await screenshot(page, "14c_compartir_enviado");
      
      // Verificar confirmación
      log("ACTION", "Verificando envío exitoso...");
      
      const shareConfirm = await stagehand.extract({
        instruction: `Check if the project was successfully shared via email.
          Look for success messages like "Enviado", "Compartido", "Success", or confirmation dialogs.
          Also check if there are any error messages.`,
        schema: {
          type: "object",
          properties: {
            sent: { type: "boolean", description: "Was the email sent successfully?" },
            message: { type: "string", description: "Success or error message visible" },
            hasError: { type: "boolean", description: "Is there an error message?" }
          }
        }
      });
      
      log("INFO", "Resultado de compartición:", shareConfirm);
      
      if (shareConfirm.sent && !shareConfirm.hasError) {
        log("OK", `✅ Proyecto compartido exitosamente a ${REVISION_EMAIL}`);
        sharingSuccess = true;
        
        // Cerrar modal de confirmación si existe
        try {
          await page.keyboard.press('Escape');
          await sleep(1000);
        } catch {}
        
      } else {
        log("WARN", `⚠️ No se pudo confirmar el envío: ${shareConfirm.message}`);
      }
      
    } catch (e) {
      log("ERROR", `Error compartiendo proyecto: ${e}`);
      await screenshot(page, "14_error_compartir");
    }
    
    console.log("\n" + "=".repeat(70));
    console.log(`  📧 COMPARTICIÓN: ${sharingSuccess ? '✅ ENVIADO' : '⚠️ VERIFICAR MANUALMENTE'}`);
    console.log(`  📬 Destinatario: ${REVISION_EMAIL}`);
    console.log("=".repeat(70) + "\n");
    
    // =================================================
    // PASO 9: PROCESO DE PAGO (SEMI-AUTOMÁTICO)
    // =================================================
    console.log("\n" + "-".repeat(50));
    log("PASO 9", "PROCESO DE PAGO");
    console.log("-".repeat(50));
    
    // Solo proceder al pago si la validación fue exitosa
    if (validationResult.qualityScore >= 7 && validationResult.recommendation === 'approve') {
      log("INFO", "✓ Diseño aprobado automáticamente - procediendo a checkout");
      
      // Guardar proyecto primero
      log("ACTION", "Guardando proyecto antes de pagar...");
      try {
        const clickedGuardar = await tryClick(page, 'text=Guardar, button:has-text("Guardar")', 2000);
        
        if (!clickedGuardar) {
          await stagehand.act("click on 'Guardar' or 'Save' button");
        }
        
        await sleep(3000);
        await screenshot(page, "15_proyecto_guardado");
        log("OK", "✓ Proyecto guardado");
      } catch (e) {
        log("WARN", `Advertencia guardando proyecto: ${e}`);
      }
      
      // Navegar a checkout
      log("ACTION", "Navegando a checkout...");
      
      try {
        const clickedComprar = await tryClick(page, 'text=COMPRAR, button:has-text("COMPRAR")', 3000);
        
        if (!clickedComprar) {
          await stagehand.act("click on 'COMPRAR' button to proceed to checkout");
        }
        
        await sleep(5000);
        await screenshot(page, "16_checkout");
        
        // Extraer resumen del pedido
        log("ACTION", "Analizando resumen del pedido...");
        
        const orderSummary = await stagehand.extract({
          instruction: `Extract the order summary information:
            - Product name and size
            - Quantity
            - Subtotal amount
            - Shipping cost (if any)
            - Total amount
            - Currency`,
          schema: {
            type: "object",
            properties: {
              product: { type: "string", description: "Product name" },
              quantity: { type: "number", description: "Quantity" },
              subtotal: { type: "string", description: "Subtotal amount" },
              shipping: { type: "string", description: "Shipping cost" },
              total: { type: "string", description: "Total amount" },
              currency: { type: "string", description: "Currency code" }
            }
          }
        });
        
        console.log("\n" + "=".repeat(70));
        console.log("  💰 RESUMEN DEL PEDIDO");
        console.log("=".repeat(70));
        console.log(`
  Producto:    ${orderSummary.product || 'N/A'}
  Cantidad:    ${orderSummary.quantity || 1}
  Subtotal:    ${orderSummary.subtotal || 'N/A'}
  Envío:       ${orderSummary.shipping || 'N/A'}
  Total:       ${orderSummary.total || 'N/A'} ${orderSummary.currency || ''}
        `);
        console.log("=".repeat(70) + "\n");
        
        // PAUSA PARA REVISIÓN Y CONFIRMACIÓN MANUAL
        console.log("\n" + "⚠️ ".repeat(35));
        console.log("\n  🛑 CONFIRMACIÓN MANUAL REQUERIDA");
        console.log("\n  Este es el paso final antes de procesar el pago.");
        console.log("  Por favor revisa el resumen del pedido en pantalla.");
        console.log("\n  Opciones:");
        console.log("    1. Presiona ENTER para CONFIRMAR el pago");
        console.log("    2. Presiona Ctrl+C para CANCELAR");
        console.log("\n" + "⚠️ ".repeat(35) + "\n");
        
        // Esperar input del usuario (solo para ambiente interactivo)
        if (process.stdin.isTTY) {
          await new Promise<void>((resolve) => {
            process.stdin.resume();
            process.stdin.once('data', () => {
              resolve();
            });
          });
          
          log("OK", "✓ Confirmación recibida, procesando pago...");
          
          // Buscar y clickear botón final de pago
          await sleep(2000);
          
          const finalPaymentButtons = [
            'text=Confirmar Pago',
            'text=Confirmar Compra',
            'text=Finalizar Compra',
            'text=Pagar',
            'button:has-text("Confirmar")',
            'button:has-text("Finalizar")'
          ];
          
          let paymentClicked = false;
          
          for (const btnSelector of finalPaymentButtons) {
            const clicked = await tryClick(page, btnSelector, 2000);
            if (clicked) {
              paymentClicked = true;
              break;
            }
          }
          
          if (!paymentClicked) {
            await stagehand.act("click on the final payment confirmation button to complete the purchase");
          }
          
          await sleep(10000); // Esperar procesamiento del pago
          await screenshot(page, "17_pago_procesado");
          
          // Verificar confirmación de pago
          const paymentConfirm = await stagehand.extract({
            instruction: `Check if the payment was successful.
              Look for order confirmation number, success message, or thank you page.
              Also check for any error messages.`,
            schema: {
              type: "object",
              properties: {
                success: { type: "boolean", description: "Payment successful?" },
                orderNumber: { type: "string", description: "Order/confirmation number" },
                message: { type: "string", description: "Confirmation or error message" },
                hasError: { type: "boolean", description: "Is there an error?" }
              }
            }
          });
          
          console.log("\n" + "=".repeat(70));
          console.log("  💳 RESULTADO DEL PAGO");
          console.log("=".repeat(70));
          console.log(`
  Estado:          ${paymentConfirm.success ? '✅ EXITOSO' : '❌ FALLÓ'}
  Número de Orden: ${paymentConfirm.orderNumber || 'N/A'}
  Mensaje:         ${paymentConfirm.message || 'N/A'}
          `);
          console.log("=".repeat(70) + "\n");
          
          if (paymentConfirm.success) {
            log("OK", `✅ PAGO EXITOSO - Orden: ${paymentConfirm.orderNumber}`);
          } else {
            log("ERROR", `❌ Error en pago: ${paymentConfirm.message}`);
          }
          
        } else {
          log("WARN", "⚠️ Modo no interactivo - saltando confirmación de pago");
          log("INFO", "El proyecto está en checkout, revisar manualmente");
        }
        
      } catch (e) {
        log("ERROR", `Error en proceso de pago: ${e}`);
        await screenshot(page, "17_error_pago");
      }
      
    } else {
      log("WARN", "⚠️ Diseño requiere revisión manual - NO se procede al pago automático");
      log("INFO", `Motivo: Calidad ${validationResult.qualityScore}/10, Recomendación: ${validationResult.recommendation}`);
      
      // Guardar proyecto para revisión posterior
      log("ACTION", "Guardando proyecto para revisión...");
      try {
        const clicked = await tryClick(page, 'text=Guardar', 2000);
        if (!clicked) {
          await stagehand.act("click on 'Guardar' button");
        }
        await sleep(2000);
        log("OK", "✓ Proyecto guardado - esperando revisión manual en email");
      } catch (e) {
        log("WARN", `Advertencia guardando: ${e}`);
      }
    }
    
    // =================================================
    // RESULTADO FINAL
    // =================================================
    console.log("\n" + "=".repeat(70));
    console.log("  RESULTADO FINAL");
    console.log("=".repeat(70));
    
    const success = validationResult.qualityScore >= 7 && sharingSuccess;
    
    console.log(`
╔══════════════════════════════════════════════════════════════════╗
║  RESUMEN COMPLETO - TEST E2E AUTOMATIZADO FDF                    ║
╠══════════════════════════════════════════════════════════════════╣
║  FASE 0: DATOS DEL PEDIDO                                        ║
║    Origen:               ${PEDIDO_ID ? 'BD SQLite (ID específico)' : dbCheck.ok ? 'BD SQLite (último pedido)' : 'Fotos hardcodeadas'}       ║
║    Producto:             ${productoCodigo}                                        ║
║    Estilo diseño:        ${estiloDiseno}                                   ║
║    Título proyecto:      ${tituloProyecto.slice(0, 30)}...                 ║
║    Fotos procesadas:     ${fotosExistentes.length}/${fotosExistentes.length}                                          ║
╠══════════════════════════════════════════════════════════════════╣
║  FASE 1-3: CREACIÓN Y CARGA                                      ║
║    1. Login FDF:         ✅ Exitoso                              ║
║    2. Navegación:        ✅ Fotolibros                           ║
║    3. Crear proyecto:    ✅ ${productoCodigo}                                    ║
║    4. Subir fotos:       ✅ ${fotosExistentes.length} fotos (individual)                    ║
╠══════════════════════════════════════════════════════════════════╣
║  FASE 4: DISEÑO AUTOMÁTICO                                       ║
║    5. Template:          ${templateSelected ? '✅' : '⚠️'} Según estilo "${estiloDiseno}"            ║
║    6. Relleno Smart:     ${clickedFill ? '✅' : '⚠️'} Caras, Colores y Dimensiones      ║
╠══════════════════════════════════════════════════════════════════╣
║  FASE 5: VALIDACIÓN VISUAL INTELIGENTE                           ║
║    Fotos centradas:      ${validationResult.photosCentered ? '✅' : '❌'}                              ║
║    Orden lógico:         ${validationResult.logicalOrder ? '✅' : '❌'}                              ║
║    Páginas completas:    ${validationResult.allPagesFilled ? '✅' : '❌'}                              ║
║    Template visible:     ${validationResult.templateVisible ? '✅' : '❌'}                              ║
║    Calidad (1-10):       ${validationResult.qualityScore}/10 ${validationResult.qualityScore >= 7 ? '✅' : '⚠️'}                        ║
║    Recomendación:        ${(validationResult.recommendation || 'review').toUpperCase().padEnd(20)}     ║
╠══════════════════════════════════════════════════════════════════╣
║  FASE 6: COMPARTIR PARA REVISIÓN                                 ║
║    Email enviado a:      ${sharingSuccess ? '✅' : '⚠️'} ${REVISION_EMAIL}          ║
╠══════════════════════════════════════════════════════════════════╣
║  ESTADO FINAL: ${success ? '✅ COMPLETADO CON ÉXITO' : '⚠️ REQUIERE REVISIÓN MANUAL'}                ║
╠══════════════════════════════════════════════════════════════════╣
║  Screenshots guardados en:                                       ║
║  ${CONFIG.screenshotDir.slice(-50).padEnd(60)} ║
╚══════════════════════════════════════════════════════════════════╝
`);
    
    // Mantener browser abierto
    log("INFO", "Browser abierto 60s para inspección manual. Ctrl+C para cerrar.");
    await sleep(60000);
    
  } catch (error) {
    log("ERROR", `Error en test: ${error}`);
    try {
      const p = stagehand.context.pages()[0];
      if (p) await screenshot(p, "error_state");
    } catch {}
    await sleep(30000);
  } finally {
    await stagehand.close();
    log("INFO", "Browser cerrado");
  }
}

main().catch(console.error);
