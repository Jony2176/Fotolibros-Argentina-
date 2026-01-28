
import { Product, Package } from './types';

export const PRODUCTS: Product[] = [
  // APAISADOS (Precios: Gráfica x2) - Imágenes horizontales
  { codigo: 'AP-21x15-BLANDA', nombre: 'Pocket 21×14,8', tamanio: '21 × 14,8 cm', paginasBase: 22, paginasMax: 80, precioBase: 29000, precioPaginaExtra: 700, tipo: 'Apaisado', tapa: 'Blanda', descripcion: 'Formato compacto ideal para recuerdos diarios.', imagen: '/gallery/blanda-apaisado.jpg' },
  { codigo: 'AP-21x15-DURA', nombre: 'Estándar 21×14,8', tamanio: '21 × 14,8 cm', paginasBase: 22, paginasMax: 80, precioBase: 43000, precioPaginaExtra: 700, tipo: 'Apaisado', tapa: 'Dura', descripcion: 'El clásico apaisado con terminación rígida.', imagen: '/gallery/verano-2024.jpg' },
  { codigo: 'AP-28x22-DURA', nombre: 'Grande 27,9×21,6', tamanio: '27,9 × 21,6 cm', paginasBase: 22, paginasMax: 80, precioBase: 60000, precioPaginaExtra: 1300, tipo: 'Apaisado', tapa: 'Dura', descripcion: 'Espacio generoso para tus mejores paisajes.', imagen: '/gallery/bebe-vertical.jpg' },
  { codigo: 'AP-41x29-DURA', nombre: 'Maxi 41×29', tamanio: '41 × 29 cm', paginasBase: 20, paginasMax: 80, precioBase: 118000, precioPaginaExtra: 2600, tipo: 'Apaisado', tapa: 'Dura', badge: 'PREMIUM', descripcion: 'Impactante tamaño para ocasiones únicas.', imagen: '/gallery/amigas-abierto.jpg' },
  { codigo: 'AP-41x29-CUERO', nombre: 'Premium 41×29', tamanio: '41 × 29 cm', paginasBase: 20, paginasMax: 160, precioBase: 124000, precioPaginaExtra: 2600, tipo: 'Apaisado', tapa: 'Simil Cuero', badge: 'LUJO', descripcion: 'El tope de gama con terminación artesanal.', imagen: '/gallery/premium-cuero-apaisado.jpg' },

  // CUADRADOS (Precios: Gráfica x2) - Imágenes cuadradas
  { codigo: 'CU-21x21-BLANDA', nombre: 'Cuadrado 21×21', tamanio: '21 × 21 cm', paginasBase: 22, paginasMax: 80, precioBase: 44000, precioPaginaExtra: 1300, tipo: 'Cuadrado', tapa: 'Blanda', descripcion: 'Formato moderno y versátil.', imagen: '/gallery/blanda-cuadrado.jpg' },
  { codigo: 'CU-21x21-DURA', nombre: 'Cuadrado 21×21', tamanio: '21 × 21 cm', paginasBase: 22, paginasMax: 80, precioBase: 60000, precioPaginaExtra: 1300, tipo: 'Cuadrado', tapa: 'Dura', badge: 'POPULAR', destacado: true, descripcion: 'Nuestro producto más vendido y equilibrado.', imagen: '/gallery/img-03.jpg' },
  { codigo: 'CU-29x29-DURA', nombre: 'Cuadrado Grande 29×29', tamanio: '29 × 29 cm', paginasBase: 20, paginasMax: 80, precioBase: 114000, precioPaginaExtra: 2600, tipo: 'Cuadrado', tapa: 'Dura', badge: 'PREMIUM', descripcion: 'Gran formato cuadrado para bodas y eventos.', imagen: '/gallery/img-02.jpg' },
  { codigo: 'CU-29x29-CUERO', nombre: 'Premium 29×29', tamanio: '29 × 29 cm', paginasBase: 20, paginasMax: 160, precioBase: 118000, precioPaginaExtra: 2600, tipo: 'Cuadrado', tapa: 'Simil Cuero', badge: 'LUJO', descripcion: 'Elegancia pura en formato cuadrado.', imagen: '/gallery/premium-cuero-negro.jpg' },

  // VERTICALES (Precios: Gráfica x2) - Imágenes verticales
  { codigo: 'VE-22x28-BLANDA', nombre: 'A4 Vertical', tamanio: '21,6 × 27,9 cm', paginasBase: 22, paginasMax: 80, precioBase: 44000, precioPaginaExtra: 1300, tipo: 'Vertical', tapa: 'Blanda', descripcion: 'El clásico formato de revista.', imagen: '/gallery/blanda-vertical.jpg' },
  { codigo: 'VE-22x28-DURA', nombre: 'A4 Vertical', tamanio: '21,6 × 27,9 cm', paginasBase: 22, paginasMax: 80, precioBase: 60000, precioPaginaExtra: 1300, tipo: 'Vertical', tapa: 'Dura', descripcion: 'Terminación robusta para tus portfolios.', imagen: '/gallery/graduacion-vertical.jpg' },

  // SOUVENIR (Precios: Gráfica x2) - Imágenes cuadradas
  { codigo: 'SV-10x10-PACK12', nombre: 'Souvenir Pack ×12', tamanio: '10 × 10 cm', paginasBase: 22, paginasMax: 80, precioBase: 60000, precioPaginaExtra: 2600, tipo: 'Mini', tapa: 'Blanda', descripcion: 'Ideal para entregar a tus invitados.', imagen: '/gallery/souvenir-pack.jpg' },
];

