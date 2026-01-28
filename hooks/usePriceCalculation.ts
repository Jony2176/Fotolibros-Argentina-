/**
 * usePriceCalculation Hook
 * ========================
 * Calcula precios, descuentos y totales basados en el pedido
 */

import { useMemo } from 'react';
import { PRODUCTS, PROVINCIAS_MAPPING, SHIPPING_COSTS } from '../constants';

// =============================================================================
// TYPES
// =============================================================================

export interface PriceBreakdown {
  // Producto
  productName: string;
  productSize: string;
  
  // Precios base
  basePrice: number;
  basePagesIncluded: number;
  
  // Páginas extra
  extraPages: number;
  pricePerExtraPage: number;
  extraPagesTotal: number;
  
  // Envío
  shippingZone: string | null;
  shippingCost: number;
  
  // Subtotales
  subtotal: number;
  
  // Descuentos
  discountPercentage: number;
  discountReason: string | null;
  discountAmount: number;
  
  // Total final
  total: number;
  
  // Helpers
  hasDiscount: boolean;
  formattedTotal: string;
  formattedSubtotal: string;
  formattedDiscount: string;
}

interface UsePriceCalculationParams {
  productoCodigo: string;
  paginasTotal: number;
  provincia: string;
  metodoPago: 'transferencia' | 'modo';
}

// =============================================================================
// CONSTANTS
// =============================================================================

const TRANSFER_DISCOUNT_PERCENTAGE = 15;

// =============================================================================
// HOOK
// =============================================================================

export function usePriceCalculation({
  productoCodigo,
  paginasTotal,
  provincia,
  metodoPago
}: UsePriceCalculationParams): PriceBreakdown {
  
  return useMemo(() => {
    // Find product
    const product = PRODUCTS.find(p => p.codigo === productoCodigo);
    
    if (!product) {
      return {
        productName: '',
        productSize: '',
        basePrice: 0,
        basePagesIncluded: 0,
        extraPages: 0,
        pricePerExtraPage: 0,
        extraPagesTotal: 0,
        shippingZone: null,
        shippingCost: 0,
        subtotal: 0,
        discountPercentage: 0,
        discountReason: null,
        discountAmount: 0,
        total: 0,
        hasDiscount: false,
        formattedTotal: '$0',
        formattedSubtotal: '$0',
        formattedDiscount: '$0'
      };
    }

    // Base calculations
    const basePrice = product.precioBase;
    const basePagesIncluded = product.paginasBase;
    const pricePerExtraPage = product.precioPaginaExtra;
    
    // Extra pages
    const extraPages = Math.max(0, paginasTotal - basePagesIncluded);
    const extraPagesTotal = extraPages * pricePerExtraPage;
    
    // Shipping
    const shippingZone = provincia ? PROVINCIAS_MAPPING[provincia] : null;
    const shippingCost = shippingZone ? SHIPPING_COSTS[shippingZone] : 0;
    
    // Subtotal (before discounts)
    const subtotal = basePrice + extraPagesTotal + shippingCost;
    
    // Discounts
    const isTransfer = metodoPago === 'transferencia';
    const discountPercentage = isTransfer ? TRANSFER_DISCOUNT_PERCENTAGE : 0;
    const discountReason = isTransfer ? 'Descuento por transferencia bancaria' : null;
    const discountAmount = isTransfer ? Math.round(subtotal * (TRANSFER_DISCOUNT_PERCENTAGE / 100)) : 0;
    
    // Final total
    const total = subtotal - discountAmount;
    
    // Format helpers
    const formatCurrency = (value: number) => 
      `$${value.toLocaleString('es-AR')}`;

    return {
      productName: product.nombre,
      productSize: product.tamanio,
      basePrice,
      basePagesIncluded,
      extraPages,
      pricePerExtraPage,
      extraPagesTotal,
      shippingZone,
      shippingCost,
      subtotal,
      discountPercentage,
      discountReason,
      discountAmount,
      total,
      hasDiscount: discountAmount > 0,
      formattedTotal: formatCurrency(total),
      formattedSubtotal: formatCurrency(subtotal),
      formattedDiscount: formatCurrency(discountAmount)
    };
  }, [productoCodigo, paginasTotal, provincia, metodoPago]);
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Calcula cuántas fotos se recomiendan según las páginas y estilo
 */
export function getRecommendedPhotos(
  paginasTotal: number, 
  estiloDiseno: string
): { min: number; max: number; recommended: number } {
  const photosPerPage: Record<string, number> = {
    'sin_diseno': 1,
    'minimalista': 1,
    'clasico': 2,
    'divertido': 3,
    'premium': 1.5
  };
  
  const ratio = photosPerPage[estiloDiseno] || 2;
  const spreadCount = Math.floor(paginasTotal / 2); // Páginas internas (doble página)
  
  const recommended = Math.round(spreadCount * ratio);
  
  return {
    min: 10,
    max: 200,
    recommended: Math.max(10, Math.min(200, recommended))
  };
}

/**
 * Estima el tiempo de producción basado en la complejidad
 */
export function estimateProductionTime(
  paginasTotal: number,
  fotosCount: number
): { minDays: number; maxDays: number; label: string } {
  // Base: 7-10 días
  let minDays = 7;
  let maxDays = 10;
  
  // Más páginas = más tiempo
  if (paginasTotal > 40) {
    minDays += 2;
    maxDays += 2;
  }
  if (paginasTotal > 60) {
    minDays += 2;
    maxDays += 2;
  }
  
  // Más fotos = más tiempo de procesamiento
  if (fotosCount > 100) {
    minDays += 1;
    maxDays += 1;
  }
  
  return {
    minDays,
    maxDays,
    label: `${minDays}-${maxDays} días hábiles`
  };
}

export default usePriceCalculation;
