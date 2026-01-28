/**
 * Photo Analyzer - Análisis Emocional y Visual Inteligente
 * =========================================================
 * Analiza cada foto para extraer información emocional, compositiva y narrativa.
 * 
 * Este módulo es el CORAZÓN ARTÍSTICO del sistema:
 * - Detecta caras, emociones, y momentos especiales
 * - Evalúa composición (regla de tercios, balance, iluminación)
 * - Identifica contexto (eventos, lugares, relaciones)
 * - Sugiere orden narrativo coherente
 */

import { Stagehand } from "@browserbasehq/stagehand";
import * as fs from 'fs';
import * as path from 'path';

export interface PhotoAnalysis {
  filepath: string;
  filename: string;
  
  // Análisis emocional
  emotions: {
    primary: string;        // 'joy', 'love', 'nostalgia', 'adventure', etc.
    intensity: number;      // 1-10
    description: string;    // Descripción textual
  };
  
  // Detección de contenido
  content: {
    peopleCount: number;
    hasFaces: boolean;
    facePositions: string[];  // 'center', 'left', 'right', 'multiple'
    mainSubject: string;      // 'portrait', 'landscape', 'group', 'object', 'pet'
    setting: string;          // 'indoor', 'outdoor', 'nature', 'urban', 'celebration'
  };
  
  // Análisis compositivo
  composition: {
    quality: number;          // 1-10
    lighting: string;         // 'natural', 'artificial', 'golden-hour', 'backlit'
    colorPalette: string;     // 'warm', 'cool', 'vibrant', 'muted', 'monochrome'
    focus: string;            // 'sharp', 'soft', 'bokeh'
    orientation: 'landscape' | 'portrait' | 'square';
  };
  
  // Narrativa
  narrative: {
    eventType: string;        // 'birthday', 'wedding', 'travel', 'everyday', 'milestone'
    suggestedCaption: string; // Título/leyenda sugerida
    sequenceHint: number;     // 1-100 (orden sugerido en la historia)
    importance: number;       // 1-10 (fotos clave vs. complementarias)
  };
  
  // Recomendaciones de diseño
  designSuggestions: {
    placement: string;        // 'full-page', 'half-page', 'collage', 'background'
    cropSuggestion: string;   // 'keep-original', 'crop-to-faces', 'crop-to-subject'
    templateStyle: string[];  // Estilos de template que funcionan con esta foto
  };
}

/**
 * Analiza una foto usando Vision AI (GPT-4o-mini con vision)
 */
