/**
 * Specialized Detectors - Detectores para Casos Específicos
 * ===========================================================
 * Detecta y ordena fotos según contextos muy específicos:
 * - Embarazo (progresión semana a semana)
 * - Viajes (ruta geográfica lógica)
 * - Cumpleaños infantil (cronología del evento)
 * - Bodas (ceremonia → fiesta → despedida)
 */

import { Stagehand } from "@browserbasehq/stagehand";
import { PhotoAnalysis } from './photo-analyzer';
import * as fs from 'fs';

/**
 * Detecta si el álbum es de EMBARAZO y ordena cronológicamente
 */
export async function detectPregnancyProgression(
  photos: PhotoAnalysis[],
  stagehand: Stagehand
): Promise<{
  isPregnancy: boolean;
  confidence: number;
  orderedPhotos?: PhotoAnalysis[];
  weekProgression?: number[];  // Semanas estimadas del embarazo
  keyMilestones?: string[];    // "Primer ultrasonido", "Baby shower", etc.
}> {
  
  console.log(`\n  🤰 Detector de Embarazo: Analizando ${photos.length} fotos...`);
  
  try {
    // Preparar información de fotos para análisis
    const photoSummaries = photos.map((p, idx) => ({
      index: idx,
      filename: p.filename,
      people: p.content.peopleCount,
      mainSubject: p.content.mainSubject,
      setting: p.content.setting,
      emotionalCaption: p.narrative.suggestedCaption
    }));
    
    const pregnancyAnalysis = await stagehand.extract({
      instruction: `Analyze if these photos show a PREGNANCY PROGRESSION.
      
        Photos:
        ${JSON.stringify(photoSummaries, null, 2)}
        
        CRITICAL INDICATORS to look for:
        
        1. BELLY GROWTH:
           - Is there visible progression of a pregnant belly across photos?
           - Look for: flat → small bump → large belly → post-birth
           - Person should be the SAME woman throughout
        
        2. TYPICAL PREGNANCY MILESTONES:
           - Pregnancy announcement photos
           - Ultrasound images (black/white medical images)
           - Baby shower decorations
           - Maternity photoshoots (special poses with belly)
           - Hospital/medical settings
           - Newborn baby photos
        
        3. TEMPORAL PROGRESSION:
           - Same woman in multiple photos with changing belly size
           - Clothing changes (from regular to maternity wear)
           - Seasonal changes spanning months
        
        4. CHRONOLOGICAL ORDER:
           - If this IS a pregnancy album, order photos from:
             * Early pregnancy (small/no bump) → Late pregnancy (large belly) → Birth/newborn
           - Consider: belly size, clothing fit, photo settings, captions
        
        5. ESTIMATED WEEKS:
           - For each photo, estimate pregnancy week (0-40)
           - 0-12: First trimester (barely showing)
           - 13-26: Second trimester (visible bump)
           - 27-40: Third trimester (large belly)
           - 40+: Postpartum/newborn
        
        6. KEY MILESTONES:
           - Identify special moments: "First ultrasound", "Gender reveal", 
             "Baby shower", "38 weeks", "First photo with baby"
        
        Be VERY careful. Only confirm if there's CLEAR evidence of pregnancy progression.`,
      
      schema: {
        type: "object",
        properties: {
          isPregnancy: {
            type: "boolean",
            description: "Is this clearly a pregnancy progression album?"
          },
          confidence: {
            type: "number",
            minimum: 0,
            maximum: 100,
            description: "Confidence level (0-100%)"
          },
          evidence: {
            type: "string",
            description: "What evidence confirms/denies pregnancy progression?"
          },
          chronologicalOrder: {
            type: "array",
            items: { type: "number" },
            description: "Indices ordered from early pregnancy to birth"
          },
          weekProgression: {
            type: "array",
            items: { type: "number" },
            description: "Estimated pregnancy week for each photo (in new order)"
          },
          keyMilestones: {
            type: "array",
            items: { type: "string" },
            description: "Identified milestones (e.g., 'First ultrasound at week 12')"
          },
          detectedMother: {
            type: "boolean",
            description: "Is the same woman visible across photos?"
          }
        },
        required: ["isPregnancy", "confidence", "evidence", "chronologicalOrder"]
      }
    });
    
    console.log(`     Resultado: ${pregnancyAnalysis.isPregnancy ? '✓ ES EMBARAZO' : '✗ NO es embarazo'}`);
    console.log(`     Confianza: ${pregnancyAnalysis.confidence}%`);
    console.log(`     Evidencia: ${pregnancyAnalysis.evidence}`);
    
    if (pregnancyAnalysis.isPregnancy && pregnancyAnalysis.confidence >= 70) {
      const orderedPhotos = pregnancyAnalysis.chronologicalOrder.map((idx: number) => photos[idx]);
      
      console.log(`\n     📅 Orden cronológico del embarazo:`);
      orderedPhotos.forEach((photo, i) => {
        const week = pregnancyAnalysis.weekProgression?.[i] || '?';
        console.log(`        ${i + 1}. Semana ~${week}: ${photo.filename}`);
      });
      
      if (pregnancyAnalysis.keyMilestones && pregnancyAnalysis.keyMilestones.length > 0) {
        console.log(`\n     🎯 Hitos detectados:`);
        pregnancyAnalysis.keyMilestones.forEach((milestone: string) => {
          console.log(`        - ${milestone}`);
        });
      }
      
      return {
        isPregnancy: true,
        confidence: pregnancyAnalysis.confidence,
        orderedPhotos,
        weekProgression: pregnancyAnalysis.weekProgression,
        keyMilestones: pregnancyAnalysis.keyMilestones
      };
    }
    
    return {
      isPregnancy: false,
      confidence: pregnancyAnalysis.confidence
    };
    
  } catch (error) {
    console.error(`     ❌ Error en detector de embarazo:`, error);
    return { isPregnancy: false, confidence: 0 };
  }
}

