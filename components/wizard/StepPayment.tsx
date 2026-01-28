/**
 * StepPayment Component
 * =====================
 * Paso 6: Selección de método de pago y finalización
 */

import React, { useRef, useCallback } from 'react';
import { 
  Building2, QrCode, Percent, Upload, FileText, X, 
  Copy, Check, Info, Loader2, PartyPopper, CreditCard
} from 'lucide-react';
import { PriceBreakdown } from '../../hooks/usePriceCalculation';

interface StepPaymentProps {
  metodoPago: 'transferencia' | 'modo';
  comprobante: File | null;
  priceBreakdown: PriceBreakdown;
  isSubmitting: boolean;
  pedidoEstado: string;
  pedidoProgreso: number;
  onMetodoChange: (metodo: 'transferencia' | 'modo') => void;
  onComprobanteChange: (file: File | null) => void;
  onSubmit: () => void;
}

// Bank account data
const BANK_ACCOUNTS = [
  {
    id: 'bbva',
    name: 'BBVA',
    color: 'blue',
    cbu: '0170099340000012345678',
    alias: 'FOTOLIBROS.BBVA',
    logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/BBVA_2019.svg/120px-BBVA_2019.svg.png'
  },
  {
    id: 'prex',
    name: 'Prex',
    color: 'purple',
    cvu: '0000076500000012345678',
    alias: 'FOTOLIBROS.PREX',
    icon: 'P'
  },
  {
    id: 'uala',
    name: 'Uala',
    color: 'red',
    cvu: '0000000000000012345678',
    alias: 'FOTOLIBROS.UALA',
    icon: 'U'
  }
];