export async function analyzePhoto(
  filepath: string, 
  stagehand: Stagehand,
  context?: {
    clientName?: string;
    eventType?: string;
    previousPhotos?: PhotoAnalysis[];
  }
): Promise<PhotoAnalysis> {
  
  // Leer la imagen como base64
  const imageBuffer = fs.readFileSync(filepath);
  const base64Image = imageBuffer.toString('base64');
  const mimeType = filepath.endsWith('.png') ? 'image/png' : 'image/jpeg';
  
  console.log(`\n[ANALYZER] 🔍 Analizando: ${path.basename(filepath)}`);
  
  // Contexto previo para coherencia narrativa
  const contextHint = context?.previousPhotos && context.previousPhotos.length > 0
    ? `Previous photos in this album showed: ${context.previousPhotos
        .map(p => `${p.narrative.eventType} (${p.emotions.primary})`)
        .slice(0, 3)
        .join(', ')}. Consider this for narrative coherence.`
    : '';
  
  try {
    const analysis = await stagehand.extract({
      instruction: `You are a professional photobook designer analyzing a photo for an emotional, artistic photobook.
      
        This photo belongs to ${context?.clientName || 'a client'} and is part of ${context?.eventType || 'their memories'}.
        
        ${contextHint}
        
        Analyze this image deeply and provide:
        
        1. EMOTIONAL ANALYSIS:
           - What is the PRIMARY emotion this photo evokes? (joy, love, nostalgia, excitement, peace, etc.)
           - Rate the emotional intensity (1-10)
           - Describe the emotional moment in 1-2 sentences
        
        2. CONTENT DETECTION:
           - Count people visible
           - Detect faces and their positions
           - Identify the main subject (portrait, landscape, group photo, pet, object, etc.)
           - Determine the setting (indoor/outdoor/celebration/nature/urban)
        
        3. COMPOSITION QUALITY:
           - Rate composition quality (1-10) considering rule of thirds, balance, focus
           - Identify lighting type (natural, golden hour, artificial, backlit)
           - Describe color palette (warm/cool/vibrant/muted)
           - Assess focus quality
        
        4. NARRATIVE CONTEXT:
           - What type of event does this represent? (birthday, wedding, travel, everyday, milestone)
           - Suggest a meaningful caption or title (emotional, not generic)
           - Estimate where this should go in a chronological story (beginning/middle/end)
           - Rate importance (1-10: is this a KEY moment or a supporting photo?)
        
        5. DESIGN RECOMMENDATIONS:
           - Best placement in photobook (full-page hero shot, half-page, collage element)
           - Cropping suggestion (keep original, crop to faces, crop to subject)
           - What template styles work best (romantic, modern, playful, elegant)
        
        Be specific and artistic - this analysis will determine the entire photobook design.`,
      
      schema: {
        type: "object",
        properties: {
          emotions: {
            type: "object",
            properties: {
              primary: { type: "string", description: "Main emotion: joy, love, nostalgia, excitement, peace, etc." },
              intensity: { type: "number", minimum: 1, maximum: 10 },
              description: { type: "string", description: "1-2 sentence emotional description" }
            },
            required: ["primary", "intensity", "description"]
          },
          content: {
            type: "object",
            properties: {
              peopleCount: { type: "number" },
              hasFaces: { type: "boolean" },
              facePositions: { 
                type: "array", 
                items: { type: "string" },
                description: "center, left, right, multiple" 
              },
              mainSubject: { type: "string", description: "portrait, landscape, group, object, pet" },
              setting: { type: "string", description: "indoor, outdoor, nature, urban, celebration" }
            },
            required: ["peopleCount", "hasFaces", "facePositions", "mainSubject", "setting"]
          },
          composition: {
            type: "object",
            properties: {
              quality: { type: "number", minimum: 1, maximum: 10 },
              lighting: { type: "string", description: "natural, artificial, golden-hour, backlit" },
              colorPalette: { type: "string", description: "warm, cool, vibrant, muted, monochrome" },
              focus: { type: "string", description: "sharp, soft, bokeh" },
              orientation: { type: "string", enum: ["landscape", "portrait", "square"] }
            },
            required: ["quality", "lighting", "colorPalette", "focus", "orientation"]
          },
          narrative: {
            type: "object",
            properties: {
              eventType: { type: "string", description: "birthday, wedding, travel, everyday, milestone" },
              suggestedCaption: { type: "string", description: "Emotional, meaningful caption" },
              sequenceHint: { type: "number", minimum: 1, maximum: 100, description: "Position in story" },
              importance: { type: "number", minimum: 1, maximum: 10, description: "Key moment rating" }
            },
            required: ["eventType", "suggestedCaption", "sequenceHint", "importance"]
          },
          designSuggestions: {
            type: "object",
            properties: {
              placement: { type: "string", description: "full-page, half-page, collage, background" },
              cropSuggestion: { type: "string", description: "keep-original, crop-to-faces, crop-to-subject" },
              templateStyle: { 
                type: "array", 
                items: { type: "string" },
                description: "Template styles that match this photo" 
              }
            },
            required: ["placement", "cropSuggestion", "templateStyle"]
          }
        },
        required: ["emotions", "content", "composition", "narrative", "designSuggestions"]
      },
      
      // CRITICAL: Incluir la imagen en la extracción
      modelClientOptions: {
        messages: [{
          role: "user",
          content: [
            {
              type: "image_url",
              image_url: {
                url: `data:${mimeType};base64,${base64Image}`
              }
            }
          ]
        }]
      }
    });
    
    const result: PhotoAnalysis = {
      filepath,
      filename: path.basename(filepath),
      ...analysis
    };
    
    // Log resumido
    console.log(`   ✓ Emoción: ${result.emotions.primary} (${result.emotions.intensity}/10)`);
    console.log(`   ✓ Sujeto: ${result.content.mainSubject} | ${result.content.peopleCount} personas`);
    console.log(`   ✓ Calidad: ${result.composition.quality}/10 | ${result.composition.lighting}`);
    console.log(`   ✓ Evento: ${result.narrative.eventType} | Importancia: ${result.narrative.importance}/10`);
    console.log(`   ✓ Título sugerido: "${result.narrative.suggestedCaption}"`);
    
    return result;
    
  } catch (error) {
    console.error(`[ANALYZER] ❌ Error analizando ${path.basename(filepath)}:`, error);
    
    // Fallback: análisis básico sin IA
    return {
      filepath,
      filename: path.basename(filepath),
      emotions: {
        primary: 'neutral',
        intensity: 5,
        description: 'Error en análisis automático'
      },
      content: {
        peopleCount: 0,
        hasFaces: false,
        facePositions: [],
        mainSubject: 'unknown',
        setting: 'unknown'
      },
      composition: {
        quality: 5,
        lighting: 'natural',
        colorPalette: 'neutral',
        focus: 'sharp',
        orientation: 'landscape'
      },
      narrative: {
        eventType: 'everyday',
        suggestedCaption: path.basename(filepath, path.extname(filepath)),
        sequenceHint: 50,
        importance: 5
      },
      designSuggestions: {
        placement: 'half-page',
        cropSuggestion: 'keep-original',
        templateStyle: ['moderno', 'clasico']
      }
    };
  }
}

