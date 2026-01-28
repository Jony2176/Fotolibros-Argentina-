/**
 * DB Reader - Lectura de fotos desde SQLite
 * ==========================================
 * Lee fotos de pedidos desde la base de datos fotolibros.db
 * 
 * Tablas utilizadas:
 * - pedidos: Informacion del pedido
 * - fotos_pedido: Paths de fotos asociadas
 */

import Database from 'better-sqlite3';
import * as path from 'path';
import * as fs from 'fs';

// Ruta a la base de datos
const DB_PATH = path.resolve(__dirname, '../fotolibros-argentina/data/fotolibros.db');

export interface Pedido {
  id: string;
  producto_codigo: string;
  estilo_diseno: string;
  paginas_total: number;
  cliente_json: string;
  titulo_tapa: string | null;
  titulo_contratapa: string | null;
  texto_lomo: string | null;
  incluir_qr: boolean | null;
  qr_url: string | null;
  adornos_extras: string | null; // JSON con configuración de adornos
  estado: string;
  created_at: string;
}

export interface FotoPedido {
  id: string;
  pedido_id: string;
  filename: string;
  filepath: string;
  created_at: string;
}

/**
 * Obtiene un pedido por ID
 */
export function getPedido(pedidoId: string): Pedido | null {
  const db = new Database(DB_PATH, { readonly: true });
  
  try {
    const row = db.prepare(`
      SELECT id, producto_codigo, estilo_diseno, paginas_total, 
             cliente_json, titulo_tapa, titulo_contratapa, texto_lomo, 
             incluir_qr, qr_url, adornos_extras, estado, created_at
      FROM pedidos 
      WHERE id = ?
    `).get(pedidoId) as Pedido | undefined;
    
    return row || null;
  } finally {
    db.close();
  }
}

/**
 * Obtiene las rutas de fotos de un pedido
 */
export function getPhotosFromDB(pedidoId: string): string[] {
  const db = new Database(DB_PATH, { readonly: true });
  
  try {
    const rows = db.prepare(`
      SELECT filepath 
      FROM fotos_pedido 
      WHERE pedido_id = ?
      ORDER BY created_at ASC
    `).all(pedidoId) as { filepath: string }[];
    
    // Filtrar solo las fotos que existen
    const validPhotos = rows
      .map(r => r.filepath)
      .filter(filepath => {
        const exists = fs.existsSync(filepath);
        if (!exists) {
          console.warn(`[DB] Foto no encontrada: ${filepath}`);
        }
        return exists;
      });
    
    return validPhotos;
  } finally {
    db.close();
  }
}

/**
 * Obtiene el ultimo pedido que tenga fotos
 */
export function getLastPedidoWithPhotos(): { pedido: Pedido; photos: string[] } | null {
  const db = new Database(DB_PATH, { readonly: true });
  
  try {
    // Buscar el pedido mas reciente que tenga fotos
    const row = db.prepare(`
      SELECT DISTINCT p.id, p.producto_codigo, p.estilo_diseno, p.paginas_total,
             p.cliente_json, p.titulo_tapa, p.titulo_contratapa, p.texto_lomo,
             p.incluir_qr, p.qr_url, p.adornos_extras, p.estado, p.created_at
      FROM pedidos p
      INNER JOIN fotos_pedido fp ON p.id = fp.pedido_id
      ORDER BY p.created_at DESC
      LIMIT 1
    `).get() as Pedido | undefined;
    
    if (!row) {
      return null;
    }
    
    // Obtener las fotos de ese pedido
    const photos = getPhotosFromDB(row.id);
    
    if (photos.length === 0) {
      return null;
    }
    
    return { pedido: row, photos };
  } finally {
    db.close();
  }
}

/**
 * Lista todos los pedidos con cantidad de fotos
 */
export function listPedidosWithPhotoCount(): Array<{ id: string; estado: string; foto_count: number; created_at: string }> {
  const db = new Database(DB_PATH, { readonly: true });
  
  try {
    const rows = db.prepare(`
      SELECT p.id, p.estado, COUNT(fp.id) as foto_count, p.created_at
      FROM pedidos p
      LEFT JOIN fotos_pedido fp ON p.id = fp.pedido_id
      GROUP BY p.id
      ORDER BY p.created_at DESC
      LIMIT 20
    `).all() as Array<{ id: string; estado: string; foto_count: number; created_at: string }>;
    
    return rows;
  } finally {
    db.close();
  }
}

