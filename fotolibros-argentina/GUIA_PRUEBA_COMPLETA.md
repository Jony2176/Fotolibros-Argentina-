# 🧪 Guía de Prueba Completa del Backend con AGNO Team

Esta guía te muestra cómo probar todo el sistema end-to-end.

---

## 🎯 Flujo Completo de Prueba

```
┌──────────────────────────────────────────────────────────────┐
│                   FLUJO DE PRUEBA E2E                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Frontend (React) → Sube fotos                           │
│  2. Backend (FastAPI) → Crea pedido en SQLite              │
│  3. AGNO Team (5 agentes) → Analiza y diseña               │
│  4. Visualizador → Ver resultado en consola                 │
│  5. Executor FDF → Crear fotolibro en navegador            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisitos

### 1. Dependencias Instaladas

```bash
# Backend Python
cd fotolibros-argentina-v2/fotolibros-argentina
pip install fastapi uvicorn python-multipart sqlite3 python-dotenv agno

# Backend AGNO
cd ../fotolibros-agno-backend
pip install agno openai python-dotenv

# Frontend React
cd ../../Fotolibros-Argentina-
npm install
```

### 2. Variables de Entorno

**En `fotolibros-argentina/.env`**:
```env
# AGNO Team
OPENROUTER_API_KEY=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
MODEL_ID=openai/gpt-4o-mini

# FDF (opcional - solo para ejecutar en FDF)
FDF_EMAIL=tu_email@ejemplo.com
FDF_PASSWORD=tu_password

# Gemini (opcional - solo para diseño con Vision)
GEMINI_API_KEY=tu_api_key_gemini
```

**En `fotolibros-agno-backend/.env`**:
```env
OPENROUTER_API_KEY=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
MODEL_ID=openai/gpt-4o-mini
```

---

## 🚀 Método 1: Prueba Completa con Frontend (RECOMENDADO)

### Paso 1: Iniciar Backend FastAPI

```bash
# Terminal 1
cd C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-argentina
python main.py
```

**Salida esperada**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Paso 2: Iniciar Frontend React

```bash
# Terminal 2
cd C:\Users\Usuario\Downloads\fotolibros_argentina\Fotolibros-Argentina-
npm run dev
```

**Salida esperada**:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

### Paso 3: Crear Pedido desde el Frontend

1. Abre http://localhost:3000 en tu navegador
2. Haz clic en **"Empezar mi fotolibro"**
3. **Paso 1 - Producto**: Selecciona "Fotolibro Cuadrado 20x20cm - 40 páginas"
4. **Paso 2 - Estilo**: Selecciona cualquier estilo (ej: "Romántico")
5. **Paso 3 - Páginas**: Deja 40 páginas o ajusta
6. **Paso 4 - Fotos**: 
   - Sube **al menos 10-12 fotos**
   - El sistema te dirá cuántas necesitas según las páginas
7. **Paso 5 - Entrega**: Completa nombre, email, dirección
8. **Paso 6 - Pago**: Selecciona "Transferencia Bancaria"
9. Haz clic en **"Finalizar Pedido"**

**Resultado**: Recibirás un ID de pedido (ej: `a309ddfc-ae43-40e7-ba66-80dc1a330cdf`)

### Paso 4: Procesar con AGNO Team

```bash
# Terminal 3
cd C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2
python procesar_pedido_agno.py
```

**Salida esperada**:
```
======================================================================
  PROCESAMIENTO CON AGNO TEAM
======================================================================

Pedido ID: a309ddfc...

[1/6] Obteniendo datos del pedido...
[2/6] Obteniendo fotos...
      Fotos encontradas: 12
      Cliente: JONY

[3/6] Cargando AGNO Team...
[OK] Sistema AGNO Team (5 agentes) cargado correctamente

[4/6] Procesando con 5 agentes especializados...
----------------------------------------------------------------------
[AGNO] Iniciando procesamiento con AGNO Team (5 agentes)
[FOTO] FASE 1/5: Analizando 12 fotos con Vision AI...
[MOTIF] FASE 2/5: Detectando motivo del fotolibro...
[CHRONO] FASE 3/5: Ordenando fotos cronológicamente...
[STORY] FASE 4/5: Generando textos emotivos...
[DESIGN] FASE 5/5: Curando diseño artístico...

[5/6] PROCESAMIENTO EXITOSO!
      Motivo detectado: generic
      Titulo: "Momentos que Inspiran"
      Template: Moderno
      Fotos ordenadas: 12

[6/6] Guardando configuracion...
      Guardado en: fotolibros-argentina/data/agno_config_a309ddfc.json

======================================================================
  EXITO - AGNO TEAM COMPLETO
======================================================================
```

### Paso 5: Visualizar el Diseño

```bash
python visualizar_agno_config.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

**Verás**:
- Título y subtítulo de tapa
- Dedicatoria completa
- 3 Capítulos con sus títulos emotivos
- Leyendas por cada foto
- Configuración de diseño
- Estadísticas

### Paso 6 (Opcional): Ejecutar en FDF

```bash
python ejecutar_fdf_con_agno.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

Esto abre Chrome y crea el fotolibro automáticamente en FDF.

---

## 🔧 Método 2: Prueba Rápida con cURL (Sin Frontend)

### Paso 1: Iniciar Backend

```bash
cd fotolibros-argentina
python main.py
```

### Paso 2: Crear Pedido Manual

```bash
curl -X POST http://localhost:8000/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "producto_codigo": "FOTOLIBRO_CUADRADO_20X20_40PAG",
    "estilo_diseno": "romantico",
    "paginas_total": 40,
    "cliente": {
      "nombre": "JONY TEST",
      "email": "test@ejemplo.com",
      "telefono": "123456789",
      "direccion": {
        "calle": "Calle Falsa 123",
        "ciudad": "Buenos Aires",
        "provincia": "Buenos Aires",
        "codigo_postal": "1000"
      }
    },
    "metodo_pago": "transferencia",
    "titulo_tapa": null,
    "texto_lomo": null
  }'
