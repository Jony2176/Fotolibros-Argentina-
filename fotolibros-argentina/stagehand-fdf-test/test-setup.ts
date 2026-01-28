/**
 * Test Setup - Crear pedido de prueba con fotos
 * ==============================================
 * Crea un nuevo pedido en la BD y copia fotos de ejemplo
 * 
 * Uso: npx tsx test-setup.ts
 * 
 * Este script:
 * 1. Busca fotos de ejemplo en uploads/ existentes
 * 2. Crea un pedido nuevo en la BD
 * 3. Copia las fotos a una carpeta del nuevo pedido
 * 4. Registra las fotos en la tabla fotos_pedido
 */

import { v4 as uuidv4 } from 'uuid';
import * as fs from 'fs';
import * as path from 'path';
import {
  checkDatabase,
  insertTestPedido,
  insertFotoPedido,
  getPhotosFromDB,
  listPedidosWithPhotoCount
} from './db-reader';

// Configuracion
const UPLOADS_BASE = path.resolve(__dirname, '../fotolibros-argentina/uploads');
const MAX_PHOTOS = 8;  // Cantidad de fotos a usar

// Fotos de ejemplo (imagenes de stock o placeholder)
const SAMPLE_PHOTOS_URLS = [
  // Usaremos fotos existentes en el proyecto
];

/**
 * Busca fotos existentes en carpetas de uploads
 */
function findExistingPhotos(): string[] {
  const photos: string[] = [];
  
  if (!fs.existsSync(UPLOADS_BASE)) {
    console.log(`[SETUP] Carpeta uploads no existe: ${UPLOADS_BASE}`);
    return photos;
  }
  
  // Buscar en subcarpetas de uploads
  const subdirs = fs.readdirSync(UPLOADS_BASE, { withFileTypes: true })
    .filter(d => d.isDirectory())
    .map(d => path.join(UPLOADS_BASE, d.name));
  
  for (const subdir of subdirs) {
    const files = fs.readdirSync(subdir)
      .filter(f => /\.(jpg|jpeg|png|webp)$/i.test(f))
      .filter(f => !f.toLowerCase().includes('comprobante'))
      .map(f => path.join(subdir, f));
    
    photos.push(...files);
  }
  
  return photos.slice(0, MAX_PHOTOS);
}

/**
 * Copia fotos a la carpeta del pedido
 */
function copyPhotosForPedido(pedidoId: string, sourcePhotos: string[]): string[] {
  const pedidoDir = path.join(UPLOADS_BASE, pedidoId);
  
  // Crear directorio del pedido
  if (!fs.existsSync(pedidoDir)) {
    fs.mkdirSync(pedidoDir, { recursive: true });
  }
  
  const copiedPhotos: string[] = [];
  
  for (const sourcePath of sourcePhotos) {
    const photoId = uuidv4();
    const ext = path.extname(sourcePath);
    const newFilename = `${photoId}${ext}`;
    const destPath = path.join(pedidoDir, newFilename);
    
    try {
      fs.copyFileSync(sourcePath, destPath);
      copiedPhotos.push(destPath);
      console.log(`  [COPY] ${path.basename(sourcePath)} -> ${newFilename}`);
    } catch (error) {
      console.error(`  [ERROR] No se pudo copiar ${sourcePath}:`, error);
    }
  }
  
  return copiedPhotos;
}

/**
 * Crea fotos de placeholder si no hay fotos existentes
 */
async function createPlaceholderPhotos(pedidoId: string, count: number): Promise<string[]> {
  const pedidoDir = path.join(UPLOADS_BASE, pedidoId);
  
  if (!fs.existsSync(pedidoDir)) {
    fs.mkdirSync(pedidoDir, { recursive: true });
  }
  
  const photos: string[] = [];
  
  // Crear imagenes de placeholder simples (1x1 pixel PNG)
  // En produccion, usarias imagenes reales
  const placeholderPng = Buffer.from(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
    'base64'
  );
  
  for (let i = 0; i < count; i++) {
    const photoId = uuidv4();
    const filename = `${photoId}.png`;
    const filepath = path.join(pedidoDir, filename);
    
    fs.writeFileSync(filepath, placeholderPng);
    photos.push(filepath);
    console.log(`  [CREATE] Placeholder ${i + 1}: ${filename}`);
  }
  
  return photos;
}

/**
 * Funcion principal
 */