/**
 * Inserta un nuevo pedido de prueba
 */
export function insertTestPedido(pedido: {
  id: string;
  producto_codigo: string;
  estilo_diseno: string;
  paginas_total: number;
  cliente_nombre: string;
  cliente_email: string;
  titulo_tapa: string;
}): boolean {
  const db = new Database(DB_PATH);
  
  try {
    const now = new Date().toISOString();
    const clienteJson = JSON.stringify({
      nombre: pedido.cliente_nombre,
      email: pedido.cliente_email,
      direccion: {
        calle: "Test Street 123",
        ciudad: "Buenos Aires",
        provincia: "CABA",
        cp: "1000"
      }
    });
    
    db.prepare(`
      INSERT INTO pedidos (
        id, producto_codigo, estilo_diseno, paginas_total,
        cliente_json, titulo_tapa, estado, progreso, mensaje,
        created_at, updated_at
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      pedido.id,
      pedido.producto_codigo,
      pedido.estilo_diseno,
      pedido.paginas_total,
      clienteJson,
      pedido.titulo_tapa,
      'pendiente',
      0,
      'Pedido de prueba E2E',
      now,
      now
    );
    
    return true;
  } catch (error) {
    console.error('[DB] Error insertando pedido:', error);
    return false;
  } finally {
    db.close();
  }
}

/**
 * Inserta una foto asociada a un pedido
 */
export function insertFotoPedido(foto: {
  id: string;
  pedido_id: string;
  filename: string;
  filepath: string;
}): boolean {
  const db = new Database(DB_PATH);
  
  try {
    const now = new Date().toISOString();
    
    db.prepare(`
      INSERT INTO fotos_pedido (id, pedido_id, filename, filepath, created_at)
      VALUES (?, ?, ?, ?, ?)
    `).run(foto.id, foto.pedido_id, foto.filename, foto.filepath, now);
    
    return true;
  } catch (error) {
    console.error('[DB] Error insertando foto:', error);
    return false;
  } finally {
    db.close();
  }
}

/**
 * Verifica si la BD existe y tiene las tablas necesarias
 */
export function checkDatabase(): { ok: boolean; message: string } {
  if (!fs.existsSync(DB_PATH)) {
    return { ok: false, message: `Base de datos no encontrada: ${DB_PATH}` };
  }
  
  const db = new Database(DB_PATH, { readonly: true });
  
  try {
    // Verificar que existen las tablas
    const tables = db.prepare(`
      SELECT name FROM sqlite_master WHERE type='table' AND name IN ('pedidos', 'fotos_pedido')
    `).all() as { name: string }[];
    
    if (tables.length < 2) {
      return { ok: false, message: 'Faltan tablas en la BD (pedidos, fotos_pedido)' };
    }
    
    return { ok: true, message: `BD OK: ${DB_PATH}` };
  } finally {
    db.close();
  }
}

// CLI: Ejecutar directamente para probar
if (require.main === module) {
  console.log('='.repeat(60));
  console.log('DB Reader - Test');
  console.log('='.repeat(60));
  
  const check = checkDatabase();
  console.log(`\n[CHECK] ${check.message}`);
  
  if (check.ok) {
    console.log('\n[PEDIDOS]');
    const pedidos = listPedidosWithPhotoCount();
    pedidos.forEach(p => {
      console.log(`  ${p.id.slice(0, 8)}... | ${p.estado.padEnd(12)} | ${p.foto_count} fotos | ${p.created_at.slice(0, 10)}`);
    });
    
    const last = getLastPedidoWithPhotos();
    if (last) {
      console.log(`\n[ULTIMO PEDIDO CON FOTOS]`);
      console.log(`  ID: ${last.pedido.id}`);
      console.log(`  Producto: ${last.pedido.producto_codigo}`);
      console.log(`  Estilo: ${last.pedido.estilo_diseno}`);
      console.log(`  Fotos: ${last.photos.length}`);
      last.photos.slice(0, 3).forEach(p => console.log(`    - ${path.basename(p)}`));
    } else {
      console.log('\n[INFO] No hay pedidos con fotos');
    }
  }
}