/**
 * Analiza TODAS las fotos de un pedido y crea un perfil narrativo
 */
export async function analyzePhotoSet(
  photoPaths: string[],
  stagehand: Stagehand,
  context?: {
    clientName?: string;
    eventType?: string;
  }
): Promise<{
  photos: PhotoAnalysis[];
  albumProfile: {
    dominantEmotion: string;
    recommendedStyle: string;
    suggestedAlbumTitle: string;
    narrativeArc: string; // 'chronological', 'emotional-journey', 'thematic'
  };
}> {
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  🎨 ANÁLISIS ARTÍSTICO DEL ÁLBUM`);
  console.log(`${'='.repeat(70)}`);
  console.log(`  Cliente: ${context?.clientName || 'Desconocido'}`);
  console.log(`  Fotos a analizar: ${photoPaths.length}`);
  console.log(`${'='.repeat(70)}\n`);
  
  const analyses: PhotoAnalysis[] = [];
  
  // Analizar cada foto secuencialmente (para mantener contexto)
  for (let i = 0; i < photoPaths.length; i++) {
    const photo = photoPaths[i];
    console.log(`\n[${i + 1}/${photoPaths.length}]`);
    
    const analysis = await analyzePhoto(photo, stagehand, {
      ...context,
      previousPhotos: analyses
    });
    
    analyses.push(analysis);
    
    // Pequeña pausa para no saturar la API
    if (i < photoPaths.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  // ANÁLISIS GLOBAL DEL ÁLBUM
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  📊 PERFIL GLOBAL DEL ÁLBUM`);
  console.log(`${'='.repeat(70)}`);
  
  // Emoción dominante (la más frecuente)
  const emotionCounts: Record<string, number> = {};
  analyses.forEach(a => {
    emotionCounts[a.emotions.primary] = (emotionCounts[a.emotions.primary] || 0) + 1;
  });
  const dominantEmotion = Object.entries(emotionCounts)
    .sort((a, b) => b[1] - a[1])[0][0];
  
  // Tipo de evento más común
  const eventCounts: Record<string, number> = {};
  analyses.forEach(a => {
    eventCounts[a.narrative.eventType] = (eventCounts[a.narrative.eventType] || 0) + 1;
  });
  const dominantEvent = Object.entries(eventCounts)
    .sort((a, b) => b[1] - a[1])[0][0];
  
  // Calidad compositiva promedio
  const avgQuality = analyses.reduce((sum, a) => sum + a.composition.quality, 0) / analyses.length;
  
  // Recomendar estilo basado en contenido
  const recommendedStyle = determineStyle(dominantEmotion, dominantEvent, analyses);
  
  // Sugerir título del álbum
  const suggestedAlbumTitle = generateAlbumTitle(dominantEmotion, dominantEvent, context?.clientName);
  
  // Determinar arco narrativo
  const narrativeArc = determineNarrativeArc(analyses);
  
  console.log(`  Emoción dominante: ${dominantEmotion}`);
  console.log(`  Evento principal: ${dominantEvent}`);
  console.log(`  Calidad compositiva promedio: ${avgQuality.toFixed(1)}/10`);
  console.log(`  Estilo recomendado: ${recommendedStyle}`);
  console.log(`  Título sugerido: "${suggestedAlbumTitle}"`);
  console.log(`  Arco narrativo: ${narrativeArc}`);
  console.log(`${'='.repeat(70)}\n`);
  
  return {
    photos: analyses,
    albumProfile: {
      dominantEmotion,
      recommendedStyle,
      suggestedAlbumTitle,
      narrativeArc
    }
  };
}

