/**
 * OrderWizard Component (Refactored)
 * ==================================
 * Wizard de pedido usando componentes modulares y hooks centralizados.
 * 
 * Estructura:
 * - useOrderState: Gestión del estado con useReducer
 * - usePriceCalculation: Cálculos de precio, descuentos y envío
 * - StepProducts/StepStyle/StepPages/StepPhotos/StepDelivery/StepPayment: Componentes de cada paso
 */

import React, { useMemo, useCallback } from 'react';
import { ArrowLeft, Check, ChevronRight } from 'lucide-react';
import { PRODUCTS } from '../constants';

// Hooks
import { useOrderState } from '../hooks/useOrderState';
import { usePriceCalculation } from '../hooks/usePriceCalculation';

// Wizard Step Components
import {
  StepProducts,
  StepStyle,
  StepPages,
  StepPhotos,
  StepDelivery,
  StepPayment
} from '../components/wizard';

// =============================================================================
// TYPES
// =============================================================================

interface OrderWizardProps {
  onBack: () => void;
  initialProductCode?: string;
}

// =============================================================================
// STEP LABELS
// =============================================================================

const STEP_LABELS = [
  'Producto',
  'Estilo',
  'Paginas',
  'Fotos',
  'Entrega',
  'Pago'
];

// =============================================================================
// MAIN COMPONENT
// =============================================================================