/**
 * Detecta si el álbum es de VIAJE y ordena geográficamente
 */
export async function detectTravelRoute(
  photos: PhotoAnalysis[],
  stagehand: Stagehand
): Promise<{
  isTravel: boolean;
  confidence: number;
  orderedPhotos?: PhotoAnalysis[];
  route?: string[];           // ["Madrid", "Barcelona", "Valencia"]
  travelType?: string;        // "road-trip", "multi-city", "beach-vacation", "backpacking"
  detectedCountries?: string[];
}> {
  
  console.log(`\n  ✈️  Detector de Viaje: Analizando ${photos.length} fotos...`);
  
  try {
    const photoSummaries = photos.map((p, idx) => ({
      index: idx,
      filename: p.filename,
      setting: p.content.setting,
      mainSubject: p.content.mainSubject,
      caption: p.narrative.suggestedCaption,
      lighting: p.composition.lighting
    }));
    
    const travelAnalysis = await stagehand.extract({
      instruction: `Analyze if these photos show a TRAVEL JOURNEY with logical geographic progression.
      
        Photos:
        ${JSON.stringify(photoSummaries, null, 2)}
        
        TRAVEL INDICATORS:
        
        1. MULTIPLE LOCATIONS:
           - Different cities, landmarks, or countries visible
           - Look for: famous monuments, different architectures, signs in different languages
           - Beach → mountains → cities progression
        
        2. TRAVEL MARKERS:
           - Airports, train stations, roads, hotels
           - Luggage, backpacks, travel gear
           - Tourist attractions, museums, landmarks
           - "Arriving at...", "Visiting...", "Leaving..." type moments
        
        3. LOGICAL ROUTE:
           - Is there a clear geographic route? (North to South, coastal route, etc.)
           - Same people in different locations
           - Progression through time (day 1 → day 7)
        
        4. TRAVEL TYPE:
           - Road trip (car, highway photos)
           - Multi-city tour (various urban settings)
           - Beach vacation (coastal locations)
           - Backpacking adventure (nature, hostels)
           - Cruise (ocean, ports)
        
        5. CHRONOLOGICAL ROUTE ORDER:
           - Order photos by travel route (start → destination → return)
           - Consider: typical travel routes, geographic logic, timestamps
           - Example: "Madrid → Barcelona → Valencia" or "Airport → Hotel → Beach → Return"
        
        6. DETECT LOCATIONS:
           - Identify cities/countries from landmarks, signs, architecture
           - List in order of visit
        
        Only confirm if there's CLEAR evidence of travel across multiple locations.`,
      
      schema: {
        type: "object",
        properties: {
          isTravel: {
            type: "boolean",
            description: "Is this clearly a travel journey album?"
          },
          confidence: {
            type: "number",
            minimum: 0,
            maximum: 100,
            description: "Confidence level (0-100%)"
          },
          evidence: {
            type: "string",
            description: "What evidence confirms/denies travel?"
          },
          travelType: {
            type: "string",
            description: "Type of travel: road-trip, multi-city, beach-vacation, backpacking, cruise"
          },
          route: {
            type: "array",
            items: { type: "string" },
            description: "Locations in order of visit (e.g., ['Paris', 'Rome', 'Barcelona'])"
          },
          chronologicalOrder: {
            type: "array",
            items: { type: "number" },
            description: "Photo indices ordered by travel route"
          },
          detectedCountries: {
            type: "array",
            items: { type: "string" },
            description: "Countries visited"
          },
          durationEstimate: {
            type: "string",
            description: "Estimated trip duration: 'weekend', 'week', 'weeks', 'months'"
          }
        },
        required: ["isTravel", "confidence", "evidence"]
      }
    });
    
    console.log(`     Resultado: ${travelAnalysis.isTravel ? '✓ ES VIAJE' : '✗ NO es viaje'}`);
    console.log(`     Confianza: ${travelAnalysis.confidence}%`);
    console.log(`     Evidencia: ${travelAnalysis.evidence}`);
    
    if (travelAnalysis.isTravel && travelAnalysis.confidence >= 70) {
      const orderedPhotos = travelAnalysis.chronologicalOrder 
        ? travelAnalysis.chronologicalOrder.map((idx: number) => photos[idx])
        : photos;
      
      console.log(`\n     🗺️  Ruta de viaje detectada:`);
      console.log(`        Tipo: ${travelAnalysis.travelType || 'Desconocido'}`);
      console.log(`        Duración estimada: ${travelAnalysis.durationEstimate || 'Desconocida'}`);
      
      if (travelAnalysis.route && travelAnalysis.route.length > 0) {
        console.log(`        Ruta: ${travelAnalysis.route.join(' → ')}`);
      }
      
      if (travelAnalysis.detectedCountries && travelAnalysis.detectedCountries.length > 0) {
        console.log(`        Países: ${travelAnalysis.detectedCountries.join(', ')}`);
      }
      
      console.log(`\n     📸 Orden de fotos por ruta:`);
      orderedPhotos.forEach((photo, i) => {
        const location = travelAnalysis.route?.[i] || '?';
        console.log(`        ${i + 1}. ${location}: ${photo.filename}`);
      });
      
      return {
        isTravel: true,
        confidence: travelAnalysis.confidence,
        orderedPhotos,
        route: travelAnalysis.route,
        travelType: travelAnalysis.travelType,
        detectedCountries: travelAnalysis.detectedCountries
      };
    }
    
    return {
      isTravel: false,
      confidence: travelAnalysis.confidence
    };
    
  } catch (error) {
    console.error(`     ❌ Error en detector de viaje:`, error);
    return { isTravel: false, confidence: 0 };
  }
}

