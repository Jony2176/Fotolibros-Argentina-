/**
 * Event Type Detector - Detector Universal de Motivos de Fotolibros
 * ==================================================================
 * Detecta automáticamente el tipo de evento/motivo y aplica
 * reglas de diseño específicas para cada uno.
 * 
 * MOTIVOS SOPORTADOS:
 * - Bodas / Casamientos
 * - Viajes / Vacaciones
 * - Cumpleaños (infantil, adulto, 15 años, etc.)
 * - Día de la Madre
 * - Día del Padre
 * - Baby Shower
 * - Bebés (primer año)
 * - Embarazo
 * - Aniversarios (pareja, empresa, etc.)
 * - Graduaciones
 * - Artístico / Portafolio
 * - Mascotas
 * - Familia
 */

import { Stagehand } from "@browserbasehq/stagehand";
import { PhotoAnalysis } from './photo-analyzer';

export type EventMotif = 
  | 'wedding'           // Boda/Casamiento
  | 'travel'            // Viaje/Vacaciones
  | 'birthday-child'    // Cumpleaños infantil
  | 'birthday-teen'     // 15 años / quinceañera
  | 'birthday-adult'    // Cumpleaños adulto
  | 'mothers-day'       // Día de la Madre
  | 'fathers-day'       // Día del Padre
  | 'baby-shower'       // Baby Shower
  | 'baby-first-year'   // Primer año del bebé
  | 'pregnancy'         // Embarazo
  | 'anniversary-couple'// Aniversario de pareja
  | 'anniversary-other' // Otro aniversario
  | 'graduation'        // Graduación
  | 'artistic'          // Portafolio artístico
  | 'pet'               // Mascota
  | 'family'            // Familia general
  | 'generic';          // Sin motivo específico

export interface EventMotifProfile {
  motif: EventMotif;
  confidence: number;           // 0-100
  evidence: string;             // Por qué se detectó este motivo
  
  // Configuración de diseño específica del motivo
  design: {
    suggestedTemplate: string;  // Template de FDF recomendado
    colorPalette: string[];     // Colores sugeridos
    decorations: string[];      // Adornos/clip-arts sugeridos
    fontStyle: string;          // Estilo tipográfico
    mood: string;               // Mood general
  };
  
  // Textos sugeridos específicos del motivo
  texts: {
    titlePrefix: string;        // "Nuestro Día Especial", "Mis Primeros Pasos", etc.
    dedicationTemplate: string; // Template de dedicatoria
    backCoverQuote: string;     // Frase para contratapa
  };
  
  // Orden narrativo específico
  narrativeFlow: {
    structure: string;          // 'chronological', 'emotional', 'thematic'
    keyMoments: string[];       // Momentos clave a destacar
    pacing: string;             // 'fast', 'medium', 'slow' (cuántas fotos por página)
  };
}

/**
 * CONFIGURACIONES POR MOTIVO
 */