export const PACKAGES: Package[] = [
  { id: 'PKG-RECUERDOS-EXPRESS', nombre: '🏃 Recuerdos Express', productoCodigo: 'AP-21x15-DURA', paginas: 22, precio: 43000, descripcion: 'Ideal para escapadas de fin de semana' },
  { id: 'PKG-GRAN-VIAJE', nombre: '✈️ Gran Viaje', productoCodigo: 'CU-21x21-DURA', paginas: 44, precio: 88000, descripcion: 'Perfecto para vacaciones épicas', badge: 'POPULAR' },
  { id: 'PKG-BODA-PREMIUM', nombre: '💒 Boda Premium', productoCodigo: 'CU-29x29-CUERO', paginas: 66, precio: 235000, descripcion: 'El día más importante merece lo mejor' },
];

export interface DesignStyle {
  id: string;
  nombre: string;
  emoji: string;
  descripcion: string;
  colorPrimario: string;
  colorSecundario: string;
  tapa: {
    conTitulo: boolean;
    conTextoLomo: boolean;
    conFondo: boolean;
    estiloFondo: 'solido' | 'gradiente' | 'ninguno';
  };
  interior: {
    fotosRecomendadas: number;
    conFondo: boolean;
    conEtiquetas: boolean;
    conAdornos: boolean;
    conQR: boolean;
  };
  idealPara: string[];
}

export const DESIGN_STYLES: DesignStyle[] = [
  {
    id: 'minimalista',
    nombre: 'Minimalista',
    emoji: '📷',
    descripcion: 'Limpio y moderno. Deja que tus fotos hablen por sí solas.',
    colorPrimario: '#ffffff',
    colorSecundario: '#f5f5f5',
    tapa: { conTitulo: false, conTextoLomo: false, conFondo: false, estiloFondo: 'ninguno' },
    interior: { fotosRecomendadas: 1, conFondo: false, conEtiquetas: false, conAdornos: false, conQR: false },
    idealPara: ['Viajes', 'Paisajes', 'Arquitectura', 'Portfolios']
  },
  {
    id: 'clasico',
    nombre: 'Clásico',
    emoji: '🎀',
    descripcion: 'Elegante y atemporal. Perfecto para momentos especiales.',
    colorPrimario: '#1a365d',
    colorSecundario: '#d69e2e',
    tapa: { conTitulo: true, conTextoLomo: true, conFondo: true, estiloFondo: 'solido' },
    interior: { fotosRecomendadas: 2, conFondo: true, conEtiquetas: true, conAdornos: false, conQR: false },
    idealPara: ['Bodas', 'Graduaciones', 'Aniversarios', 'Familia']
  },
  {
    id: 'divertido',
    nombre: 'Divertido',
    emoji: '🎉',
    descripcion: 'Colorido y alegre. Ideal para celebraciones.',
    colorPrimario: '#ed8936',
    colorSecundario: '#38a169',
    tapa: { conTitulo: true, conTextoLomo: false, conFondo: true, estiloFondo: 'gradiente' },
    interior: { fotosRecomendadas: 3, conFondo: true, conEtiquetas: true, conAdornos: true, conQR: true },
    idealPara: ['Cumpleaños', 'Bebés', 'Mascotas', 'Fiestas']
  },
  {
    id: 'premium',
    nombre: 'Premium',
    emoji: '✨',
    descripcion: 'Lujo y sofisticación. Para regalos inolvidables.',
    colorPrimario: '#2d3748',
    colorSecundario: '#c9a227',
    tapa: { conTitulo: true, conTextoLomo: true, conFondo: true, estiloFondo: 'gradiente' },
    interior: { fotosRecomendadas: 1, conFondo: true, conEtiquetas: true, conAdornos: true, conQR: false },
    idealPara: ['Regalos', 'Aniversarios', 'Quinceañeras', 'Empresas']
  }
];

