"""
FDF Pattern Cache - Cache de Patrones Visuales
===============================================
Almacena coordenadas de slots aprendidas para evitar llamadas
repetidas al modelo de Vision.

Beneficios:
- Reduccion 80%+ en llamadas a Vision API
- Mayor velocidad en ejecuciones repetidas
- Aprendizaje incremental de layouts

Uso:
    cache = FDFPatternCache("data/fdf_patterns.db")
    
    # Intentar obtener del cache
    coords = cache.get_cached_slot("collage_2x2", "top_left", 1920, 1080)
    
    if coords:
        # Usar coordenadas cacheadas (gratis)
        await drag_to(coords["center_x"], coords["center_y"])
    else:
        # Detectar con Vision y guardar
        coords = await vision.find_slot(...)
        cache.save_slot_pattern("collage_2x2", "top_left", 1920, 1080, coords)
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, Dict, List
from contextlib import contextmanager

from .error_handling import logger


class FDFPatternCache:
    """
    Cache SQLite para patrones visuales del editor FDF.
    Almacena coordenadas de slots y elementos UI aprendidos.
    """
    
    def __init__(self, db_path: str = "data/fdf_patterns.db"):
        """
        Inicializa el cache.
        
        Args:
            db_path: Ruta a la base de datos SQLite.
                     Usar ":memory:" para cache en memoria (testing).
        """
        self.db_path = db_path
        
        # Crear directorio si no existe
        if db_path != ":memory:":
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
        logger.info(f"[Cache] Inicializado en {db_path}")
    
    def _init_db(self):
        """Crea las tablas si no existen"""
        cursor = self.conn.cursor()
        
        # Tabla de patrones de slots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS slot_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                layout_name TEXT NOT NULL,
                slot_id TEXT NOT NULL,
                viewport_width INTEGER NOT NULL,
                viewport_height INTEGER NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL,
                width REAL NOT NULL,
                height REAL NOT NULL,
                center_x REAL NOT NULL,
                center_y REAL NOT NULL,
                confidence REAL DEFAULT 1.0,
                hit_count INTEGER DEFAULT 1,
                success_count INTEGER DEFAULT 1,
                fail_count INTEGER DEFAULT 0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(layout_name, slot_id, viewport_width, viewport_height)
            )
        """)
        
        # Tabla de elementos UI (botones, menus, etc.)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ui_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                element_name TEXT NOT NULL,
                page_context TEXT DEFAULT 'general',
                viewport_width INTEGER NOT NULL,
                viewport_height INTEGER NOT NULL,
                selector TEXT,
                x REAL,
                y REAL,
                width REAL,
                height REAL,
                hit_count INTEGER DEFAULT 1,
                success_count INTEGER DEFAULT 1,
                fail_count INTEGER DEFAULT 0,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(element_name, page_context, viewport_width, viewport_height)
            )
        """)
        
        # Tabla de templates de FDF
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT NOT NULL,
                category TEXT,
                viewport_width INTEGER NOT NULL,
                viewport_height INTEGER NOT NULL,
                card_x REAL,
                card_y REAL,
                card_width REAL,
                card_height REAL,
                hit_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(template_name, viewport_width, viewport_height)
            )
        """)
        
        # Indices para mejor performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_slot_lookup 
            ON slot_patterns(layout_name, slot_id, viewport_width, viewport_height)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ui_lookup 
            ON ui_elements(element_name, page_context, viewport_width, viewport_height)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_template_lookup 
            ON template_patterns(template_name, viewport_width, viewport_height)
        """)
        
        self.conn.commit()
    
    @contextmanager
    def _get_cursor(self):
        """Context manager para cursor con commit automatico"""
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
    
    # =========================================
    # SLOT PATTERNS
    # =========================================
    
    def get_cached_slot(
        self,
        layout_name: str,
        slot_id: str,
        viewport_width: int,
        viewport_height: int,
        tolerance: int = 50
    ) -> Optional[Dict]:
        """
        Busca un slot en el cache.
        
        Args:
            layout_name: Nombre del layout (ej: "collage_2x2")
            slot_id: ID del slot (ej: "top_left")
            viewport_width: Ancho del viewport
            viewport_height: Alto del viewport
            tolerance: Tolerancia en pixeles para viewport (para manejar pequenas diferencias)
            
        Returns:
            Dict con coordenadas o None si no esta en cache
        """
        with self._get_cursor() as cursor:
            # Buscar con tolerancia de viewport
            cursor.execute("""
                SELECT x, y, width, height, center_x, center_y, confidence, hit_count
                FROM slot_patterns
                WHERE layout_name = ? AND slot_id = ?
                  AND ABS(viewport_width - ?) <= ?
                  AND ABS(viewport_height - ?) <= ?
                ORDER BY hit_count DESC, last_used DESC
                LIMIT 1
            """, (layout_name, slot_id, viewport_width, tolerance, viewport_height, tolerance))
            
            row = cursor.fetchone()
            
            if row:
                # Actualizar estadisticas de uso
                cursor.execute("""
                    UPDATE slot_patterns 
                    SET hit_count = hit_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE layout_name = ? AND slot_id = ?
                      AND ABS(viewport_width - ?) <= ?
                      AND ABS(viewport_height - ?) <= ?
                """, (layout_name, slot_id, viewport_width, tolerance, viewport_height, tolerance))
                
                logger.debug(f"[Cache HIT] Slot {slot_id} en {layout_name} (hits: {row['hit_count']+1})")
                
                return {
                    "x": row["x"],
                    "y": row["y"],
                    "width": row["width"],
                    "height": row["height"],
                    "center_x": row["center_x"],
                    "center_y": row["center_y"],
                    "confidence": row["confidence"],
                    "from_cache": True,
                    "hit_count": row["hit_count"] + 1
                }
            
            logger.debug(f"[Cache MISS] Slot {slot_id} en {layout_name}")
            return None
    
    def save_slot_pattern(
        self,
        layout_name: str,
        slot_id: str,
        viewport_width: int,
        viewport_height: int,
        coords: Dict,
        confidence: float = 1.0
    ) -> bool:
        """
        Guarda un patron de slot en el cache.
        
        Args:
            layout_name: Nombre del layout
            slot_id: ID del slot
            viewport_width: Ancho del viewport
            viewport_height: Alto del viewport
            coords: Dict con x, y, width, height, center_x, center_y
            confidence: Nivel de confianza (0.0-1.0)
            
        Returns:
            True si se guardo correctamente
        """
        try:
            with self._get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO slot_patterns 
                    (layout_name, slot_id, viewport_width, viewport_height,
                     x, y, width, height, center_x, center_y, confidence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(layout_name, slot_id, viewport_width, viewport_height)
                    DO UPDATE SET
                        x = excluded.x,
                        y = excluded.y,
                        width = excluded.width,
                        height = excluded.height,
                        center_x = excluded.center_x,
                        center_y = excluded.center_y,
                        confidence = excluded.confidence,
                        last_used = CURRENT_TIMESTAMP
                """, (
                    layout_name, slot_id, viewport_width, viewport_height,
                    coords.get("x", 0), coords.get("y", 0),
                    coords.get("width", 0), coords.get("height", 0),
                    coords.get("center_x", coords.get("x", 0) + coords.get("width", 0) / 2),
                    coords.get("center_y", coords.get("y", 0) + coords.get("height", 0) / 2),
                    confidence
                ))
                
                logger.info(f"[Cache SAVE] Slot {slot_id} en {layout_name} guardado")
                return True
                
        except Exception as e:
            logger.error(f"[Cache ERROR] Error guardando slot: {e}")
            return False
    
    def mark_slot_success(self, layout_name: str, slot_id: str, viewport_width: int, viewport_height: int):
        """Marca un slot como exitoso (incrementa success_count)"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                UPDATE slot_patterns 
                SET success_count = success_count + 1
                WHERE layout_name = ? AND slot_id = ? 
                  AND viewport_width = ? AND viewport_height = ?
            """, (layout_name, slot_id, viewport_width, viewport_height))
    
    def mark_slot_failure(self, layout_name: str, slot_id: str, viewport_width: int, viewport_height: int):
        """Marca un slot como fallido (incrementa fail_count, puede invalidar si hay muchos fallos)"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                UPDATE slot_patterns 
                SET fail_count = fail_count + 1
                WHERE layout_name = ? AND slot_id = ? 
                  AND viewport_width = ? AND viewport_height = ?
            """, (layout_name, slot_id, viewport_width, viewport_height))
            
            # Si hay muchos fallos, invalidar el patron
            cursor.execute("""
                DELETE FROM slot_patterns
                WHERE layout_name = ? AND slot_id = ? 
                  AND viewport_width = ? AND viewport_height = ?
                  AND fail_count > 3 AND fail_count > success_count
            """, (layout_name, slot_id, viewport_width, viewport_height))
    
    # =========================================
    # UI ELEMENTS
    # =========================================
    
    def get_cached_ui_element(
        self,
        element_name: str,
        viewport_width: int,
        viewport_height: int,
        page_context: str = "general"
    ) -> Optional[Dict]:
        """Busca un elemento UI en el cache"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT selector, x, y, width, height, hit_count
                FROM ui_elements
                WHERE element_name = ? AND page_context = ?
                  AND viewport_width = ? AND viewport_height = ?
            """, (element_name, page_context, viewport_width, viewport_height))
            
            row = cursor.fetchone()
            
            if row:
                cursor.execute("""
                    UPDATE ui_elements 
                    SET hit_count = hit_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE element_name = ? AND page_context = ?
                      AND viewport_width = ? AND viewport_height = ?
                """, (element_name, page_context, viewport_width, viewport_height))
                
                return {
                    "selector": row["selector"],
                    "x": row["x"],
                    "y": row["y"],
                    "width": row["width"],
                    "height": row["height"],
                    "from_cache": True
                }
            
            return None
    
    def save_ui_element(
        self,
        element_name: str,
        viewport_width: int,
        viewport_height: int,
        coords: Dict,
        selector: str = None,
        page_context: str = "general"
    ) -> bool:
        """Guarda un elemento UI en el cache"""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO ui_elements 
                    (element_name, page_context, viewport_width, viewport_height,
                     selector, x, y, width, height)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(element_name, page_context, viewport_width, viewport_height)
                    DO UPDATE SET
                        selector = COALESCE(excluded.selector, selector),
                        x = excluded.x,
                        y = excluded.y,
                        width = excluded.width,
                        height = excluded.height,
                        last_used = CURRENT_TIMESTAMP
                """, (
                    element_name, page_context, viewport_width, viewport_height,
                    selector,
                    coords.get("x"), coords.get("y"),
                    coords.get("width"), coords.get("height")
                ))
                return True
        except Exception as e:
            logger.error(f"[Cache ERROR] Error guardando UI element: {e}")
            return False
    
    # =========================================
    # TEMPLATE PATTERNS
    # =========================================
    
    def get_cached_template(
        self,
        template_name: str,
        viewport_width: int,
        viewport_height: int
    ) -> Optional[Dict]:
        """Busca coordenadas de un template card en el cache"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT card_x, card_y, card_width, card_height, category, hit_count
                FROM template_patterns
                WHERE template_name = ?
                  AND viewport_width = ? AND viewport_height = ?
            """, (template_name, viewport_width, viewport_height))
            
            row = cursor.fetchone()
            
            if row:
                cursor.execute("""
                    UPDATE template_patterns 
                    SET hit_count = hit_count + 1, last_used = CURRENT_TIMESTAMP
                    WHERE template_name = ?
                      AND viewport_width = ? AND viewport_height = ?
                """, (template_name, viewport_width, viewport_height))
                
                return {
                    "x": row["card_x"],
                    "y": row["card_y"],
                    "width": row["card_width"],
                    "height": row["card_height"],
                    "category": row["category"],
                    "from_cache": True
                }
            
            return None
    
    def save_template_pattern(
        self,
        template_name: str,
        viewport_width: int,
        viewport_height: int,
        coords: Dict,
        category: str = None
    ) -> bool:
        """Guarda coordenadas de un template card"""
        try:
            with self._get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO template_patterns 
                    (template_name, category, viewport_width, viewport_height,
                     card_x, card_y, card_width, card_height)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(template_name, viewport_width, viewport_height)
                    DO UPDATE SET
                        category = COALESCE(excluded.category, category),
                        card_x = excluded.card_x,
                        card_y = excluded.card_y,
                        card_width = excluded.card_width,
                        card_height = excluded.card_height,
                        last_used = CURRENT_TIMESTAMP
                """, (
                    template_name, category, viewport_width, viewport_height,
                    coords.get("x"), coords.get("y"),
                    coords.get("width"), coords.get("height")
                ))
                return True
        except Exception as e:
            logger.error(f"[Cache ERROR] Error guardando template: {e}")
            return False
    
    # =========================================
    # UTILITIES
    # =========================================
    
    def get_cache_stats(self) -> Dict:
        """Obtiene estadisticas del cache"""
        with self._get_cursor() as cursor:
            # Stats de slots
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(hit_count) as total_hits,
                    AVG(confidence) as avg_confidence,
                    SUM(success_count) as total_success,
                    SUM(fail_count) as total_fails
                FROM slot_patterns
            """)
            slot_stats = cursor.fetchone()
            
            # Stats de UI elements
            cursor.execute("""
                SELECT COUNT(*) as total, SUM(hit_count) as total_hits
                FROM ui_elements
            """)
            ui_stats = cursor.fetchone()
            
            # Stats de templates
            cursor.execute("""
                SELECT COUNT(*) as total, SUM(hit_count) as total_hits
                FROM template_patterns
            """)
            template_stats = cursor.fetchone()
            
            total_patterns = (slot_stats["total"] or 0) + (ui_stats["total"] or 0) + (template_stats["total"] or 0)
            total_hits = (slot_stats["total_hits"] or 0) + (ui_stats["total_hits"] or 0) + (template_stats["total_hits"] or 0)
            
            return {
                "slots": {
                    "total": slot_stats["total"] or 0,
                    "hits": slot_stats["total_hits"] or 0,
                    "avg_confidence": round(slot_stats["avg_confidence"] or 0, 2),
                    "success_rate": round(
                        (slot_stats["total_success"] or 0) / 
                        max((slot_stats["total_success"] or 0) + (slot_stats["total_fails"] or 0), 1) * 100,
                        1
                    )
                },
                "ui_elements": {
                    "total": ui_stats["total"] or 0,
                    "hits": ui_stats["total_hits"] or 0
                },
                "templates": {
                    "total": template_stats["total"] or 0,
                    "hits": template_stats["total_hits"] or 0
                },
                "total_patterns": total_patterns,
                "total_hits": total_hits,
                "cache_efficiency": f"{total_hits / max(total_patterns, 1):.1f}x" if total_patterns > 0 else "0x"
            }
    
    def clear_old_patterns(self, days: int = 30):
        """Limpia patrones no usados en X dias"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM slot_patterns
                WHERE last_used < datetime('now', ?)
            """, (f'-{days} days',))
            slots_deleted = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM ui_elements
                WHERE last_used < datetime('now', ?)
            """, (f'-{days} days',))
            ui_deleted = cursor.rowcount
            
            cursor.execute("""
                DELETE FROM template_patterns
                WHERE last_used < datetime('now', ?)
            """, (f'-{days} days',))
            templates_deleted = cursor.rowcount
            
            total = slots_deleted + ui_deleted + templates_deleted
            if total > 0:
                logger.info(f"[Cache CLEANUP] Eliminados {total} patrones antiguos")
            
            return total
    
    def invalidate_slot(self, layout_name: str, slot_id: str):
        """Invalida un slot especifico (forzar re-aprendizaje)"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM slot_patterns
                WHERE layout_name = ? AND slot_id = ?
            """, (layout_name, slot_id))
            logger.info(f"[Cache INVALIDATE] Slot {slot_id} en {layout_name}")
    
    def invalidate_layout(self, layout_name: str):
        """Invalida todos los slots de un layout"""
        with self._get_cursor() as cursor:
            cursor.execute("""
                DELETE FROM slot_patterns
                WHERE layout_name = ?
            """, (layout_name,))
            logger.info(f"[Cache INVALIDATE] Layout {layout_name} completo")
    
    def clear_all(self):
        """Limpia todo el cache"""
        with self._get_cursor() as cursor:
            cursor.execute("DELETE FROM slot_patterns")
            cursor.execute("DELETE FROM ui_elements")
            cursor.execute("DELETE FROM template_patterns")
            logger.warning("[Cache CLEAR] Todo el cache eliminado")
    
    def close(self):
        """Cierra la conexion"""
        if self.conn:
            self.conn.close()
            logger.info("[Cache] Conexion cerrada")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Singleton global (opcional)
_global_cache: Optional[FDFPatternCache] = None

def get_pattern_cache(db_path: str = "data/fdf_patterns.db") -> FDFPatternCache:
    """Obtiene instancia singleton del cache"""
    global _global_cache
    if _global_cache is None:
        _global_cache = FDFPatternCache(db_path)
    return _global_cache
