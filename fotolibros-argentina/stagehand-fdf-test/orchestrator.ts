/**
 * Orchestrator - Orquestador Híbrido Inteligente
 * ================================================
 * Agente maestro que coordina todo el flujo,
 * delegando tareas pesadas a funciones especializadas.
 */

import { Stagehand } from "@browserbasehq/stagehand";
import { analyzePhotoSet, PhotoAnalysis } from './photo-analyzer';
import { detectEventMotif, EventMotifProfile } from './event-type-detector';
import { detectAndOrderIntelligently } from './specialized-detectors';
import { buildPhotobookStory, PhotobookStory } from './story-builder';
import { curateDesign, DesignDecisions } from './artistic-curator';

export interface OrchestratorInput {
  photos: string[];           // Rutas de fotos
  clientName: string;
  clientEmail: string;
  clientHint?: string;        // Hint del tipo de evento
  customTitle?: string;       // Título personalizado opcional
}

export interface OrchestratorOutput {
  success: boolean;
  
  // Resultados de cada fase
  photoAnalysis: {
    photos: PhotoAnalysis[];
    albumProfile: any;
  };
  
  motifProfile: EventMotifProfile;
  
  chronology: {
    detectedType: string;
    orderedPhotos: PhotoAnalysis[];
    metadata: any;
  };
  
  story: PhotobookStory;
  
  design: DesignDecisions;
  
  // Metadata de ejecución
  execution: {
    totalTimeMs: number;
    phaseTimes: Record<string, number>;
    errors: string[];
    warnings: string[];
  };
}

/**
 * Orquestador principal - Ejecuta todo el flujo artístico
 */