```

**Respuesta esperada**:
```json
{
  "id": "abc12345-...",
  "estado": "pendiente",
  "created_at": "2026-01-25T..."
}
```

### Paso 3: Subir Fotos

```bash
# Copia el ID del pedido de la respuesta anterior
PEDIDO_ID="abc12345-..."

curl -X POST http://localhost:8000/pedidos/$PEDIDO_ID/fotos \
  -F "fotos=@/ruta/a/foto1.jpg" \
  -F "fotos=@/ruta/a/foto2.jpg" \
  -F "fotos=@/ruta/a/foto3.jpg"
```

### Paso 4: Procesar con AGNO Team

```bash
python procesar_pedido_agno.py
```

Selecciona el pedido que acabas de crear.

---

## 📊 Método 3: Verificar en la Base de Datos

### Ver Pedidos Existentes

```bash
cd fotolibros-argentina
sqlite3 data/fotolibros.db
```

```sql
-- Ver todos los pedidos
SELECT 
  id, 
  cliente_nombre, 
  estado, 
  created_at,
  producto_codigo,
  paginas_total
FROM pedidos 
ORDER BY created_at DESC 
LIMIT 10;

-- Ver fotos de un pedido específico
SELECT COUNT(*) as total_fotos
FROM fotos
WHERE pedido_id = 'a309ddfc-ae43-40e7-ba66-80dc1a330cdf';

-- Salir
.exit
```

---

## 🎨 Verificar que AGNO Team está Integrado

### Ver logs del backend cuando se crea un pedido:

Cuando creas un pedido desde el frontend, deberías ver en la consola del backend:

```
INFO:     127.0.0.1:xxxxx - "POST /pedidos HTTP/1.1" 200 OK
INFO:     Pedido creado: a309ddfc-...
INFO:     AGNO Team disponible: True
```

### Verificar archivos generados:

```bash
ls -la fotolibros-argentina/data/

# Deberías ver:
# - fotolibros.db (base de datos SQLite)
# - agno_config_a309ddfc.json (configuración AGNO)
```

---

## 🐛 Troubleshooting

### Error: "Cannot connect to backend"

**Causa**: Backend no está corriendo.

**Solución**:
```bash
cd fotolibros-argentina
python main.py
```

Verifica que esté en http://localhost:8000

---

### Error: "No se encontró el pedido"

**Causa**: ID de pedido incorrecto o pedido no existe.

**Solución**:
```bash
# Ver pedidos en la DB
cd fotolibros-argentina
sqlite3 data/fotolibros.db "SELECT id, cliente_nombre FROM pedidos ORDER BY created_at DESC LIMIT 5;"
```

---

### Error: "AGNO Team failed"

**Causa**: API keys no configuradas o inválidas.

**Solución**:
```bash
# Verificar .env
cat fotolibros-agno-backend/.env

# Debe tener:
# OPENROUTER_API_KEY=sk-or-v1-...
# MODEL_ID=openai/gpt-4o-mini
```

---

### Error: "Fotos no encontradas"

**Causa**: Las fotos no se subieron correctamente.

**Solución**:
```bash
# Verificar directorio de uploads
ls -la fotolibros-argentina/uploads/a309ddfc-*/

# Si está vacío, re-sube las fotos desde el frontend
```

---

## 📁 Estructura de Archivos de Prueba

```
fotolibros-argentina-v2/
├── fotolibros-argentina/
│   ├── main.py                      ← Iniciar con: python main.py
│   ├── data/
│   │   ├── fotolibros.db            ← Base de datos SQLite
│   │   └── agno_config_*.json       ← Configuraciones AGNO generadas
│   └── uploads/
│       └── a309ddfc-.../            ← Fotos subidas por pedido
│
├── procesar_pedido_agno.py          ← Procesar con AGNO Team
├── visualizar_agno_config.py        ← Ver diseño generado
└── ejecutar_fdf_con_agno.py         ← Ejecutar en FDF (opcional)
```

---

## ✅ Checklist de Prueba Completa

- [ ] Backend FastAPI corriendo en :8000
- [ ] Frontend React corriendo en :3000
- [ ] Crear pedido desde frontend
- [ ] Verificar pedido en SQLite
- [ ] Verificar fotos subidas en /uploads
- [ ] Ejecutar `procesar_pedido_agno.py`
- [ ] Ver archivo `agno_config_*.json` generado
- [ ] Ejecutar `visualizar_agno_config.py`
- [ ] (Opcional) Ejecutar `ejecutar_fdf_con_agno.py`

---

## 🎯 Comandos Rápidos (Copy-Paste)

```bash
# Terminal 1: Backend
cd fotolibros-argentina-v2/fotolibros-argentina && python main.py

# Terminal 2: Frontend
cd Fotolibros-Argentina- && npm run dev

# Terminal 3: Procesar pedido (después de crear desde frontend)
cd fotolibros-argentina-v2 && python procesar_pedido_agno.py

# Terminal 3: Visualizar (reemplaza ID)
python visualizar_agno_config.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

---

## 📞 Siguiente Paso

Una vez que hayas probado todo:

1. **Crea un pedido real desde http://localhost:3000**
2. **Procesa con AGNO Team**
3. **Visualiza el resultado**
4. **Si todo funciona**, puedes integrar con FDF

**¡El sistema está listo para producción!** 🎉
