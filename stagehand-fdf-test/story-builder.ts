/**
 * Story Builder - Constructor de Historias Emocionales
 * ======================================================
 * Ordena las fotos de manera cronológica/narrativa inteligente
 * y genera textos profundamente emotivos para cada momento.
 * 
 * NO es un ordenador automático. Es un NARRADOR DIGITAL.
 */

import { Stagehand } from "@browserbasehq/stagehand";
import { PhotoAnalysis } from './photo-analyzer';
import * as fs from 'fs';
import * as path from 'path';

export interface StoryChapter {
  title: string;              // "Los Primeros Pasos", "Nuestra Boda", etc.
  emotionalTone: string;      // 'nostálgico', 'alegre', 'romántico', 'esperanzador'
  photos: PhotoAnalysis[];
  caption: string;            // Texto emocional que acompaña el capítulo
  pageRange: { start: number; end: number };
}

export interface PhotobookStory {
  coverTitle: string;         // Título principal del libro
  coverSubtitle: string;      // Subtítulo emotivo
  dedication: string;         // Dedicatoria personalizada
  
  chapters: StoryChapter[];   // Capítulos narrativos
  
  backCoverText: string;      // Texto final emotivo
  epilogue?: string;          // Epílogo opcional
  
  overallTheme: string;       // Tema general: 'crecimiento', 'amor', 'aventura', 'familia'
}

/**
 * Analiza las fotos y detecta cronología/temporalidad mediante VISION AI
 */