/**
 * Determina el estilo de diseño según el análisis
 */
function determineStyle(emotion: string, event: string, photos: PhotoAnalysis[]): string {
  // Mapeo emocional → estilo
  const emotionStyleMap: Record<string, string> = {
    'joy': 'divertido',
    'love': 'romantico',
    'nostalgia': 'clasico',
    'peace': 'natural',
    'excitement': 'moderno',
    'elegance': 'clasico'
  };
  
  // Mapeo por evento
  const eventStyleMap: Record<string, string> = {
    'wedding': 'romantico',
    'birthday': 'divertido',
    'travel': 'moderno',
    'everyday': 'minimalista',
    'milestone': 'clasico'
  };
  
  // Prioridad: emoción > evento > default
  return emotionStyleMap[emotion] || eventStyleMap[event] || 'moderno';
}

/**
 * Genera título del álbum basado en contenido
 */
function generateAlbumTitle(emotion: string, event: string, clientName?: string): string {
  const templates: Record<string, string[]> = {
    'joy': ['Momentos de Alegría', 'Sonrisas y Recuerdos', 'Días Felices'],
    'love': ['Nuestro Amor', 'Juntos Para Siempre', 'Historia de Amor'],
    'nostalgia': ['Recuerdos Eternos', 'Tiempos Inolvidables', 'Memorias del Corazón'],
    'travel': ['Aventuras y Destinos', 'Viajando Juntos', 'Nuestro Viaje'],
    'wedding': ['Nuestro Día Especial', 'Para Siempre', 'El Inicio de Todo'],
    'birthday': ['Celebrando la Vida', 'Un Año Más', 'Feliz Cumpleaños']
  };
  
  const titleOptions = templates[emotion] || templates[event] || ['Nuestros Momentos'];
  const baseTitle = titleOptions[Math.floor(Math.random() * titleOptions.length)];
  
  return clientName ? `${baseTitle} - ${clientName}` : baseTitle;
}

/**
 * Determina el arco narrativo del álbum
 */
function determineNarrativeArc(photos: PhotoAnalysis[]): string {
  // Si hay clara progresión temporal (sequenceHint ordenados)
  const sequences = photos.map(p => p.narrative.sequenceHint).sort((a, b) => a - b);
  const isChronological = sequences.every((val, i, arr) => i === 0 || val >= arr[i - 1]);
  
  if (isChronological) return 'chronological';
  
  // Si hay variación emocional alta (journey)
  const emotionalVariance = new Set(photos.map(p => p.emotions.primary)).size;
  if (emotionalVariance >= 3) return 'emotional-journey';
  
  return 'thematic';
}

/**
 * Ordena fotos según narrativa óptima
 */
export function sortPhotosByNarrative(photos: PhotoAnalysis[]): PhotoAnalysis[] {
  return [...photos].sort((a, b) => {
    // Prioridad 1: Secuencia narrativa
    if (a.narrative.sequenceHint !== b.narrative.sequenceHint) {
      return a.narrative.sequenceHint - b.narrative.sequenceHint;
    }
    
    // Prioridad 2: Importancia (fotos clave primero)
    if (a.narrative.importance !== b.narrative.importance) {
      return b.narrative.importance - a.narrative.importance;
    }
    
    // Prioridad 3: Calidad compositiva
    return b.composition.quality - a.composition.quality;
  });
}