const MOTIF_CONFIGS: Record<EventMotif, Omit<EventMotifProfile, 'motif' | 'confidence' | 'evidence'>> = {
  'wedding': {
    design: {
      suggestedTemplate: 'Romántico - Flores',
      colorPalette: ['#FFFFFF', '#F5E6D3', '#D4AF37', '#8B7355'],
      decorations: ['flores', 'corazones', 'anillos', 'palomas'],
      fontStyle: 'elegant',
      mood: 'romantic'
    },
    texts: {
      titlePrefix: 'Nuestro Día Especial',
      dedicationTemplate: 'Para [NOMBRE], el día que prometimos amarnos para siempre. Este libro guarda cada momento del inicio de nuestra historia juntos.',
      backCoverQuote: '"Y desde ese día, cada momento es más hermoso porque lo vivimos juntos"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Preparación', 'Ceremonia', 'Primer baile', 'Brindis', 'Fiesta'],
      pacing: 'slow'
    }
  },
  
  'travel': {
    design: {
      suggestedTemplate: 'Moderno - Geométrico',
      colorPalette: ['#4A90E2', '#50E3C2', '#F5A623', '#FFFFFF'],
      decorations: ['mapas', 'brújula', 'avión', 'maleta'],
      fontStyle: 'modern',
      mood: 'adventurous'
    },
    texts: {
      titlePrefix: 'Nuestras Aventuras',
      dedicationTemplate: 'A cada lugar que nos abrió sus puertas, a cada momento que nos recordó por qué vale la pena perderse para encontrarse.',
      backCoverQuote: '"El mundo es un libro y quienes no viajan solo leen una página"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Salida', 'Primer destino', 'Momentos especiales', 'Regreso'],
      pacing: 'fast'
    }
  },
  
  'birthday-child': {
    design: {
      suggestedTemplate: 'Divertido - Colorful',
      colorPalette: ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3'],
      decorations: ['globos', 'confetti', 'estrellas', 'cake'],
      fontStyle: 'playful',
      mood: 'joyful'
    },
    texts: {
      titlePrefix: 'Celebrando Tu Día',
      dedicationTemplate: 'Para [NOMBRE], en tu día especial. Que cada año que pase esté lleno de risas, juegos y momentos mágicos como estos.',
      backCoverQuote: '"Cada cumpleaños es una aventura nueva"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Decoración', 'Invitados', 'Torta', 'Juegos', 'Regalos'],
      pacing: 'fast'
    }
  },
  
  'birthday-teen': {
    design: {
      suggestedTemplate: 'Romántico - Elegante',
      colorPalette: ['#E91E63', '#9C27B0', '#FFD700', '#FFFFFF'],
      decorations: ['flores', 'coronas', 'brillos', 'mariposas'],
      fontStyle: 'elegant',
      mood: 'celebratory'
    },
    texts: {
      titlePrefix: 'Mis Quince Años',
      dedicationTemplate: 'Para [NOMBRE], en el día que marcó el inicio de una nueva etapa. Que este recuerdo te acompañe siempre.',
      backCoverQuote: '"Quince años de sueños, el resto de la vida para cumplirlos"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Preparación', 'Vals', 'Familia', 'Amigos', 'Fiesta'],
      pacing: 'medium'
    }
  },
  
  'birthday-adult': {
    design: {
      suggestedTemplate: 'Clásico - Elegante',
      colorPalette: ['#2C3E50', '#E74C3C', '#ECF0F1', '#BDC3C7'],
      decorations: ['marcos-vintage', 'copas', 'velas'],
      fontStyle: 'elegant',
      mood: 'sophisticated'
    },
    texts: {
      titlePrefix: 'Un Año Más de Vida',
      dedicationTemplate: 'Para [NOMBRE], celebrando otro año de experiencias, aprendizajes y momentos compartidos.',
      backCoverQuote: '"Los años no se cuentan, se celebran"'
    },
    narrativeFlow: {
      structure: 'emotional',
      keyMoments: ['Brindis', 'Familia', 'Amigos', 'Celebración'],
      pacing: 'medium'
    }
  },
  
  'mothers-day': {
    design: {
      suggestedTemplate: 'Romántico - Flores',
      colorPalette: ['#FFC0CB', '#FFB6C1', '#DDA0DD', '#FFFFFF'],
      decorations: ['flores', 'corazones', 'mariposas'],
      fontStyle: 'handwritten',
      mood: 'tender'
    },
    texts: {
      titlePrefix: 'Para Mi Mamá',
      dedicationTemplate: 'Para mamá, quien nos dio la vida y nos enseñó a vivirla con amor. Cada foto es un gracias que nunca será suficiente.',
      backCoverQuote: '"Madre: la palabra más bella pronunciada por el ser humano"'
    },
    narrativeFlow: {
      structure: 'emotional',
      keyMoments: ['Momentos juntos', 'Recuerdos especiales', 'Familia'],
      pacing: 'slow'
    }
  },
  
  'fathers-day': {
    design: {
      suggestedTemplate: 'Clásico - Vintage',
      colorPalette: ['#2C3E50', '#34495E', '#7F8C8D', '#95A5A6'],
      decorations: ['marcos-clasicos', 'corbatas', 'herramientas'],
      fontStyle: 'modern',
      mood: 'respectful'
    },
    texts: {
      titlePrefix: 'Para Mi Papá',
      dedicationTemplate: 'Para papá, nuestro héroe, nuestro guía, nuestro ejemplo. Gracias por cada enseñanza y cada momento a tu lado.',
      backCoverQuote: '"Cualquiera puede ser padre, pero se necesita alguien especial para ser papá"'
    },
    narrativeFlow: {
      structure: 'thematic',
      keyMoments: ['Actividades juntos', 'Enseñanzas', 'Familia'],
      pacing: 'medium'
    }
  },
  
  'baby-shower': {
    design: {
      suggestedTemplate: 'Divertido - Infantil',
      colorPalette: ['#A8E6CF', '#FFD3B6', '#FFAAA5', '#FF8B94'],
      decorations: ['ositos', 'chupetes', 'nubes', 'estrellas'],
      fontStyle: 'playful',
      mood: 'sweet'
    },
    texts: {
      titlePrefix: 'Esperando Tu Llegada',
      dedicationTemplate: 'Para [BEBÉ], antes de conocerte ya te amábamos. Este día celebramos tu próxima llegada rodeados de amor.',
      backCoverQuote: '"Un bebé es el comienzo de todas las cosas: esperanza, sueños, posibilidades"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Decoración', 'Mamá', 'Juegos', 'Regalos', 'Familia'],
      pacing: 'medium'
    }
  },
  
  'baby-first-year': {
    design: {
      suggestedTemplate: 'Natural - Suave',
      colorPalette: ['#FFF8DC', '#F0E68C', '#FFE4B5', '#FAFAD2'],
      decorations: ['ositos', 'nubes', 'lunas', 'estrellas'],
      fontStyle: 'handwritten',
      mood: 'tender'
    },
    texts: {
      titlePrefix: 'Mi Primer Año',
      dedicationTemplate: 'Para [BEBÉ], en tu primer año de vida. Cada día contigo es un regalo que atesoramos con todo nuestro corazón.',
      backCoverQuote: '"En un año pasaste de ser un sueño a ser nuestra realidad más hermosa"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Recién nacido', 'Primer mes', '3 meses', '6 meses', '9 meses', 'Primer año'],
      pacing: 'slow'
    }
  },
  
  'pregnancy': {
    design: {
      suggestedTemplate: 'Romántico - Delicado',
      colorPalette: ['#F8E8E8', '#E8D5D5', '#D5C2C2', '#FFFFFF'],
      decorations: ['flores-delicadas', 'corazones-sutiles', 'mariposas'],
      fontStyle: 'elegant',
      mood: 'expectant'
    },
    texts: {
      titlePrefix: 'Nueve Meses de Amor',
      dedicationTemplate: 'Para nuestro bebé, cada día de espera fue un paso más cerca de ti. Este libro guarda los latidos de tu llegada.',
      backCoverQuote: '"Nueve meses de sueños se convirtieron en una vida de amor"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Anuncio', 'Primer trimestre', 'Segundo trimestre', 'Tercer trimestre', 'Llegada'],
      pacing: 'slow'
    }
  },
  
  'anniversary-couple': {
    design: {
      suggestedTemplate: 'Romántico - Elegante',
      colorPalette: ['#8B0000', '#FFD700', '#FFFFFF', '#F5F5DC'],
      decorations: ['corazones', 'flores', 'anillos'],
      fontStyle: 'elegant',
      mood: 'romantic'
    },
    texts: {
      titlePrefix: 'Nuestros [X] Años Juntos',
      dedicationTemplate: 'Para nosotros, celebrando [X] años de amor, risas, desafíos superados y sueños compartidos. Cada año juntos es un tesoro.',
      backCoverQuote: '"El amor no se mide en años, sino en momentos compartidos"'
    },
    narrativeFlow: {
      structure: 'emotional',
      keyMoments: ['Inicio', 'Momentos especiales', 'Viajes', 'Familia', 'Presente'],
      pacing: 'medium'
    }
  },
  
  'anniversary-other': {
    design: {
      suggestedTemplate: 'Clásico - Formal',
      colorPalette: ['#1C3A6E', '#D4AF37', '#FFFFFF', '#E8E8E8'],
      decorations: ['marcos-elegantes', 'sellos', 'insignias'],
      fontStyle: 'modern',
      mood: 'professional'
    },
    texts: {
      titlePrefix: '[X] Años de Historia',
      dedicationTemplate: 'Celebrando [X] años de logros, crecimiento y momentos que marcaron nuestra trayectoria.',
      backCoverQuote: '"Los años pasan, las historias permanecen"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Inicio', 'Hitos', 'Logros', 'Equipo', 'Futuro'],
      pacing: 'fast'
    }
  },
  
  'graduation': {
    design: {
      suggestedTemplate: 'Moderno - Académico',
      colorPalette: ['#003366', '#C5B358', '#FFFFFF', '#F0F0F0'],
      decorations: ['birrete', 'diploma', 'libros', 'estrellas'],
      fontStyle: 'modern',
      mood: 'achievement'
    },
    texts: {
      titlePrefix: 'Un Nuevo Comienzo',
      dedicationTemplate: 'Para [NOMBRE], en el día que marca el final de una etapa y el inicio de infinitas posibilidades.',
      backCoverQuote: '"El futuro pertenece a quienes creen en la belleza de sus sueños"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: ['Preparación', 'Ceremonia', 'Familia', 'Amigos', 'Celebración'],
      pacing: 'medium'
    }
  },
  
  'artistic': {
    design: {
      suggestedTemplate: 'Minimalista - Clean',
      colorPalette: ['#000000', '#FFFFFF', '#808080', '#B8B8B8'],
      decorations: [],
      fontStyle: 'modern',
      mood: 'minimalist'
    },
    texts: {
      titlePrefix: 'Portafolio',
      dedicationTemplate: 'Colección de trabajos que representan mi visión artística y evolución creativa.',
      backCoverQuote: '"El arte habla donde las palabras no pueden explicar"'
    },
    narrativeFlow: {
      structure: 'thematic',
      keyMoments: ['Serie A', 'Serie B', 'Serie C'],
      pacing: 'slow'
    }
  },
  
  'pet': {
    design: {
      suggestedTemplate: 'Divertido - Natural',
      colorPalette: ['#8B4513', '#DEB887', '#F4A460', '#FFDEAD'],
      decorations: ['huellas', 'huesos', 'corazones'],
      fontStyle: 'playful',
      mood: 'loving'
    },
    texts: {
      titlePrefix: 'Mi Mejor Amigo',
      dedicationTemplate: 'Para [MASCOTA], quien nos enseñó que el amor más puro viene con cuatro patas y un corazón gigante.',
      backCoverQuote: '"No son solo mascotas, son familia"'
    },
    narrativeFlow: {
      structure: 'emotional',
      keyMoments: ['Llegada', 'Momentos diarios', 'Aventuras', 'Amor'],
      pacing: 'medium'
    }
  },
  
  'family': {
    design: {
      suggestedTemplate: 'Clásico - Cálido',
      colorPalette: ['#8B4513', '#CD853F', '#DEB887', '#F5DEB3'],
      decorations: ['marcos-familiares', 'corazones', 'casas'],
      fontStyle: 'handwritten',
      mood: 'warm'
    },
    texts: {
      titlePrefix: 'Nuestra Familia',
      dedicationTemplate: 'Para nosotros, nuestra familia. Cada momento juntos es un tesoro que vale más que cualquier cosa en el mundo.',
      backCoverQuote: '"La familia no es algo importante, es todo"'
    },
    narrativeFlow: {
      structure: 'emotional',
      keyMoments: ['Reuniones', 'Celebraciones', 'Momentos cotidianos', 'Tradiciones'],
      pacing: 'medium'
    }
  },
  
  'generic': {
    design: {
      suggestedTemplate: 'Moderno',
      colorPalette: ['#FFFFFF', '#E0E0E0', '#9E9E9E', '#616161'],
      decorations: [],
      fontStyle: 'modern',
      mood: 'neutral'
    },
    texts: {
      titlePrefix: 'Nuestros Momentos',
      dedicationTemplate: 'Recuerdos que queremos conservar para siempre.',
      backCoverQuote: '"Los momentos se convierten en recuerdos"'
    },
    narrativeFlow: {
      structure: 'chronological',
      keyMoments: [],
      pacing: 'medium'
    }
  }
};

