/**
 * Artistic Curator - Curador Inteligente de Diseño
 * ==================================================
 * Toma decisiones artísticas basadas en el análisis de fotos.
 * No es un selector automático, es un DISEÑADOR DIGITAL.
 */

import { PhotoAnalysis } from './photo-analyzer';

export interface DesignDecisions {
  // Template selection
  templateChoice: {
    primary: string;          // Template principal elegido
    reasoning: string;        // Por qué se eligió
    backupOptions: string[];  // Alternativas
  };
  
  // Layout strategy
  layoutStrategy: {
    heroPages: number[];      // Índices de páginas que deben ser full-page
    collagePages: number[];   // Páginas con múltiples fotos
    bleedPages: number[];     // Fotos que llegan al borde
    emptyPages: number[];     // Páginas dejadas en blanco intencionalmente (respiro)
  };
  
  // Typography
  typography: {
    coverTitle: string;       // Título generado para tapa
    backCoverText: string;    // Texto para contratapa
    spineText: string;        // Texto para lomo
    pageC aptions: string[];   // Leyendas por página
    fontStyle: string;        // 'elegant', 'playful', 'modern', 'handwritten'
  };
  
  // Color palette
  colorScheme: {
    primary: string;          // Color principal (hex)
    secondary: string;        // Color secundario
    accent: string;           // Color de acento
    mood: string;             // 'warm', 'cool', 'vibrant', 'muted'
  };
  
  // Decorative elements
  decorations: {
    useFrames: boolean;
    useClipArts: string[];    // ['flores', 'corazones', etc.]
    useBackgrounds: boolean;
    style: string;            // 'minimal', 'ornate', 'modern'
  };
  
  // Quality targets
  qualityTargets: {
    minimumPageQuality: number;   // 1-10
    emotionalImpact: number;      // 1-10
    coherenceScore: number;       // 1-10
  };
}

/**
 * Genera decisiones de diseño basadas en análisis de fotos
 */