export const SHIPPING_COSTS: Record<string, number> = {
  'CABA': 2500,
  'AMBA': 3000,
  'Centro': 4500,
  'Cuyo': 5500,
  'NOA': 6500,
  'NEA': 6500,
  'Patagonia Norte': 7000,
  'Patagonia Sur': 9000
};

export const PROVINCIAS_MAPPING: Record<string, string> = {
  'Ciudad Autónoma de Buenos Aires': 'CABA',
  'Buenos Aires': 'AMBA',
  'Córdoba': 'Centro',
  'Santa Fe': 'Centro',
  'Entre Ríos': 'Centro',
  'Mendoza': 'Cuyo',
  'San Juan': 'Cuyo',
  'San Luis': 'Cuyo',
  'Tucumán': 'NOA',
  'Salta': 'NOA',
  'Jujuy': 'NOA',
  'Catamarca': 'NOA',
  'Santiago del Estero': 'NOA',
  'La Rioja': 'NOA',
  'Misiones': 'NEA',
  'Corrientes': 'NEA',
  'Chaco': 'NEA',
  'Formosa': 'NEA',
  'La Pampa': 'Patagonia Norte',
  'Neuquén': 'Patagonia Norte',
  'Río Negro': 'Patagonia Norte',
  'Chubut': 'Patagonia Sur',
  'Santa Cruz': 'Patagonia Sur',
  'Tierra del Fuego': 'Patagonia Sur'
};

// Ciudades principales por provincia para dropdown dinámico
export const CIUDADES_POR_PROVINCIA: Record<string, string[]> = {
  'Ciudad Autónoma de Buenos Aires': ['Balvanera', 'Belgrano', 'Caballito', 'Flores', 'Palermo', 'Recoleta', 'San Telmo', 'Villa Crespo', 'Villa Urquiza'],
  'Buenos Aires': ['La Plata', 'Mar del Plata', 'Bahía Blanca', 'San Justo', 'Ramos Mejía', 'Morón', 'Castelar', 'Ituzaingó', 'Merlo', 'Moreno', 'Caseros', 'San Martín', 'Munro', 'Olivos', 'Vicente López', 'San Isidro', 'Martínez', 'Don Torcuato', 'Tigre', 'San Fernando', 'Avellaneda', 'Lanús', 'Banfield', 'Lomas de Zamora', 'Temperley', 'Adrogué', 'Quilmes', 'Bernal', 'Berazategui', 'Florencio Varela', 'Ezeiza', 'Canning', 'San Vicente', 'Luján', 'Pilar', 'Escobar'],
  'Córdoba': ['Córdoba Capital', 'Villa Carlos Paz', 'Río Cuarto', 'Villa María', 'San Francisco', 'Jesús María', 'Alta Gracia', 'La Falda', 'Cosquín'],
  'Santa Fe': ['Rosario', 'Santa Fe Capital', 'Rafaela', 'Venado Tuerto', 'Reconquista', 'Villa Gobernador Gálvez', 'Casilda', 'Esperanza'],
  'Entre Ríos': ['Paraná', 'Concordia', 'Gualeguaychú', 'Concepción del Uruguay', 'Gualeguay', 'Colón', 'Victoria'],
  'Mendoza': ['Mendoza Capital', 'San Rafael', 'Godoy Cruz', 'Las Heras', 'Guaymallén', 'Luján de Cuyo', 'Maipú', 'Tunuyán'],
  'San Juan': ['San Juan Capital', 'Rawson', 'Rivadavia', 'Chimbas', 'Pocito', 'Caucete'],
  'San Luis': ['San Luis Capital', 'Villa Mercedes', 'Merlo', 'La Punta', 'Juana Koslay'],
  'Tucumán': ['San Miguel de Tucumán', 'Yerba Buena', 'Tafí Viejo', 'Banda del Río Salí', 'Concepción', 'Famaillá'],
  'Salta': ['Salta Capital', 'San Ramón de la Nueva Orán', 'Tartagal', 'General Güemes', 'Cafayate'],
  'Jujuy': ['San Salvador de Jujuy', 'Palpalá', 'San Pedro', 'Libertador General San Martín', 'Tilcara', 'Humahuaca'],
  'Catamarca': ['San Fernando del Valle de Catamarca', 'Recreo', 'Fray Mamerto Esquiú', 'Andalgalá', 'Belén'],
  'Santiago del Estero': ['Santiago del Estero Capital', 'La Banda', 'Termas de Río Hondo', 'Añatuya', 'Frías'],
  'La Rioja': ['La Rioja Capital', 'Chilecito', 'Aimogasta', 'Chamical'],
  'Misiones': ['Posadas', 'Oberá', 'Eldorado', 'Puerto Iguazú', 'San Vicente', 'Apóstoles'],
  'Corrientes': ['Corrientes Capital', 'Goya', 'Paso de los Libres', 'Mercedes', 'Curuzú Cuatiá', 'Bella Vista'],
  'Chaco': ['Resistencia', 'Presidencia Roque Sáenz Peña', 'Villa Ángela', 'General San Martín', 'Barranqueras'],
  'Formosa': ['Formosa Capital', 'Clorinda', 'Pirané', 'El Colorado'],
  'La Pampa': ['Santa Rosa', 'General Pico', 'Toay', 'General Acha'],
  'Neuquén': ['Neuquén Capital', 'Centenario', 'Plottier', 'San Martín de los Andes', 'Villa La Angostura', 'Zapala'],
  'Río Negro': ['Viedma', 'San Carlos de Bariloche', 'General Roca', 'Cipolletti', 'Villa Regina', 'El Bolsón'],
  'Chubut': ['Rawson', 'Comodoro Rivadavia', 'Trelew', 'Puerto Madryn', 'Esquel'],
  'Santa Cruz': ['Río Gallegos', 'Caleta Olivia', 'El Calafate', 'Pico Truncado', 'Puerto Deseado'],
  'Tierra del Fuego': ['Ushuaia', 'Río Grande', 'Tolhuin']
};

