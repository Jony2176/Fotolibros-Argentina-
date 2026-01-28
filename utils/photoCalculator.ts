/**
 * Photo Calculator Utility
 * =========================
 * Calcula cuántas fotos mínimas y recomendadas necesita el cliente
 * según el tamaño del libro y la cantidad de páginas.
 */

export interface PhotoRequirements {
  minPhotos: number;
  recommendedMin: number;
  recommendedMax: number;
  photosPerPage: {
    min: number;
    max: number;
  };
  warnings: string[];
  tips: string[];
}

/**
 * Calcula requisitos de fotos según el tamaño del libro y páginas totales
 */
export function calculatePhotoRequirements(
  productCode: string,
  totalPages: number
): PhotoRequirements {
  // Páginas útiles (sin contar tapa, contratapa, dedicatoria)
  const usablePages = Math.max(0, totalPages - 4);
  
  // Configuración según tamaño del libro
  const sizeConfig = getSizeConfiguration(productCode);
  
  // Cálculos
  const minPhotosPerPage = sizeConfig.minPhotosPerPage;
  const maxPhotosPerPage = sizeConfig.maxPhotosPerPage;
  const recommendedPhotosPerPage = sizeConfig.recommendedPhotosPerPage;
  
  const minPhotos = Math.max(10, usablePages * minPhotosPerPage);
  const recommendedMin = usablePages * recommendedPhotosPerPage;
  const recommendedMax = usablePages * maxPhotosPerPage;
  
  // Warnings y tips
  const warnings: string[] = [];
  const tips: string[] = [];
  
  if (usablePages < 10) {
    warnings.push('Libro muy corto. Considera agregar más páginas para un mejor resultado.');
  }
  
  if (minPhotos > 100) {
    warnings.push('Este libro requiere muchas fotos. Asegúrate de tener suficientes imágenes de calidad.');
  }
  
  // Tips según tamaño
  tips.push(...sizeConfig.tips);
  
  // Tip general
  tips.push(`Recomendamos ${recommendedPhotosPerPage} fotos por página para un diseño equilibrado.`);
  
  if (sizeConfig.allowsFullPagePhotos) {
    tips.push('Puedes usar fotos a página completa para momentos especiales.');
  }
  
  return {
    minPhotos,
    recommendedMin,
    recommendedMax,
    photosPerPage: {
      min: minPhotosPerPage,
      max: maxPhotosPerPage
    },
    warnings,
    tips
  };
}

interface SizeConfiguration {
  minPhotosPerPage: number;
  maxPhotosPerPage: number;
  recommendedPhotosPerPage: number;
  allowsFullPagePhotos: boolean;
  tips: string[];
}

/**
 * Configuración de fotos por tamaño de libro
 */
