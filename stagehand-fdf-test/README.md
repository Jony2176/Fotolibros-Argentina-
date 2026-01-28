# Test E2E - Stagehand v3 + Fotos desde BD

Test end-to-end automatizado para Fábrica de Fotolibros usando Stagehand v3 con fotos almacenadas en la base de datos SQLite.

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│               TEST E2E HIBRIDO                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  SQLite          Playwright         Stagehand v3       │
│  (BD)            (Bajo nivel)       (IA/Vision)        │
│    │                  │                   │            │
│    ▼                  ▼                   ▼            │
│  Leer fotos      Login directo      Selección smart   │
│  Pedidos         Upload files       Navegación IA     │
│                  Screenshots        Extract/Act       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Requisitos

- Node.js 18+
- Chrome instalado
- Base de datos SQLite con fotos
- API key de OpenRouter (o Gemini/Ollama)

## Instalación

```bash
npm install
```

## Configuración

### Opción 1: Variables de entorno

```bash
# LLM Provider (openrouter | gemini | ollama)
export LLM_PROVIDER=openrouter

# API Keys
export OPENROUTER_API_KEY=sk-or-v1-...
# O para Gemini gratis:
export GEMINI_API_KEY=AIza...

# Credenciales FDF (opcional, hay defaults)
export FDF_EMAIL=tu@email.com
export FDF_PASSWORD=tupassword
```

### Opción 2: Editar código

Las credenciales están hardcodeadas en `test-e2e-from-db.ts` (líneas 30-60).

## Uso

### 1. Crear pedido de prueba

```bash
npm run setup
```

Esto:
- Busca fotos existentes en `uploads/` o crea placeholders
- Crea un pedido en la BD SQLite
- Guarda el pedido ID en `last-test-pedido.txt`

### 2. Ejecutar test E2E

```bash
# Usar el último pedido con fotos
npm run e2e

# O especificar un pedido
npx tsx test-e2e-from-db.ts <pedido-id>
```

## Flujo del Test

1. **Login** (Playwright directo - selectores estables)
2. **Navegación** (Stagehand act - lenguaje natural)
   - Seleccionar versión "Para Profesionales"
   - Click en "Fotolibros"
   - Seleccionar producto 21x21
3. **Crear proyecto** (Stagehand act)
   - Llenar título del proyecto
4. **Subir fotos** (Playwright directo - operación de archivos)
   - Leer rutas desde BD con `db-reader.ts`
   - Upload con `setInputFiles()`
5. **Seleccionar template** (Stagehand extract + act)
   - Analizar templates disponibles
   - Evitar "Vacío"
   - Seleccionar según estilo del pedido
6. **Modo de relleno** (Stagehand act)
   - Click en "Relleno fotos smart"
   - Esperar procesamiento automático
7. **Verificación** (Stagehand extract)
   - Analizar fotos en canvas
   - Puntuación de calidad
   - Issues detectados

## Screenshots

Los screenshots se guardan en `screenshots/`:

```
01_login_page.png           - Página de login
02_logged_in.png            - Después del login
03_product_selected.png     - Producto seleccionado
04_project_created.png      - Proyecto creado
05_photos_uploaded.png      - Fotos subidas
06_templates.png            - Pantalla de templates
07_template_selected.png    - Template seleccionado
08_fill_options.png         - Opciones de relleno
09_after_smart_click.png    - Después de click smart
10_smart_fill_processing.png - Procesando smart fill
11_editor_loaded.png        - Editor cargado
```

## Modelos LLM

| Provider | Modelo | Costo | Velocidad |
|----------|--------|-------|-----------|
| **OpenRouter** | `openai/gpt-4o-mini` | $$ | Rápido |
| **Gemini** | `google/gemini-2.0-flash` | Gratis | Rápido |
| **Ollama** | `ollama/llava` | Gratis | Medio |

Para cambiar:

```bash
export LLM_PROVIDER=gemini  # o ollama
```

## Troubleshooting

### Error: "No page available"
- Asegúrate que Chrome esté instalado en la ruta correcta
- Actualiza `chromePath` en `test-e2e-from-db.ts:56`

### Error: "BD no encontrada"
- Ejecuta primero el backend Python para crear la BD
- O ejecuta `npm run setup` para crear un pedido

### Template "Vacío" seleccionado
- El LLM no está analizando correctamente
- Prueba con un modelo más potente: `gpt-4o` en lugar de `gpt-4o-mini`

### Fotos no se colocan
- Verifica que "Relleno fotos smart" fue clickeado
- Aumenta el tiempo de espera en línea 276 (`sleep(15000)`)
- Revisa screenshots para ver en qué paso falló

## Archivos

```
stagehand-fdf-test/
├── package.json              # Dependencias y scripts
├── db-reader.ts              # Lectura de BD SQLite
├── test-setup.ts             # Crear pedido de prueba
├── test-e2e-from-db.ts       # Test E2E principal
├── screenshots/              # Screenshots generados
├── last-test-pedido.txt      # Último pedido creado
└── README.md                 # Esta documentación
```

## Desarrollo

Para debugging, el test mantiene el browser abierto 60 segundos al finalizar.

Para ejecutar con más logs:

```bash
DEBUG=* npx tsx test-e2e-from-db.ts
```

## Licencia

MIT