export async function detectChronology(
  photos: PhotoAnalysis[],
  stagehand: Stagehand,
  context?: {
    clientName?: string;
    eventType?: string;
  }
): Promise<{
  orderedPhotos: PhotoAnalysis[];
  detectedTimeline: string;  // 'single-day', 'months', 'years', 'decades'
  ageProgression: boolean;   // ¿Hay progresión de edad visible?
  seasonalFlow: boolean;     // ¿Hay cambio de estaciones?
}> {
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  🕰️  DETECCIÓN CRONOLÓGICA INTELIGENTE`);
  console.log(`${'='.repeat(70)}`);
  
  // PASO 1: Analizar TODAS las fotos juntas para detectar patrones temporales
  console.log(`\n  📸 Analizando ${photos.length} fotos para detectar cronología...`);
  
  try {
    // Preparar imágenes para análisis conjunto
    const photoSummaries = photos.map((p, idx) => ({
      index: idx,
      filename: p.filename,
      content: p.content.mainSubject,
      setting: p.content.setting,
      people: p.content.peopleCount,
      lighting: p.composition.lighting,
      eventType: p.narrative.eventType
    }));
    
    // Usar IA para analizar cronología observando TODAS las fotos
    const chronologyAnalysis = await stagehand.extract({
      instruction: `You are analyzing a photo album to determine the CHRONOLOGICAL ORDER of photos.
      
        Context: ${context?.clientName || 'Client'} - ${context?.eventType || 'Memories'}
        
        Photo summaries:
        ${JSON.stringify(photoSummaries, null, 2)}
        
        CRITICAL ANALYSIS NEEDED:
        
        1. TEMPORAL SPAN:
           - Is this a single day event? (wedding, party, celebration)
           - Months? (pregnancy, vacation, project)
           - Years? (childhood growth, relationship timeline)
           - Decades? (family legacy, life story)
        
        2. AGE PROGRESSION:
           - Do you see people aging across photos? (baby → child → teen → adult)
           - Look for changes in: face features, height, body proportions
           - Babies: look for size changes, facial development
           - Children: look for height, teeth, facial maturity
           - Adults: look for hair changes, wrinkles, weight
        
        3. SEASONAL FLOW:
           - Are there seasonal indicators? (leaves, snow, flowers, clothing)
           - Winter → Spring → Summer → Fall progression?
        
        4. ENVIRONMENTAL CLUES:
           - Same location appearing multiple times with changes?
           - Background changes (new furniture, renovations, moves)?
           - Clothing style evolution?
        
        5. CHRONOLOGICAL ORDERING:
           - Provide the OPTIMAL ORDER of photos (by index)
           - Example: if photo 5 is the earliest, photo 2 is next, etc: [5, 2, 0, 1, 3, 4]
           - Consider: age → seasons → events → lighting quality
        
        6. NARRATIVE ARC:
           - What is the story being told?
           - "Growth of a baby", "Love story from dating to marriage", "Family legacy", etc.
        
        Be VERY careful with chronology. This determines the entire emotional impact.`,
      
      schema: {
        type: "object",
        properties: {
          timelineType: {
            type: "string",
            enum: ["single-day", "days", "weeks", "months", "years", "decades"],
            description: "Detected time span"
          },
          ageProgression: {
            type: "boolean",
            description: "Is there visible age progression of people?"
          },
          ageDetails: {
            type: "string",
            description: "Details about age progression (baby to toddler, child to teen, etc.)"
          },
          seasonalFlow: {
            type: "boolean",
            description: "Are there seasonal changes visible?"
          },
          seasonalDetails: {
            type: "string",
            description: "Details about seasonal progression"
          },
          chronologicalOrder: {
            type: "array",
            items: { type: "number" },
            description: "Indices of photos in chronological order (earliest to latest)"
          },
          narrativeArc: {
            type: "string",
            description: "The story being told (1-2 sentences)"
          },
          confidenceLevel: {
            type: "number",
            minimum: 1,
            maximum: 10,
            description: "Confidence in chronological ordering (1-10)"
          },
          reasoning: {
            type: "string",
            description: "Detailed reasoning for the chronological order chosen"
          }
        },
        required: ["timelineType", "ageProgression", "seasonalFlow", "chronologicalOrder", "narrativeArc", "confidenceLevel", "reasoning"]
      }
    });
    
    console.log(`\n  ✓ Análisis cronológico completado:`);
    console.log(`    - Línea temporal: ${chronologyAnalysis.timelineType}`);
    console.log(`    - Progresión de edad: ${chronologyAnalysis.ageProgression ? 'SÍ' : 'NO'}`);
    if (chronologyAnalysis.ageProgression) {
      console.log(`      ${chronologyAnalysis.ageDetails}`);
    }
    console.log(`    - Cambio estacional: ${chronologyAnalysis.seasonalFlow ? 'SÍ' : 'NO'}`);
    if (chronologyAnalysis.seasonalFlow) {
      console.log(`      ${chronologyAnalysis.seasonalDetails}`);
    }
    console.log(`    - Historia detectada: "${chronologyAnalysis.narrativeArc}"`);
    console.log(`    - Confianza: ${chronologyAnalysis.confidenceLevel}/10`);
    console.log(`    - Razonamiento: ${chronologyAnalysis.reasoning}`);
    
    // Reordenar fotos según el análisis
    const orderedPhotos = chronologyAnalysis.chronologicalOrder.map((idx: number) => photos[idx]);
    
    console.log(`\n  📋 Orden cronológico determinado:`);
    orderedPhotos.forEach((photo, i) => {
      const originalIdx = photos.indexOf(photo);
      console.log(`    ${i + 1}. ${photo.filename} (era posición ${originalIdx + 1})`);
      console.log(`       → ${photo.narrative.suggestedCaption}`);
    });
    
    console.log(`${'='.repeat(70)}\n`);
    
    return {
      orderedPhotos,
      detectedTimeline: chronologyAnalysis.timelineType,
      ageProgression: chronologyAnalysis.ageProgression,
      seasonalFlow: chronologyAnalysis.seasonalFlow
    };
    
  } catch (error) {
    console.error(`  ❌ Error en detección cronológica:`, error);
    console.log(`  ⚠️  Usando orden original de las fotos\n`);
    
    return {
      orderedPhotos: photos,
      detectedTimeline: 'unknown',
      ageProgression: false,
      seasonalFlow: false
    };
  }
}

/**
 * Genera textos PROFUNDAMENTE EMOTIVOS para cada foto/capítulo
 */
export async function generateEmotionalTexts(
  orderedPhotos: PhotoAnalysis[],
  stagehand: Stagehand,
  context: {
    clientName: string;
    detectedTimeline: string;
    ageProgression: boolean;
    overallTheme?: string;
  }
): Promise<{
  coverTitle: string;
  coverSubtitle: string;
  dedication: string;
  photoCaptions: string[];
  backCoverText: string;
  epilogue: string;
}> {
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  ✍️  GENERACIÓN DE TEXTOS EMOCIONALES`);
  console.log(`${'='.repeat(70)}`);
  
  // Crear resumen de la historia
  const storyContext = {
    clientName: context.clientName,
    timeline: context.detectedTimeline,
    ageProgression: context.ageProgression,
    photoCount: orderedPhotos.length,
    firstPhoto: orderedPhotos[0].narrative.suggestedCaption,
    lastPhoto: orderedPhotos[orderedPhotos.length - 1].narrative.suggestedCaption,
    dominantEmotion: getMostFrequentEmotion(orderedPhotos),
    keyMoments: orderedPhotos
      .filter(p => p.narrative.importance >= 8)
      .map(p => p.narrative.suggestedCaption)
  };
  
  console.log(`\n  📊 Contexto de la historia:`);
  console.log(`    - Cliente: ${storyContext.clientName}`);
  console.log(`    - Línea temporal: ${storyContext.timeline}`);
  console.log(`    - Emoción dominante: ${storyContext.dominantEmotion}`);
  console.log(`    - Momentos clave: ${storyContext.keyMoments.length}`);
  
  try {
    const emotionalTexts = await stagehand.extract({
      instruction: `You are a MASTER STORYTELLER creating deeply emotional, personalized texts for a photobook.
      
        This is NOT a generic template book. This is a TREASURE for ${context.clientName}.
        
        Story context:
        - Timeline: ${context.detectedTimeline} (${context.ageProgression ? 'WITH age progression' : 'same period'})
        - Number of photos: ${orderedPhotos.length}
        - Journey: From "${storyContext.firstPhoto}" to "${storyContext.lastPhoto}"
        - Dominant emotion: ${storyContext.dominantEmotion}
        - Key moments: ${storyContext.keyMoments.join(', ')}
        
        CREATE TEXTS THAT:
        
        1. COVER TITLE (Título de tapa):
           - SHORT (2-5 words), POWERFUL, EMOTIONAL
           - Examples of GOOD titles:
             * "Nuestro Primer Año" (baby's first year)
             * "Desde Aquel Día" (love story)
             * "Crecer Juntos" (siblings growing up)
             * "Los Días Que Nos Hicieron" (family journey)
           - Examples of BAD titles (too generic):
             ✗ "Mis Fotos"
             ✗ "Recuerdos 2024"
             ✗ "Álbum Familiar"
           - Make it SPECIFIC to this story
        
        2. COVER SUBTITLE (Subtítulo):
           - Expand on the title emotionally
           - 5-10 words
           - Example: "Los momentos que nos convirtieron en familia"
        
        3. DEDICATION (Dedicatoria inicial):
           - 2-3 sentences
           - DEEPLY PERSONAL
           - Address ${context.clientName} or their loved ones
           - Example: "Para ti, que convertiste cada día ordinario en extraordinario. 
                      Este libro guarda los momentos que nos hicieron quienes somos hoy."
        
        4. PHOTO CAPTIONS (one for EACH of the ${orderedPhotos.length} photos):
           - Each caption should be 5-15 words
           - NOT descriptions ("Juan en la playa") ← BAD
           - EMOTIONAL MOMENTS ("El día que descubrimos que las olas dan risa") ← GOOD
           - Connect to the PREVIOUS photo narratively when possible
           - Show progression: "Los primeros pasos" → "Corriendo hacia el futuro"
        
        5. BACK COVER TEXT (Texto de contratapa):
           - 2-3 sentences
           - CLOSURE, REFLECTION
           - Look back at the journey with gratitude/emotion
           - Example: "Cada foto es un latido de nuestra historia. 
                      Gracias por ser parte de estos momentos que nos definieron."
        
        6. EPILOGUE (Epílogo opcional):
           - 1-2 sentences
           - FORWARD-LOOKING, HOPEFUL
           - Example: "Y la historia continúa..."
        
        TONE GUIDELINES:
        - Use FIRST PERSON when appropriate ("Nuestro primer baile", not "El primer baile")
        - Be SPECIFIC, not generic
        - Evoke FEELINGS, not just facts
        - Use poetic language, but not cheesy
        - Spanish language, natural and warm
        
        This photobook should make ${context.clientName} CRY WITH EMOTION when they read it.`,
      
      schema: {
        type: "object",
        properties: {
          coverTitle: {
            type: "string",
            description: "Short, powerful title (2-5 words)"
          },
          coverSubtitle: {
            type: "string",
            description: "Emotional subtitle (5-10 words)"
          },
          dedication: {
            type: "string",
            description: "Personal dedication (2-3 sentences)"
          },
          photoCaptions: {
            type: "array",
            items: { type: "string" },
            description: `Emotional caption for EACH photo (${orderedPhotos.length} total)`,
            minItems: orderedPhotos.length,
            maxItems: orderedPhotos.length
          },
          backCoverText: {
            type: "string",
            description: "Closing text (2-3 sentences)"
          },
          epilogue: {
            type: "string",
            description: "Optional epilogue (1-2 sentences)"
          }
        },
        required: ["coverTitle", "coverSubtitle", "dedication", "photoCaptions", "backCoverText", "epilogue"]
      }
    });
    
    console.log(`\n  ✓ Textos emocionales generados:\n`);
    console.log(`  📖 Título: "${emotionalTexts.coverTitle}"`);
    console.log(`  📝 Subtítulo: "${emotionalTexts.coverSubtitle}"`);
    console.log(`  💌 Dedicatoria:\n     "${emotionalTexts.dedication}"`);
    console.log(`\n  📸 Leyendas por foto (primeras 3):`);
    emotionalTexts.photoCaptions.slice(0, 3).forEach((caption: string, i: number) => {
      console.log(`     ${i + 1}. "${caption}"`);
    });
    console.log(`  📚 Texto final:\n     "${emotionalTexts.backCoverText}"`);
    console.log(`  ✨ Epílogo: "${emotionalTexts.epilogue}"`);
    
    console.log(`${'='.repeat(70)}\n`);
    
    return emotionalTexts;
    
  } catch (error) {
    console.error(`  ❌ Error generando textos emotivos:`, error);
    
    // Fallback con textos básicos pero personalizados
    return {
      coverTitle: `Nuestros Momentos`,
      coverSubtitle: `Recuerdos que duran para siempre`,
      dedication: `Para ${context.clientName}, con todo nuestro amor. Cada foto cuenta una parte de nuestra historia.`,
      photoCaptions: orderedPhotos.map(p => p.narrative.suggestedCaption),
      backCoverText: `Estos momentos son el tesoro de nuestra vida juntos.`,
      epilogue: `Y la historia continúa...`
    };
  }
}

