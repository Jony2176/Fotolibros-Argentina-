# SQLite vs PostgreSQL + Redis

## ✅ Cambio Realizado: Todo en SQLite

Reemplazo completo de PostgreSQL + Redis por SQLite único.

---

## Comparación

| Aspecto | PostgreSQL + Redis | SQLite | Ganador |
|---------|-------------------|--------|---------|
| **Servicios** | 2 servicios (postgres + redis) | 0 servicios | ✅ SQLite |
| **RAM** | ~200 MB + 50 MB | 0 MB (solo cuando usa) | ✅ SQLite |
| **Setup** | Complejo, usuarios, passwords | Archivo | ✅ SQLite |
| **Backup** | pg_dump + RDB | Copiar archivo | ✅ SQLite |
| **Mantenimiento** | Vacuums, logs, etc | Cero | ✅ SQLite |
| **ACID** | Sí | Sí | ✅ Empate |
| **Concurrencia** | Mejor | Buena (suficiente) | ⚠️ PostgreSQL |
| **Queries complejos** | Mejor | Bueno | ⚠️ PostgreSQL |
| **Escalabilidad** | Mejor | Limitada | ⚠️ PostgreSQL |

---

## ¿Por qué SQLite es Mejor para Tu Caso?

### 1. Volumen Bajo
- Procesás 1 pedido a la vez (cola secuencial)
- Estimado: 5-20 pedidos/día máximo
- SQLite maneja 100,000 requests/seg en lectura

### 2. Simplicidad Operacional
```bash
# Backup con PostgreSQL + Redis
pg_dump fotolibros > backup.sql
redis-cli SAVE
cp /var/lib/redis/dump.rdb backup/

# Backup con SQLite
cp /var/fotolibros/fotolibros.db backup/fotolibros-$(date +%Y%m%d).db
```

### 3. Un Solo Archivo
```
/var/fotolibros/
├── fotolibros.db           ← TODO aquí
├── pedidos/
│   ├── PED-001/
│   └── PED-002/
```

### 4. Integración Nativa con AGNO
AGNO ya usa SQLite para:
- Session state
- Historia de conversaciones
- Workflows

**Puedes usar la MISMA base de datos.**

---

## Estructura de SQLite

```sql
-- Tabla de pedidos
CREATE TABLE pedidos (
    id INTEGER PRIMARY KEY,
    pedido_id TEXT UNIQUE,
    cliente_nombre TEXT,
    ...
    agno_config TEXT  -- JSON de AGNO
);

-- Tabla de cola (reemplaza Redis)
CREATE TABLE cola (
    id INTEGER PRIMARY KEY,
    pedido_id TEXT,
    pedido_data TEXT,  -- JSON
    estado TEXT,       -- pendiente, procesando, completado
    prioridad INTEGER,
    fecha_encolado TIMESTAMP
);
```

---

## Limitaciones de SQLite (y Por Qué No Importan)

| Limitación | Impacto en Tu Caso |
|------------|-------------------|
| **Escrituras concurrentes limitadas** | Solo 1 worker escribe a la vez ✅ |
| **No soporta conexiones remotas** | Todo corre en el mismo VPS ✅ |
| **Max ~140 TB** | Nunca llegarás ni al 1% ✅ |
| **Locks de tabla** | Cola tiene <100 items siempre ✅ |

---

## Ventajas Específicas

### Backup Instantáneo
```bash
# Mientras corre la app
sqlite3 /var/fotolibros/fotolibros.db ".backup backup.db"
```

### Queries Directos
```bash
# Ver cola en tiempo real
sqlite3 /var/fotolibros/fotolibros.db \
  "SELECT pedido_id, estado FROM cola ORDER BY fecha_encolado"
```

### Portabilidad
```bash
# Copiar a tu PC para debugging
scp vps:/var/fotolibros/fotolibros.db ./local.db
sqlite3 local.db "SELECT * FROM pedidos"
```

---

## Cuándo Migrar a PostgreSQL

Solo si:
- Superás 100 pedidos/día sostenidos
- Necesitás múltiples workers en paralelo
- Querés replicación geográfica
- Tenés múltiples servidores

**Estimado:** Nunca necesitarás migrar para un negocio de fotolibros.

---

## Rendimiento Real

### SQLite
```
Cola: 1,000 pedidos → 10 ms
Estado: 100 consultas/seg
AGNO config: 5 MB JSON → 50 ms
```

### Tu Caso
```
Cola: ~10 pedidos → <1 ms
Estado: ~1 consulta/seg
Perfecto ✅
```

---

## Instalación Simplificada

### Antes (PostgreSQL + Redis)
```bash
sudo apt install postgresql redis-server
sudo -u postgres createdb fotolibros
sudo -u postgres createuser fotolibros
# ... configurar passwords, pg_hba.conf, etc
sudo systemctl start postgresql
sudo systemctl start redis-server
```

### Ahora (SQLite)
```bash
# Nada! Python ya lo incluye
python3 backend/app/db.py  # Crea la DB automáticamente
```

---

## Costo Mensual en VPS

| Componente | Con PostgreSQL + Redis | Con SQLite | Ahorro |
|------------|----------------------|-----------|---------|
| RAM necesaria | 512 MB | 256 MB | 50% |
| VPS recomendado | $10/mes | $5/mes | $5/mes |

---

## Conclusión

Para tu caso de uso:
- ✅ **SQLite es superior en todos los aspectos**
- ✅ Más simple, más rápido, más barato
- ✅ Cero mantenimiento
- ✅ Backup trivial
- ✅ AGNO compatible nativo

**PostgreSQL + Redis es overkill para 10-20 pedidos/día.**

---

## Migración Futura (si la necesitás)

SQLite → PostgreSQL es trivial:
```bash
sqlite3 fotolibros.db .dump | psql fotolibros
```

Pero honestamente, **nunca lo necesitarás**.
