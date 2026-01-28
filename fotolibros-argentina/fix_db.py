
import asyncio
import aiosqlite
import os

DB_PATH = "data/fotolibros.db"

async def fix_database():
    print(f"🔧 Reparando base de datos en {DB_PATH}...")
    
    if not os.path.exists(DB_PATH):
        print("❌ La base de datos no existe.")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        # 1. Verificar si existe la tabla pedidos
        try:
            await db.execute("SELECT count(*) FROM pedidos")
            print("✅ Tabla 'pedidos' existe.")
        except Exception as e:
            print(f"❌ Tabla 'pedidos' no existe: {e}")
            return

        # 2. Intentar agregar la columna verificacion_json
        try:
            print("⏳ Agregando columna 'verificacion_json'...")
            await db.execute("ALTER TABLE pedidos ADD COLUMN verificacion_json TEXT")
            await db.commit()
            print("✅ Columna agregada correctamente.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("✅ La columna 'verificacion_json' ya existía.")
            else:
                print(f"⚠️ Alerta al agregar columna: {e}")

        # 3. Verificar tabla fotos_pedido
        try:
            print("⏳ Verificando tabla 'fotos_pedido'...")
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fotos_pedido (
                    id TEXT PRIMARY KEY,
                    pedido_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    filepath TEXT NOT NULL,
                    analisis_json TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (pedido_id) REFERENCES pedidos(id)
                )
            """)
            await db.commit()
            print("✅ Tabla 'fotos_pedido' verificada.")
        except Exception as e:
            print(f"❌ Error en tabla 'fotos_pedido': {e}")

    print("\n🏁 Reparación finalizada. Reinicia el backend ahora.")

if __name__ == "__main__":
    asyncio.run(fix_database())