async function main() {
  console.log('='.repeat(60));
  console.log('TEST SETUP - Crear pedido de prueba');
  console.log('='.repeat(60));
  
  // Verificar BD
  const dbCheck = checkDatabase();
  if (!dbCheck.ok) {
    console.error(`\n[ERROR] ${dbCheck.message}`);
    console.log('\nAsegurate de que el backend Python haya sido ejecutado al menos una vez');
    console.log('para crear la base de datos.');
    process.exit(1);
  }
  console.log(`\n[OK] ${dbCheck.message}`);
  
  // Buscar fotos existentes
  console.log('\n[BUSCAR] Buscando fotos existentes...');
  let sourcePhotos = findExistingPhotos();
  console.log(`  Fotos encontradas: ${sourcePhotos.length}`);
  
  // Generar ID del pedido
  const pedidoId = uuidv4();
  console.log(`\n[PEDIDO] Creando pedido: ${pedidoId}`);
  
  // Determinar fotos a usar
  let photosToUse: string[];
  
  if (sourcePhotos.length >= 3) {
    // Copiar fotos existentes
    console.log('\n[COPY] Copiando fotos existentes...');
    photosToUse = copyPhotosForPedido(pedidoId, sourcePhotos);
  } else {
    // Crear placeholders
    console.log('\n[CREATE] Creando fotos de placeholder...');
    console.log('  (Para mejores resultados, agrega fotos reales a uploads/)');
    photosToUse = await createPlaceholderPhotos(pedidoId, 5);
  }
  
  if (photosToUse.length === 0) {
    console.error('\n[ERROR] No hay fotos para el pedido');
    process.exit(1);
  }
  
  // Insertar pedido en BD
  console.log('\n[DB] Insertando pedido en base de datos...');
  const pedidoOk = insertTestPedido({
    id: pedidoId,
    producto_codigo: 'CU-21x21-DURA',
    estilo_diseno: 'minimalista',
    paginas_total: 24,
    cliente_nombre: 'Test E2E User',
    cliente_email: 'test@e2e.local',
    titulo_tapa: 'Test E2E Hibrido'
  });
  
  if (!pedidoOk) {
    console.error('[ERROR] No se pudo insertar el pedido');
    process.exit(1);
  }
  console.log('  Pedido insertado OK');
  
  // Insertar fotos en BD
  console.log('\n[DB] Insertando fotos en base de datos...');
  for (const photoPath of photosToUse) {
    const fotoId = uuidv4();
    const filename = path.basename(photoPath);
    
    const fotoOk = insertFotoPedido({
      id: fotoId,
      pedido_id: pedidoId,
      filename: filename,
      filepath: photoPath
    });
    
    if (fotoOk) {
      console.log(`  [OK] ${filename}`);
    } else {
      console.log(`  [ERROR] ${filename}`);
    }
  }
  
  // Verificar
  console.log('\n[VERIFY] Verificando...');
  const photosInDb = getPhotosFromDB(pedidoId);
  console.log(`  Fotos en BD: ${photosInDb.length}`);
  
  // Resumen
  console.log('\n' + '='.repeat(60));
  console.log('RESUMEN');
  console.log('='.repeat(60));
  console.log(`
  Pedido ID:    ${pedidoId}
  Producto:     CU-21x21-DURA
  Estilo:       minimalista
  Fotos:        ${photosInDb.length}
  
  Para ejecutar el test E2E:
  
    npx tsx test-e2e-from-db.ts ${pedidoId}
  
  O usa el ultimo pedido automaticamente:
  
    npx tsx test-e2e-from-db.ts
`);
  
  // Mostrar todos los pedidos
  console.log('[PEDIDOS EN BD]');
  const pedidos = listPedidosWithPhotoCount();
  pedidos.slice(0, 5).forEach(p => {
    const marker = p.id === pedidoId ? ' <-- NUEVO' : '';
    console.log(`  ${p.id.slice(0, 8)}... | ${p.estado.padEnd(12)} | ${p.foto_count} fotos${marker}`);
  });
  
  // Guardar el ID en un archivo para facil acceso
  const configPath = path.join(__dirname, 'last-test-pedido.txt');
  fs.writeFileSync(configPath, pedidoId);
  console.log(`\n[SAVED] Pedido ID guardado en: last-test-pedido.txt`);
}

main().catch(console.error);