// Códigos postales típicos por ciudad (para auto-completar)
export const CP_POR_CIUDAD: Record<string, string> = {
  // CABA
  'Balvanera': '1178', 'Belgrano': '1428', 'Caballito': '1405', 'Flores': '1406',
  'Palermo': '1425', 'Recoleta': '1010', 'San Telmo': '1068', 'Villa Crespo': '1414', 'Villa Urquiza': '1431',
  // Buenos Aires
  'La Plata': '1900', 'Mar del Plata': '7600', 'Bahía Blanca': '8000', 'Tandil': '7000',
  'San Isidro': '1642', 'Vicente López': '1638', 'Quilmes': '1878', 'Lomas de Zamora': '1832',
  'Tigre': '1648', 'Pilar': '1629', 'Morón': '1708', 'Avellaneda': '1870', 'Lanús': '1824',
  // Córdoba
  'Córdoba Capital': '5000', 'Villa Carlos Paz': '5152', 'Río Cuarto': '5800', 'Villa María': '5900',
  // Santa Fe
  'Rosario': '2000', 'Santa Fe Capital': '3000', 'Rafaela': '2300', 'Venado Tuerto': '2600',
  // Mendoza
  'Mendoza Capital': '5500', 'San Rafael': '5600', 'Godoy Cruz': '5501', 'Luján de Cuyo': '5507',
  // Tucumán
  'San Miguel de Tucumán': '4000', 'Yerba Buena': '4107',
  // Salta
  'Salta Capital': '4400', 'Cafayate': '4427',
  // Neuquén
  'Neuquén Capital': '8300', 'San Martín de los Andes': '8370', 'Villa La Angostura': '8407',
  // Río Negro
  'San Carlos de Bariloche': '8400', 'Cipolletti': '8324', 'General Roca': '8332', 'El Bolsón': '8430',
  // Chubut
  'Comodoro Rivadavia': '9000', 'Trelew': '9100', 'Puerto Madryn': '9120', 'Esquel': '9200',
  // Santa Cruz
  'Río Gallegos': '9400', 'El Calafate': '9405', 'Caleta Olivia': '9011',
  // Tierra del Fuego
  'Ushuaia': '9410', 'Río Grande': '9420',
  // Misiones
  'Posadas': '3300', 'Puerto Iguazú': '3370',
  // Corrientes
  'Corrientes Capital': '3400',
  // Entre Ríos
  'Paraná': '3100', 'Concordia': '3200',
};