export function curateDesign(
  photoAnalyses: PhotoAnalysis[],
  albumProfile: {
    dominantEmotion: string;
    recommendedStyle: string;
    suggestedAlbumTitle: string;
    narrativeArc: string;
  },
  clientPreferences?: {
    estilo_cliente?: string;
    titulo_cliente?: string;
    incluir_qr?: boolean;
    qr_url?: string;
  }
): DesignDecisions {
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  🎨 CURACIÓN ARTÍSTICA DEL DISEÑO`);
  console.log(`${'='.repeat(70)}`);
  
  // 1. SELECCIÓN DE TEMPLATE
  const templateChoice = selectTemplate(photoAnalyses, albumProfile, clientPreferences);
  console.log(`\n  📐 TEMPLATE SELECCIONADO: ${templateChoice.primary}`);
  console.log(`     Razón: ${templateChoice.reasoning}`);
  
  // 2. ESTRATEGIA DE LAYOUT
  const layoutStrategy = planLayout(photoAnalyses, albumProfile.narrativeArc);
  console.log(`\n  📄 ESTRATEGIA DE PÁGINAS:`);
  console.log(`     - Páginas hero (full): ${layoutStrategy.heroPages.length}`);
  console.log(`     - Páginas collage: ${layoutStrategy.collagePages.length}`);
  console.log(`     - Páginas respiro: ${layoutStrategy.emptyPages.length}`);
  
  // 3. TIPOGRAFÍA
  const typography = designTypography(
    photoAnalyses, 
    albumProfile, 
    clientPreferences?.titulo_cliente
  );
  console.log(`\n  ✍️  TIPOGRAFÍA:`);
  console.log(`     - Tapa: "${typography.coverTitle}"`);
  console.log(`     - Contratapa: "${typography.backCoverText}"`);
  console.log(`     - Estilo: ${typography.fontStyle}`);
  
  // 4. PALETA DE COLORES
  const colorScheme = extractColorScheme(photoAnalyses, albumProfile.dominantEmotion);
  console.log(`\n  🎨 PALETA DE COLORES:`);
  console.log(`     - Primario: ${colorScheme.primary}`);
  console.log(`     - Secundario: ${colorScheme.secondary}`);
  console.log(`     - Mood: ${colorScheme.mood}`);
  
  // 5. DECORACIONES
  const decorations = selectDecorations(albumProfile, clientPreferences);
  console.log(`\n  ✨ DECORACIONES:`);
  console.log(`     - Clip-arts: ${decorations.useClipArts.join(', ') || 'Ninguno'}`);
  console.log(`     - Estilo: ${decorations.style}`);
  
  // 6. OBJETIVOS DE CALIDAD
  const qualityTargets = {
    minimumPageQuality: 8,    // Muy alta
    emotionalImpact: 9,       // Máximo impacto emocional
    coherenceScore: 8         // Alta coherencia
  };
  
  console.log(`\n  🎯 OBJETIVOS DE CALIDAD:`);
  console.log(`     - Calidad mínima por página: ${qualityTargets.minimumPageQuality}/10`);
  console.log(`     - Impacto emocional: ${qualityTargets.emotionalImpact}/10`);
  console.log(`     - Coherencia: ${qualityTargets.coherenceScore}/10`);
  
  console.log(`${'='.repeat(70)}\n`);
  
  return {
    templateChoice,
    layoutStrategy,
    typography,
    colorScheme,
    decorations,
    qualityTargets
  };
}

/**
 * Selecciona el template óptimo
 */
function selectTemplate(
  photos: PhotoAnalysis[],
  profile: any,
  clientPrefs?: any
): { primary: string; reasoning: string; backupOptions: string[] } {
  
  // Mapeo sofisticado: emoción + contenido → template
  const templateRules: Record<string, { keywords: string[]; reasoning: string }> = {
    'Romántico - Flores': {
      keywords: ['love', 'wedding', 'romantic', 'elegant'],
      reasoning: 'Fotos con alta carga emocional romántica, perfectas para decoración floral'
    },
    'Moderno - Geométrico': {
      keywords: ['modern', 'urban', 'architecture', 'clean'],
      reasoning: 'Composiciones limpias y modernas requieren templates minimalistas'
    },
    'Clásico - Elegante': {
      keywords: ['nostalgia', 'classic', 'portrait', 'formal'],
      reasoning: 'Fotografías clásicas y retratos merecen marcos elegantes tradicionales'
    },
    'Divertido - Colorful': {
      keywords: ['joy', 'birthday', 'children', 'playful'],
      reasoning: 'Momentos alegres necesitan diseños vibrantes y juguetones'
    },
    'Natural - Orgánico': {
      keywords: ['nature', 'outdoor', 'peace', 'landscape'],
      reasoning: 'Fotografías de naturaleza combinan con elementos orgánicos y terrosos'
    },
    'Minimalista - Simple': {
      keywords: ['minimal', 'clean', 'simple', 'modern'],
      reasoning: 'Fotos de alta calidad compositiva lucen mejor sin distracciones'
    }
  };
  
  // Analizar keywords de las fotos
  const photoKeywords = [
    profile.dominantEmotion,
    ...photos.map(p => p.narrative.eventType),
    ...photos.map(p => p.content.mainSubject),
    ...photos.map(p => p.content.setting)
  ];
  
  // Scoring de templates
  const scores: Record<string, number> = {};
  
  Object.entries(templateRules).forEach(([template, rule]) => {
    scores[template] = rule.keywords.filter(kw => 
      photoKeywords.some(pk => pk.toLowerCase().includes(kw))
    ).length;
  });
  
  // Considerar preferencia del cliente
  if (clientPrefs?.estilo_cliente) {
    const clientStyle = clientPrefs.estilo_cliente.toLowerCase();
    Object.keys(scores).forEach(template => {
      if (template.toLowerCase().includes(clientStyle)) {
        scores[template] += 5; // Boost significativo
      }
    });
  }
  
  // Ordenar por score
  const sorted = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .map(([template]) => template);
  
  const primary = sorted[0] || 'Moderno - Geométrico';
  const reasoning = templateRules[primary]?.reasoning || 'Template por defecto';
  const backupOptions = sorted.slice(1, 4);
  
  return { primary, reasoning, backupOptions };
}

/**
 * Planifica el layout de páginas
 */
function planLayout(
  photos: PhotoAnalysis[],
  narrativeArc: string
): {
  heroPages: number[];
  collagePages: number[];
  bleedPages: number[];
  emptyPages: number[];
} {
  
  const heroPages: number[] = [];
  const collagePages: number[] = [];
  const bleedPages: number[] = [];
  const emptyPages: number[] = [];
  
  // Identificar fotos HERO (importancia >= 8, calidad >= 7)
  photos.forEach((photo, index) => {
    if (photo.narrative.importance >= 8 && photo.composition.quality >= 7) {
      heroPages.push(index);
    }
  });
  
  // Primera y última foto siempre son hero
  if (!heroPages.includes(0)) heroPages.unshift(0);
  if (!heroPages.includes(photos.length - 1)) heroPages.push(photos.length - 1);
  
  // Páginas collage: fotos de importancia media (4-7)
  photos.forEach((photo, index) => {
    if (photo.narrative.importance >= 4 && 
        photo.narrative.importance < 8 && 
        !heroPages.includes(index)) {
      collagePages.push(index);
    }
  });
  
  // Bleed: fotos de paisaje o naturaleza (impacto visual)
  photos.forEach((photo, index) => {
    if ((photo.content.mainSubject === 'landscape' || 
         photo.content.setting === 'nature') &&
        photo.composition.quality >= 7) {
      bleedPages.push(index);
    }
  });
  
  // Páginas vacías (respiro) - cada 8-10 páginas
  const totalPages = photos.length;
  for (let i = 8; i < totalPages; i += 10) {
    if (!heroPages.includes(i) && !collagePages.includes(i)) {
      emptyPages.push(i);
    }
  }
  
  return { heroPages, collagePages, bleedPages, emptyPages };
}

/**
 * Diseña tipografía
 */
function designTypography(
  photos: PhotoAnalysis[],
  profile: any,
  clientTitle?: string
): {
  coverTitle: string;
  backCoverText: string;
  spineText: string;
  pageCaptions: string[];
  fontStyle: string;
} {
  
  // Título de tapa
  const coverTitle = clientTitle || profile.suggestedAlbumTitle;
  
  // Texto de contratapa (cita emocional)
  const backCoverQuotes: Record<string, string[]> = {
    'love': [
      '"Cada momento juntos es un tesoro"',
      '"El amor en cada página de nuestra historia"',
      '"Recuerdos que duran para siempre"'
    ],
    'joy': [
      '"Momentos que nos hicieron sonreír"',
      '"Alegría capturada en cada imagen"',
      '"Días llenos de felicidad"'
    ],
    'nostalgia': [
      '"Tiempos que nunca olvidaremos"',
      '"Memorias que viven en nuestros corazones"',
      '"El ayer que sigue presente hoy"'
    ]
  };
  
  const quotes = backCoverQuotes[profile.dominantEmotion] || backCoverQuotes['joy'];
  const backCoverText = quotes[Math.floor(Math.random() * quotes.length)];
  
  // Texto de lomo (título corto)
  const spineText = coverTitle.length > 20 
    ? coverTitle.substring(0, 17) + '...' 
    : coverTitle;
  
  // Leyendas por página (usar los captions sugeridos)
  const pageCaptions = photos.map(p => p.narrative.suggestedCaption);
  
  // Estilo de fuente
  const fontStyleMap: Record<string, string> = {
    'love': 'elegant',
    'romantic': 'elegant',
    'joy': 'playful',
    'birthday': 'playful',
    'nostalgia': 'handwritten',
    'modern': 'modern',
    'peace': 'modern'
  };
  
  const fontStyle = fontStyleMap[profile.dominantEmotion] || 'modern';
  
  return { coverTitle, backCoverText, spineText, pageCaptions, fontStyle };
}

/**
 * Extrae paleta de colores
 */
function extractColorScheme(
  photos: PhotoAnalysis[],
  dominantEmotion: string
): {
  primary: string;
  secondary: string;
  accent: string;
  mood: string;
} {
  
  // Analizar paletas de fotos
  const palettes = photos.map(p => p.composition.colorPalette);
  const paletteCounts: Record<string, number> = {};
  palettes.forEach(p => {
    paletteCounts[p] = (paletteCounts[p] || 0) + 1;
  });
  
  const dominantPalette = Object.entries(paletteCounts)
    .sort((a, b) => b[1] - a[1])[0][0];
  
  // Mapeo paleta → colores hex
  const colorMap: Record<string, { primary: string; secondary: string; accent: string }> = {
    'warm': { primary: '#D4A574', secondary: '#8B4513', accent: '#FFD700' },
    'cool': { primary: '#4A90A4', secondary: '#2C5F75', accent: '#87CEEB' },
    'vibrant': { primary: '#FF6B6B', secondary: '#4ECDC4', accent: '#FFE66D' },
    'muted': { primary: '#9B9B9B', secondary: '#6B6B6B', accent: '#C4C4C4' },
    'monochrome': { primary: '#2C2C2C', secondary: '#808080', accent: '#D4D4D4' }
  };
  
  const colors = colorMap[dominantPalette] || colorMap['warm'];
  
  // Ajustar mood según emoción
  const moodMap: Record<string, string> = {
    'love': 'warm',
    'joy': 'vibrant',
    'nostalgia': 'muted',
    'peace': 'cool',
    'excitement': 'vibrant'
  };
  
  const mood = moodMap[dominantEmotion] || dominantPalette;
  
  return { ...colors, mood };
}

/**
 * Selecciona decoraciones
 */
function selectDecorations(
  profile: any,
  clientPrefs?: any
): {
  useFrames: boolean;
  useClipArts: string[];
  useBackgrounds: boolean;
  style: string;
} {
  
  // Mapeo estilo → decoraciones
  const decorMap: Record<string, { useFrames: boolean; clipArts: string[]; style: string }> = {
    'romantico': { 
      useFrames: true, 
      clipArts: ['flores', 'corazones', 'mariposas'], 
      style: 'ornate' 
    },
    'divertido': { 
      useFrames: true, 
      clipArts: ['estrellas', 'globos', 'confetti'], 
      style: 'playful' 
    },
    'clasico': { 
      useFrames: true, 
      clipArts: ['marcos-vintage', 'esquinas'], 
      style: 'ornate' 
    },
    'moderno': { 
      useFrames: false, 
      clipArts: [], 
      style: 'minimal' 
    },
    'minimalista': { 
      useFrames: false, 
      clipArts: [], 
      style: 'minimal' 
    },
    'natural': { 
      useFrames: false, 
      clipArts: ['hojas', 'flores-silvestres'], 
      style: 'minimal' 
    }
  };
  
  const style = profile.recommendedStyle || 'moderno';
  const decor = decorMap[style.toLowerCase()] || decorMap['moderno'];
  
  // Considerar preferencias del cliente
  let useClipArts = decor.clipArts;
  
  if (clientPrefs?.adornos_extras) {
    try {
      const clientAdornos = JSON.parse(clientPrefs.adornos_extras);
      if (clientAdornos.items && Array.isArray(clientAdornos.items)) {
        useClipArts = [...useClipArts, ...clientAdornos.items];
      }
    } catch {}
  }
  
  return {
    useFrames: decor.useFrames,
    useClipArts: useClipArts.slice(0, 3), // Máximo 3
    useBackgrounds: style !== 'minimalista',
    style: decor.style
  };
}
