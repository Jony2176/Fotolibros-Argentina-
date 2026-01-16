
import { Product, Package } from './types';

export const PRODUCTS: Product[] = [
  { codigo: 'CU-21x21-DURA', nombre: '21x21 Tapa Dura', paginasBase: 22, precioBase: 40800, precioPaginaExtra: 850, tipo: 'Cuadrado', imagen: 'https://picsum.photos/seed/p1/400/400' },
  { codigo: 'CU-21x21-BLANDA', nombre: '21x21 Tapa Blanda', paginasBase: 22, precioBase: 30600, precioPaginaExtra: 700, tipo: 'Cuadrado', imagen: 'https://picsum.photos/seed/p2/400/400' },
  { codigo: 'CU-15x15-DURA', nombre: '15x15 Tapa Dura', paginasBase: 22, precioBase: 28900, precioPaginaExtra: 600, tipo: 'Cuadrado', imagen: 'https://picsum.photos/seed/p3/400/400' },
  { codigo: 'CU-15x15-BLANDA', nombre: '15x15 Tapa Blanda', paginasBase: 22, precioBase: 23000, precioPaginaExtra: 500, tipo: 'Cuadrado', imagen: 'https://picsum.photos/seed/p4/400/400' },
  { codigo: 'HO-21x15-DURA', nombre: 'Horizontal Tapa Dura', paginasBase: 22, precioBase: 35700, precioPaginaExtra: 750, tipo: 'Horizontal', imagen: 'https://picsum.photos/seed/p5/400/400' },
  { codigo: 'VE-15x21-DURA', nombre: 'Vertical Tapa Dura', paginasBase: 22, precioBase: 35700, precioPaginaExtra: 750, tipo: 'Vertical', imagen: 'https://picsum.photos/seed/p6/400/400' },
  { codigo: 'CU-30x30-DURA', nombre: '30x30 Tapa Dura', paginasBase: 22, precioBase: 73500, precioPaginaExtra: 1500, tipo: 'Cuadrado', imagen: 'https://picsum.photos/seed/p7/400/400' },
  { codigo: 'MINI-10x10', nombre: 'Mini 10x10', paginasBase: 22, precioBase: 14300, precioPaginaExtra: 300, tipo: 'Mini', imagen: 'https://picsum.photos/seed/p8/400/400' },
];

export const PACKAGES: Package[] = [
  { nombre: '🏃 Recuerdos Express', productoCodigo: 'CU-21x21-DURA', paginas: 22, precio: 23500, descripcion: 'Ideal para escapadas de fin de semana', badge: 'POPULAR' },
  { nombre: '✈️ Gran Viaje', productoCodigo: 'CU-21x21-DURA', paginas: 44, precio: 42000, descripcion: 'Perfecto para vacaciones épicas' },
  { nombre: '💒 Boda Premium', productoCodigo: 'CU-30x30-DURA', paginas: 66, precio: 95000, descripcion: 'El día más importante merece lo mejor' },
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
