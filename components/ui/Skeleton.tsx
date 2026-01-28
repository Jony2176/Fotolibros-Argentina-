/**
 * Skeleton Component
 * ==================
 * Componente de loading state con efecto shimmer para mejorar UX
 * durante la carga de contenido.
 */

import React from 'react';

// =============================================================================
// BASE SKELETON
// =============================================================================

interface SkeletonProps {
  className?: string;
  /** Ancho del skeleton (ej: "100%", "200px", "w-full") */
  width?: string;
  /** Alto del skeleton (ej: "20px", "h-4") */
  height?: string;
  /** Forma: rectangular o circular */
  variant?: 'rectangular' | 'circular' | 'text';
  /** Animacion activa */
  animate?: boolean;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  className = '',
  width,
  height,
  variant = 'rectangular',
  animate = true
}) => {
  const baseClasses = 'bg-gray-200';
  const animationClasses = animate ? 'animate-pulse' : '';
  
  const variantClasses = {
    rectangular: 'rounded-md',
    circular: 'rounded-full',
    text: 'rounded'
  };

  const style: React.CSSProperties = {};
  if (width) style.width = width;
  if (height) style.height = height;

  return (
    <div 
      className={`${baseClasses} ${animationClasses} ${variantClasses[variant]} ${className}`}
      style={style}
      aria-hidden="true"
      role="presentation"
    />
  );
};

// =============================================================================
// PRESET SKELETONS
// =============================================================================

/**
 * Skeleton para tarjeta de producto
 */
export const ProductCardSkeleton: React.FC = () => (
  <div className="bg-white p-4 rounded-xl border border-gray-100 shadow-sm space-y-3">
    {/* Image placeholder */}
    <Skeleton className="w-full h-32 md:h-40" variant="rectangular" />
    
    {/* Title */}
    <Skeleton className="h-4 w-3/4" variant="text" />
    
    {/* Subtitle */}
    <Skeleton className="h-3 w-1/2" variant="text" />
    
    {/* Price row */}
    <div className="flex justify-between items-center pt-2">
      <div className="space-y-1">
        <Skeleton className="h-2 w-12" variant="text" />
        <Skeleton className="h-5 w-16" variant="text" />
      </div>
      <Skeleton className="w-9 h-9" variant="circular" />
    </div>
  </div>
);

/**
 * Skeleton para grid de productos
 */
export const ProductGridSkeleton: React.FC<{ count?: number }> = ({ count = 8 }) => (
  <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 md:gap-4">
    {Array(count).fill(0).map((_, i) => (
      <ProductCardSkeleton key={i} />
    ))}
  </div>
);

/**
 * Skeleton para formulario de delivery
 */
export const DeliveryFormSkeleton: React.FC = () => (
  <div className="space-y-4">
    <Skeleton className="h-6 w-40" variant="text" />
    
    <div className="bg-white p-4 md:p-5 rounded-xl border border-gray-100 space-y-4">
      {/* Row 1: Name & Email */}
      <div className="grid sm:grid-cols-2 gap-3">
        <div className="space-y-1">
          <Skeleton className="h-3 w-24 ml-1" variant="text" />
          <Skeleton className="h-12 w-full" variant="rectangular" />
        </div>
        <div className="space-y-1">
          <Skeleton className="h-3 w-16 ml-1" variant="text" />
          <Skeleton className="h-12 w-full" variant="rectangular" />
        </div>
      </div>
      
      {/* Row 2: Phone */}
      <div className="space-y-1">
        <Skeleton className="h-3 w-20 ml-1" variant="text" />
        <Skeleton className="h-12 w-full" variant="rectangular" />
      </div>
      
      {/* Row 3: Province & City */}
      <div className="grid sm:grid-cols-2 gap-3">
        <div className="space-y-1">
          <Skeleton className="h-3 w-20 ml-1" variant="text" />
          <Skeleton className="h-12 w-full" variant="rectangular" />
        </div>
        <div className="space-y-1">
          <Skeleton className="h-3 w-16 ml-1" variant="text" />
          <Skeleton className="h-12 w-full" variant="rectangular" />
        </div>
      </div>
      
      {/* Row 4: Address & CP */}
      <div className="grid sm:grid-cols-3 gap-3">
        <div className="sm:col-span-2 space-y-1">
          <Skeleton className="h-3 w-28 ml-1" variant="text" />
          <Skeleton className="h-12 w-full" variant="rectangular" />
        </div>
        <div className="space-y-1">
          <Skeleton className="h-3 w-8 ml-1" variant="text" />
          <Skeleton className="h-12 w-full" variant="rectangular" />
        </div>
      </div>
    </div>
  </div>
);

/**
 * Skeleton para resumen de pedido
 */
export const OrderSummarySkeleton: React.FC = () => (
  <div className="bg-white p-4 md:p-5 rounded-xl border border-gray-100 space-y-3">
    <Skeleton className="h-5 w-24" variant="text" />
    
    <div className="space-y-2">
      {[1, 2, 3].map(i => (
        <div key={i} className="flex justify-between">
          <Skeleton className="h-3 w-16" variant="text" />
          <Skeleton className="h-3 w-12" variant="text" />
        </div>
      ))}
      
      <div className="border-t pt-2 flex justify-between">
        <Skeleton className="h-3 w-12" variant="text" />
        <Skeleton className="h-5 w-20" variant="text" />
      </div>
    </div>
  </div>
);

/**
 * Skeleton para galeria de fotos
 */
export const PhotoGridSkeleton: React.FC<{ count?: number }> = ({ count = 12 }) => (
  <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-10 lg:grid-cols-12 gap-1.5">
    {Array(count).fill(0).map((_, i) => (
      <Skeleton key={i} className="aspect-square" variant="rectangular" />
    ))}
  </div>
);

/**
 * Skeleton para boton de pago
 */
export const PaymentButtonSkeleton: React.FC = () => (
  <Skeleton className="h-14 w-full rounded-xl" variant="rectangular" />
);

// =============================================================================
// LOADING OVERLAY
// =============================================================================

interface LoadingOverlayProps {
  message?: string;
  progress?: number;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({ 
  message = 'Cargando...', 
  progress 
}) => (
  <div className="fixed inset-0 z-50 bg-white/80 backdrop-blur-sm flex items-center justify-center">
    <div className="text-center space-y-4 p-8">
      {/* Spinner */}
      <div className="w-12 h-12 border-4 border-gray-200 border-t-primary rounded-full animate-spin mx-auto" />
      
      {/* Message */}
      <p className="text-gray-600 font-medium">{message}</p>
      
      {/* Progress bar (optional) */}
      {progress !== undefined && (
        <div className="w-48 mx-auto">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-300 rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-xs text-gray-400 mt-1">{progress}%</p>
        </div>
      )}
    </div>
  </div>
);

export default Skeleton;