export async function orchestratePhotobookCreation(
  input: OrchestratorInput,
  stagehand: Stagehand
): Promise<OrchestratorOutput> {
  
  const startTime = Date.now();
  const phaseTimes: Record<string, number> = {};
  const errors: string[] = [];
  const warnings: string[] = [];
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  🎨 ORQUESTADOR DE FOTOLIBROS ARTÍSTICOS`);
  console.log(`${'='.repeat(70)}`);
  console.log(`  Cliente: ${input.clientName}`);
  console.log(`  Fotos: ${input.photos.length}`);
  if (input.clientHint) {
    console.log(`  Tipo sugerido: ${input.clientHint}`);
  }
  console.log(`${'='.repeat(70)}\n`);
  
  let photoAnalysis: any;
  let motifProfile: EventMotifProfile;
  let chronology: any;
  let story: PhotobookStory;
  let design: DesignDecisions;
  
  try {
    // ===================================================
    // FASE 1: ANÁLISIS EMOCIONAL DE FOTOS
    // ===================================================
    console.log(`\n📸 FASE 1/5: Análisis Emocional de Fotos`);
    const phase1Start = Date.now();
    
    try {
      photoAnalysis = await analyzePhotoSet(
        input.photos,
        stagehand,
        {
          clientName: input.clientName,
          eventType: input.clientHint
        }
      );
      
      phaseTimes['photo_analysis'] = Date.now() - phase1Start;
      console.log(`✅ Fase 1 completada en ${(phaseTimes['photo_analysis'] / 1000).toFixed(1)}s`);
      
    } catch (error) {
      errors.push(`Fase 1 (Análisis): ${error}`);
      throw new Error(`Error crítico en análisis de fotos: ${error}`);
    }
    
    // ===================================================
    // FASE 2: DETECCIÓN DE MOTIVO
    // ===================================================
    console.log(`\n🎯 FASE 2/5: Detección de Motivo del Fotolibro`);
    const phase2Start = Date.now();
    
    try {
      motifProfile = await detectEventMotif(
        photoAnalysis.photos,
        stagehand,
        input.clientHint
      );
      
      phaseTimes['motif_detection'] = Date.now() - phase2Start;
      console.log(`✅ Fase 2 completada en ${(phaseTimes['motif_detection'] / 1000).toFixed(1)}s`);
      
      // Advertencia si confianza es baja
      if (motifProfile.confidence < 70) {
        warnings.push(`Confianza baja en detección de motivo: ${motifProfile.confidence}%`);
        console.log(`⚠️  Advertencia: Confianza ${motifProfile.confidence}% (< 70%)`);
      }
      
    } catch (error) {
      errors.push(`Fase 2 (Motivo): ${error}`);
      
      // Fallback a motivo genérico
      warnings.push(`No se pudo detectar motivo específico, usando genérico`);
      console.log(`⚠️  Usando configuración genérica por error en detección`);
      
      motifProfile = {
        motif: 'generic',
        confidence: 0,
        evidence: 'Error en detección',
        design: {
          suggestedTemplate: 'Moderno',
          colorPalette: ['#FFFFFF', '#000000'],
          decorations: [],
          fontStyle: 'modern',
          mood: 'neutral'
        },
        texts: {
          titlePrefix: 'Nuestros Momentos',
          dedicationTemplate: 'Recuerdos que atesoramos',
          backCoverQuote: '"Los momentos se convierten en recuerdos"'
        },
        narrativeFlow: {
          structure: 'chronological',
          keyMoments: [],
          pacing: 'medium'
        }
      };
    }
    
    // ===================================================
    // FASE 3: DETECCIÓN ESPECIALIZADA Y ORDENAMIENTO
    // ===================================================
    console.log(`\n🔍 FASE 3/5: Detección Especializada y Ordenamiento Cronológico`);
    const phase3Start = Date.now();
    
    try {
      chronology = await detectAndOrderIntelligently(
        photoAnalysis.photos,
        stagehand
      );
      
      phaseTimes['chronology'] = Date.now() - phase3Start;
      console.log(`✅ Fase 3 completada en ${(phaseTimes['chronology'] / 1000).toFixed(1)}s`);
      
      if (chronology.detectedType !== 'generic') {
        console.log(`🎯 Tipo especializado detectado: ${chronology.detectedType}`);
      }
      
    } catch (error) {
      errors.push(`Fase 3 (Cronología): ${error}`);
      
      // Fallback: usar orden original
      warnings.push(`No se pudo determinar orden cronológico, usando orden original`);
      console.log(`⚠️  Usando orden original de fotos`);
      
      chronology = {
        detectedType: 'generic',
        orderedPhotos: photoAnalysis.photos,
        metadata: {}
      };
      
      phaseTimes['chronology'] = Date.now() - phase3Start;
    }
    
    // ===================================================
    // FASE 4: CONSTRUCCIÓN DE LA HISTORIA
    // ===================================================
    console.log(`\n✍️  FASE 4/5: Construcción de la Historia Emotiva`);
    const phase4Start = Date.now();
    
    try {
      story = await buildPhotobookStory(
        chronology.orderedPhotos,
        stagehand,
        {
          clientName: input.clientName,
          eventType: chronology.detectedType !== 'generic' ? chronology.detectedType : motifProfile.motif,
          clientPreferences: {
            titulo_cliente: input.customTitle,
            estilo_diseno: motifProfile.motif
          }
        }
      );
      
      phaseTimes['story_building'] = Date.now() - phase4Start;
      console.log(`✅ Fase 4 completada en ${(phaseTimes['story_building'] / 1000).toFixed(1)}s`);
      
    } catch (error) {
      errors.push(`Fase 4 (Historia): ${error}`);
      
      // Fallback: historia básica
      warnings.push(`Error generando historia completa, usando textos básicos`);
      console.log(`⚠️  Usando textos básicos por error en generación`);
      
      story = {
        coverTitle: input.customTitle || 'Nuestros Momentos',
        coverSubtitle: 'Recuerdos que atesoramos',
        dedication: `Para ${input.clientName}, con amor.`,
        chapters: [],
        backCoverText: 'Estos momentos son nuestro tesoro.',
        epilogue: 'Y la historia continúa...',
        overallTheme: 'familia'
      };
      
      phaseTimes['story_building'] = Date.now() - phase4Start;
    }
    
    // ===================================================
    // FASE 5: CURACIÓN ARTÍSTICA DEL DISEÑO
    // ===================================================
    console.log(`\n🎨 FASE 5/5: Curación Artística del Diseño`);
    const phase5Start = Date.now();
    
    try {
      design = curateDesign(
        chronology.orderedPhotos,
        photoAnalysis.albumProfile,
        {
          estilo_cliente: motifProfile.motif,
          titulo_cliente: input.customTitle
        }
      );
      
      phaseTimes['design_curation'] = Date.now() - phase5Start;
      console.log(`✅ Fase 5 completada en ${(phaseTimes['design_curation'] / 1000).toFixed(1)}s`);
      
    } catch (error) {
      errors.push(`Fase 5 (Diseño): ${error}`);
      throw new Error(`Error crítico en curación de diseño: ${error}`);
    }
    
    // ===================================================
    // RESUMEN FINAL
    // ===================================================
    const totalTime = Date.now() - startTime;
    
    console.log(`\n${'='.repeat(70)}`);
    console.log(`  ✅ ORQUESTACIÓN COMPLETADA`);
    console.log(`${'='.repeat(70)}`);
    console.log(`  Tiempo total: ${(totalTime / 1000).toFixed(1)}s`);
    console.log(`\n  Desglose por fase:`);
    console.log(`    1. Análisis de fotos:    ${(phaseTimes['photo_analysis'] / 1000).toFixed(1)}s`);
    console.log(`    2. Detección de motivo:  ${(phaseTimes['motif_detection'] / 1000).toFixed(1)}s`);
    console.log(`    3. Ordenamiento:         ${(phaseTimes['chronology'] / 1000).toFixed(1)}s`);
    console.log(`    4. Historia emotiva:     ${(phaseTimes['story_building'] / 1000).toFixed(1)}s`);
    console.log(`    5. Curación de diseño:   ${(phaseTimes['design_curation'] / 1000).toFixed(1)}s`);
    
    if (warnings.length > 0) {
      console.log(`\n  ⚠️  Advertencias: ${warnings.length}`);
      warnings.forEach((w, i) => console.log(`    ${i + 1}. ${w}`));
    }
    
    if (errors.length > 0) {
      console.log(`\n  ❌ Errores recuperados: ${errors.length}`);
      errors.forEach((e, i) => console.log(`    ${i + 1}. ${e}`));
    }
    
    console.log(`\n  📊 Resultado:`);
    console.log(`    • Motivo detectado: ${motifProfile.motif} (${motifProfile.confidence}%)`);
    console.log(`    • Tipo cronológico: ${chronology.detectedType}`);
    console.log(`    • Fotos ordenadas: ${chronology.orderedPhotos.length}`);
    console.log(`    • Capítulos: ${story.chapters.length}`);
    console.log(`    • Template: ${design.templateChoice.primary}`);
    console.log(`${'='.repeat(70)}\n`);
    
    return {
      success: true,
      photoAnalysis,
      motifProfile,
      chronology,
      story,
      design,
      execution: {
        totalTimeMs: totalTime,
        phaseTimes,
        errors,
        warnings
      }
    };
    
  } catch (error) {
    console.error(`\n❌ ERROR CRÍTICO EN ORQUESTACIÓN: ${error}`);
    throw error;
  }
}
