# 🎨 Sistema AGNO de Fotolibros Artísticos

Sistema de IA multi-agente que crea fotolibros personalizados con **alma y emoción**, no productos genéricos.

## 🌟 Características

- **5 Agentes Especializados** coordinados con AGNO Framework
- **Análisis Emocional** de cada foto con Vision AI
- **17 Motivos Específicos** detectados automáticamente
- **Ordenamiento Cronológico Inteligente** (embarazo/viaje/evento)
- **Textos Profundamente Emotivos** generados con IA
- **Curación Artística Profesional** de diseño y layout

## 📦 Instalación

### 1. Crear entorno virtual

```bash
cd fotolibros-agno-backend

# Crear entorno virtual
python -m venv .venv

# Activar (Windows)
.venv\Scripts\activate

# Activar (Linux/Mac)
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install agno python-dotenv pillow
```

### 3. Configurar API Key

El archivo `.env` ya está configurado con tu API key de OpenRouter:

```bash
# .env
OPENROUTER_API_KEY=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
MODEL_ID=openai/gpt-4o-mini
```

## 🚀 Uso

### Opción 1: Procesar fotos de un directorio

```bash
python main.py --photos-dir ./mis_fotos --client "Ana y Carlos" --output config.json
```

### Opción 2: Procesar con hint de motivo

```bash
python main.py --photos-dir ./embarazo --client "María" --hint pregnancy
```

### Opción 3: Procesar fotos específicas

```bash
python main.py --photos foto1.jpg foto2.jpg foto3.jpg --client "Juan"
```

### Opción 4: Desde base de datos (integración futura)

```python
from db_utils import process_pedido_from_db

config = process_pedido_from_db('PEDIDO_123', 'output.json')
```

## 📋 Parámetros

```
--photos-dir DIR       Directorio con fotos a procesar
--photos FILE [FILE]   Lista de rutas de fotos específicas
--client NAME          Nombre del cliente (REQUERIDO)
--recipient NAME       Destinatario del fotolibro (opcional)
--hint TYPE            Hint del tipo de evento (opcional)
--year YEAR            Año del evento (opcional)
--output PATH          Ruta del archivo de salida (default: data/fotolibro_config.json)
```

### Hints de motivo disponibles:

- `wedding` - Bodas
- `travel` - Viajes
- `pregnancy` - Embarazo
- `baby-shower` - Baby shower
- `baby-first-year` - Primer año del bebé
- `birthday-child` - Cumpleaños infantil
- `birthday-teen` - Cumpleaños adolescente (15 años)
- `mothers-day` - Día de la madre
- `fathers-day` - Día del padre
- `anniversary-couple` - Aniversario de pareja
- `family` - Familia
- `pet` - Mascotas
- `generic` - Genérico

## 🎯 Flujo del Sistema

```
ENTRADA: Fotos + Contexto del Cliente
   │
   ├─► FASE 1: PhotoAnalyzer
   │    └─► Analiza cada foto (emoción, composición, importancia)
   │
   ├─► FASE 2: MotifDetector
   │    └─► Detecta motivo (17 opciones) + configuración de diseño
   │
   ├─► FASE 3: ChronologySpecialist
   │    └─► Ordena cronológicamente + identifica hitos
   │
   ├─► FASE 4: StoryGenerator
   │    └─► Genera textos emotivos (títulos, dedicatorias, leyendas)
   │
   └─► FASE 5: DesignCurator
        └─► Toma decisiones artísticas (template, layout, colores)

SALIDA: fotolibro_config.json
```

## 📄 Formato de Salida

El sistema genera un archivo JSON con la configuración completa del fotolibro:

```json
{
  "metadata": {
    "client_name": "Ana y Carlos",
    "recipient_name": "Nuestro bebé",
    "year": "2024",
    "total_photos": 25
  },
  "photos": [
    {
      "filepath": "/path/to/photo1.jpg",
      "filename": "photo1.jpg",
      "emotion": "amor",
      "importance": 9,
      "caption": "El día que supimos que venías en camino",
      "week": 12
    }
  ],
  "motif": {
    "type": "pregnancy",
    "confidence": 95,
    "design_config": {...}
  },
  "chronology": {
    "type": "pregnancy",
    "temporal_metadata": {
      "weeks": [8, 12, 16, 20, 24, 28, 32, 36, 40],
      "milestones": ["Primera ecografía", "Baby shower", "Parto"]
    }
  },
  "story": {
    "cover": {
      "title": "Nueve Meses de Amor",
      "subtitle": "Ana y Carlos - 2024"
    },
    "dedication": {
      "text": "Para nuestro bebé, cada día de espera fue un paso más cerca de ti...",
      "recipient": "Para nuestro bebé"
    },
    "chapters": [...],
    "photo_captions": [...],
    "back_cover": {...}
  },
  "design": {
    "template_choice": {
      "primary": "Romántico - Delicado",
      "reasoning": "Template específico para embarazo..."
    },
    "layout_strategy": {
      "hero_pages": [0, 5, 12, 24],
      "collage_pages": [...]
    },
    "color_scheme": {...},
    "decorations": {...}
  }
}
```

## 🎨 Arquitectura de Agentes

### 1. PhotoAnalyzer
- Analiza cada foto con Vision AI
- Detecta emociones, composición, contenido
- Asigna importancia narrativa
- Genera títulos emotivos sugeridos

