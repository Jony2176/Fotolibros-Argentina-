
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { PRODUCTS, PACKAGES, PROVINCIAS_MAPPING, SHIPPING_COSTS } from '../constants';
import { OrderDetails, Product, OrderStatus } from '../types';
import { GoogleGenAI, Type } from "@google/genai";
import TTSButton from '../components/TTSButton';

interface OrderWizardProps {
  onBack: () => void;
}

const OrderWizard: React.FC<OrderWizardProps> = ({ onBack }) => {
  const [step, setStep] = useState(1);
  const [filterTipo, setFilterTipo] = useState<string>('all');
  const [filterTapa, setFilterTapa] = useState<string>('all');
  
  const [orderDetails, setOrderDetails] = useState<Partial<OrderDetails>>({
    productoCodigo: '',
    paginasTotal: 22,
    fotos: [],
    cliente: {
      nombre: '',
      email: '',
      telefono: '',
      direccion: { calle: '', ciudad: '', provincia: '', cp: '' }
    },
    metodoPago: 'mercadopago',
    total: 0,
    estado: OrderStatus.PENDIENTE_PAGO
  });

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisSummary, setAnalysisSummary] = useState<any>(null);
  const [isCoverModalOpen, setIsCoverModalOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [coverPrompts, setCoverPrompts] = useState({ theme: '', style: 'Elegante' });
  const [generatedCovers, setGeneratedCovers] = useState<string[]>([]);
  const [selectedCover, setSelectedCover] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('fl_draft');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setOrderDetails(prev => ({ ...prev, ...parsed, fotos: [] }));
      } catch (e) { console.error("Error loading draft", e); }
    }
  }, []);

  useEffect(() => {
    const { fotos, ...toSave } = orderDetails;
    localStorage.setItem('fl_draft', JSON.stringify(toSave));
  }, [orderDetails]);

  const selectedProduct = PRODUCTS.find(p => p.codigo === orderDetails.productoCodigo);
  
  const priceBreakdown = useMemo(() => {
    if (!selectedProduct) return { base: 0, extras: 0, extraCost: 0, shipping: 0, total: 0 };
    const base = selectedProduct.precioBase;
    const extraQty = Math.max(0, (orderDetails.paginasTotal || 0) - selectedProduct.paginasBase);
    const extraCost = extraQty * selectedProduct.precioPaginaExtra;
    
    const prov = orderDetails.cliente?.direccion?.provincia;
    const zona = prov ? PROVINCIAS_MAPPING[prov] : null;
    const shipping = zona ? SHIPPING_COSTS[zona] : 0;
    
    return {
      base,
      extraQty,
      extraCost,
      shipping,
      total: base + extraCost + shipping
    };
  }, [selectedProduct, orderDetails.paginasTotal, orderDetails.cliente?.direccion?.provincia]);

  const nextStep = () => setStep(s => Math.min(s + 1, 5));
  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  const removePhoto = (index: number) => {
    setOrderDetails(prev => ({
      ...prev,
      fotos: (prev.fotos || []).filter((_, i) => i !== index)
    }));
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      const updatedFotos = [...(orderDetails.fotos || []), ...newFiles].slice(0, 200);
      setOrderDetails(prev => ({ ...prev, fotos: updatedFotos }));
      if (updatedFotos.length >= 10) analyzePhotosAI(updatedFotos);
    }
  };

  const analyzePhotosAI = async (fotos: File[]) => {
    setIsAnalyzing(true);
    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: `Analiza ${fotos.length} fotos. Detecta duplicados y calidad. JSON format.`,
        config: {
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              borrosas: { type: Type.NUMBER },
              duplicados: { type: Type.NUMBER }
            }
          }
        }
      });
      setAnalysisSummary(JSON.parse(response.text));
    } catch (e) { console.error(e); } finally { setIsAnalyzing(false); }
  };

  const filteredProducts = useMemo(() => {
    return PRODUCTS.filter(p => {
      const matchTipo = filterTipo === 'all' || p.tipo === filterTipo;
      const matchTapa = filterTapa === 'all' || p.tapa === filterTapa;
      return matchTipo && matchTapa;
    });
  }, [filterTipo, filterTapa]);

  const inputClasses = "w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-xl outline-none focus:ring-4 focus:ring-primary/5 focus:border-primary transition-all placeholder:text-gray-300 shadow-sm";

  return (
    <div className="bg-cream min-h-screen flex flex-col font-sans">
      <header className="bg-white border-b px-4 py-4 md:py-6 shadow-sm relative md:sticky md:top-0 z-50">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-4 md:mb-8">
            <button onClick={onBack} className="text-gray-400 hover:text-primary flex items-center gap-1 text-sm md:text-base">← Volver</button>
            <div className="font-display font-bold text-primary uppercase tracking-widest text-xs md:text-sm">Fotolibros Argentina</div>
            <div className="flex items-center gap-2">
              <TTSButton text={`Paso ${step}.`} />
              <div className="text-[10px] text-gray-400 font-bold hidden md:block">PASO {step} / 5</div>
            </div>
          </div>
          <div className="flex items-center justify-between relative px-2">
            <div className="absolute top-1/2 left-0 w-full h-0.5 md:h-1 bg-gray-100 -translate-y-1/2 -z-10"></div>
            <div className="absolute top-1/2 left-0 h-0.5 md:h-1 bg-primary -translate-y-1/2 -z-10 transition-all duration-500" style={{ width: `${((step - 1) / 4) * 100}%` }}></div>
            {[1, 2, 3, 4, 5].map((s) => (
              <div key={s} className={`w-6 h-6 md:w-8 md:h-8 rounded-full flex items-center justify-center text-[10px] md:text-sm font-bold transition-all ${step === s ? 'step-active scale-110 shadow-lg' : step > s ? 'step-done' : 'step-pending'}`}>{step > s ? '✓' : s}</div>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto w-full p-4 py-6 md:py-10 flex-grow pb-32 md:pb-10">
        
        {step === 1 && (
          <div className="animate-fade-in">
            <div className="text-center mb-10">
              <h2 className="text-2xl md:text-3xl font-display font-bold text-primary mb-2">Elegí tu modelo</h2>
              <p className="text-gray-500 text-sm">Papel fotográfico premium de 170g y terminación artesanal.</p>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 md:gap-6">
              {filteredProducts.map((prod) => (
                <div key={prod.codigo} onClick={() => { setOrderDetails(p => ({...p, productoCodigo: prod.codigo, paginasTotal: prod.paginasBase})); nextStep(); }} className="cursor-pointer group bg-white p-5 rounded-3xl border-2 border-gray-100 hover:border-primary transition-all shadow-sm flex flex-col relative overflow-hidden">
                  {prod.badge && <span className="absolute top-3 right-3 bg-accent text-white text-[9px] font-bold px-3 py-1 rounded-full shadow-md z-10">{prod.badge}</span>}
                  <div className="relative overflow-hidden rounded-2xl mb-4 aspect-[4/3]">
                    <img src={prod.imagen} className="w-full h-full object-cover group-hover:scale-105 transition-transform" />
                  </div>
                  <h4 className="font-bold text-primary text-lg mb-1">{prod.nombre}</h4>
                  <p className="text-[10px] text-gray-400 mb-3">{prod.tamanio} • Tapa {prod.tapa}</p>
                  
                  <div className="space-y-1.5 mb-6">
                    <div className="flex items-center gap-2 text-[10px] text-gray-500">
                      <span>💎</span> Papel Ilustración 170g
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-gray-500">
                      <span>📖</span> Encuadernación cosida
                    </div>
                    <div className="flex items-center gap-2 text-[10px] text-accent font-bold">
                      <span>➕</span> Página extra: ${prod.precioPaginaExtra}
                    </div>
                  </div>

                  <div className="mt-auto flex justify-between items-center pt-4 border-t border-gray-50">
                    <div className="flex flex-col">
                      <span className="text-[9px] font-bold text-gray-400 uppercase">Base</span>
                      <span className="text-xl font-bold text-primary">${prod.precioBase.toLocaleString()}</span>
                    </div>
                    <button className="bg-primary text-white w-9 h-9 rounded-full flex items-center justify-center font-bold">→</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="max-w-2xl mx-auto animate-fade-in">
            <h2 className="text-2xl md:text-3xl font-display font-bold text-primary text-center mb-10">Configurá las páginas</h2>
            <div className="bg-white p-6 md:p-8 rounded-3xl shadow-xl border border-gray-100 space-y-6 md:space-y-8">
              <div className="bg-blue-50 p-4 rounded-2xl flex items-start gap-3 border border-blue-100">
                <span className="text-xl">💡</span>
                <p className="text-xs text-blue-800 leading-relaxed">
                  <strong>Importante:</strong> El precio base incluye <strong>{selectedProduct?.paginasBase} páginas</strong>. El máximo es 80 páginas. <br/>Cada página adicional cuesta <strong>${selectedProduct?.precioPaginaExtra}</strong>.
                </p>
              </div>

              <div className="flex items-center justify-between bg-cream p-4 md:p-6 rounded-3xl border border-primary/5">
                <button onClick={() => setOrderDetails(prev => ({ ...prev, paginasTotal: Math.max(selectedProduct!.paginasBase, (prev.paginasTotal || 0) - 2) }))} className="w-12 h-12 md:w-16 md:h-16 rounded-xl md:rounded-2xl bg-white shadow-md text-2xl md:text-3xl font-bold text-primary hover:bg-primary hover:text-white transition-all">-</button>
                <div className="text-center">
                  <div className="text-4xl md:text-6xl font-display font-bold text-primary">{orderDetails.paginasTotal}</div>
                  <div className="text-[10px] text-gray-400 font-bold tracking-widest uppercase">Páginas Totales</div>
                  <div className="text-[9px] text-gray-400">({(orderDetails.paginasTotal || 0)/2} Hojas)</div>
                </div>
                <button onClick={() => setOrderDetails(prev => ({ ...prev, paginasTotal: Math.min(selectedProduct!.paginasMax, (prev.paginasTotal || 0) + 2) }))} className="w-12 h-12 md:w-16 md:h-16 rounded-xl md:rounded-2xl bg-white shadow-md text-2xl md:text-3xl font-bold text-primary hover:bg-primary hover:text-white transition-all">+</button>
              </div>

              <div className="bg-gray-50 p-4 md:p-6 rounded-2xl space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Precio Base ({selectedProduct?.paginasBase} págs)</span>
                  <span className="font-bold text-primary">${priceBreakdown.base.toLocaleString()}</span>
                </div>
                {priceBreakdown.extraQty > 0 && (
                  <div className="flex justify-between text-sm text-accent">
                    <span>{priceBreakdown.extraQty} Páginas adicionales</span>
                    <span className="font-bold">+ ${priceBreakdown.extraCost.toLocaleString()}</span>
                  </div>
                )}
                <div className="border-t border-gray-200 pt-4 flex justify-between items-baseline">
                  <span className="font-bold text-primary">Subtotal</span>
                  <span className="text-2xl md:text-3xl font-display font-bold text-primary">${(priceBreakdown.base + priceBreakdown.extraCost).toLocaleString()}</span>
                </div>
              </div>
              
              <button onClick={nextStep} className="w-full py-5 bg-primary text-white font-bold rounded-2xl shadow-lg transform active:scale-[0.98] transition-all">Siguiente Paso →</button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="animate-fade-in space-y-10">
            <div className="text-center">
              <h2 className="text-2xl md:text-3xl font-display font-bold text-primary mb-2">Subí tus mejores momentos</h2>
              <p className="text-gray-500 text-sm">Mínimo 10 fotos. Recomendamos 2 a 4 fotos por página.</p>
            </div>

            <div className="max-w-xl mx-auto px-2">
               <div className="mb-4 flex justify-between items-end">
                  <span className={`text-[10px] font-bold uppercase tracking-wider ${orderDetails.fotos!.length < 10 ? 'text-error' : 'text-success'}`}>
                    {orderDetails.fotos!.length < 10 ? `Faltan ${10 - orderDetails.fotos!.length} fotos` : '¡Mínimo alcanzado!'}
                  </span>
                  <span className="text-[10px] font-bold text-gray-400">{orderDetails.fotos!.length} / 200</span>
               </div>
               <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden mb-6">
                  <div className={`h-full transition-all duration-500 ${orderDetails.fotos!.length < 10 ? 'bg-orange-400' : 'bg-success'}`} style={{ width: `${Math.min(100, (orderDetails.fotos!.length / 200) * 100)}%` }}></div>
               </div>
            </div>

            <div onClick={() => fileInputRef.current?.click()} className="border-4 border-dashed border-gray-200 rounded-3xl p-10 md:p-20 text-center hover:bg-white hover:border-primary transition-all bg-gray-50 cursor-pointer group shadow-sm">
              <span className="text-4xl md:text-6xl mb-6 block group-hover:scale-110 transition-transform">📸</span>
              <h3 className="text-lg md:text-xl font-bold text-primary mb-2">Seleccioná o Arrastrá tus fotos</h3>
              <p className="text-gray-400 text-xs md:text-sm">JPG o PNG de alta resolución</p>
              <input type="file" multiple hidden ref={fileInputRef} onChange={handleFileUpload} accept="image/*" />
            </div>

            <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-8 lg:grid-cols-10 gap-2">
              {orderDetails.fotos?.map((f, i) => (
                <div key={i} className="relative aspect-square rounded-lg md:rounded-xl overflow-hidden shadow-sm border group">
                  <img src={URL.createObjectURL(f)} className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                  <button onClick={() => removePhoto(i)} className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white transition-opacity">✕</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="animate-fade-in grid md:grid-cols-3 gap-6 md:gap-10">
            <div className="md:col-span-2 space-y-6">
              <h2 className="text-2xl md:text-3xl font-display font-bold text-primary mb-2">Datos de Entrega</h2>
              <div className="bg-white p-5 md:p-8 rounded-3xl border border-gray-100 shadow-xl space-y-6">
                <div className="grid sm:grid-cols-2 gap-4 md:gap-6">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest ml-1">Nombre Completo</label>
                    <input type="text" className={inputClasses} placeholder="Juan Pérez" value={orderDetails.cliente?.nombre} onChange={e => setOrderDetails(p => ({...p, cliente: {...p.cliente!, nombre: e.target.value}}))} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest ml-1">Email</label>
                    <input type="email" className={inputClasses} placeholder="tu@email.com" value={orderDetails.cliente?.email} onChange={e => setOrderDetails(p => ({...p, cliente: {...p.cliente!, email: e.target.value}}))} />
                  </div>
                </div>
                <div className="grid sm:grid-cols-2 gap-4 md:gap-6">
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest ml-1">Provincia</label>
                    <select className={inputClasses} value={orderDetails.cliente?.direccion.provincia} onChange={e => setOrderDetails(p => ({...p, cliente: {...p.cliente!, direccion: {...p.cliente!.direccion, provincia: e.target.value}}}))}>
                      <option value="">Seleccionar...</option>
                      {Object.keys(PROVINCIAS_MAPPING).map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest ml-1">Ciudad</label>
                    <input type="text" className={inputClasses} placeholder="Rosario" value={orderDetails.cliente?.direccion.ciudad} onChange={e => setOrderDetails(p => ({...p, cliente: {...p.cliente!, direccion: {...p.cliente!.direccion, ciudad: e.target.value}}}))} />
                  </div>
                </div>
                <div className="grid sm:grid-cols-3 gap-4 md:gap-6">
                  <div className="sm:col-span-2 space-y-1">
                    <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest ml-1">Dirección Completa</label>
                    <input type="text" className={inputClasses} placeholder="Av. Pellegrini 1234" value={orderDetails.cliente?.direccion.calle} onChange={e => setOrderDetails(p => ({...p, cliente: {...p.cliente!, direccion: {...p.cliente!.direccion, calle: e.target.value}}}))} />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[10px] font-bold text-gray-500 uppercase tracking-widest ml-1">CP</label>
                    <input type="text" className={inputClasses} placeholder="2000" value={orderDetails.cliente?.direccion.cp} onChange={e => setOrderDetails(p => ({...p, cliente: {...p.cliente!, direccion: {...p.cliente!.direccion, cp: e.target.value}}}))} />
                  </div>
                </div>
              </div>
            </div>

            <div className="md:col-span-1">
              <div className="bg-white p-6 md:p-8 rounded-3xl border border-gray-100 shadow-xl h-fit md:sticky md:top-32 space-y-6">
                <h3 className="font-display font-bold text-primary text-xl mb-2">Tu Pedido</h3>
                <div className="space-y-4 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Modelo</span>
                    <span className="font-bold text-primary text-right">{selectedProduct?.nombre}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Páginas</span>
                    <span className="font-bold text-primary">{orderDetails.paginasTotal}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Envío</span>
                    <span className="font-bold text-primary">${priceBreakdown.shipping.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between border-t pt-4">
                    <span className="text-gray-500 font-bold uppercase text-xs">Total</span>
                    <span className="text-2xl font-display font-bold text-primary">${priceBreakdown.total.toLocaleString()}</span>
                  </div>
                </div>
                <button 
                  onClick={nextStep} 
                  disabled={!orderDetails.cliente?.nombre || !orderDetails.cliente?.direccion.provincia} 
                  className="w-full py-5 bg-primary text-white font-bold rounded-2xl shadow-lg disabled:opacity-30 md:block hidden"
                >
                  Pagar Ahora →
                </button>
              </div>
            </div>
          </div>
        )}

        {step === 5 && (
          <div className="max-w-2xl mx-auto animate-fade-in text-primary">
            <h2 className="text-2xl md:text-3xl font-display font-bold text-center mb-10">Finalizar Compra</h2>
            <div className="bg-white p-6 md:p-10 rounded-3xl shadow-2xl border border-gray-100 space-y-8">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <button 
                  onClick={() => setOrderDetails(p => ({...p, metodoPago: 'mercadopago'}))} 
                  className={`p-6 md:p-8 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${orderDetails.metodoPago === 'mercadopago' ? 'border-primary bg-primary/5' : 'border-gray-200 bg-white'}`}
                >
                  <span className="text-3xl md:text-4xl mb-2">💳</span>
                  <span className="font-bold text-sm text-primary">MercadoPago</span>
                </button>
                <button 
                  onClick={() => setOrderDetails(p => ({...p, metodoPago: 'transferencia'}))} 
                  className={`p-6 md:p-8 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${orderDetails.metodoPago === 'transferencia' ? 'border-primary bg-primary/5' : 'border-gray-200 bg-white'}`}
                >
                  <span className="text-3xl md:text-4xl mb-2">🏦</span>
                  <span className="font-bold text-sm text-primary">Transferencia</span>
                </button>
              </div>

              {orderDetails.metodoPago === 'transferencia' && (
                <div className="bg-cream/60 p-5 md:p-6 rounded-2xl border border-primary/10 space-y-3">
                  <p className="font-bold text-primary text-sm md:text-base">Datos de la Cuenta:</p>
                  <div className="space-y-1">
                    <p className="text-xs md:text-sm text-primary font-medium"><strong>CBU:</strong> 0720000088000012345678</p>
                    <p className="text-xs md:text-sm text-primary font-medium"><strong>Alias:</strong> fotolibros.arg</p>
                  </div>
                  <p className="text-[10px] text-accent font-bold italic mt-2">"Se iniciará la producción tras validar el comprobante."</p>
                </div>
              )}

              <div className="pt-6 md:pt-8 border-t flex justify-between items-center">
                <span className="text-primary/60 font-bold uppercase tracking-widest text-[11px] md:text-xs">Total a abonar</span>
                <span className="text-3xl md:text-4xl font-display font-bold text-primary">${priceBreakdown.total.toLocaleString()}</span>
              </div>

              <button 
                onClick={() => alert('¡Gracias por tu compra! (Simulación)')} 
                className="w-full py-6 bg-accent text-white font-bold rounded-2xl shadow-xl hover:scale-[1.01] transition-all active:scale-95"
              >
                {orderDetails.metodoPago === 'mercadopago' ? 'Pagar con MercadoPago' : 'Confirmar Pedido'}
              </button>
            </div>
          </div>
        )}
      </main>

      {step < 5 && (
        <footer className="bg-white border-t p-3 md:p-5 flex items-center justify-between sticky bottom-0 z-50 shadow-2xl">
          <button onClick={prevStep} disabled={step === 1} className="px-4 md:px-8 py-2 md:py-3 font-bold text-gray-400 disabled:opacity-0 text-sm">← Atrás</button>
          <div className="text-center">
             <div className="text-primary font-bold text-base md:text-xl leading-none md:leading-normal">${priceBreakdown.total.toLocaleString()}</div>
          </div>
          <button 
            onClick={nextStep} 
            disabled={(step === 1 && !orderDetails.productoCodigo) || (step === 3 && orderDetails.fotos!.length < 10) || (step === 4 && (!orderDetails.cliente?.nombre || !orderDetails.cliente?.direccion.provincia))} 
            className="px-6 md:px-10 py-2 md:py-3 bg-primary text-white font-bold rounded-lg md:rounded-xl shadow-lg transition-all disabled:opacity-30 text-sm"
          >
            Siguiente →
          </button>
        </footer>
      )}
    </div>
  );
};

export default OrderWizard;
