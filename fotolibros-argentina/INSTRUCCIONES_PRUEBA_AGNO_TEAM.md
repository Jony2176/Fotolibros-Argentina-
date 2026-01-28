# 🚀 Instrucciones para Probar AGNO Team Integrado

## ✅ INTEGRACIÓN COMPLETADA

El sistema **AGNO Team de 5 agentes especializados** ya está integrado con el backend existente.

### Cambios Realizados:

1. ✅ **Nuevo módulo**: `orquestador_agno_team.py` creado
2. ✅ **Orquestador modificado**: Usa AGNO Team automáticamente
3. ✅ **Dependencies actualizadas**: Pillow agregado para Vision AI
4. ✅ **Fallback inteligente**: Si AGNO Team falla, usa sistema legacy

---

## 🎯 Cómo Probar el Sistema

### Paso 1: Instalar/Actualizar Dependencias

```bash
cd C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-argentina

# Activar entorno virtual (si existe)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar que AGNO y Pillow están instalados
pip list | findstr agno
pip list | findstr Pillow
```

### Paso 2: Iniciar el Backend

```bash
# En la misma terminal
python main.py
```

Deberías ver en la consola:
```
✅ Sistema AGNO Team (5 agentes) cargado correctamente
```

Si ves esto, la integración está activa.

### Paso 3: Iniciar el Frontend

```bash
# En OTRA terminal
cd C:\Users\Usuario\Downloads\fotolibros_argentina\Fotolibros-Argentina-

npm run dev
```

Abre: http://localhost:3000

### Paso 4: Crear un Pedido de Prueba

1. **Abre el frontend**: http://localhost:3000
2. **Sube fotos** (al menos 5-10 fotos)
3. **Crea un pedido**
4. **Observa la consola del backend**

---

## 📊 Qué Esperar en la Consola

Si AGNO Team está funcionando, verás logs como:

```
[HH:MM:SS] [INFO] 🎨 Usando sistema AGNO Team (5 agentes especializados)...
[HH:MM:SS] [INFO] 📸 FASE 1/5: Analizando 10 fotos con Vision AI...
[HH:MM:SS] [INFO] 🎯 FASE 2/5: Detectando motivo del fotolibro...
[HH:MM:SS] [INFO] ⏰ FASE 3/5: Ordenando fotos cronológicamente...
[HH:MM:SS] [INFO] 📝 FASE 4/5: Generando textos emotivos...
[HH:MM:SS] [INFO] 🎨 FASE 5/5: Curando diseño artístico...

[HH:MM:SS] [INFO] 📸 Evento detectado: embarazo
[HH:MM:SS] [INFO] 📸 Confianza: 95%
[HH:MM:SS] [INFO] 📝 Título sugerido: "Nueve Meses de Amor"
[HH:MM:SS] [INFO] 🎨 Template sugerido: Romántico - Delicado

[HH:MM:SS] [INFO] 🎨 Usando diseño curado por AGNO Team...
[HH:MM:SS] [INFO] 📐 Template: romantico
[HH:MM:SS] [INFO] 📝 Título: "Nueve Meses de Amor"
[HH:MM:SS] [INFO] 💌 Dedicatoria generada
[HH:MM:SS] [INFO] 📖 Capítulos: 3
```

---

## 🔍 Comparación: Antes vs Después

### ANTES (Sistema Legacy)
```
[INFO] Analizando 10 fotos...
[INFO] Evento detectado: otro
[INFO] Confianza: 50%
```

### DESPUÉS (AGNO Team)
```
[INFO] 🎨 Usando sistema AGNO Team (5 agentes especializados)...
[INFO] 📸 FASE 1/5: Analizando 10 fotos con Vision AI...
   ✓ 10 fotos analizadas
[INFO] 🎯 FASE 2/5: Detectando motivo del fotolibro...
   ✓ Motivo: pregnancy (95%)
   ✓ Template sugerido: Romántico - Delicado
[INFO] ⏰ FASE 3/5: Ordenando fotos cronológicamente...
   ✓ Tipo cronológico: pregnancy
   ✓ Fotos reordenadas: 10
   ✓ Hitos detectados: 3
[INFO] 📝 FASE 4/5: Generando textos emotivos...
   ✓ Título: "Nueve Meses de Amor"
   ✓ Capítulos: 3
   ✓ Leyendas: 10
[INFO] 🎨 FASE 5/5: Curando diseño artístico...
   ✓ Template final: Romántico - Delicado
   ✓ Páginas hero: 3
   ✓ Estilo tipográfico: elegant

[INFO] 📝 Título sugerido: "Nueve Meses de Amor"
[INFO] 🎨 Template sugerido: Romántico - Delicado
```

