---
name: fotolibros-fdf
description: Ejecutar disenos de fotolibros en el editor de Fabrica de Fotolibros (FDF)
metadata: {"clawdbot":{"requires":{"config":["browser.enabled"],"env":["FDF_USER","FDF_PASS"]},"emoji":"📚","primaryEnv":"FDF_USER"}}
---

# Skill: Fotolibros FDF

Este skill te permite ejecutar disenos de fotolibros en el editor online de Fabrica de Fotolibros.

## Credenciales

- **URL**: https://online.fabricadefotolibros.com/
- **Usuario**: Variable de entorno `FDF_USER`
- **Password**: Variable de entorno `FDF_PASS`

## Catalogo de Productos

| Codigo | Tamano | Tapa | Pags Base | Nombre en Editor |
|--------|--------|------|-----------|------------------|
| CU-21x21-BLANDA | 21x21 | Blanda | 22 | "Cuadrado 21x21 - Tapa Blanda" |
| CU-21x21-DURA | 21x21 | Dura | 22 | "Cuadrado 21x21 - Tapa Dura" |
| CU-29x29-DURA | 29x29 | Dura | 20 | "Cuadrado 29x29 - Tapa Dura" |
| AP-28x22-DURA | 28x22 | Dura | 22 | "Apaisado 28x22 - Tapa Dura" |
| VE-22x28-DURA | 22x28 | Dura | 22 | "Vertical 22x28 - Tapa Dura" |

## Flujo Completo en el Editor

### Paso 1: Abrir Browser y Navegar

```bash
clawdbot browser start
clawdbot browser navigate https://online.fabricadefotolibros.com/
clawdbot browser wait --load networkidle
clawdbot browser snapshot --interactive
```

### Paso 2: Login

1. Buscar boton "Ingresar" o "Login" o "Iniciar Sesion"
2. Click en el boton de login
3. Esperar modal o pagina de login
4. Ingresar usuario en campo email/usuario
5. Ingresar password en campo password
6. Click en boton "Ingresar" o "Entrar"
7. Esperar redireccion al dashboard
8. Verificar que aparece menu de usuario o "Mis Proyectos"

```bash
clawdbot browser snapshot --interactive
# Buscar ref del boton login
clawdbot browser click <ref-login>
clawdbot browser wait --text "Usuario" --timeout-ms 5000
clawdbot browser snapshot --interactive
clawdbot browser type <ref-email> "$FDF_USER"
clawdbot browser type <ref-pass> "$FDF_PASS"
clawdbot browser click <ref-submit>
clawdbot browser wait --load networkidle
```

### Paso 3: Crear Nuevo Proyecto

1. Click en "Nuevo Proyecto" o "Crear Fotolibro" o icono "+"
2. Seleccionar categoria "Fotolibros"
3. Seleccionar tamano segun codigo de producto:
   - 21x21 → buscar "21x21" o "Cuadrado"
   - 29x29 → buscar "29x29" o "Cuadrado Grande"
   - 28x22 → buscar "Apaisado"
   - 22x28 → buscar "Vertical"
4. Seleccionar tipo de tapa (Dura o Blanda)
5. Ingresar nombre del proyecto: "PED-{pedido_id}"
6. Click en "Crear" o "Continuar"
7. Esperar que cargue el editor

### Paso 4: Subir Fotos

**IMPORTANTE**: Subir fotos EN EL ORDEN EXACTO del JSON `chronology.ordered_photos`

1. Buscar panel de fotos (generalmente a la izquierda)
2. Click en "Subir Fotos" o icono de camara/imagen
3. Se abre selector de archivos
4. Subir fotos UNA POR UNA en orden o en batch manteniendo orden
5. Esperar barra de progreso
6. Verificar que todas las fotos aparecen en el panel

```bash
# Para cada foto del array ordered_photos
clawdbot browser upload /ruta/a/foto.jpg
clawdbot browser wait --text "100%" --timeout-ms 30000
```

**Notificar progreso cada 15 fotos**:
- "📤 Subiendo fotos (15/45)..."
- "📤 Subiendo fotos (30/45)..."

### Paso 5: Seleccionar Template/Plantilla

1. Ir a seccion "Plantillas" o "Templates" o "Disenos"
2. Buscar la categoria segun el estilo:
   - minimalista → "Minimal", "Clean", "Simple", "Blanco"
   - clasico → "Classic", "Elegant", "Tradicional"
   - divertido → "Fun", "Party", "Colorful", "Fiesta"
   - romantico → "Romance", "Love", "Floral", "Boda"
   - infantil → "Kids", "Baby", "Infantil", "Ninos"
3. Buscar template especifico de `design.template_choice.primary`
4. Click en el template para previsualizar
5. Click en "Aplicar" o "Usar Template"
6. Confirmar aplicacion si hay dialogo

### Paso 6: Insertar Textos

**Textos del JSON `story`:**

1. **Titulo de Portada** (`story.cover.title`):
   - Ir a pagina de portada
   - Click en area de texto de titulo
   - Borrar texto placeholder
   - Escribir titulo del JSON