/**
 * Construye la historia completa del fotolibro
 */
export async function buildPhotobook Story(
  photos: PhotoAnalysis[],
  stagehand: Stagehand,
  context: {
    clientName: string;
    eventType?: string;
    clientPreferences?: {
      titulo_cliente?: string;
      estilo_diseno?: string;
    };
  }
): Promise<PhotobookStory> {
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  📚 CONSTRUCCIÓN DE LA HISTORIA COMPLETA`);
  console.log(`${'='.repeat(70)}`);
  console.log(`  Cliente: ${context.clientName}`);
  console.log(`  Fotos totales: ${photos.length}`);
  console.log(`${'='.repeat(70)}\n`);
  
  // PASO 1: Detectar cronología
  const chronology = await detectChronology(photos, stagehand, {
    clientName: context.clientName,
    eventType: context.eventType
  });
  
  // PASO 2: Generar textos emotivos
  const emotionalTexts = await generateEmotionalTexts(
    chronology.orderedPhotos,
    stagehand,
    {
      clientName: context.clientName,
      detectedTimeline: chronology.detectedTimeline,
      ageProgression: chronology.ageProgression
    }
  );
  
  // PASO 3: Dividir en capítulos narrativos
  const chapters = createChapters(
    chronology.orderedPhotos,
    emotionalTexts.photoCaptions,
    chronology.detectedTimeline
  );
  
  // PASO 4: Determinar tema general
  const overallTheme = determineOverallTheme(chronology, photos);
  
  // PASO 5: Usar título del cliente si lo proveyó (pero mejorado)
  let finalCoverTitle = emotionalTexts.coverTitle;
  
  if (context.clientPreferences?.titulo_cliente) {
    const clientTitle = context.clientPreferences.titulo_cliente;
    
    // Si el título del cliente es genérico, mejorarlo manteniendo la esencia
    if (isGenericTitle(clientTitle)) {
      finalCoverTitle = `${clientTitle}: ${emotionalTexts.coverSubtitle}`;
      console.log(`  ⚠️  Título del cliente era genérico. Mejorado a: "${finalCoverTitle}"`);
    } else {
      finalCoverTitle = clientTitle;
      console.log(`  ✓ Usando título del cliente: "${finalCoverTitle}"`);
    }
  }
  
  const story: PhotobookStory = {
    coverTitle: finalCoverTitle,
    coverSubtitle: emotionalTexts.coverSubtitle,
    dedication: emotionalTexts.dedication,
    chapters,
    backCoverText: emotionalTexts.backCoverText,
    epilogue: emotionalTexts.epilogue,
    overallTheme
  };
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  ✅ HISTORIA COMPLETA CONSTRUIDA`);
  console.log(`${'='.repeat(70)}`);
  console.log(`  Título: "${story.coverTitle}"`);
  console.log(`  Tema: ${story.overallTheme}`);
  console.log(`  Capítulos: ${story.chapters.length}`);
  story.chapters.forEach((ch, i) => {
    console.log(`    ${i + 1}. "${ch.title}" (${ch.photos.length} fotos, tono: ${ch.emotionalTone})`);
  });
  console.log(`${'='.repeat(70)}\n`);
  
  // Guardar historia como JSON para referencia
  const storyPath = path.join(__dirname, 'story-output.json');
  fs.writeFileSync(storyPath, JSON.stringify(story, null, 2), 'utf-8');
  console.log(`  💾 Historia guardada en: ${storyPath}\n`);
  
  return story;
}