/**
 * Detecta el motivo del fotolibro analizando las fotos
 */
export async function detectEventMotif(
  photos: PhotoAnalysis[],
  stagehand: Stagehand,
  clientHint?: string  // Hint del cliente si lo especificó
): Promise<EventMotifProfile> {
  
  console.log(`\n${'='.repeat(70)}`);
  console.log(`  🎯 DETECCIÓN DE MOTIVO DEL FOTOLIBRO`);
  console.log(`${'='.repeat(70)}`);
  
  if (clientHint) {
    console.log(`  💡 Hint del cliente: "${clientHint}"`);
  }
  
  try {
    // Preparar resumen de fotos para análisis
    const photoSummaries = photos.map((p, idx) => ({
      index: idx,
      filename: p.filename,
      mainSubject: p.content.mainSubject,
      setting: p.content.setting,
      people: p.content.peopleCount,
      emotion: p.emotions.primary,
      eventType: p.narrative.eventType,
      caption: p.narrative.suggestedCaption
    }));
    
    const motifAnalysis = await stagehand.extract({
      instruction: `You are analyzing a photobook to determine its PRIMARY MOTIF/THEME.
      
        ${clientHint ? `Client hint: "${clientHint}"` : ''}
        
        Photos summary:
        ${JSON.stringify(photoSummaries.slice(0, 10), null, 2)}
        ${photos.length > 10 ? `... and ${photos.length - 10} more photos` : ''}
        
        DETECT THE PRIMARY MOTIF from these options:
        
        🎊 CELEBRATIONS:
        - wedding: Wedding ceremony and reception (bride, groom, ceremony, dance, rings)
        - birthday-child: Children's birthday party (under 12 years, toys, cake, games)
        - birthday-teen: Quinceañera / Sweet 16 (15-16 years, formal dress, waltz)
        - birthday-adult: Adult birthday celebration (mature people, dinner, toast)
        
        👶 BABIES & FAMILY:
        - pregnancy: Pregnancy progression (growing belly, ultrasounds, maternity photos)
        - baby-shower: Baby shower event (decorations, games, gifts for baby)
        - baby-first-year: Baby's first year (newborn to 12 months progression)
        - mothers-day: Mother's Day tribute (mother with children, family moments)
        - fathers-day: Father's Day tribute (father with children, dad activities)
        - family: General family moments (multi-generational, holidays, everyday)
        
        💑 RELATIONSHIPS:
        - anniversary-couple: Couple's anniversary (romantic moments, years together)
        - anniversary-other: Business/friendship anniversary (professional, team)
        
        🎓 MILESTONES:
        - graduation: Graduation ceremony (caps, gowns, diplomas, university)
        
        ✈️ ADVENTURES:
        - travel: Travel journey (multiple locations, landmarks, vacation)
        
        🎨 CREATIVE:
        - artistic: Artistic portfolio (professional photos, no people, compositions)
        - pet: Pet album (dogs, cats, animals as main subject)
        
        - generic: No specific motif detected
        
        ANALYSIS CRITERIA:
        1. Look at MAIN SUBJECTS: Are they people? Animals? Landscapes?
        2. Look at SETTINGS: Indoor celebration? Multiple cities? Hospital/medical?
        3. Look at PROGRESSION: Age changes? Location changes? Time of day?
        4. Look at DECORATIONS: Birthday decorations? Wedding flowers? Travel landmarks?
        5. Consider CLIENT HINT if provided
        
        Be VERY specific. For example:
        - If you see a pregnant woman in multiple photos → pregnancy
        - If you see baby + decorations + gifts → baby-shower
        - If you see baby alone in multiple months → baby-first-year
        - If you see wedding dress + ceremony → wedding
        - If you see multiple cities/landmarks → travel
        
        Choose the MOST SPECIFIC motif that matches. Only use 'generic' if really unclear.`,
      
      schema: {
        type: "object",
        properties: {
          primaryMotif: {
            type: "string",
            enum: [
              'wedding', 'travel', 'birthday-child', 'birthday-teen', 'birthday-adult',
              'mothers-day', 'fathers-day', 'baby-shower', 'baby-first-year', 'pregnancy',
              'anniversary-couple', 'anniversary-other', 'graduation', 'artistic', 'pet',
              'family', 'generic'
            ],
            description: "The primary detected motif"
          },
          confidence: {
            type: "number",
            minimum: 0,
            maximum: 100,
            description: "Confidence level 0-100%"
          },
          evidence: {
            type: "string",
            description: "Detailed evidence explaining why this motif was chosen"
          },
          secondaryMotif: {
            type: "string",
            description: "Secondary motif if applicable (e.g., travel + family)"
          },
          keyIndicators: {
            type: "array",
            items: { type: "string" },
            description: "Key visual indicators that led to this conclusion"
          }
        },
        required: ["primaryMotif", "confidence", "evidence"]
      }
    });
    
    const detectedMotif = motifAnalysis.primaryMotif as EventMotif;
    const config = MOTIF_CONFIGS[detectedMotif];
    
    console.log(`\n  ✅ MOTIVO DETECTADO: ${detectedMotif.toUpperCase()}`);
    console.log(`  📊 Confianza: ${motifAnalysis.confidence}%`);
    console.log(`  📝 Evidencia: ${motifAnalysis.evidence}`);
    
    if (motifAnalysis.keyIndicators && motifAnalysis.keyIndicators.length > 0) {
      console.log(`\n  🔍 Indicadores clave:`);
      motifAnalysis.keyIndicators.forEach((indicator: string) => {
        console.log(`     • ${indicator}`);
      });
    }
    
    if (motifAnalysis.secondaryMotif) {
      console.log(`  💡 Motivo secundario: ${motifAnalysis.secondaryMotif}`);
    }
    
    console.log(`\n  🎨 Configuración de diseño aplicada:`);
    console.log(`     Template: ${config.design.suggestedTemplate}`);
    console.log(`     Estilo tipográfico: ${config.design.fontStyle}`);
    console.log(`     Mood: ${config.design.mood}`);
    console.log(`     Decoraciones: ${config.design.decorations.join(', ') || 'Ninguna'}`);
    
    console.log(`${'='.repeat(70)}\n`);
    
    return {
      motif: detectedMotif,
      confidence: motifAnalysis.confidence,
      evidence: motifAnalysis.evidence,
      ...config
    };
    
  } catch (error) {
    console.error(`  ❌ Error detectando motivo:`, error);
    console.log(`  ⚠️  Usando configuración genérica\n`);
    
    return {
      motif: 'generic',
      confidence: 0,
      evidence: 'Error en detección automática',
      ...MOTIF_CONFIGS['generic']
    };
  }
}

/**
 * Aplica configuración específica del motivo a los textos generados
 */
export function applyMotifToTexts(
  motifProfile: EventMotifProfile,
  clientName: string,
  customTitle?: string
): {
  coverTitle: string;
  dedication: string;
  backCoverQuote: string;
} {
  
  // Título
  let coverTitle = customTitle || motifProfile.texts.titlePrefix;
  
  // Reemplazar placeholders
  coverTitle = coverTitle.replace('[NOMBRE]', clientName);
  coverTitle = coverTitle.replace('[X]', ''); // Se llenaría con años específicos
  
  // Dedicatoria
  let dedication = motifProfile.texts.dedicationTemplate;
  dedication = dedication.replace('[NOMBRE]', clientName);
  dedication = dedication.replace('[BEBÉ]', clientName);
  dedication = dedication.replace('[MASCOTA]', clientName);
  dedication = dedication.replace('[X]', ''); // Años
  
  // Frase de contratapa
  const backCoverQuote = motifProfile.texts.backCoverQuote;
  
  return {
    coverTitle,
    dedication,
    backCoverQuote
  };
}
