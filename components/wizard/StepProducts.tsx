/**
 * StepProducts Component
 * ======================
 * Paso 1: Selección de producto/modelo de fotolibro
 */

import React, { useMemo, useState } from 'react';
import { ChevronRight, Gem, Filter } from 'lucide-react';
import { PRODUCTS } from '../../constants';
import { Product } from '../../types';

interface StepProductsProps {
  onSelect: (codigo: string, paginasBase: number) => void;
  selectedCode?: string;
}

type FilterType = 'all' | 'Apaisado' | 'Cuadrado' | 'Vertical' | 'Mini';
type FilterTapa = 'all' | 'Blanda' | 'Dura' | 'Simil Cuero';

const StepProducts: React.FC<StepProductsProps> = ({ onSelect, selectedCode }) => {
  const [filterTipo, setFilterTipo] = useState<FilterType>('all');
  const [filterTapa, setFilterTapa] = useState<FilterTapa>('all');
  const [showFilters, setShowFilters] = useState(false);

  const filteredProducts = useMemo(() => {
    return PRODUCTS.filter(p => {
      const matchTipo = filterTipo === 'all' || p.tipo === filterTipo;
      const matchTapa = filterTapa === 'all' || p.tapa === filterTapa;
      return matchTipo && matchTapa;
    });
  }, [filterTipo, filterTapa]);

  const handleSelect = (product: Product) => {
    onSelect(product.codigo, product.paginasBase);
  };

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-xl md:text-2xl font-display font-bold text-primary mb-2">
          Elegi tu modelo
        </h2>
        <p className="text-gray-500 text-sm">
          Papel fotografico premium de 170g y terminacion artesanal.
        </p>
      </div>

      {/* Filters Toggle (Mobile) */}
      <div className="mb-4 md:hidden">
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          aria-expanded={showFilters}
          aria-controls="product-filters"
        >
          <Filter className="w-4 h-4" />
          Filtrar productos
        </button>
      </div>

      {/* Filters */}
      <div 
        id="product-filters"
        className={`mb-6 ${showFilters ? 'block' : 'hidden md:block'}`}
      >
        <div className="flex flex-wrap gap-2 justify-center">
          {/* Tipo Filter */}
          <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
            {(['all', 'Apaisado', 'Cuadrado', 'Vertical'] as FilterType[]).map(tipo => (
              <button
                key={tipo}
                onClick={() => setFilterTipo(tipo)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all min-h-[36px] ${
                  filterTipo === tipo
                    ? 'bg-white text-primary shadow-sm'
                    : 'text-gray-600 hover:text-primary'
                }`}
                aria-pressed={filterTipo === tipo}
              >
                {tipo === 'all' ? 'Todos' : tipo}
              </button>
            ))}
          </div>

          {/* Tapa Filter */}
          <div className="flex gap-1 p-1 bg-gray-100 rounded-lg">
            {(['all', 'Blanda', 'Dura', 'Simil Cuero'] as FilterTapa[]).map(tapa => (
              <button
                key={tapa}
                onClick={() => setFilterTapa(tapa)}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-all min-h-[36px] ${
                  filterTapa === tapa
                    ? 'bg-white text-primary shadow-sm'
                    : 'text-gray-600 hover:text-primary'
                }`}
                aria-pressed={filterTapa === tapa}
              >
                {tapa === 'all' ? 'Todas' : tapa}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div 
        className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 md:gap-4"
        role="list"
        aria-label="Lista de productos"
      >
        {filteredProducts.map((prod) => {
          const isSelected = selectedCode === prod.codigo;
          
          // Calcular escala basada en el tamaño real del producto
          const sizeMatch = prod.tamanio.match(/(\d+(?:,\d+)?)\s*[×x]\s*(\d+(?:,\d+)?)/);
          const width = sizeMatch ? parseFloat(sizeMatch[1].replace(',', '.')) : 21;
          const height = sizeMatch ? parseFloat(sizeMatch[2].replace(',', '.')) : 21;
          const maxDim = Math.max(width, height);
          // Escala: 10cm = 60%, 21cm = 80%, 29cm = 95%, 41cm = 100%
          const scale = Math.min(100, Math.max(50, 50 + (maxDim / 41) * 50));
          const imgHeight = prod.tipo === 'Mini' ? 'h-20 md:h-24' : 
                           maxDim >= 35 ? 'h-36 md:h-44' : 
                           maxDim >= 27 ? 'h-32 md:h-40' : 
                           'h-28 md:h-32';

          return (
            <article
              key={prod.codigo}
              role="listitem"
              onClick={() => handleSelect(prod)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleSelect(prod);
                }
              }}
              tabIndex={0}
              className={`
                cursor-pointer group bg-white p-3 md:p-4 rounded-xl border-2 
                hover:border-primary hover:shadow-lg transition-all duration-200 
                shadow-sm flex flex-col relative focus:outline-none focus:ring-2 
                focus:ring-primary focus:ring-offset-2
                ${isSelected ? 'border-primary ring-2 ring-primary/20' : 'border-gray-100'}
              `}
              aria-selected={isSelected}
            >
              {/* Badge */}
              {prod.badge && (
                <span className="absolute top-2 right-2 bg-accent text-white text-[8px] font-bold px-2 py-0.5 rounded-full shadow-md z-10">
                  {prod.badge}
                </span>
              )}

              {/* Product Image */}
              <div className="flex items-center justify-center py-2 mb-2 min-h-[120px] md:min-h-[160px]">
                <img 
                  src={prod.imagen} 
                  alt={prod.nombre}
                  className={`w-full ${imgHeight} object-contain rounded-lg`}
                  style={{ maxWidth: `${scale}%` }}
                />
              </div>

              {/* Product Info */}
              <h3 className="font-bold text-primary text-sm mb-0.5 leading-tight">
                {prod.nombre}
              </h3>
              <p className="text-[9px] text-gray-400 mb-2">
                {prod.tamanio} · Tapa {prod.tapa}
              </p>

              {/* Features (Desktop only) */}
              <div className="space-y-0.5 mb-3 hidden md:block">
                <div className="flex items-center gap-1.5 text-[9px] text-gray-500">
                  <Gem className="w-3 h-3 text-primary" />
                  <span>Papel 170g</span>
                </div>
                <div className="flex items-center gap-1.5 text-[9px] text-accent font-bold">
                  <span>+</span>
                  <span>${prod.precioPaginaExtra}/pag extra</span>
                </div>
              </div>

              {/* Price & CTA */}
              <div className="mt-auto flex justify-between items-center pt-2 border-t border-gray-50">
                <div className="flex flex-col">
                  <span className="text-[8px] font-bold text-gray-400 uppercase">
                    Base
                  </span>
                  <span className="text-base font-bold text-primary">
                    ${prod.precioBase.toLocaleString('es-AR')}
                  </span>
                </div>
                <button
                  className="bg-primary text-white w-8 h-8 md:w-9 md:h-9 rounded-full flex items-center justify-center font-bold text-sm group-hover:scale-110 transition-transform duration-200 min-w-[44px] min-h-[44px]"
                  aria-label={`Seleccionar ${prod.nombre}`}
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </article>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredProducts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No hay productos que coincidan con los filtros.</p>
          <button
            onClick={() => { setFilterTipo('all'); setFilterTapa('all'); }}
            className="mt-4 text-primary font-medium hover:underline"
          >
            Limpiar filtros
          </button>
        </div>
      )}
    </div>
  );
};

export default StepProducts;