/**
 * Detecta si es un evento puntual (boda, cumpleaños) y ordena cronológicamente
 */
export async function detectEventChronology(
  photos: PhotoAnalysis[],
  stagehand: Stagehand
): Promise<{
  isEvent: boolean;
  eventType?: string;  // "wedding", "birthday-party", "graduation", "quinceañera"
  confidence: number;
  orderedPhotos?: PhotoAnalysis[];
  eventPhases?: string[];  // ["Preparación", "Ceremonia", "Fiesta", "Despedida"]
}> {
  
  console.log(`\n  🎉 Detector de Evento: Analizando ${photos.length} fotos...`);
  
  try {
    const photoSummaries = photos.map((p, idx) => ({
      index: idx,
      filename: p.filename,
      eventType: p.narrative.eventType,
      setting: p.content.setting,
      people: p.content.peopleCount,
      caption: p.narrative.suggestedCaption
    }));
    
    const eventAnalysis = await stagehand.extract({
      instruction: `Analyze if these photos show a SINGLE EVENT with chronological phases.
      
        Photos:
        ${JSON.stringify(photoSummaries, null, 2)}
        
        EVENT INDICATORS:
        
        1. EVENT TYPE DETECTION:
           - Wedding: ceremony, bride/groom, reception, dancing
           - Birthday party: cake, decorations, celebration
           - Quinceañera: formal dress, waltz, ceremony
           - Graduation: caps, gowns, diplomas, auditorium
           - Baby shower: decorations, games, gifts
        
        2. CHRONOLOGICAL PHASES:
           - PREPARATION: getting ready, decorations being set up
           - BEGINNING: arrivals, greetings, formal moments
           - CEREMONY/MAIN EVENT: key moment (vows, cake, speech)
           - CELEBRATION: party, dancing, mingling
           - CLOSING: farewells, cleanup, late moments
        
        3. TIME-OF-DAY PROGRESSION:
           - Morning → Afternoon → Evening → Night
           - Look at lighting: natural daylight → golden hour → artificial lights
        
        4. LOGICAL EVENT FLOW:
           - Same location(s), same people, same day
           - Decorations consistent
           - Clothing doesn't change (except bride/groom outfit changes)
        
        5. ORDER PHOTOS BY EVENT TIMELINE:
           - Start: Preparation/arrival
           - Middle: Ceremony/key moment
           - End: Party/celebration/farewell
        
        Only confirm if photos clearly show phases of a SINGLE EVENT.`,
      
      schema: {
        type: "object",
        properties: {
          isEvent: {
            type: "boolean",
            description: "Is this a single event album?"
          },
          eventType: {
            type: "string",
            description: "Type: wedding, birthday-party, graduation, quinceañera, baby-shower, etc."
          },
          confidence: {
            type: "number",
            minimum: 0,
            maximum: 100
          },
          evidence: {
            type: "string",
            description: "Evidence for event detection"
          },
          eventPhases: {
            type: "array",
            items: { type: "string" },
            description: "Detected phases in order: ['Preparación', 'Ceremonia', 'Fiesta']"
          },
          chronologicalOrder: {
            type: "array",
            items: { type: "number" },
            description: "Photo indices in event timeline order"
          },
          timeSpan: {
            type: "string",
            description: "Estimated duration: 'hours', 'full-day', 'two-days'"
          }
        },
        required: ["isEvent", "confidence", "evidence"]
      }
    });
    
    console.log(`     Resultado: ${eventAnalysis.isEvent ? '✓ ES EVENTO' : '✗ NO es evento único'}`);
    console.log(`     Confianza: ${eventAnalysis.confidence}%`);
    
    if (eventAnalysis.isEvent && eventAnalysis.confidence >= 70) {
      console.log(`     Tipo: ${eventAnalysis.eventType || 'Desconocido'}`);
      console.log(`     Duración: ${eventAnalysis.timeSpan || 'Desconocida'}`);
      
      const orderedPhotos = eventAnalysis.chronologicalOrder
        ? eventAnalysis.chronologicalOrder.map((idx: number) => photos[idx])
        : photos;
      
      if (eventAnalysis.eventPhases && eventAnalysis.eventPhases.length > 0) {
        console.log(`\n     📋 Fases del evento:`);
        eventAnalysis.eventPhases.forEach((phase: string, i: number) => {
          console.log(`        ${i + 1}. ${phase}`);
        });
      }
      
      return {
        isEvent: true,
        eventType: eventAnalysis.eventType,
        confidence: eventAnalysis.confidence,
        orderedPhotos,
        eventPhases: eventAnalysis.eventPhases
      };
    }
    
    return {
      isEvent: false,
      confidence: eventAnalysis.confidence
    };
    
  } catch (error) {
    console.error(`     ❌ Error en detector de evento:`, error);
    return { isEvent: false, confidence: 0 };
  }
}