const StepPayment: React.FC<StepPaymentProps> = ({
  metodoPago,
  comprobante,
  priceBreakdown,
  isSubmitting,
  pedidoEstado,
  pedidoProgreso,
  onMetodoChange,
  onComprobanteChange,
  onSubmit
}) => {
  const comprobanteInputRef = useRef<HTMLInputElement>(null);
  const [copiedAlias, setCopiedAlias] = React.useState<string | null>(null);

  const handleCopyAlias = useCallback((alias: string) => {
    navigator.clipboard.writeText(alias);
    setCopiedAlias(alias);
    setTimeout(() => setCopiedAlias(null), 2000);
  }, []);

  const handleComprobanteDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && (file.type.startsWith('image/') || file.type === 'application/pdf')) {
      onComprobanteChange(file);
    }
  }, [onComprobanteChange]);

  const handleComprobantePaste = useCallback((e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (items) {
      for (let i = 0; i < items.length; i++) {
        if (items[i].type.startsWith('image/')) {
          const file = items[i].getAsFile();
          if (file) {
            const namedFile = new File([file], `comprobante-${Date.now()}.png`, { type: file.type });
            onComprobanteChange(namedFile);
            break;
          }
        }
      }
    }
  }, [onComprobanteChange]);

  return (
    <div className="max-w-lg mx-auto animate-fade-in text-primary">
      <h2 className="text-xl md:text-2xl font-display font-bold text-center mb-6">
        Finalizar Compra
      </h2>

      <div className="bg-white p-4 md:p-6 rounded-xl shadow-xl border border-gray-100 space-y-4">
        {/* Payment Method Selection */}
        <div className="space-y-3">
          <p className="text-xs font-bold text-gray-500 uppercase tracking-widest">
            Elegi como pagar:
          </p>

          <div className="grid grid-cols-2 gap-3">
            {/* Transferencia Option */}
            <button
              type="button"
              onClick={() => onMetodoChange('transferencia')}
              className={`
                p-4 rounded-xl border-2 transition-all duration-200 flex flex-col items-center gap-2 relative
                min-h-[120px] focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2
                ${metodoPago === 'transferencia'
                  ? 'border-green-500 bg-green-50 shadow-lg'
                  : 'border-gray-200 bg-white hover:border-green-300'
                }
              `}
              aria-pressed={metodoPago === 'transferencia'}
            >
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-full shadow-md flex items-center gap-1">
                <Percent className="w-2.5 h-2.5" />
                15% OFF
              </span>
              <Building2 className={`w-10 h-10 ${metodoPago === 'transferencia' ? 'text-green-600' : 'text-gray-400'}`} />
              <span className="font-bold text-xs text-green-700">Transferencia</span>
              <span className="text-[10px] text-green-600">BBVA / Prex / Uala</span>
            </button>

            {/* MODO Option */}
            <button
              type="button"
              onClick={() => onMetodoChange('modo')}
              className={`
                p-4 rounded-xl border-2 transition-all duration-200 flex flex-col items-center gap-2
                min-h-[120px] focus:outline-none focus:ring-2 focus:ring-[#00B4E5] focus:ring-offset-2
                ${metodoPago === 'modo'
                  ? 'border-[#00B4E5] bg-[#00B4E5]/10 shadow-lg'
                  : 'border-gray-200 bg-white hover:border-[#00B4E5]/50'
                }
              `}
              aria-pressed={metodoPago === 'modo'}
            >
              <div className="w-10 h-10 bg-[#00B4E5] rounded-lg flex items-center justify-center">
                <QrCode className="w-6 h-6 text-white" />
              </div>
              <span className="font-bold text-xs text-[#00B4E5]">MODO</span>
              <span className="text-[10px] text-gray-500">Pago QR</span>
            </button>
          </div>
        </div>

        {/* Transferencia Details */}
        {metodoPago === 'transferencia' && (
          <div className="space-y-3 animate-fade-in">
            {/* Discount Alert */}
            <div className="flex items-center gap-2 p-2 bg-green-100 rounded-lg">
              <PartyPopper className="w-4 h-4 text-green-600" />
              <p className="text-xs font-bold text-green-700">
                Ahorras {priceBreakdown.formattedDiscount} con transferencia!
              </p>
            </div>

            <p className="text-xs font-bold text-gray-500 uppercase tracking-widest">
              Elegi donde transferir:
            </p>

            {/* Bank Accounts */}
            {BANK_ACCOUNTS.map((bank) => (
              <div 
                key={bank.id}
                className={`p-3 rounded-xl border-2 border-${bank.color}-200 bg-gradient-to-r from-${bank.color}-50 to-white space-y-2`}
              >
                <div className="flex items-center gap-2">
                  {bank.logo ? (
                    <img src={bank.logo} alt={bank.name} className="h-5 object-contain" />
                  ) : (
                    <div className={`w-5 h-5 rounded-full bg-gradient-to-br from-${bank.color}-500 to-${bank.color}-600 flex items-center justify-center`}>
                      <span className="text-white text-[10px] font-bold">{bank.icon}</span>
                    </div>
                  )}
                  <span className={`font-bold text-${bank.color}-800 text-sm`}>{bank.name}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-gray-500">{bank.cbu ? 'CBU' : 'CVU'}:</span>
                    <p className="font-mono font-bold text-primary select-all text-[11px]">
                      {bank.cbu || bank.cvu}
                    </p>
                  </div>
                  <div>
                    <span className="text-gray-500">Alias:</span>
                    <button
                      onClick={() => handleCopyAlias(bank.alias)}
                      className="flex items-center gap-1 font-mono font-bold text-primary text-[11px] hover:text-primary/80 transition-colors"
                    >
                      {bank.alias}
                      {copiedAlias === bank.alias ? (
                        <Check className="w-3 h-3 text-green-500" />
                      ) : (
                        <Copy className="w-3 h-3" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            ))}

            {/* Instructions */}
            <div className="bg-amber-50 p-3 rounded-xl border border-amber-200">
              <p className="text-xs text-amber-800 font-medium">
                <strong>Instrucciones:</strong><br />
                1. Transferi el monto exacto a cualquiera de las cuentas<br />
                2. Guarda el comprobante<br />
                3. Confirma el pedido y te contactamos
              </p>
            </div>

            {/* Comprobante Upload */}
            <div
              className={`
                bg-white p-4 rounded-xl border-2 border-dashed space-y-3 transition-all duration-200
                ${!comprobante ? 'border-green-300 hover:border-green-400 hover:bg-green-50/50' : 'border-green-500 bg-green-50/30'}
              `}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleComprobanteDrop}
              onPaste={handleComprobantePaste}
              tabIndex={0}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Upload className="w-4 h-4 text-green-600" />
                  <p className="font-bold text-sm text-primary">Subi tu comprobante de pago</p>
                </div>
                <span className="text-[10px] bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium flex items-center gap-1">
                  <Info className="w-3 h-3" />
                  Ctrl+V para pegar
                </span>
              </div>

              <input
                type="file"
                ref={comprobanteInputRef}
                accept="image/*,.pdf"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) onComprobanteChange(file);
                }}
              />

              {!comprobante ? (
                <button
                  type="button"
                  onClick={() => comprobanteInputRef.current?.click()}
                  className="w-full py-6 border-2 border-green-200 rounded-xl text-green-700 font-medium hover:bg-green-50 transition-all duration-200 flex flex-col items-center justify-center gap-2 cursor-pointer min-h-[100px]"
                >
                  <Upload className="w-8 h-8 text-green-400" />
                  <span className="text-sm">Arrastra, hace clic, o pega (Ctrl+V)</span>
                  <span className="text-xs text-gray-400">Imagenes o PDF</span>
                </button>
              ) : (
                <div className="flex items-center gap-3 p-3 bg-green-50 rounded-xl">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center overflow-hidden">
                    {comprobante.type.includes('image') ? (
                      <img
                        src={URL.createObjectURL(comprobante)}
                        alt="Comprobante"
                        className="w-full h-full object-cover rounded-lg"
                      />
                    ) : (
                      <FileText className="w-6 h-6 text-green-600" />
                    )}
                  </div>
                  <div className="flex-grow">
                    <p className="text-xs font-bold text-green-800 truncate max-w-[150px]">
                      {comprobante.name}
                    </p>
                    <p className="text-[10px] text-green-600">
                      {(comprobante.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => onComprobanteChange(null)}
                    className="text-red-500 hover:bg-red-50 p-2 rounded-lg transition-all min-w-[44px] min-h-[44px] flex items-center justify-center"
                    aria-label="Eliminar comprobante"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              )}

              <p className="text-[10px] text-gray-400 text-center">
                Nuestro sistema verifica automaticamente tu pago en segundos
              </p>
            </div>
          </div>
        )}

        {/* MODO Details */}
        {metodoPago === 'modo' && (
          <div className="space-y-4 animate-fade-in">
            <div className="bg-[#00B4E5]/10 p-4 rounded-xl border border-[#00B4E5]/30 text-center space-y-3">
              <div className="flex items-center justify-center gap-2">
                <CreditCard className="w-6 h-6 text-[#00B4E5]" />
                <span className="font-bold text-[#00B4E5]">MODO</span>
              </div>
              <p className="text-sm text-gray-600">Escanea el QR desde la app de tu banco</p>

              {/* QR Placeholder */}
              <div className="bg-white p-4 rounded-xl inline-block mx-auto border-2 border-[#00B4E5]">
                <div className="w-40 h-40 bg-gray-100 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <QrCode className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                    <p className="text-xs text-gray-500">QR se genera<br />al confirmar</p>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap justify-center gap-2 text-[10px] text-gray-500">
                {['Galicia', 'Santander', 'BBVA', 'ICBC', '+30 bancos'].map(bank => (
                  <span key={bank} className="px-2 py-1 bg-white rounded-full">{bank}</span>
                ))}
              </div>
            </div>

            <div className="bg-blue-50 p-3 rounded-xl border border-blue-200">
              <p className="text-xs text-blue-800 font-medium">
                <strong>Como funciona MODO?</strong><br />
                1. Abri la app de tu banco y busca "MODO" o "QR"<br />
                2. Escanea el codigo que aparecera<br />
                3. Confirma el pago - Listo!
              </p>
            </div>
          </div>
        )}

        {/* Price Summary */}
        <div className="pt-3 border-t">
          <div className="flex justify-between items-center">
            <span className="text-primary/60 font-bold uppercase tracking-widest text-[10px]">
              Total a abonar
            </span>
            <div className="text-right">
              {priceBreakdown.hasDiscount ? (
                <>
                  <span className="text-gray-400 line-through text-sm mr-2">
                    {priceBreakdown.formattedSubtotal}
                  </span>
                  <span className="text-2xl md:text-3xl font-display font-bold text-green-600">
                    {priceBreakdown.formattedTotal}
                  </span>
                </>
              ) : (
                <span className="text-2xl md:text-3xl font-display font-bold text-primary">
                  {priceBreakdown.formattedTotal}
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="button"
          onClick={onSubmit}
          disabled={isSubmitting}
          className={`
            w-full py-4 rounded-xl font-bold text-lg transition-all duration-200
            flex items-center justify-center gap-2 min-h-[56px]
            focus:outline-none focus:ring-4 focus:ring-primary/20
            ${isSubmitting
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-primary text-white hover:bg-primary-dark hover:shadow-lg active:scale-[0.98]'
            }
          `}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              {pedidoEstado || 'Procesando...'}
            </>
          ) : (
            <>
              Confirmar Pedido
              <Check className="w-5 h-5" />
            </>
          )}
        </button>

        {/* Progress (when submitting) */}
        {isSubmitting && pedidoProgreso > 0 && (
          <div className="space-y-2">
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-primary transition-all duration-500 rounded-full"
                style={{ width: `${pedidoProgreso}%` }}
              />
            </div>
            <p className="text-center text-xs text-gray-500">
              {pedidoProgreso}% completado
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default StepPayment;