2. **Subtitulo** (`story.cover.subtitle`):
   - Click en area de subtitulo si existe
   - Escribir subtitulo

3. **Dedicatoria** (`story.dedication.text`):
   - Buscar pagina de dedicatoria (generalmente pagina 1 o 2)
   - Click en area de texto
   - Escribir dedicatoria

4. **Leyendas de fotos** (`story.photo_captions[]`):
   - Para cada foto con leyenda asignada
   - Click en foto → agregar texto
   - Escribir leyenda

### Paso 7: Ordenar Fotos en Paginas

Si el template no auto-fill, ordenar manualmente:

1. Para cada pagina segun `design.layout_strategy`:
   - Paginas "hero": 1 foto grande
   - Paginas "collage": multiples fotos
   - Paginas "respiro": texto o espacio

2. Arrastrar fotos del panel a las posiciones
3. Respetar orden de `chronology.ordered_photos`

### Paso 8: Smart Fill (si disponible)

Algunos templates tienen "Smart Fill" o "Auto-rellenar":

1. Click en "Smart Fill" o "Auto"
2. Esperar procesamiento
3. Verificar resultado
4. Ajustar si es necesario

### Paso 9: Previsualizar

1. Click en "Vista Previa" o "Preview" o icono de ojo
2. Navegar por todas las paginas
3. Verificar:
   - Fotos correctamente posicionadas
   - Textos visibles y legibles
   - No hay paginas vacias accidentales
   - Template aplicado correctamente

### Paso 10: Capturar Preview para Confirmacion

```bash
# Capturar screenshots de paginas clave
clawdbot browser screenshot --full-page
# o navegar pagina por pagina y capturar
```

### Paso 11: Finalizar (solo si aprobado)

1. Click en "Finalizar" o "Enviar a Produccion" o "Guardar y Pedir"
2. Confirmar en dialogo si aparece
3. Esperar confirmacion del sistema
4. Guardar numero de pedido FDF si aparece

## Mapeo de Estilos a Busqueda en FDF

| Mi Estilo | Buscar en FDF | Keywords alternativos |
|-----------|---------------|----------------------|
| minimalista | "Minimal" | "Clean", "Simple", "White", "Blanco" |
| clasico | "Classic" | "Elegant", "Traditional", "Vintage" |
| divertido | "Fun" | "Party", "Colorful", "Bright", "Fiesta" |
| romantico | "Romance" | "Love", "Floral", "Wedding", "Soft" |
| infantil | "Kids" | "Baby", "Cartoon", "Playful", "Child" |

## Manejo de Errores Comunes

| Error | Solucion |
|-------|----------|
| "Sesion expirada" | Re-login y continuar desde ultimo paso |
| "Foto no soportada" | Saltar esa foto, notificar, continuar |
| "Proyecto no guardado" | Esperar 5s, reintentar guardado |
| "Editor no responde" | Refresh pagina, esperar 10s, reintentar |
| "Timeout en carga de foto" | Reintentar esa foto hasta 3 veces |
| "Template no encontrado" | Usar template alternativo de `template_choice.fallback` |
| "Elemento no visible" | Scroll, esperar, reintentar |

## Verificaciones de Calidad

Antes de pedir confirmacion, verificar:

- [ ] Todas las fotos subidas (comparar cantidad)
- [ ] Template correcto aplicado
- [ ] Titulo de portada correcto
- [ ] Dedicatoria insertada (si aplica)
- [ ] No hay paginas vacias
- [ ] Fotos no cortadas incorrectamente

## Ejemplo de Sesion Completa

```
1. browser navigate https://online.fabricadefotolibros.com/
2. browser snapshot --interactive
3. browser click [login-btn]
4. browser type [email-field] "$FDF_USER"
5. browser type [pass-field] "$FDF_PASS"
6. browser click [submit-btn]
7. browser wait --load networkidle
8. browser snapshot
9. browser click [nuevo-proyecto]
10. browser click [fotolibros]
11. browser click [21x21-dura]
12. browser type [nombre-proyecto] "PED-2026-0042"
13. browser click [crear]
14. browser wait --load networkidle
15. # Subir fotos en orden...
16. browser click [templates]
17. browser click [elegant-template]
18. browser click [aplicar]
19. # Insertar textos...
20. browser click [preview]
21. browser screenshot
22. # Esperar confirmacion...
23. browser click [finalizar]
```

## Variables de Entorno Requeridas

- `FDF_USER`: Usuario para login en FDF
- `FDF_PASS`: Password para login en FDF

## Notas Importantes

1. **Orden de fotos es CRITICO**: AGNO ya decidio el orden cronologico/narrativo
2. **No improvisar**: El JSON tiene TODO decidido
3. **Notificar progreso**: Mantener informado por Telegram
4. **Screenshots en errores**: Siempre capturar antes de reportar
5. **Confirmacion obligatoria**: Si `modo_confirmacion: true`, NO finalizar sin aprobacion