---

## 🎨 Características del Sistema AGNO Team

### 1. **PhotoAnalyzer**
- Analiza CADA foto con Vision AI
- Detecta emociones (alegría, amor, nostalgia, etc.)
- Califica calidad compositiva (1-10)
- Asigna importancia narrativa
- Genera títulos emotivos

### 2. **MotifDetector**
- Detecta 17 motivos específicos:
  - wedding, travel, pregnancy, baby-shower
  - baby-first-year, birthday-child, mothers-day
  - fathers-day, family, pet, generic, etc.
- Carga configuración de diseño específica
- Confidence scoring

### 3. **ChronologySpecialist**
- Ordena fotos cronológicamente
- Detecta progresión temporal:
  - Embarazo: semana 8 → 40
  - Viaje: ruta geográfica
  - Evento: preparación → ceremonia → fiesta
- Identifica hitos clave

### 4. **StoryGenerator**
- Genera textos PROFUNDAMENTE emotivos
- Título poderoso y específico
- Dedicatoria personalizada (hace llorar)
- Leyendas por foto (momentos, NO descripciones)
- Capítulos narrativos
- Texto de contratapa emotivo

### 5. **DesignCurator**
- Selecciona template óptimo
- Planifica layout (hero/collage/respiro)
- Define paleta de colores
- Selecciona decoraciones
- Objetivo de calidad: 8/10 mínimo

---

## 🐛 Troubleshooting

### Error: "Sistema AGNO Team no disponible"

**Causa**: No se pudo importar el módulo AGNO Team

**Solución**:
```bash
# Verificar que el directorio existe
dir C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-agno-backend

# Instalar dependencias de AGNO
cd C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-argentina-v2\fotolibros-agno-backend
pip install agno python-dotenv pillow
```

### Error: "OPENROUTER_API_KEY not found"

**Causa**: Falta la API key de OpenRouter

**Solución**:
Verificar que `.env` tiene:
```bash
OPENROUTER_API_KEY=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
```

### Sistema usa fallback (sistema legacy)

**Causa**: AGNO Team falló, sistema usa backup automático

**Logs esperados**:
```
[WARN] Error con AGNO Team, usando fallback: ...
```

**Solución**: Revisar logs detallados en consola para ver el error específico

---

## 📝 Casos de Prueba Sugeridos

### Caso 1: Álbum de Embarazo
- **Fotos**: 10-15 fotos de embarazo
- **Resultado esperado**:
  - Motivo: `pregnancy`
  - Título: "Nueve Meses de Amor" (o similar)
  - Fotos ordenadas por semanas
  - Template: Romántico - Delicado

### Caso 2: Viaje
- **Fotos**: Fotos de diferentes ciudades
- **Resultado esperado**:
  - Motivo: `travel`
  - Fotos ordenadas por ruta geográfica
  - Template: Moderno - Geométrico

### Caso 3: Boda
- **Fotos**: Fotos de boda
- **Resultado esperado**:
  - Motivo: `wedding`
  - Fotos ordenadas: preparación → ceremonia → fiesta
  - Template: Romántico - Flores

---

## 🎯 Próximos Pasos

Una vez confirmado que funciona:

1. **Revisar textos generados** en la base de datos
2. **Validar orden cronológico** de las fotos
3. **Verificar template seleccionado**
4. **Testear con diferentes tipos de eventos**

---

## 💡 Notas Importantes

- El sistema tiene **fallback automático** al sistema legacy si AGNO Team falla
- Los logs son **muy detallados** para debugging
- Cada fase del procesamiento se loguea por separado
- El sistema es **compatible con el flujo existente**
- No rompe funcionalidad actual, solo la **mejora**

---

**¿Listo para probar?** 🚀

Ejecuta los pasos 1-4 y observa la magia de los 5 agentes trabajando juntos!