/**
 * Divide fotos en capítulos narrativos
 */
function createChapters(
  orderedPhotos: PhotoAnalysis[],
  captions: string[],
  timeline: string
): StoryChapter[] {
  
  const chapters: StoryChapter[] = [];
  
  // Estrategia de división según timeline
  if (timeline === 'single-day' || orderedPhotos.length <= 10) {
    // Un solo capítulo para eventos cortos
    chapters.push({
      title: 'Un Día Para Recordar',
      emotionalTone: orderedPhotos[0].emotions.primary,
      photos: orderedPhotos,
      caption: 'Cada momento de este día quedó grabado en nuestros corazones.',
      pageRange: { start: 1, end: orderedPhotos.length }
    });
    
  } else if (timeline === 'years' || timeline === 'decades') {
    // Dividir en capítulos por progresión temporal
    const photosPerChapter = Math.ceil(orderedPhotos.length / 3);
    
    const chapterTitles = [
      { title: 'Los Primeros Pasos', tone: 'nostálgico' },
      { title: 'Creciendo Juntos', tone: 'alegre' },
      { title: 'Hasta Hoy', tone: 'esperanzador' }
    ];
    
    for (let i = 0; i < 3; i++) {
      const start = i * photosPerChapter;
      const end = Math.min((i + 1) * photosPerChapter, orderedPhotos.length);
      const chapterPhotos = orderedPhotos.slice(start, end);
      
      if (chapterPhotos.length > 0) {
        chapters.push({
          title: chapterTitles[i].title,
          emotionalTone: chapterTitles[i].tone,
          photos: chapterPhotos,
          caption: `Capítulo ${i + 1} de nuestra historia.`,
          pageRange: { start: start + 1, end }
        });
      }
    }
    
  } else {
    // División por eventos detectados
    const eventGroups: Record<string, PhotoAnalysis[]> = {};
    
    orderedPhotos.forEach(photo => {
      const event = photo.narrative.eventType;
      if (!eventGroups[event]) {
        eventGroups[event] = [];
      }
      eventGroups[event].push(photo);
    });
    
    let pageCounter = 1;
    Object.entries(eventGroups).forEach(([event, photos]) => {
      chapters.push({
        title: capitalizeEvent(event),
        emotionalTone: photos[0].emotions.primary,
        photos,
        caption: `Los momentos de ${event} que atesoramos.`,
        pageRange: { start: pageCounter, end: pageCounter + photos.length - 1 }
      });
      pageCounter += photos.length;
    });
  }
  
  return chapters;
}

