/**
 * StepPhotos Component (Enhanced with Smart Photo Calculator)
 * ===========================================================
 * Paso 4: Subida de fotos CON sugerencias inteligentes
 * basadas en el tamaño del libro y cantidad de páginas.
 */

import React, { useRef, useCallback, useMemo } from 'react';
import { Upload, X, Image, Info, Lightbulb, AlertCircle, CheckCircle, TrendingUp } from 'lucide-react';
import { calculatePhotoRequirements, isPhotoCountSufficient, formatPhotoRequirements } from '../../utils/photoCalculator';

interface StepPhotosProps {
  photos: File[];
  productCode: string;      // Código del producto seleccionado
  totalPages: number;        // Total de páginas del libro
  onUpload: (files: File[]) => void;
  onRemove: (index: number) => void;
}

const StepPhotos: React.FC<StepPhotosProps> = ({
  photos,
  productCode,
  totalPages,
  onUpload,
  onRemove
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Calcular requisitos inteligentes según el libro
  const photoReqs = useMemo(
    () => calculatePhotoRequirements(productCode, totalPages),
    [productCode, totalPages]
  );

  // Evaluar estado actual
  const currentStatus = useMemo(
    () => isPhotoCountSufficient(photos.length, photoReqs),
    [photos.length, photoReqs]
  );

  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      onUpload(newFiles);
    }
    // Reset input to allow selecting same file again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [onUpload]);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFiles = Array.from(e.dataTransfer.files).filter(
      file => file.type.startsWith('image/')
    );
    
    if (droppedFiles.length > 0) {
      onUpload(droppedFiles);
    }
  }, [onUpload]);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const photosCount = photos.length;
  const maxPhotos = 200;
  const progressPercent = Math.min(100, (photosCount / photoReqs.recommendedMax) * 100);

  // Status colors
  const statusColors = {
    insufficient: { bg: 'bg-red-50', border: 'border-red-200', text: 'text-red-600', progress: 'bg-red-400' },
    minimum: { bg: 'bg-orange-50', border: 'border-orange-200', text: 'text-orange-600', progress: 'bg-orange-400' },
    good: { bg: 'bg-green-50', border: 'border-green-200', text: 'text-green-600', progress: 'bg-green-500' },
    excellent: { bg: 'bg-blue-50', border: 'border-blue-200', text: 'text-blue-600', progress: 'bg-blue-500' }
  };

  const statusColor = statusColors[currentStatus.status];

  return (
    <div className="animate-fade-in space-y-4 md:space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-xl md:text-2xl font-display font-bold text-primary mb-1">
          Subi tus mejores momentos
        </h2>
        <p className="text-gray-500 text-xs">
          {formatPhotoRequirements(photoReqs)}
        </p>
      </div>

      {/* Smart Recommendation Box */}
      <div className={`max-w-md mx-auto p-4 rounded-xl border-2 ${statusColor.border} ${statusColor.bg}`}>
        <div className="flex items-start gap-3">
          <div className="flex-shrink-0">
            {currentStatus.status === 'insufficient' && <AlertCircle className={`w-5 h-5 ${statusColor.text}`} />}
            {currentStatus.status === 'minimum' && <Info className={`w-5 h-5 ${statusColor.text}`} />}
            {currentStatus.status === 'good' && <CheckCircle className={`w-5 h-5 ${statusColor.text}`} />}
            {currentStatus.status === 'excellent' && <TrendingUp className={`w-5 h-5 ${statusColor.text}`} />}
          </div>
          <div className="flex-1">
            <h3 className={`text-sm font-bold ${statusColor.text} mb-1`}>
              {currentStatus.status === 'insufficient' && 'Necesitas más fotos'}
              {currentStatus.status === 'minimum' && 'Mínimo alcanzado'}
              {currentStatus.status === 'good' && '¡Cantidad ideal!'}
              {currentStatus.status === 'excellent' && '¡Excelente selección!'}
            </h3>
            <p className={`text-xs ${statusColor.text.replace('600', '700')}`}>
              {currentStatus.message}
            </p>
            <div className="mt-2 flex items-center gap-2 text-[10px] font-bold">
              <span className={statusColor.text}>
                {photoReqs.photosPerPage.min}-{photoReqs.photosPerPage.max} fotos por página
              </span>
              <span className="text-gray-400">•</span>
              <span className="text-gray-500">
                {totalPages - 4} páginas útiles
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Progress with Smart Targets */}
      <div className="max-w-md mx-auto px-2">
        <div className="mb-2 flex justify-between items-end">
          <span 
            className={`text-[9px] font-bold uppercase tracking-wider flex items-center gap-1 ${statusColor.text}`}
          >
            {currentStatus.isSufficient ? (
              <>
                <CheckCircle className="w-3 h-3" />
                {currentStatus.status === 'good' || currentStatus.status === 'excellent' ? 'Perfecto!' : 'Mínimo OK'}
              </>
            ) : (
              <>
                <AlertCircle className="w-3 h-3" />
                Faltan {photoReqs.minPhotos - photosCount} fotos
              </>
            )}
          </span>
          <span className="text-[9px] font-bold text-gray-400">
            {photosCount} / {photoReqs.recommendedMax} recom.
          </span>
        </div>
        
        {/* Multi-target Progress Bar */}
        <div className="relative h-2 w-full bg-gray-100 rounded-full overflow-hidden mb-1">
          {/* Current progress */}
          <div 
            className={`h-full transition-all duration-500 ${statusColor.progress}`}
            style={{ width: `${progressPercent}%` }}
            role="progressbar"
            aria-valuenow={photosCount}
            aria-valuemin={0}
            aria-valuemax={photoReqs.recommendedMax}
          />
          
          {/* Minimum marker */}
          <div 
            className="absolute top-0 bottom-0 w-0.5 bg-orange-400"
            style={{ left: `${(photoReqs.minPhotos / photoReqs.recommendedMax) * 100}%` }}
            title="Mínimo requerido"
          />
          
          {/* Recommended minimum marker */}
          <div 
            className="absolute top-0 bottom-0 w-0.5 bg-green-400"
            style={{ left: `${(photoReqs.recommendedMin / photoReqs.recommendedMax) * 100}%` }}
            title="Recomendado mínimo"
          />
        </div>

        {/* Legend */}
        <div className="flex items-center justify-between text-[8px] text-gray-400 px-1">
          <span>Mín: {photoReqs.minPhotos}</span>
          <span>Ideal: {photoReqs.recommendedMin}-{photoReqs.recommendedMax}</span>
          <span>Máx: {maxPhotos}</span>
        </div>
      </div>

      {/* Tips Collapsible */}
      {photoReqs.tips.length > 0 && (
        <div className="max-w-md mx-auto">
          <details className="group">
            <summary className="flex items-center justify-center gap-2 text-primary text-[10px] font-bold cursor-pointer hover:underline list-none">
              <Lightbulb className="w-3.5 h-3.5" />
              <span>Consejos para este libro</span>
              <span className="text-gray-400 group-open:rotate-180 transition-transform">▼</span>
            </summary>
            <div className="mt-3 bg-blue-50 p-3 rounded-xl border border-blue-100">
              <ul className="text-[10px] text-blue-800 space-y-1.5">
                {photoReqs.tips.map((tip, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-blue-400 flex-shrink-0">•</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </details>
        </div>
      )}

      {/* Warnings */}
      {photoReqs.warnings.length > 0 && (
        <div className="max-w-md mx-auto">
          {photoReqs.warnings.map((warning, index) => (
            <div key={index} className="bg-yellow-50 p-3 rounded-xl flex items-start gap-2 border border-yellow-200">
              <AlertCircle className="w-4 h-4 text-yellow-600 flex-shrink-0 mt-0.5" />
              <p className="text-[10px] text-yellow-800 leading-relaxed">
                <strong>Atención:</strong> {warning}
              </p>
            </div>
          ))}
        </div>
      )}

      {/* Upload Zone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        className="max-w-lg mx-auto border-3 border-dashed border-gray-200 rounded-2xl p-6 md:p-10 text-center hover:bg-white hover:border-primary transition-all duration-200 bg-gray-50 cursor-pointer group shadow-sm focus-within:ring-2 focus-within:ring-primary focus-within:ring-offset-2"
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        aria-label="Subir fotos"
      >
        <Upload className="w-10 h-10 md:w-12 md:h-12 mx-auto mb-3 text-gray-400 group-hover:text-primary group-hover:scale-110 transition-all duration-200" />
        <h3 className="text-base md:text-lg font-bold text-primary mb-1">
          Selecciona o Arrastra tus fotos
        </h3>
        <p className="text-gray-400 text-[10px] md:text-xs mb-2">
          JPG o PNG de alta resolución
        </p>
        {!currentStatus.isSufficient && (
          <p className="text-orange-600 text-[11px] font-bold">
            Necesitas al menos {photoReqs.minPhotos} fotos para este libro
          </p>
        )}
        <input
          type="file"
          multiple
          hidden
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          aria-label="Seleccionar archivos de imagen"
        />
      </div>

      {/* Photos Grid */}
      {photos.length > 0 && (
        <div 
          className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-10 lg:grid-cols-12 gap-1.5"
          role="list"
          aria-label="Fotos subidas"
        >
          {photos.map((file, index) => (
            <div 
              key={`${file.name}-${index}`} 
              className="relative aspect-square rounded-md overflow-hidden shadow-sm border group"
              role="listitem"
            >
              <img
                src={URL.createObjectURL(file)}
                alt={`Foto ${index + 1}`}
                className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-200"
                loading="lazy"
              />
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onRemove(index);
                }}
                className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white transition-opacity duration-200 focus:opacity-100"
                aria-label={`Eliminar foto ${index + 1}`}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {photos.length === 0 && (
        <div className="text-center py-8">
          <Image className="w-12 h-12 mx-auto text-gray-300 mb-3" />
          <p className="text-sm text-gray-400 mb-1">
            Todavia no subiste ninguna foto
          </p>
          <p className="text-xs text-gray-400">
            Necesitas {photoReqs.minPhotos} fotos como mínimo
          </p>
        </div>
      )}

      {/* Disclaimer */}
      <p className="text-center text-[10px] text-gray-400 mt-6 italic">
        * Las imagenes son a modo ilustrativo. Los colores y texturas pueden variar ligeramente en el producto final.
      </p>
    </div>
  );
};

export default StepPhotos;