/**
 * ORQUESTADOR: Ejecuta todos los detectores especializados
 */
export async function detectAndOrderIntelligently(
  photos: PhotoAnalysis[],
  stagehand: Stagehand
): Promise<{
  detectedType: string;  // "pregnancy", "travel", "event", "generic"
  orderedPhotos: PhotoAnalysis[];
  metadata: any;
}> {
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  🔍 DETECCIÓN INTELIGENTE DE TIPO DE ÁLBUM`);
  console.log(`${'='.repeat(70)}`);
  
  // Ejecutar detectores en paralelo
  const [pregnancyResult, travelResult, eventResult] = await Promise.all([
    detectPregnancyProgression(photos, stagehand),
    detectTravelRoute(photos, stagehand),
    detectEventChronology(photos, stagehand)
  ]);
  
  console.log(`\n  📊 Resultados de detección:`);
  console.log(`     Embarazo: ${pregnancyResult.confidence}%`);
  console.log(`     Viaje: ${travelResult.confidence}%`);
  console.log(`     Evento: ${eventResult.confidence}%`);
  
  // Seleccionar el detector con mayor confianza
  const detectors = [
    { type: 'pregnancy', confidence: pregnancyResult.confidence, result: pregnancyResult },
    { type: 'travel', confidence: travelResult.confidence, result: travelResult },
    { type: 'event', confidence: eventResult.confidence, result: eventResult }
  ];
  
  const bestDetector = detectors.sort((a, b) => b.confidence - a.confidence)[0];
  
  if (bestDetector.confidence >= 70) {
    console.log(`\n  ✅ TIPO DETECTADO: ${bestDetector.type.toUpperCase()}`);
    console.log(`     Confianza: ${bestDetector.confidence}%`);
    
    let orderedPhotos = photos;
    let metadata: any = {};
    
    if (bestDetector.type === 'pregnancy' && pregnancyResult.orderedPhotos) {
      orderedPhotos = pregnancyResult.orderedPhotos;
      metadata = {
        weekProgression: pregnancyResult.weekProgression,
        keyMilestones: pregnancyResult.keyMilestones
      };
    } else if (bestDetector.type === 'travel' && travelResult.orderedPhotos) {
      orderedPhotos = travelResult.orderedPhotos;
      metadata = {
        route: travelResult.route,
        travelType: travelResult.travelType,
        countries: travelResult.detectedCountries
      };
    } else if (bestDetector.type === 'event' && eventResult.orderedPhotos) {
      orderedPhotos = eventResult.orderedPhotos;
      metadata = {
        eventType: eventResult.eventType,
        phases: eventResult.eventPhases
      };
    }
    
    console.log(`${'='.repeat(70)}\n`);
    
    return {
      detectedType: bestDetector.type,
      orderedPhotos,
      metadata
    };
  }
  
  console.log(`\n  ℹ️  No se detectó tipo específico - usando orden genérico`);
  console.log(`${'='.repeat(70)}\n`);
  
  return {
    detectedType: 'generic',
    orderedPhotos: photos,
    metadata: {}
  };
}
