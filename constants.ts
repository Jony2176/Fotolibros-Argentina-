
import { Product, Package } from './types';

export const PRODUCTS: Product[] = [
  // APAISADOS
  { codigo: 'AP-21x15-BLANDA', nombre: 'Pocket 21×14,8', tamanio: '21 × 14,8 cm', paginasBase: 22, paginasMax: 80, precioBase: 19550, precioPaginaExtra: 425, tipo: 'Apaisado', tapa: 'Blanda', descripcion: 'Formato compacto ideal para recuerdos diarios.', imagen: 'https://picsum.photos/seed/ap1/400/300' },
  { codigo: 'AP-21x15-DURA', nombre: 'Estándar 21×14,8', tamanio: '21 × 14,8 cm', paginasBase: 22, paginasMax: 80, precioBase: 28730, precioPaginaExtra: 425, tipo: 'Apaisado', tapa: 'Dura', descripcion: 'El clásico apaisado con terminación rígida.', imagen: 'https://picsum.photos/seed/ap2/400/300' },
  { codigo: 'AP-28x22-DURA', nombre: 'Grande 27,9×21,6', tamanio: '27,9 × 21,6 cm', paginasBase: 22, paginasMax: 80, precioBase: 40800, precioPaginaExtra: 850, tipo: 'Apaisado', tapa: 'Dura', descripcion: 'Espacio generoso para tus mejores paisajes.', imagen: 'https://picsum.photos/seed/ap3/400/300' },
  { codigo: 'AP-41x29-DURA', nombre: 'Maxi 41×29', tamanio: '41 × 29 cm', paginasBase: 20, paginasMax: 80, precioBase: 79900, precioPaginaExtra: 1700, tipo: 'Apaisado', tapa: 'Dura', badge: 'PREMIUM', descripcion: 'Impactante tamaño para ocasiones únicas.', imagen: 'https://picsum.photos/seed/ap4/400/300' },
  { codigo: 'AP-41x29-CUERO', nombre: 'Premium 41×29', tamanio: '41 × 29 cm', paginasBase: 20, paginasMax: 80, precioBase: 83300, precioPaginaExtra: 1700, tipo: 'Apaisado', tapa: 'Simil Cuero', badge: 'LUJO', descripcion: 'El tope de gama con terminación artesanal.', imagen: 'https://picsum.photos/seed/ap5/400/300' },
  
  // CUADRADOS
  { codigo: 'CU-21x21-BLANDA', nombre: 'Cuadrado 21×21', tamanio: '21 × 21 cm', paginasBase: 22, paginasMax: 80, precioBase: 29750, precioPaginaExtra: 850, tipo: 'Cuadrado', tapa: 'Blanda', descripcion: 'Formato moderno y versátil.', imagen: 'https://picsum.photos/seed/cu1/400/400' },
  { codigo: 'CU-21x21-DURA', nombre: 'Cuadrado 21×21', tamanio: '21 × 21 cm', paginasBase: 22, paginasMax: 80, precioBase: 40800, precioPaginaExtra: 850, tipo: 'Cuadrado', tapa: 'Dura', badge: 'POPULAR', destacado: true, descripcion: 'Nuestro producto más vendido y equilibrado.', imagen: 'https://picsum.photos/seed/cu2/400/400' },
  { codigo: 'CU-29x29-DURA', nombre: 'Cuadrado Grande 29×29', tamanio: '29 × 29 cm', paginasBase: 20, paginasMax: 80, precioBase: 76500, precioPaginaExtra: 1700, tipo: 'Cuadrado', tapa: 'Dura', badge: 'PREMIUM', descripcion: 'Gran formato cuadrado para bodas y eventos.', imagen: 'https://picsum.photos/seed/cu3/400/400' },
  { codigo: 'CU-29x29-CUERO', nombre: 'Premium 29×29', tamanio: '29 × 29 cm', paginasBase: 20, paginasMax: 80, precioBase: 79900, precioPaginaExtra: 1700, tipo: 'Cuadrado', tapa: 'Simil Cuero', badge: 'LUJO', descripcion: 'Elegancia pura en formato cuadrado.', imagen: 'https://picsum.photos/seed/cu4/400/400' },

  // VERTICALES
  { codigo: 'VE-22x28-BLANDA', nombre: 'A4 Vertical', tamanio: '21,6 × 27,9 cm', paginasBase: 22, paginasMax: 80, precioBase: 29750, precioPaginaExtra: 850, tipo: 'Vertical', tapa: 'Blanda', descripcion: 'El clásico formato de revista.', imagen: 'https://picsum.photos/seed/ve1/400/500' },
  { codigo: 'VE-22x28-DURA', nombre: 'A4 Vertical', tamanio: '21,6 × 27,9 cm', paginasBase: 22, paginasMax: 80, precioBase: 40800, precioPaginaExtra: 850, tipo: 'Vertical', tapa: 'Dura', descripcion: 'Terminación robusta para tus portfolios.', imagen: 'https://picsum.photos/seed/ve2/400/500' },

  // SOUVENIR
  { codigo: 'SV-10x10-PACK12', nombre: 'Souvenir Pack ×12', tamanio: '10 × 10 cm', paginasBase: 22, paginasMax: 80, precioBase: 40800, precioPaginaExtra: 1700, tipo: 'Mini', tapa: 'Blanda', descripcion: 'Ideal para entregar a tus invitados.', imagen: 'https://picsum.photos/seed/sv1/400/400' },
];

export const PACKAGES: Package[] = [
  { id: 'PKG-RECUERDOS-EXPRESS', nombre: '🏃 Recuerdos Express', productoCodigo: 'AP-21x15-DURA', paginas: 22, precio: 23500, descripcion: 'Ideal para escapadas de fin de semana' },
  { id: 'PKG-GRAN-VIAJE', nombre: '✈️ Gran Viaje', productoCodigo: 'CU-21x21-DURA', paginas: 44, precio: 42000, descripcion: 'Perfecto para vacaciones épicas', badge: 'POPULAR' },
  { id: 'PKG-BODA-PREMIUM', nombre: '💒 Boda Premium', productoCodigo: 'CU-29x29-CUERO', paginas: 66, precio: 95000, descripcion: 'El día más importante merece lo mejor' },
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
