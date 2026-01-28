# 🎨 Cómo Ejecutar Fotolibros AGNO Team en FDF

Esta guía explica cómo ver y ejecutar los fotolibros generados por AGNO Team en la Fábrica de Fotolibros (FDF).

---

## 📋 Tabla de Contenidos

1. [Resumen del Flujo](#resumen-del-flujo)
2. [Prerequisitos](#prerequisitos)
3. [Paso 1: Visualizar el Diseño](#paso-1-visualizar-el-diseño)
4. [Paso 2: Ejecutar en FDF](#paso-2-ejecutar-en-fdf)
5. [Estructura del Fotolibro](#estructura-del-fotolibro)
6. [Troubleshooting](#troubleshooting)

---

## 🎯 Resumen del Flujo

```
┌────────────────────────────────────────────────────────────────┐
│                    FLUJO COMPLETO                              │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  1. Cliente sube fotos → Backend FastAPI                      │
│  2. Pedido creado → SQLite (fotolibros.db)                    │
│  3. AGNO Team analiza → agno_config_XXXXX.json               │
│  4. Visualizar diseño → visualizar_agno_config.py             │
│  5. Ejecutar en FDF → ejecutar_fdf_con_agno.py                │
│  6. Navegador automatizado → Crea fotolibro en FDF            │
│  7. Descarga PDF → Entrega al cliente                         │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## ✅ Prerequisitos

### 1. Archivo de Configuración Generado

Primero debes haber ejecutado el procesamiento con AGNO Team:

```bash
python procesar_pedido_agno.py
```

Esto genera:
```
fotolibros-argentina/data/agno_config_a309ddfc.json
```

### 2. Variables de Entorno Configuradas

En tu archivo `.env`:

```env
# AGNO Team
OPENROUTER_API_KEY=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
MODEL_ID=openai/gpt-4o-mini

# FDF (Fábrica de Fotolibros)
FDF_EMAIL=tu_email@ejemplo.com
FDF_PASSWORD=tu_password_fdf

# Gemini Vision (para diseño inteligente)
GEMINI_API_KEY=tu_api_key_de_gemini
```

### 3. Dependencias Instaladas

```bash
pip install playwright agno python-dotenv
playwright install chromium
```

---

## 📊 Paso 1: Visualizar el Diseño

Antes de ejecutar en FDF, puedes ver cómo quedará el fotolibro:

```bash
python visualizar_agno_config.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

**Salida esperada:**

```
######################################################################
  VISUALIZADOR AGNO TEAM
######################################################################

======================================================================
  TAPA DEL FOTOLIBRO
======================================================================
  Titulo:     Momentos que Inspiran
  Subtitulo:  Un viaje a través de instantes eternos
  Autor:      Jony - 2024

======================================================================
  DEDICATORIA (Pagina 1)
======================================================================
  Para: Para todos los que comparten el viaje de la vida
  "A esos momentos fugaces que han dejado huella en mi alma..."

======================================================================
  ESTRUCTURA DEL FOTOLIBRO
======================================================================
  Total de capitulos: 3
  Total de fotos: 12

  CAPITULO 1: "El Susurro de la Existencia"
    Tono emocional: nostálgico
    Fotos en este capitulo (4 fotos):
      Pagina 3: "El instante en que la vida nos habló en susurros."
      Pagina 4: "Cuando capturamos el reflejo de nuestras auténticas sonrisas."
      ...

  CAPITULO 2: "Los Días de Luz"
    Tono emocional: alegre
    ...

  CAPITULO 3: "El Viaje Interior"
    Tono emocional: reflectivo
    ...

======================================================================
  RESUMEN FINAL
======================================================================
  Titulo:          "Momentos que Inspiran"
  Template:        Moderno
  Total paginas:   ~17
  Total fotos:     12
  Capitulos:       3
```

---

## 🚀 Paso 2: Ejecutar en FDF

Una vez que hayas validado el diseño, ejecuta en FDF:

```bash
python ejecutar_fdf_con_agno.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

### ¿Qué hace este script?

1. **Inicia navegador Chrome** (visible, no headless)
2. **Login automático en FDF** con tus credenciales
3. **Crea proyecto nuevo** con el template detectado por AGNO Team
4. **Sube fotos** en el orden cronológico determinado por ChronologySpecialist
5. **Configura textos**:
   - Título de tapa: "Momentos que Inspiran"
   - Dedicatoria: Texto emotivo generado por StoryGenerator
   - Leyendas por foto: Textos individuales para cada imagen
6. **Diseña capítulos** según la estructura de StoryGenerator
7. **Configura contratapa** con texto de cierre y epílogo

### Salida esperada:

```
======================================================================
  EJECUTOR FDF CON AGNO TEAM
======================================================================

[1/7] Cargando configuracion AGNO Team...
      Archivo: fotolibros-argentina/data/agno_config_a309ddfc.json
      [OK] Configuracion cargada
      Motivo: generic
      Titulo: "Momentos que Inspiran"
      Fotos: 12
      Capitulos: 3

[2/7] Inicializando toolkit FDF...
      [OK] Navegador listo

[3/7] Iniciando sesion en FDF...
      Usuario: tu_email@ejemplo.com
      [OK] Sesion iniciada

[4/7] Creando proyecto nuevo...
      Template AGNO: Moderno
      Template FDF: moderno
      [OK] Proyecto creado: 12345

[5/7] Subiendo 12 fotos en orden cronologico...
      [1/12] Subiendo: df543a27-271e-461e-92f5-6c2af2572164.png
      [2/12] Subiendo: 18006573-d889-4d61-828c-e31375fa22e5.png
      ...
      [OK] Todas las fotos subidas

[6/7] Disenando fotolibro con configuracion AGNO...

      === TEXTOS DE TAPA ===
      Titulo: "Momentos que Inspiran"
      Subtitulo: "Un viaje a través de instantes eternos"
      Autor: "Jony - 2024"

      === DEDICATORIA ===
      Para: Para todos los que comparten el viaje de la vida
      Texto: A esos momentos fugaces que han dejado huella...

      === CAPITULOS ===
      Capitulo 1: "El Susurro de la Existencia"
         Tono: nostálgico
         Fotos: 4
         - Foto 1: "El instante en que la vida nos habló..."
         ...

[OK] ===================================
[OK] FOTOLIBRO COMPLETADO EXITOSAMENTE
[OK] ===================================

      Titulo: "Momentos que Inspiran"
      Paginas disenadas: 17
      Fotos incluidas: 12
      Capitulos: 3

      El fotolibro esta listo para revision en el navegador.
      Revisa el diseno y descargalo desde FDF.

      Presiona ENTER para cerrar el navegador...
```

---

## 📖 Estructura del Fotolibro

El fotolibro generado tiene esta estructura:

```
┌─────────────────────────────────────┐
│ TAPA                                │
│ • Título emotivo                    │
│ • Subtítulo                         │
│ • Autor/Año                         │
├─────────────────────────────────────┤
│ PAGINA 1: Dedicatoria               │
│ • Texto emotivo personalizado       │
├─────────────────────────────────────┤
│ PAGINA 2: Apertura Capítulo 1       │
│ • Título: "El Susurro..."           │
│ • Intro del capítulo                │
├─────────────────────────────────────┤
│ PAGINAS 3-6: Fotos Capítulo 1       │
│ • 4 fotos con leyendas emotivas     │
├─────────────────────────────────────┤
│ PAGINA 7: Apertura Capítulo 2       │
│ • Título: "Los Días de Luz"         │
│ • Intro del capítulo                │
├─────────────────────────────────────┤
│ PAGINAS 8-10: Fotos Capítulo 2      │
│ • 3 fotos con leyendas emotivas     │
├─────────────────────────────────────┤
│ PAGINA 11: Apertura Capítulo 3      │
│ • Título: "El Viaje Interior"       │
│ • Intro del capítulo                │
├─────────────────────────────────────┤
│ PAGINAS 12-16: Fotos Capítulo 3     │
│ • 5 fotos con leyendas emotivas     │
├─────────────────────────────────────┤
│ CONTRATAPA                          │
│ • Texto de cierre                   │
│ • Frase inspiradora                 │
│ • Epílogo                           │
└─────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Error: "No se encontró agno_config_*.json"

**Causa**: No has ejecutado el procesamiento AGNO Team primero.

**Solución**:
```bash
python procesar_pedido_agno.py
```

---

### Error: "Faltan credenciales de FDF"

**Causa**: Variables `FDF_EMAIL` o `FDF_PASSWORD` no están en `.env`.

**Solución**: Agrega en `.env`:
```env
FDF_EMAIL=tu_email@fabricadefotolibros.com
FDF_PASSWORD=tu_password
```

---

### Error: "Login failed"

**Causa**: Credenciales incorrectas o FDF cambió su página de login.

**Solución**:
1. Verifica que tus credenciales sean correctas
2. Intenta login manual en https://www.fabricadefotolibros.com
3. Revisa los logs del navegador

---

### El navegador se queda colgado

**Causa**: Conexión lenta o elemento no encontrado.

**Solución**:
- El script tiene reintentos automáticos (3 intentos por acción)
- Si persiste, presiona Ctrl+C y vuelve a ejecutar
- Puedes modificar `headless=False` para ver qué está pasando

---

### Las fotos no se suben correctamente

**Causa**: Rutas de fotos incorrectas.

**Solución**: Verifica que las fotos estén en:
```
fotolibros-argentina/uploads/a309ddfc-.../foto.jpg
```

---

## 📁 Archivos Importantes

```
fotolibros-argentina-v2/
├── procesar_pedido_agno.py           # Paso 1: Procesar con AGNO Team
├── visualizar_agno_config.py         # Paso 2: Ver diseño sin ejecutar
├── ejecutar_fdf_con_agno.py          # Paso 3: Ejecutar en FDF
│
├── fotolibros-argentina/data/
│   └── agno_config_a309ddfc.json     # Configuración generada
│
└── fotolibros-agno-backend/agents/
    ├── photo_analyzer.py              # Agente 1: Vision AI
    ├── motif_detector.py              # Agente 2: Detección de motivo
    ├── chronology_specialist.py       # Agente 3: Orden cronológico
    ├── story_generator.py             # Agente 4: Textos emotivos
    └── design_curator.py              # Agente 5: Diseño artístico
```

---

## 🎯 Comandos Rápidos

```bash
# 1. Procesar pedido con AGNO Team
python procesar_pedido_agno.py

# 2. Ver diseño generado
python visualizar_agno_config.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf

# 3. Ejecutar en FDF
python ejecutar_fdf_con_agno.py a309ddfc-ae43-40e7-ba66-80dc1a330cdf
```

---

## 📞 Soporte

Si tienes problemas:

1. Verifica que todas las dependencias estén instaladas
2. Revisa que las variables de entorno estén configuradas
3. Ejecuta primero el visualizador para validar la configuración
4. Revisa los logs del navegador cuando ejecutes en FDF

---

## 🎉 ¡Listo!

Ahora tienes un sistema completo que:

✅ Analiza fotos con Vision AI  
✅ Detecta motivos automáticamente  
✅ Ordena fotos cronológicamente  
✅ Genera textos emotivos que "hacen llorar"  
✅ Cura diseño artístico profesional  
✅ Ejecuta automáticamente en FDF  

**El resultado: Fotolibros con alma y emoción, no productos genéricos.**