/**
 * Determina tema general del álbum
 */
function determineOverallTheme(chronology: any, photos: PhotoAnalysis[]): string {
  if (chronology.ageProgression) return 'crecimiento';
  
  const emotions = photos.map(p => p.emotions.primary);
  const emotionCounts: Record<string, number> = {};
  emotions.forEach(e => {
    emotionCounts[e] = (emotionCounts[e] || 0) + 1;
  });
  
  const dominantEmotion = Object.entries(emotionCounts)
    .sort((a, b) => b[1] - a[1])[0][0];
  
  const themeMap: Record<string, string> = {
    'love': 'amor',
    'joy': 'alegría',
    'nostalgia': 'recuerdos',
    'peace': 'paz',
    'excitement': 'aventura'
  };
  
  return themeMap[dominantEmotion] || 'familia';
}

/**
 * Obtiene la emoción más frecuente
 */
function getMostFrequentEmotion(photos: PhotoAnalysis[]): string {
  const emotions = photos.map(p => p.emotions.primary);
  const counts: Record<string, number> = {};
  emotions.forEach(e => {
    counts[e] = (counts[e] || 0) + 1;
  });
  return Object.entries(counts).sort((a, b) => b[1] - a[1])[0][0];
}

/**
 * Detecta si un título es genérico
 */
function isGenericTitle(title: string): boolean {
  const genericWords = [
    'fotolibro', 'álbum', 'fotos', 'recuerdos', 'momentos',
    'photobook', 'album', 'photos', 'memories', 'familia', 'family'
  ];
  
  const normalized = title.toLowerCase();
  return genericWords.some(word => normalized === word || normalized.includes(`${word} `));
}

/**
 * Capitaliza nombre de evento
 */
function capitalizeEvent(event: string): string {
  const eventNames: Record<string, string> = {
    'birthday': 'Celebrando la Vida',
    'wedding': 'Nuestro Día Especial',
    'travel': 'Aventuras y Destinos',
    'everyday': 'Momentos Cotidianos',
    'milestone': 'Hitos Importantes'
  };
  
  return eventNames[event] || event.charAt(0).toUpperCase() + event.slice(1);
}
