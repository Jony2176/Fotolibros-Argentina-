
export interface Product {
  codigo: string;
  nombre: string;
  tamanio: string;           // "21 × 21 cm"
  paginasBase: number;
  paginasMax: number;
  precioBase: number;        // Precio de venta
  precioPaginaExtra: number;
  tipo: 'Cuadrado' | 'Apaisado' | 'Vertical' | 'Mini';
  tapa: 'Blanda' | 'Dura' | 'Simil Cuero';
  descripcion: string;
  imagen: string;
  badge?: string;
  destacado?: boolean;
}

export interface Package {
  id: string;
  nombre: string;
  productoCodigo: string;
  paginas: number;
  precio: number;
  descripcion: string;
  badge?: string;
}

export interface OrderDetails {
  id?: string;
  productoCodigo: string;
  paginasTotal: number;
  fotos: File[];
  cliente: {
    nombre: string;
    email: string;
    telefono: string;
    direccion: {
      calle: string;
      piso?: string;
      ciudad: string;
      provincia: string;
      cp: string;
    };
  };
  metodoPago: 'mercadopago' | 'transferencia';
  comprobante?: File;
  estado: OrderStatus;
  total: number;
}

export enum OrderStatus {
  PENDIENTE_PAGO = 'pendiente_pago',
  VERIFICANDO_PAGO = 'verificando_pago',
  PAGO_APROBADO = 'pago_aprobado',
  EN_PRODUCCION = 'en_produccion',
  EN_DEPOSITO = 'en_deposito',
  ENVIADO = 'enviado',
  ENTREGADO = 'entregado'
}

export const STATUS_CONFIG = {
  [OrderStatus.PENDIENTE_PAGO]: { label: 'Pendiente de Pago', color: 'bg-yellow-100 text-yellow-800', dot: 'bg-yellow-500' },
  [OrderStatus.VERIFICANDO_PAGO]: { label: 'Verificando Pago', color: 'bg-blue-100 text-blue-800', dot: 'bg-blue-500' },
  [OrderStatus.PAGO_APROBADO]: { label: 'Pago Aprobado', color: 'bg-green-100 text-green-800', dot: 'bg-green-500' },
  [OrderStatus.EN_PRODUCCION]: { label: 'En Producción', color: 'bg-orange-100 text-orange-800', dot: 'bg-orange-500' },
  [OrderStatus.EN_DEPOSITO]: { label: 'En Mi Domicilio', color: 'bg-purple-100 text-purple-800', dot: 'bg-purple-500' },
  [OrderStatus.ENVIADO]: { label: 'Enviado', color: 'bg-indigo-100 text-indigo-800', dot: 'bg-indigo-500' },
  [OrderStatus.ENTREGADO]: { label: 'Entregado', color: 'bg-gray-100 text-gray-800', dot: 'bg-gray-500' },
};