const OrderWizard: React.FC<OrderWizardProps> = ({ onBack, initialProductCode }) => {
  // Initialize order state hook
  const { state, actions, canProceed } = useOrderState(initialProductCode);

  // Get selected product for calculations
  const selectedProduct = useMemo(
    () => PRODUCTS.find(p => p.codigo === state.productoCodigo),
    [state.productoCodigo]
  );

  // Calculate prices using hook
  const priceBreakdown = usePriceCalculation({
    productoCodigo: state.productoCodigo,
    paginasTotal: state.paginasTotal,
    provincia: state.cliente.direccion.provincia,
    metodoPago: state.metodoPago
  });

  // =============================================================================
  // HANDLERS
  // =============================================================================

  const handleProductSelect = useCallback((codigo: string, paginasBase: number) => {
    actions.setProduct(codigo, paginasBase);
    actions.nextStep();
  }, [actions]);

  const handleStyleSelect = useCallback((styleId: string) => {
    actions.setStyle(styleId);
    actions.nextStep();
  }, [actions]);

  const handlePagesChange = useCallback((pages: number) => {
    actions.setPages(pages);
  }, [actions]);

  const handlePhotosUpload = useCallback((files: File[]) => {
    const validFiles = files.filter(f => f.type.startsWith('image/'));
    const totalAllowed = 200 - state.fotos.length;
    actions.addPhotos(validFiles.slice(0, totalAllowed));
  }, [actions, state.fotos.length]);

  const handlePhotoRemove = useCallback((index: number) => {
    actions.removePhoto(index);
  }, [actions]);

  // Submit order to backend
  const handleSubmit = useCallback(async () => {
    actions.setSubmitting(true);
    actions.setPedidoStatus({ estado: 'Enviando pedido...' });

    try {
      // Create order payload (formato esperado por backend)
      const payload = {
        cliente: {
          nombre: state.cliente.nombre,
          email: state.cliente.email,
          telefono: state.cliente.telefono || undefined
        },
        libro: {
          codigo_producto: state.productoCodigo,
          tamano: selectedProduct?.tamanio || '',
          tapa: selectedProduct?.tapa || '',
          estilo: state.estiloDiseno,
          ocasion: undefined,
          titulo_personalizado: undefined
        },
        modo_confirmacion: true,
        notas_cliente: undefined
      };

      // Send order
      const response = await fetch('http://168.231.98.115:8002/api/pedidos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Error al crear pedido');

      const data = await response.json();
      actions.setPedidoStatus({ id: data.pedido_id, estado: 'Pedido creado, subiendo fotos...' });

      // Upload photos
      if (state.fotos.length > 0) {
        const photosFormData = new FormData();
        state.fotos.forEach(photo => {
          photosFormData.append('fotos', photo);
        });

        await fetch(`http://168.231.98.115:8002/api/pedidos/${data.pedido_id}/fotos`, {
          method: 'POST',
          body: photosFormData
        });
      }

      // Upload comprobante if exists (for transfer)
      if (state.comprobante && state.metodoPago === 'transferencia') {
        actions.setPedidoStatus({ estado: 'Subiendo comprobante de pago...' });
        
        const formData = new FormData();
        formData.append('comprobante', state.comprobante);
        formData.append('monto_esperado', String(priceBreakdown.total));

        await fetch(`http://168.231.98.115:8002/api/pedidos/${data.pedido_id}/comprobante`, {
          method: 'POST',
          body: formData
        });
      }

      // Start polling status
      pollOrderStatus(data.pedido_id);

    } catch (error) {
      console.error('Error:', error);
      actions.setPedidoStatus({ estado: 'Error al enviar pedido' });
      actions.setSubmitting(false);
    }
  }, [state, actions, priceBreakdown.total]);

  // Poll order status
  const pollOrderStatus = useCallback(async (id: string) => {
    try {
      const response = await fetch(`http://168.231.98.115:8002/api/pedidos/${id}/estado`);
      const data = await response.json();

      actions.setPedidoStatus({ 
        estado: data.mensaje, 
        progreso: data.progreso 
      });

      if (data.estado === 'completado' || data.progreso === 100) {
        actions.setSubmitting(false);
      } else if (data.estado === 'error') {
        actions.setSubmitting(false);
      } else {
        setTimeout(() => pollOrderStatus(id), 2000);
      }
    } catch (error) {
      console.error('Error consultando estado:', error);
    }
  }, [actions]);

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <div className="bg-slate-50 min-h-screen flex flex-col pt-24 md:pt-28 font-sans">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20 px-4 py-3 md:py-4">
        <div className="max-w-4xl mx-auto">
          {/* Top Row */}
          <div className="flex items-center justify-between mb-3 md:mb-4">
            <button 
              onClick={onBack} 
              className="text-slate-500 hover:text-primary flex items-center gap-1 text-xs md:text-sm min-h-[44px] px-2 -ml-2 transition-colors"
              aria-label="Volver al inicio"
            >
              <ArrowLeft className="w-4 h-4" />
              Volver
            </button>
            
            <button 
              onClick={onBack} 
              className="transition-transform hover:scale-105 active:scale-95"
            >
              <img src="/logo.png" alt="Fotolibros Argentina" className="h-6 md:h-8" />
            </button>
            
            <div className="flex items-center gap-2">
              <div className="text-[9px] text-gray-400 font-bold hidden md:block">
                PASO {state.step} / 6
              </div>
            </div>
          </div>

          {/* Progress Stepper */}
          <nav 
            className="flex items-center justify-between relative px-2"
            aria-label="Progreso del pedido"
          >
            {/* Background line */}
            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-100 -translate-y-1/2 -z-10" />
            
            {/* Active progress line */}
            <div 
              className="absolute top-1/2 left-0 h-0.5 bg-primary -translate-y-1/2 -z-10 transition-all duration-500" 
              style={{ width: `${((state.step - 1) / 5) * 100}%` }}
            />
            
            {/* Step indicators */}
            {[1, 2, 3, 4, 5, 6].map((stepNum) => (
              <div 
                key={stepNum}
                className={`
                  w-6 h-6 md:w-7 md:h-7 rounded-full flex items-center justify-center 
                  text-[10px] md:text-xs font-bold transition-all duration-200
                  ${state.step === stepNum 
                    ? 'bg-primary text-white scale-110 shadow-lg ring-4 ring-primary/20' 
                    : state.step > stepNum 
                      ? 'bg-primary text-white' 
                      : 'bg-gray-200 text-gray-400'
                  }
                `}
                aria-current={state.step === stepNum ? 'step' : undefined}
                aria-label={`${STEP_LABELS[stepNum - 1]} - ${state.step > stepNum ? 'Completado' : state.step === stepNum ? 'Actual' : 'Pendiente'}`}
              >
                {state.step > stepNum ? <Check className="w-3 h-3" /> : stepNum}
              </div>
            ))}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto w-full p-4 py-4 md:py-6 flex-grow pb-24 md:pb-6">
        
        {/* Step 1: Products */}
        {state.step === 1 && (
          <StepProducts
            onSelect={handleProductSelect}
            selectedCode={state.productoCodigo}
          />
        )}

        {/* Step 2: Style */}
        {state.step === 2 && (
          <StepStyle
            selectedStyle={state.estiloDiseno}
            onSelect={handleStyleSelect}
          />
        )}

        {/* Step 3: Pages */}
        {state.step === 3 && selectedProduct && (
          <StepPages
            pages={state.paginasTotal}
            minPages={selectedProduct.paginasBase}
            maxPages={selectedProduct.paginasMax}
            pricePerExtraPage={selectedProduct.precioPaginaExtra}
            priceBreakdown={priceBreakdown}
            onChange={handlePagesChange}
          />
        )}

        {/* Step 4: Photos */}
        {state.step === 4 && (
          <StepPhotos
            photos={state.fotos}
            productCode={state.productoCodigo}
            totalPages={state.paginasTotal}
            onUpload={handlePhotosUpload}
            onRemove={handlePhotoRemove}
          />
        )}

        {/* Step 5: Delivery */}
        {state.step === 5 && (
          <StepDelivery
            cliente={state.cliente}
            priceBreakdown={priceBreakdown}
            onClienteChange={actions.setCliente}
            onDireccionChange={actions.setClienteDireccion}
          />
        )}

        {/* Step 6: Payment */}
        {state.step === 6 && (
          <StepPayment
            metodoPago={state.metodoPago}
            comprobante={state.comprobante}
            priceBreakdown={priceBreakdown}
            isSubmitting={state.isSubmitting}
            pedidoEstado={state.pedidoEstado}
            pedidoProgreso={state.pedidoProgreso}
            onMetodoChange={actions.setMetodoPago}
            onComprobanteChange={actions.setComprobante}
            onSubmit={handleSubmit}
          />
        )}

      </main>

      {/* Footer Navigation (Steps 1-5) */}
      {state.step < 6 && (
        <footer className="bg-white/90 backdrop-blur-md border-t border-slate-200 p-3 md:p-4 flex items-center justify-between fixed bottom-0 left-0 right-0 z-50 shadow-lg">
          {/* Back Button */}
          <button 
            onClick={actions.prevStep} 
            disabled={state.step === 1}
            className={`
              px-4 md:px-6 py-2 md:py-2.5 font-bold text-sm md:text-base
              rounded-lg transition-all duration-200 min-h-[44px]
              ${state.step === 1 
                ? 'text-gray-300 cursor-not-allowed' 
                : 'text-slate-500 hover:text-primary hover:bg-gray-50'
              }
            `}
            aria-label="Paso anterior"
          >
            <span className="flex items-center gap-1">
              <ArrowLeft className="w-4 h-4" />
              <span className="hidden sm:inline">Atras</span>
            </span>
          </button>

          {/* Price Display */}
          <div className="text-center">
            <div className="text-primary font-bold text-base md:text-lg leading-none">
              {priceBreakdown.formattedSubtotal}
            </div>
            {priceBreakdown.hasDiscount && (
              <div className="text-[10px] text-green-600 font-medium">
                -{priceBreakdown.discountPercentage}% con transferencia
              </div>
            )}
          </div>

          {/* Next Button */}
          <button
            onClick={actions.nextStep}
            disabled={!canProceed}
            className={`
              px-5 md:px-8 py-2 md:py-2.5 font-bold text-sm md:text-base
              rounded-xl shadow-lg transition-all duration-200 min-h-[44px]
              flex items-center gap-2
              ${canProceed
                ? 'bg-primary text-white hover:bg-primary-dark active:scale-95'
                : 'bg-gray-200 text-gray-400 cursor-not-allowed'
              }
            `}
            aria-label={state.step === 5 ? 'Ir a pago' : 'Siguiente paso'}
          >
            {state.step === 5 ? 'Ir a Pago' : 'Siguiente'}
            <ChevronRight className="w-4 h-4" />
          </button>
        </footer>
      )}

      {/* Order Completion Success (shown after successful submit) */}
      {state.pedidoId && !state.isSubmitting && state.pedidoProgreso === 100 && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-primary/40 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8 text-center space-y-6 animate-slide-up">
            {/* Success Icon */}
            <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto text-white shadow-lg">
              <Check className="w-10 h-10" />
            </div>
            
            {/* Title */}
            <div>
              <h3 className="text-2xl font-display font-bold text-green-800">
                Pedido Confirmado!
              </h3>
              <p className="text-green-600 mt-1">
                Tu fotolibro ya esta en produccion
              </p>
            </div>

            {/* Order ID */}
            <div className="bg-gray-50 p-4 rounded-xl border border-gray-200">
              <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">
                Tu codigo de seguimiento
              </div>
              <div className="font-mono font-bold text-lg text-primary select-all break-all">
                {state.pedidoId}
              </div>
              <button
                onClick={() => navigator.clipboard.writeText(state.pedidoId!)}
                className="text-xs text-accent mt-2 hover:underline flex items-center justify-center gap-1 mx-auto"
              >
                Copiar ID
              </button>
            </div>

            {/* Info */}
            <div className="text-sm text-green-700 bg-green-50 p-3 rounded-lg border border-green-100">
              <strong>Guarda este codigo</strong> y usalo junto con tu email para consultar el estado en cualquier momento.
            </div>

            {/* Action Button */}
            <button
              onClick={onBack}
              className="w-full px-6 py-3 bg-primary text-white font-bold rounded-xl hover:bg-primary-dark transition-all"
            >
              Volver al Inicio
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderWizard;