function getSizeConfiguration(productCode: string): SizeConfiguration {
  // Mapeo de códigos de producto a configuración
  const configurations: Record<string, SizeConfiguration> = {
    // Fotolibros Cuadrados 20x20cm (más común)
    'FOTOLIBRO_CUADRADO_20X20_20PAG': {
      minPhotosPerPage: 1,
      maxPhotosPerPage: 4,
      recommendedPhotosPerPage: 2,
      allowsFullPagePhotos: true,
      tips: [
        'Tamaño cuadrado ideal para collages y diseños creativos.',
        'Combina fotos individuales con composiciones de 2-4 fotos.'
      ]
    },
    
    'FOTOLIBRO_CUADRADO_20X20_40PAG': {
      minPhotosPerPage: 1,
      maxPhotosPerPage: 4,
      recommendedPhotosPerPage: 2,
      allowsFullPagePhotos: true,
      tips: [
        '40 páginas permiten contar una historia más completa.',
        'Alterna páginas con 1 foto grande y páginas con 3-4 fotos pequeñas.'
      ]
    },
    
    'FOTOLIBRO_CUADRADO_20X20_60PAG': {
      minPhotosPerPage: 2,
      maxPhotosPerPage: 6,
      recommendedPhotosPerPage: 3,
      allowsFullPagePhotos: true,
      tips: [
        'Libro grande: perfecto para eventos completos (bodas, viajes largos).',
        'Usa 2-3 fotos por página para mantener calidad visual.'
      ]
    },
    
    // Fotolibros Horizontales 28x20cm
    'FOTOLIBRO_HORIZONTAL_28X20_20PAG': {
      minPhotosPerPage: 1,
      maxPhotosPerPage: 3,
      recommendedPhotosPerPage: 2,
      allowsFullPagePhotos: true,
      tips: [
        'Formato horizontal ideal para fotos panorámicas y paisajes.',
        'Usa 1-2 fotos horizontales por página para mejor impacto.'
      ]
    },
    
    'FOTOLIBRO_HORIZONTAL_28X20_40PAG': {
      minPhotosPerPage: 1,
      maxPhotosPerPage: 4,
      recommendedPhotosPerPage: 2,
      allowsFullPagePhotos: true,
      tips: [
        'Perfecto para viajes y eventos con muchas fotos panorámicas.',
        'Combina fotos apaisadas grandes con collages de 3-4 fotos.'
      ]
    },
    
    // Fotolibros Grandes 30x30cm
    'FOTOLIBRO_CUADRADO_30X30_20PAG': {
      minPhotosPerPage: 1,
      maxPhotosPerPage: 6,
      recommendedPhotosPerPage: 3,
      allowsFullPagePhotos: true,
      tips: [
        'Tamaño premium: ideal para fotos de alta resolución.',
        'Aprovecha el espacio con 3-4 fotos por página o 1 foto a sangre completa.'
      ]
    },
    
    'FOTOLIBRO_CUADRADO_30X30_40PAG': {
      minPhotosPerPage: 2,
      maxPhotosPerPage: 6,
      recommendedPhotosPerPage: 3,
      allowsFullPagePhotos: true,
      tips: [
        'Tamaño profesional: perfecto para bodas y eventos especiales.',
        'Usa diseños variados: 1 foto grande, 2-3 medianas, o collages de 4-6.'
      ]
    },
    
    // Revistas A5 (14.8x21cm)
    'REVISTA_A5_20PAG': {
      minPhotosPerPage: 1,
      maxPhotosPerPage: 2,
      recommendedPhotosPerPage: 1,
      allowsFullPagePhotos: true,
      tips: [
        'Formato compacto: mejor con 1-2 fotos por página.',
        'Ideal para catálogos o recuerdos de eventos breves.'
      ]
    },
    
    'REVISTA_A5_40PAG': {
      minPhotosPerPage: 1,
      maxPhotosPerPage: 3,
      recommendedPhotosPerPage: 2,
      allowsFullPagePhotos: true,
      tips: [
        'Revista más extensa: perfecto para storytelling.',
        'Alterna 1 foto grande con páginas de 2-3 fotos.'
      ]
    },
    
    // Revistas A4 (21x29.7cm)
    'REVISTA_A4_20PAG': {
      minPhotosPerPage: 1,
      maxPhotosPerPage: 4,
      recommendedPhotosPerPage: 2,
      allowsFullPagePhotos: true,
      tips: [
        'Formato revista: ideal para presentaciones profesionales.',
        'Usa layouts editoriales con 2-4 fotos por spread.'
      ]
    },
    
    'REVISTA_A4_40PAG': {
      minPhotosPerPage: 2,
      maxPhotosPerPage: 6,
      recommendedPhotosPerPage: 3,
      allowsFullPagePhotos: true,
      tips: [
        'Revista profesional: perfecto para portfolios.',
        'Combina fotos full-page con grids de 3-6 fotos.'
      ]
    }
  };
  
  // Default para productos no configurados
  const defaultConfig: SizeConfiguration = {
    minPhotosPerPage: 1,
    maxPhotosPerPage: 4,
    recommendedPhotosPerPage: 2,
    allowsFullPagePhotos: true,
    tips: [
      'Usa fotos de alta resolución para mejor calidad de impresión.',
      'Combina fotos individuales con collages para variedad.'
    ]
  };
  
  return configurations[productCode] || defaultConfig;
}

/**
 * Calcula si la cantidad de fotos actual es suficiente
 */
export function isPhotoCountSufficient(
  currentPhotoCount: number,
  requirements: PhotoRequirements
): {
  isSufficient: boolean;
  status: 'insufficient' | 'minimum' | 'good' | 'excellent';
  message: string;
} {
  if (currentPhotoCount < requirements.minPhotos) {
    return {
      isSufficient: false,
      status: 'insufficient',
      message: `Faltan ${requirements.minPhotos - currentPhotoCount} fotos para alcanzar el mínimo`
    };
  }
  
  if (currentPhotoCount < requirements.recommendedMin) {
    return {
      isSufficient: true,
      status: 'minimum',
      message: 'Has alcanzado el mínimo. Considera agregar más fotos para un mejor diseño.'
    };
  }
  
  if (currentPhotoCount <= requirements.recommendedMax) {
    return {
      isSufficient: true,
      status: 'good',
      message: '¡Perfecto! Tienes la cantidad ideal de fotos.'
    };
  }
  
  return {
    isSufficient: true,
    status: 'excellent',
    message: '¡Excelente! Tienes muchas fotos para crear un fotolibro espectacular.'
  };
}

/**
 * Formatea los requisitos para mostrar al usuario
 */
export function formatPhotoRequirements(requirements: PhotoRequirements): string {
  const { recommendedMin, recommendedMax, photosPerPage } = requirements;
  
  return `
Se recomienda entre ${recommendedMin} y ${recommendedMax} fotos 
(${photosPerPage.min}-${photosPerPage.max} fotos por página)
  `.trim();
}
