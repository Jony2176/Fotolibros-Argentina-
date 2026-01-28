import sqlite3
import json
import hashlib
from datetime import datetime
from typing import Optional
from playwright.async_api import Page


class FDFPatternCache:
    """
    Cache de patrones visuales del editor FDF.
    Almacena coordenadas aprendidas para evitar llamadas repetidas al modelo de visión.
    """
    
    def __init__(self, db_path: str = "fdf_patterns.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._init_db()
    
    def _init_db(self):
        """Inicializa la base de datos"""
        self.conn.execute("""
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
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(layout_name, slot_id, viewport_width, viewport_height)
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS ui_elements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                element_name TEXT NOT NULL,
                viewport_width INTEGER NOT NULL,
                viewport_height INTEGER NOT NULL,
                selector TEXT,
                x REAL,
                y REAL,
                width REAL,
                height REAL,
                hit_count INTEGER DEFAULT 1,
                last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(element_name, viewport_width, viewport_height)
            )
        """)
        
        self.conn.commit()
    
    def get_cached_slot(
        self,
        layout_name: str,
        slot_id: str,
        viewport_width: int,
        viewport_height: int
    ) -> Optional[dict]:
        """Busca un slot en el cache"""
        cursor = self.conn.execute("""
            SELECT x, y, width, height, center_x, center_y, confidence
            FROM slot_patterns
            WHERE layout_name = ? AND slot_id = ? 
              AND viewport_width = ? AND viewport_height = ?
        """, (layout_name, slot_id, viewport_width, viewport_height))
        
        row = cursor.fetchone()
        if row:
            # Actualizar estadísticas de uso
            self.conn.execute("""
                UPDATE slot_patterns 
                SET hit_count = hit_count + 1, last_used = CURRENT_TIMESTAMP
                WHERE layout_name = ? AND slot_id = ?
                  AND viewport_width = ? AND viewport_height = ?
            """, (layout_name, slot_id, viewport_width, viewport_height))
            self.conn.commit()
            
            return {
                "x": row[0],
                "y": row[1],
                "width": row[2],
                "height": row[3],
                "center_x": row[4],
                "center_y": row[5],
                "confidence": row[6],
                "from_cache": True
            }
        
        return None
    
    def save_slot_pattern(
        self,
        layout_name: str,
        slot_id: str,
        viewport_width: int,
        viewport_height: int,
        coords: dict,
        confidence: float = 1.0
    ):
        """Guarda un patrón de slot en el cache"""
        self.conn.execute("""
            INSERT OR REPLACE INTO slot_patterns 
            (layout_name, slot_id, viewport_width, viewport_height, 
             x, y, width, height, center_x, center_y, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            layout_name, slot_id, viewport_width, viewport_height,
            coords["x"], coords["y"], coords["width"], coords["height"],
            coords["center_x"], coords["center_y"], confidence
        ))
        self.conn.commit()
    
    async def get_or_learn_slot(
        self,
        page: Page,
        layout_name: str,
        slot_id: str,
        vision_verifier  # GeminiVisionVerifier instance
    ) -> dict:
        """
        Obtiene coordenadas del cache o las aprende con visión.
        """
        viewport = page.viewport_size
        if not viewport:
            viewport = {"width": 1280, "height": 720}
        
        # Intentar obtener del cache
        cached = self.get_cached_slot(
            layout_name, slot_id,
            viewport["width"], viewport["height"]
        )
        
        if cached:
            return cached
        
        # Aprender con visión
        slot_description = f"slot '{slot_id}' del layout '{layout_name}'"
        detected = await vision_verifier.detect_slot_position(page, slot_description)
        
        if detected.get("encontrado"):
            coords = {
                "x": detected["x"],
                "y": detected["y"],
                "width": detected["width"],
                "height": detected["height"],
                "center_x": detected["center_x"],
                "center_y": detected["center_y"]
            }
            
            # Guardar para futuras ejecuciones
            self.save_slot_pattern(
                layout_name, slot_id,
                viewport["width"], viewport["height"],
                coords
            )
            
            coords["from_cache"] = False
            return coords
        
        raise Exception(f"No se pudo detectar el slot {slot_id} en layout {layout_name}")
    
    def get_cache_stats(self) -> dict:
        """Obtiene estadísticas del cache"""
        cursor = self.conn.execute("""
            SELECT 
                COUNT(*) as total_patterns,
                SUM(hit_count) as total_hits,
                AVG(confidence) as avg_confidence
            FROM slot_patterns
        """)
        row = cursor.fetchone()
        
        return {
            "total_patterns": row[0] or 0,
            "total_hits": row[1] or 0,
            "avg_confidence": row[2] or 0.0,
            "cache_efficiency": f"{(row[1] or 0) / max(row[0] or 1, 1):.1f}x"
        }
    
    def clear_old_patterns(self, days: int = 30):
        """Limpia patrones no usados en X días"""
        self.conn.execute("""
            DELETE FROM slot_patterns
            WHERE last_used < datetime('now', ?)
        """, (f'-{days} days',))
        self.conn.commit()