### 2. MotifDetector
- Detecta el motivo específico (17 opciones)
- Carga configuración de diseño del motivo
- Confidence scoring

### 3. ChronologySpecialist
- Detecta tipo de cronología (embarazo/viaje/evento/genérico)
- Ordena fotos cronológicamente
- Identifica hitos clave
- Asigna metadata temporal

### 4. StoryGenerator
- Genera textos PROFUNDAMENTE emotivos
- Título, subtítulo, dedicatoria
- Leyendas por foto (momentos, NO descripciones)
- Capítulos narrativos
- Texto de contratapa

### 5. DesignCurator
- Selecciona template óptimo
- Planifica layout (hero/collage/respiro)
- Define paleta de colores
- Selecciona decoraciones

## 📂 Estructura del Proyecto

```
fotolibros-agno-backend/
├── .env                    # API keys (configurado)
├── .env.example            # Template
├── requirements.txt        # Dependencias
├── README.md               # Este archivo
├── main.py                 # Punto de entrada principal
├── team.py                 # Configuración del AGNO Team
├── db_utils.py             # Helper para SQLite (opcional)
├── agents/                 # Agentes especializados
│   ├── __init__.py
│   ├── photo_analyzer.py
│   ├── motif_detector.py
│   ├── chronology_specialist.py
│   ├── story_generator.py
│   └── design_curator.py
└── data/                   # Outputs y base de datos
    └── fotolibro_config.json
```

## 🔄 Integración con Stagehand

Una vez generado el `fotolibro_config.json`, el siguiente paso es ejecutar Stagehand para crear el fotolibro en FDF:

```bash
# Volver al directorio de Stagehand
cd ../stagehand-fdf-test

# Ejecutar desde JSON (TO DO: crear este script)
npm run execute-from-json -- ../fotolibros-agno-backend/data/fotolibro_config.json
```

## 💡 Ejemplos

### Ejemplo 1: Álbum de Embarazo

```bash
python main.py \
  --photos-dir ./fotos_embarazo \
  --client "Ana y Carlos" \
  --recipient "Nuestro bebé" \
  --hint pregnancy \
  --year "2024" \
  --output embarazo_config.json
```

Resultado:
- Fotos ordenadas por semanas (8→40)
- Título: "Nueve Meses de Amor"
- Leyendas emotivas por foto
- Template: "Romántico - Delicado"
- Decoraciones: flores sutiles, corazones

### Ejemplo 2: Viaje por Europa

```bash
python main.py \
  --photos-dir ./viaje_europa \
  --client "María y Juan" \
  --hint travel \
  --output viaje_config.json
```

Resultado:
- Fotos ordenadas por ruta geográfica
- Título: "Tres Semanas de Libertad"
- Capítulos por ciudad
- Template: "Moderno - Geométrico"
- Decoraciones: mapas, brújula

### Ejemplo 3: Boda

```bash
python main.py \
  --photos-dir ./boda \
  --client "Laura y Pedro" \
  --hint wedding \
  --year "2024" \
  --output boda_config.json
```

Resultado:
- Fotos ordenadas por fases (preparación→ceremonia→fiesta)
- Título: "Nuestro Día Especial"
- Template: "Romántico - Flores"
- Decoraciones: flores, corazones, anillos

## ⚠️ Troubleshooting

### Error: "OPENROUTER_API_KEY not found"
- Verifica que el archivo `.env` existe y contiene la API key

### Error: "No module named 'agno'"
- Activa el entorno virtual: `.venv\Scripts\activate`
- Instala dependencias: `pip install agno python-dotenv pillow`

### Error: "No se encontraron fotos"
- Verifica que el directorio contiene archivos .jpg, .jpeg, .png, .webp o .heic
- Verifica que las rutas de fotos existen

### Errores de API (timeouts, rate limits)
- El modelo `gpt-4o-mini` tiene límites de requests
- Espera unos segundos entre ejecuciones
- Si persiste, verifica tu crédito en OpenRouter

## 📊 Costos Estimados

- Análisis de fotos (Vision AI): ~$0.05 por 20 fotos
- Detección de motivo: ~$0.01
- Generación de textos: ~$0.02
- Ordenamiento cronológico: ~$0.02
- **TOTAL: ~$0.10 USD** por fotolibro de 20 fotos

## 🎯 Próximos Pasos

1. ✅ Backend AGNO completado
2. ⏳ Crear executor TypeScript que lea `fotolibro_config.json`
3. ⏳ Integrar con Stagehand + FDF
4. ⏳ Testing E2E completo
5. ⏳ Optimizaciones de performance

## 📝 Notas Importantes

- **NO es un sistema genérico**: Cada fotolibro es una OBRA DE ARTE personalizada
- **Calidad > Cantidad**: Objetivo de calidad mínima 8/10 por página
- **Textos emotivos obligatorios**: Nunca genéricos, siempre personalizados
- **Orden cronológico lógico**: Embarazos por semanas, viajes por ruta, eventos por fases

## 🤝 Contribuir

Este es un sistema privado para Fábrica de Fotolibros (FDF).

## 📄 Licencia

Propietary - Fábrica de Fotolibros 2024

---

**Creado con ❤️ por el equipo de AGNO**  
_Convirtiendo fotos en recuerdos que duran para siempre_
