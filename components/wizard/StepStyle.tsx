/**
 * StepStyle Component
 * ===================
 * Paso 2: Selección de estilo de diseño
 */

import React from 'react';
import { ChevronRight, Camera, Ribbon, PartyPopper, Sparkles, Info } from 'lucide-react';
import { DESIGN_STYLES, DesignStyle } from '../../constants';

interface StepStyleProps {
  selectedStyle: string;
  onSelect: (styleId: string) => void;
}

// Map emoji IDs to Lucide icons
const STYLE_ICONS: Record<string, React.ReactNode> = {
  'minimalista': <Camera className="w-6 h-6 md:w-7 md:h-7" />,
  'clasico': <Ribbon className="w-6 h-6 md:w-7 md:h-7" />,
  'divertido': <PartyPopper className="w-6 h-6 md:w-7 md:h-7" />,
  'premium': <Sparkles className="w-6 h-6 md:w-7 md:h-7" />,
};

const StepStyle: React.FC<StepStyleProps> = ({ selectedStyle, onSelect }) => {
  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="text-center mb-6">
        <h2 className="text-xl md:text-2xl font-display font-bold text-primary mb-2">
          Elegi el estilo de diseno
        </h2>
        <p className="text-gray-500 text-sm">
          Esto define como se vera tu fotolibro. Podes cambiarlo despues!
        </p>
      </div>

      {/* Styles Grid */}
      <div 
        className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 max-w-4xl mx-auto"
        role="radiogroup"
        aria-label="Estilos de diseno disponibles"
      >
        {DESIGN_STYLES.map((style) => {
          const isSelected = selectedStyle === style.id;
          const Icon = STYLE_ICONS[style.id];

          return (
            <article
              key={style.id}
              role="radio"
              aria-checked={isSelected}
              tabIndex={0}
              onClick={() => onSelect(style.id)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  onSelect(style.id);
                }
              }}
              className={`
                cursor-pointer group bg-white p-4 md:p-5 rounded-2xl border-2 
                transition-all duration-200 shadow-sm hover:shadow-xl flex flex-col
                focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2
                ${isSelected 
                  ? 'border-primary ring-4 ring-primary/10' 
                  : 'border-gray-100 hover:border-primary/50'
                }
              `}
            >
              {/* Icon & Title */}
              <div className="flex items-center gap-2 mb-3">
                <div className={`
                  p-2 rounded-xl transition-colors
                  ${isSelected ? 'bg-primary/10 text-primary' : 'bg-gray-100 text-gray-600 group-hover:bg-primary/5 group-hover:text-primary'}
                `}>
                  {Icon}
                </div>
                <h3 className="font-bold text-primary text-sm md:text-base">
                  {style.nombre}
                </h3>
              </div>

              {/* Description */}
              <p className="text-[10px] md:text-xs text-gray-500 mb-3 leading-relaxed flex-grow">
                {style.descripcion}
              </p>

              {/* Preview */}
              <div
                className="h-16 md:h-20 rounded-xl mb-3 flex items-center justify-center relative overflow-hidden"
                style={{
                  background: style.tapa.estiloFondo === 'gradiente'
                    ? `linear-gradient(135deg, ${style.colorPrimario}, ${style.colorSecundario})`
                    : style.colorPrimario
                }}
                aria-hidden="true"
              >
                {style.tapa.conTitulo && (
                  <div 
                    className="text-white text-[10px] md:text-xs font-bold text-center px-2" 
                    style={{ textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}
                  >
                    {style.id === 'clasico' ? 'Nuestra Boda' : 
                     style.id === 'divertido' ? 'Feliz Cumple!' : 
                     style.id === 'premium' ? 'Recuerdos 2025' : ''}
                  </div>
                )}
                {style.interior.conAdornos && (
                  <Sparkles className="absolute top-2 right-2 w-4 h-4 text-white/50" />
                )}
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-1">
                {style.idealPara.slice(0, 2).map((tag, i) => (
                  <span 
                    key={i} 
                    className="text-[8px] md:text-[9px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>

              {/* Footer */}
              <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                <span className="text-[9px] text-gray-400">
                  {style.interior.fotosRecomendadas} foto{style.interior.fotosRecomendadas > 1 ? 's' : ''}/pag
                </span>
                <button 
                  className={`
                    w-7 h-7 md:w-8 md:h-8 rounded-full flex items-center justify-center 
                    text-xs transition-all duration-200 min-w-[44px] min-h-[44px]
                    ${isSelected 
                      ? 'bg-primary text-white' 
                      : 'bg-gray-100 text-gray-400 group-hover:bg-primary group-hover:text-white group-hover:scale-110'
                    }
                  `}
                  aria-label={`Seleccionar estilo ${style.nombre}`}
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </article>
          );
        })}
      </div>

      {/* Tip */}
      <div className="mt-6 max-w-2xl mx-auto">
        <div className="bg-blue-50 p-3 rounded-xl flex items-start gap-2 border border-blue-100">
          <Info className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <p className="text-[11px] text-blue-800 leading-relaxed">
            <strong>Consejo:</strong> Si no estas seguro, <strong>Clasico</strong> es nuestra opcion mas versatil. 
            El estilo define colores, fondos y cantidad de fotos por pagina, pero siempre podes personalizar cada detalle.
          </p>
        </div>
      </div>
    </div>
  );
};

export default StepStyle;
