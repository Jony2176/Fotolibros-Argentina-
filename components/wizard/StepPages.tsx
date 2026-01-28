/**
 * StepPages Component
 * ===================
 * Paso 3: Configuración de cantidad de páginas
 */

import React from 'react';
import { Minus, Plus, Info, BookOpen } from 'lucide-react';
import { PriceBreakdown } from '../../hooks/usePriceCalculation';

interface StepPagesProps {
  pages: number;
  minPages: number;
  maxPages: number;
  pricePerExtraPage: number;
  priceBreakdown: PriceBreakdown;
  onChange: (pages: number) => void;
}

const StepPages: React.FC<StepPagesProps> = ({
  pages,
  minPages,
  maxPages,
  pricePerExtraPage,
  priceBreakdown,
  onChange
}) => {
  const handleDecrease = () => {
    const newPages = Math.max(minPages, pages - 2);
    onChange(newPages);
  };

  const handleIncrease = () => {
    const newPages = Math.min(maxPages, pages + 2);
    onChange(newPages);
  };

  const sheets = Math.floor(pages / 2);

  return (
    <div className="max-w-lg mx-auto animate-fade-in">
      {/* Header */}
      <h2 className="text-xl md:text-2xl font-display font-bold text-primary text-center mb-6">
        Configura las paginas
      </h2>

      <div className="bg-white p-4 md:p-5 rounded-2xl shadow-xl border border-gray-100 space-y-4">
        {/* Info Box */}
        <div className="bg-blue-50 p-3 rounded-xl flex items-start gap-2 border border-blue-100">
          <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-[11px] text-blue-800 leading-relaxed">
            <strong>Importante:</strong> El precio base incluye <strong>{priceBreakdown.basePagesIncluded} paginas</strong>. 
            El maximo es {maxPages} paginas. Cada pagina adicional cuesta <strong>${pricePerExtraPage}</strong>.
          </p>
        </div>

        {/* Page Counter */}
        <div className="flex items-center justify-center gap-4 md:gap-6 bg-cream p-4 rounded-2xl border border-primary/5">
          {/* Decrease Button */}
          <button
            onClick={handleDecrease}
            disabled={pages <= minPages}
            className={`
              flex-shrink-0 w-12 h-12 md:w-14 md:h-14 rounded-xl bg-white shadow-md 
              text-xl md:text-2xl font-bold transition-all duration-200
              flex items-center justify-center min-w-[44px] min-h-[44px]
              focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
              ${pages <= minPages 
                ? 'text-gray-300 cursor-not-allowed' 
                : 'text-primary hover:bg-primary hover:text-white active:scale-95'
              }
            `}
            aria-label="Reducir 2 paginas"
            aria-disabled={pages <= minPages}
          >
            <Minus className="w-5 h-5" />
          </button>

          {/* Counter Display */}
          <div className="text-center flex-shrink-0 min-w-[100px]">
            <div 
              className="text-4xl md:text-5xl font-display font-bold text-primary leading-none"
              aria-live="polite"
              aria-atomic="true"
            >
              {pages}
            </div>
            <div className="text-[9px] text-gray-400 font-bold tracking-widest uppercase mt-1">
              Paginas Totales
            </div>
            <div className="text-[8px] text-gray-400 flex items-center justify-center gap-1 mt-0.5">
              <BookOpen className="w-3 h-3" />
              <span>({sheets} Hojas)</span>
            </div>
          </div>

          {/* Increase Button */}
          <button
            onClick={handleIncrease}
            disabled={pages >= maxPages}
            className={`
              flex-shrink-0 w-12 h-12 md:w-14 md:h-14 rounded-xl bg-white shadow-md 
              text-xl md:text-2xl font-bold transition-all duration-200
              flex items-center justify-center min-w-[44px] min-h-[44px]
              focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
              ${pages >= maxPages 
                ? 'text-gray-300 cursor-not-allowed' 
                : 'text-primary hover:bg-primary hover:text-white active:scale-95'
              }
            `}
            aria-label="Agregar 2 paginas"
            aria-disabled={pages >= maxPages}
          >
            <Plus className="w-5 h-5" />
          </button>
        </div>

        {/* Price Summary */}
        <div className="bg-gray-50 p-3 md:p-4 rounded-xl space-y-2">
          {/* Base Price */}
          <div className="flex justify-between text-sm">
            <span className="text-gray-500">
              Precio Base ({priceBreakdown.basePagesIncluded} pags)
            </span>
            <span className="font-bold text-primary">
              ${priceBreakdown.basePrice.toLocaleString('es-AR')}
            </span>
          </div>

          {/* Extra Pages */}
          {priceBreakdown.extraPages > 0 && (
            <div className="flex justify-between text-sm text-accent">
              <span>{priceBreakdown.extraPages} Paginas adicionales</span>
              <span className="font-bold">
                + ${priceBreakdown.extraPagesTotal.toLocaleString('es-AR')}
              </span>
            </div>
          )}

          {/* Subtotal */}
          <div className="border-t border-gray-200 pt-3 flex justify-between items-baseline">
            <span className="font-bold text-primary">Subtotal</span>
            <span className="text-xl md:text-2xl font-display font-bold text-primary">
              ${(priceBreakdown.basePrice + priceBreakdown.extraPagesTotal).toLocaleString('es-AR')}
            </span>
          </div>
        </div>

        {/* Pages Range Indicator */}
        <div className="relative pt-2">
          <div className="flex justify-between text-[9px] text-gray-400 mb-1">
            <span>{minPages} pags</span>
            <span>{maxPages} pags</span>
          </div>
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <div 
              className="h-full bg-primary transition-all duration-300 rounded-full"
              style={{ width: `${((pages - minPages) / (maxPages - minPages)) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default StepPages;
