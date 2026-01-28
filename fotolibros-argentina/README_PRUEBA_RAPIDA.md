# 🚀 Prueba Rápida del Backend con AGNO Team

## TL;DR - 3 Comandos para Probar Todo

```bash
# 1. Iniciar backend (Terminal 1)
cd fotolibros-argentina && python main.py

# 2. Iniciar frontend (Terminal 2) 
cd ../Fotolibros-Argentina- && npm run dev

# 3. Crear pedido desde http://localhost:3000
# Luego ejecutar (Terminal 3):
cd ../fotolibros-argentina-v2 && python visualizar_agno_config.py a309ddfc
```

---

## 📋 Paso a Paso Detallado

### ✅ **Paso 1: Verificar que tienes el pedido de prueba**

Ya tienes un pedido creado con ID: `a309ddfc-ae43-40e7-ba66-80dc1a330cdf`

Puedes verificarlo:

```bash
cd fotolibros-argentina
sqlite3 data/fotolibros.db "SELECT id, cliente_nombre, estado FROM pedidos WHERE id LIKE 'a309ddfc%';"
```

**Salida esperada**:
```
a309ddfc-ae43-40e7-ba66-80dc1a330cdf|JONY|pendiente
```

---

### ✅ **Paso 2: Verificar fotos**

```bash
ls -la fotolibros-argentina/uploads/a309ddfc-ae43-40e7-ba66-80dc1a330cdf/
```

**Deberías ver 12 fotos** (jpg, png, jpeg)

---

### ✅ **Paso 3: Verificar que ya procesaste con AGNO Team**

```bash
ls -la fotolibros-argentina/data/agno_config_a309ddfc.json
```

**Si existe el archivo**: Ya procesaste el pedido ✓

**Si NO existe**: Ejecuta:
```bash
python procesar_pedido_agno.py
```

---

### ✅ **Paso 4: Visualizar el Diseño (AHORA MISMO)**

```bash
python visualizar_agno_config.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

**Esto mostrará**:
- ✅ Título: "Momentos que Inspiran"
- ✅ Dedicatoria completa
- ✅ 3 Capítulos con títulos emotivos
- ✅ 12 Leyendas por foto
- ✅ Configuración de diseño

---

### ✅ **Paso 5: Ver el archivo JSON generado**

```bash
cat fotolibros-argentina/data/agno_config_a309ddfc.json | head -50
```

O ábrelo con cualquier editor de texto.

---

## 🔧 Prueba con el Backend Corriendo

### Terminal 1: Iniciar Backend

```bash
cd C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-argentina
python main.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Terminal 2: Probar endpoint de salud

```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{"status":"ok"}
```

### Terminal 3: Ver pedidos via API

```bash
curl http://localhost:8000/pedidos | python -m json.tool
```

Deberías ver tu pedido `a309ddfc...` en la lista.

---

## 🎨 Prueba con el Frontend

### Terminal 1: Backend (si no está corriendo)

```bash
cd fotolibros-argentina
python main.py
```

### Terminal 2: Frontend

```bash
cd ../Fotolibros-Argentina-
npm run dev
```

### Navegador

1. Abre http://localhost:3000
2. Clic en "Empezar mi fotolibro"
3. **Producto**: Selecciona "Fotolibro Cuadrado 20x20cm - 40 páginas"
4. **Estilo**: Cualquiera
5. **Páginas**: 40
6. **Fotos**: Sube 10-12 fotos
7. **Entrega**: Completa datos
8. **Pago**: Transferencia
9. Clic en "Finalizar Pedido"

**Obtendrás un nuevo ID de pedido** (ej: `b1234567-...`)

### Terminal 3: Procesar el nuevo pedido

```bash
cd fotolibros-argentina-v2
python procesar_pedido_agno.py
```

Selecciona el pedido que acabas de crear.

---

## ✨ Verificación Rápida (Copy-Paste)

Ejecuta este bloque completo:

```bash
# Ir al directorio raíz
cd C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2

# Verificar pedido existente
echo "=== Pedido de prueba ==="
cd fotolibros-argentina
sqlite3 data/fotolibros.db "SELECT id, cliente_nombre, estado, created_at FROM pedidos WHERE id LIKE 'a309ddfc%';"

# Verificar fotos
echo ""
echo "=== Fotos subidas ==="
ls uploads/a309ddfc-ae43-40e7-ba66-80dc1a330cdf/ | wc -l

# Verificar configuración AGNO
echo ""
echo "=== Configuración AGNO ==="
ls -lh data/agno_config_a309ddfc.json

cd ..

# Visualizar diseño
echo ""
echo "=== Visualizando diseño ==="
python visualizar_agno_config.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

---

## 🎯 ¿Qué Deberías Ver?

Si todo funciona correctamente:

```
✓ Backend corriendo en :8000
✓ Frontend corriendo en :3000
✓ Pedido en SQLite: a309ddfc-...
✓ 12 fotos en /uploads
✓ Archivo agno_config_a309ddfc.json (18 KB)
✓ Visualización con título, capítulos y leyendas
```

---

## 🐛 Si Algo Falla

### Backend no inicia

```bash
# Verificar dependencias
pip install fastapi uvicorn python-multipart sqlite3 python-dotenv

# Verificar puerto libre
netstat -ano | findstr :8000
```

### Frontend no inicia

```bash
# Reinstalar dependencias
cd Fotolibros-Argentina-
npm install
npm run dev
```

### No se procesa con AGNO Team

```bash
# Verificar .env
cat fotolibros-agno-backend/.env

# Debe tener:
# OPENROUTER_API_KEY=sk-or-v1-...
# MODEL_ID=openai/gpt-4o-mini
```

---

## 📞 Siguiente Paso

Una vez que veas el diseño generado con `visualizar_agno_config.py`:

```bash
# Ejecutar en FDF (opcional)
python ejecutar_fdf_con_agno.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

Esto abrirá Chrome y creará el fotolibro automáticamente en FDF.

---

## ✅ Checklist Rápido

- [ ] Backend corriendo (python main.py)
- [ ] Pedido existe en SQLite
- [ ] Fotos subidas (12 archivos)
- [ ] Archivo agno_config_a309ddfc.json existe
- [ ] Visualizador muestra el diseño
- [ ] (Opcional) Ejecutar en FDF

**¡Todo listo para probar!** 🎉
