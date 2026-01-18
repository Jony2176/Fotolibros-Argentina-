
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { PRODUCTS, PACKAGES, PROVINCIAS_MAPPING, SHIPPING_COSTS, DESIGN_STYLES, CIUDADES_POR_PROVINCIA, CP_POR_CIUDAD } from '../constants';
import { OrderDetails, Product, OrderStatus } from '../types';
import { GoogleGenAI, Type } from "@google/genai";
import TTSButton from '../components/TTSButton';
import Book3D, { COVER_COLORS } from '../components/Book3D';

interface OrderWizardProps {
  onBack: () => void;
}

const OrderWizard: React.FC<OrderWizardProps> = ({ onBack }) => {
  const [step, setStep] = useState(1);
  const [filterTipo, setFilterTipo] = useState<string>('all');
  const [filterTapa, setFilterTapa] = useState<string>('all');
  const [estiloDiseno, setEstiloDiseno] = useState<string>('clasico');

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

  // Estados para envío al backend
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [pedidoId, setPedidoId] = useState<string | null>(null);
  const [pedidoEstado, setPedidoEstado] = useState<string>('');
  const [pedidoProgreso, setPedidoProgreso] = useState(0);
  const [manualCityMode, setManualCityMode] = useState(false);
  const [isTipsModalOpen, setIsTipsModalOpen] = useState(false);

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
    if (!selectedProduct) return { base: 0, extras: 0, extraCost: 0, shipping: 0, total: 0, discount: 0, finalTotal: 0, extraQty: 0 };
    const base = selectedProduct.precioBase;
    const extraQty = Math.max(0, (orderDetails.paginasTotal || 0) - selectedProduct.paginasBase);
    const extraCost = extraQty * selectedProduct.precioPaginaExtra;

    const prov = orderDetails.cliente?.direccion?.provincia;
    const zona = prov ? PROVINCIAS_MAPPING[prov] : null;
    const shipping = zona ? SHIPPING_COSTS[zona] : 0;

    const subtotal = base + extraCost + shipping;

    // 15% de descuento por transferencia bancaria
    const isTransfer = orderDetails.metodoPago === 'transferencia';
    const discount = isTransfer ? Math.round(subtotal * 0.15) : 0;
    const finalTotal = subtotal - discount;

    return {
      base,
      extraQty,
      extraCost,
      shipping,
      total: subtotal,
      discount,
      finalTotal
    };
  }, [selectedProduct, orderDetails.paginasTotal, orderDetails.cliente?.direccion?.provincia, orderDetails.metodoPago]);

  const nextStep = () => setStep(s => Math.min(s + 1, 6));
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

  // Función para enviar pedido al backend
  const enviarPedido = async () => {
    setIsSubmitting(true);
    setPedidoEstado('Enviando pedido...');

    try {
      const payload = {
        producto_codigo: orderDetails.productoCodigo,
        estilo_diseno: estiloDiseno,
        paginas_total: orderDetails.paginasTotal,
        cliente: {
          nombre: orderDetails.cliente?.nombre,
          email: orderDetails.cliente?.email,
          telefono: orderDetails.cliente?.telefono || '',
          direccion: orderDetails.cliente?.direccion
        },
        metodo_pago: orderDetails.metodoPago,
        titulo_tapa: null,
        texto_lomo: null
      };

      const response = await fetch('http://localhost:8000/pedidos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) throw new Error('Error al crear pedido');

      const data = await response.json();
      setPedidoId(data.id);
      setPedidoEstado('Pedido creado, procesando...');

      // Iniciar polling del estado
      consultarEstado(data.id);

    } catch (error) {
      console.error('Error:', error);
      setPedidoEstado('Error al enviar pedido');
      setIsSubmitting(false);
    }
  };

  // Función para consultar estado del pedido
  const consultarEstado = async (id: string) => {
    try {
      const response = await fetch(`http://localhost:8000/pedidos/${id}`);
      const data = await response.json();

      setPedidoEstado(data.mensaje);
      setPedidoProgreso(data.progreso);

      if (data.estado === 'completado') {
        setIsSubmitting(false);
      } else if (data.estado === 'error') {
        setIsSubmitting(false);
      } else {
        setTimeout(() => consultarEstado(id), 2000);
      }
    } catch (error) {
      console.error('Error consultando estado:', error);
    }
  };

  const inputClasses = "w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-xl outline-none focus:ring-4 focus:ring-primary/5 focus:border-primary transition-all placeholder:text-gray-300 shadow-sm";

  return (
    <div className="bg-cream min-h-screen flex flex-col font-sans">
      <header className="bg-white border-b px-4 py-3 md:py-4 shadow-sm relative md:sticky md:top-0 z-50">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-3 md:mb-4">
            <button onClick={onBack} className="text-gray-400 hover:text-primary flex items-center gap-1 text-xs md:text-sm">← Volver</button>
            <button onClick={onBack} className="transition-transform hover:scale-105 active:scale-95">
              <img src="/logo.png" alt="Fotolibros Argentina" className="h-6 md:h-8" />
            </button>
            <div className="flex items-center gap-2">
              <div className="text-[9px] text-gray-400 font-bold hidden md:block">PASO {step} / 6</div>
            </div>
          </div>
          <div className="flex items-center justify-between relative px-2">
            <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-100 -translate-y-1/2 -z-10"></div>
            <div className="absolute top-1/2 left-0 h-0.5 bg-primary -translate-y-1/2 -z-10 transition-all duration-500" style={{ width: `${((step - 1) / 5) * 100}%` }}></div>
            {[1, 2, 3, 4, 5, 6].map((s) => (
              <div key={s} className={`w-5 h-5 md:w-6 md:h-6 rounded-full flex items-center justify-center text-[9px] md:text-[10px] font-bold transition-all ${step === s ? 'step-active scale-110 shadow-lg' : step > s ? 'step-done' : 'step-pending'}`}>{step > s ? '✓' : s}</div>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto w-full p-4 py-4 md:py-6 flex-grow pb-24 md:pb-6">

        {step === 1 && (
          <div className="animate-fade-in">
            <div className="text-center mb-4 md:mb-6">
              <h2 className="text-xl md:text-2xl font-display font-bold text-primary mb-1">Elegí tu modelo</h2>
              <p className="text-gray-500 text-xs">Papel fotográfico premium de 170g y terminación artesanal.</p>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3 md:gap-4">
              {filteredProducts.map((prod) => {
                const sizeMatch = prod.tamanio.match(/(\d+(?:,\d+)?)\s*×\s*(\d+(?:,\d+)?)/);
                const bookWidth = sizeMatch ? parseFloat(sizeMatch[1].replace(',', '.')) : 21;
                const bookHeight = sizeMatch ? parseFloat(sizeMatch[2].replace(',', '.')) : 21;

                return (
                  <div
                    key={prod.codigo}
                    onClick={() => { setOrderDetails(p => ({ ...p, productoCodigo: prod.codigo, paginasTotal: prod.paginasBase })); nextStep(); }}
                    className="cursor-pointer group bg-white p-3 md:p-4 rounded-xl border-2 border-gray-100 hover:border-primary hover:shadow-lg transition-all shadow-sm flex flex-col relative"
                  >
                    {prod.badge && <span className="absolute top-2 right-2 bg-accent text-white text-[8px] font-bold px-2 py-0.5 rounded-full shadow-md z-10">{prod.badge}</span>}

                    <div className="flex items-center justify-center py-4 md:py-6 mb-2 bg-gradient-to-b from-gray-50 to-white rounded-lg">
                      <Book3D
                        width={bookWidth}
                        height={bookHeight}
                        coverType={prod.tapa as 'Blanda' | 'Dura' | 'Simil Cuero'}
                        color={COVER_COLORS[prod.tapa as keyof typeof COVER_COLORS] || '#1a365d'}
                        imageUrl={prod.imagen}
                        title={prod.nombre.includes('Grande') && prod.tipo === 'Cuadrado' ? "Recuerdos 2025" : undefined}
                      />
                    </div>

                    <h4 className="font-bold text-primary text-sm mb-0.5 leading-tight">{prod.nombre}</h4>
                    <p className="text-[9px] text-gray-400 mb-2">{prod.tamanio} • Tapa {prod.tapa}</p>

                    <div className="space-y-0.5 mb-3 hidden md:block">
                      <div className="flex items-center gap-1 text-[9px] text-gray-500">
                        <span>💎</span> Papel 170g
                      </div>
                      <div className="flex items-center gap-1 text-[9px] text-accent font-bold">
                        <span>➕</span> +${prod.precioPaginaExtra}/pág
                      </div>
                    </div>

                    <div className="mt-auto flex justify-between items-center pt-2 border-t border-gray-50">
                      <div className="flex flex-col">
                        <span className="text-[8px] font-bold text-gray-400 uppercase">Base</span>
                        <span className="text-base font-bold text-primary">${prod.precioBase.toLocaleString()}</span>
                      </div>
                      <button className="bg-primary text-white w-7 h-7 rounded-full flex items-center justify-center font-bold text-sm group-hover:scale-110 transition-transform">→</button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="animate-fade-in">
            <div className="text-center mb-4 md:mb-6">
              <h2 className="text-xl md:text-2xl font-display font-bold text-primary mb-1">Elegí el estilo de diseño</h2>
              <p className="text-gray-500 text-xs">Esto define cómo se verá tu fotolibro. ¡Podés cambiarlo después!</p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 max-w-4xl mx-auto">
              {DESIGN_STYLES.map((style) => (
                <div
                  key={style.id}
                  onClick={() => { setEstiloDiseno(style.id); nextStep(); }}
                  className={`cursor-pointer group bg-white p-4 md:p-5 rounded-2xl border-2 transition-all shadow-sm hover:shadow-xl flex flex-col ${estiloDiseno === style.id ? 'border-primary ring-4 ring-primary/10' : 'border-gray-100 hover:border-primary/50'}`}
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span className="text-2xl md:text-3xl">{style.emoji}</span>
                    <h4 className="font-bold text-primary text-sm md:text-base">{style.nombre}</h4>
                  </div>

                  <p className="text-[10px] md:text-xs text-gray-500 mb-3 leading-relaxed flex-grow">{style.descripcion}</p>

                  <div
                    className="h-16 md:h-20 rounded-xl mb-3 flex items-center justify-center relative overflow-hidden"
                    style={{
                      background: style.tapa.estiloFondo === 'gradiente'
                        ? `linear-gradient(135deg, ${style.colorPrimario}, ${style.colorSecundario})`
                        : style.colorPrimario
                    }}
                  >
                    {style.tapa.conTitulo && (
                      <div className="text-white text-[10px] md:text-xs font-bold text-center px-2" style={{ textShadow: '0 1px 2px rgba(0,0,0,0.3)' }}>
                        {style.id === 'clasico' ? 'Nuestra Boda' : style.id === 'divertido' ? '¡Feliz Cumple!' : style.id === 'premium' ? 'Recuerdos 2025' : ''}
                      </div>
                    )}
                    {style.interior.conAdornos && (
                      <div className="absolute top-1 right-1 text-white/50 text-lg">✨</div>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-1">
                    {style.idealPara.slice(0, 2).map((tag, i) => (
                      <span key={i} className="text-[8px] md:text-[9px] bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full">{tag}</span>
                    ))}
                  </div>

                  <div className="mt-3 pt-3 border-t border-gray-100 flex items-center justify-between">
                    <span className="text-[9px] text-gray-400">{style.interior.fotosRecomendadas} foto{style.interior.fotosRecomendadas > 1 ? 's' : ''}/pág</span>
                    <button className="bg-primary text-white w-6 h-6 rounded-full flex items-center justify-center text-xs group-hover:scale-110 transition-transform">→</button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 max-w-2xl mx-auto">
              <div className="bg-blue-50 p-3 rounded-xl flex items-start gap-2 border border-blue-100">
                <span className="text-base">💡</span>
                <p className="text-[11px] text-blue-800 leading-relaxed">
                  <strong>Consejo:</strong> Si no estás seguro, <strong>Clásico</strong> es nuestra opción más versátil. El estilo define colores, fondos y cantidad de fotos por página, pero siempre podés personalizar cada detalle.
                </p>
              </div>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className="max-w-lg mx-auto animate-fade-in">
            <h2 className="text-xl md:text-2xl font-display font-bold text-primary text-center mb-4 md:mb-6">Configurá las páginas</h2>
            <div className="bg-white p-4 md:p-5 rounded-2xl shadow-xl border border-gray-100 space-y-4">
              <div className="bg-blue-50 p-3 rounded-xl flex items-start gap-2 border border-blue-100">
                <span className="text-base">💡</span>
                <p className="text-[11px] text-blue-800 leading-relaxed">
                  <strong>Importante:</strong> El precio base incluye <strong>{selectedProduct?.paginasBase} páginas</strong>. El máximo es 80 páginas. Cada página adicional cuesta <strong>${selectedProduct?.precioPaginaExtra}</strong>.
                </p>
              </div>

              <div className="flex items-center justify-center gap-4 md:gap-6 bg-cream p-4 rounded-2xl border border-primary/5">
                <button
                  onClick={() => setOrderDetails(prev => ({ ...prev, paginasTotal: Math.max(selectedProduct!.paginasBase, (prev.paginasTotal || 0) - 2) }))}
                  className="flex-shrink-0 w-11 h-11 md:w-12 md:h-12 rounded-xl bg-white shadow-md text-xl md:text-2xl font-bold text-primary hover:bg-primary hover:text-white transition-all flex items-center justify-center"
                >
                  −
                </button>
                <div className="text-center flex-shrink-0 min-w-[100px]">
                  <div className="text-4xl md:text-5xl font-display font-bold text-primary leading-none">{orderDetails.paginasTotal}</div>
                  <div className="text-[9px] text-gray-400 font-bold tracking-widest uppercase mt-1">Páginas Totales</div>
                  <div className="text-[8px] text-gray-400">({(orderDetails.paginasTotal || 0) / 2} Hojas)</div>
                </div>
                <button
                  onClick={() => setOrderDetails(prev => ({ ...prev, paginasTotal: Math.min(selectedProduct!.paginasMax, (prev.paginasTotal || 0) + 2) }))}
                  className="flex-shrink-0 w-11 h-11 md:w-12 md:h-12 rounded-xl bg-white shadow-md text-xl md:text-2xl font-bold text-primary hover:bg-primary hover:text-white transition-all flex items-center justify-center"
                >
                  +
                </button>
              </div>

              <div className="bg-gray-50 p-3 md:p-4 rounded-xl space-y-2">
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
                <div className="border-t border-gray-200 pt-3 flex justify-between items-baseline">
                  <span className="font-bold text-primary">Subtotal</span>
                  <span className="text-xl md:text-2xl font-display font-bold text-primary">${(priceBreakdown.base + priceBreakdown.extraCost).toLocaleString()}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 4 && (
          <div className="animate-fade-in space-y-4 md:space-y-6">
            <div className="text-center">
              <h2 className="text-xl md:text-2xl font-display font-bold text-primary mb-1">Subí tus mejores momentos</h2>
              <p className="text-gray-500 text-xs">Mínimo 10 fotos. Recomendamos 2 a 4 fotos por página.</p>
            </div>

            <div className="max-w-md mx-auto px-2">
              <div className="mb-4 flex justify-center">
                <button
                  onClick={() => setIsTipsModalOpen(true)}
                  className="text-primary text-[10px] font-bold border border-primary/20 bg-white px-3 py-1.5 rounded-full hover:bg-primary/5 transition-all flex items-center gap-1.5"
                >
                  <span>💡</span> Consejos para fotos perfectas
                </button>
              </div>

              <div className="mb-2 flex justify-between items-end">
                <span className={`text-[9px] font-bold uppercase tracking-wider ${orderDetails.fotos!.length < 10 ? 'text-error' : 'text-success'}`}>
                  {orderDetails.fotos!.length < 10 ? `Faltan ${10 - orderDetails.fotos!.length} fotos` : '¡Mínimo alcanzado!'}
                </span>
                <span className="text-[9px] font-bold text-gray-400">{orderDetails.fotos!.length} / 200</span>
              </div>
              <div className="h-1.5 w-full bg-gray-100 rounded-full overflow-hidden mb-4">
                <div className={`h-full transition-all duration-500 ${orderDetails.fotos!.length < 10 ? 'bg-orange-400' : 'bg-success'}`} style={{ width: `${Math.min(100, (orderDetails.fotos!.length / 200) * 100)}%` }}></div>
              </div>
            </div>

            <div onClick={() => fileInputRef.current?.click()} className="max-w-lg mx-auto border-3 border-dashed border-gray-200 rounded-2xl p-6 md:p-10 text-center hover:bg-white hover:border-primary transition-all bg-gray-50 cursor-pointer group shadow-sm">
              <span className="text-3xl md:text-4xl mb-3 block group-hover:scale-110 transition-transform">📸</span>
              <h3 className="text-base md:text-lg font-bold text-primary mb-1">Seleccioná o Arrastrá tus fotos</h3>
              <p className="text-gray-400 text-[10px] md:text-xs">JPG o PNG de alta resolución</p>
              <input type="file" multiple hidden ref={fileInputRef} onChange={handleFileUpload} accept="image/*" />
            </div>

            <div className="grid grid-cols-5 sm:grid-cols-6 md:grid-cols-10 lg:grid-cols-12 gap-1.5">
              {orderDetails.fotos?.map((f, i) => (
                <div key={i} className="relative aspect-square rounded-md overflow-hidden shadow-sm border group">
                  <img src={URL.createObjectURL(f)} className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                  <button onClick={() => removePhoto(i)} className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white transition-opacity text-xs">✕</button>
                </div>
              ))}
            </div>

            <p className="text-center text-[10px] text-gray-400 mt-6 italic">
              * Las imágenes son a modo ilustrativo. Los colores y texturas pueden variar ligeramente en el producto final.
            </p>
          </div>
        )}

        {step === 5 && (
          <div className="animate-fade-in grid md:grid-cols-3 gap-4 md:gap-6">
            <div className="md:col-span-2 space-y-3">
              <h2 className="text-xl md:text-2xl font-display font-bold text-primary">Datos de Entrega</h2>
              <div className="bg-white p-4 md:p-5 rounded-xl border border-gray-100 shadow-lg space-y-3">
                <div className="grid sm:grid-cols-2 gap-3">
                  <div className="space-y-0.5">
                    <label className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1">Nombre Completo</label>
                    <input type="text" className={inputClasses} placeholder="Juan Pérez" value={orderDetails.cliente?.nombre} onChange={e => setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, nombre: e.target.value } }))} />
                  </div>
                  <div className="space-y-0.5">
                    <label className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1">Email</label>
                    <input type="email" className={`${inputClasses} ${orderDetails.cliente?.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(orderDetails.cliente?.email) ? 'border-red-400 bg-red-50' : ''}`} placeholder="tu@email.com" value={orderDetails.cliente?.email} onChange={e => setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, email: e.target.value } }))} />
                    {orderDetails.cliente?.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(orderDetails.cliente?.email) && <span className="text-[9px] text-red-500 ml-1">Email inválido</span>}
                  </div>
                </div>
                <div className="grid sm:grid-cols-2 gap-3">
                  <div className="space-y-0.5">
                    <label className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1">Provincia</label>
                    <select className={inputClasses} value={orderDetails.cliente?.direccion.provincia} onChange={e => { setManualCityMode(false); setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, direccion: { ...p.cliente!.direccion, provincia: e.target.value, ciudad: '' } } })); }}>
                      <option value="">Seleccionar...</option>
                      {Object.keys(PROVINCIAS_MAPPING).map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </div>
                  <div className="space-y-0.5">
                    <label className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1">Ciudad</label>
                    {orderDetails.cliente?.direccion.provincia && CIUDADES_POR_PROVINCIA[orderDetails.cliente.direccion.provincia] && !manualCityMode ? (
                      <select
                        className={inputClasses}
                        value={CIUDADES_POR_PROVINCIA[orderDetails.cliente.direccion.provincia].includes(orderDetails.cliente.direccion.ciudad) ? orderDetails.cliente.direccion.ciudad : ''}
                        onChange={e => {
                          const val = e.target.value;
                          if (val === 'Otra') {
                            setManualCityMode(true);
                            setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, direccion: { ...p.cliente!.direccion, ciudad: '' } } }));
                          } else {
                            setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, direccion: { ...p.cliente!.direccion, ciudad: val } } }));
                          }
                        }}
                      >
                        <option value="">Seleccionar...</option>
                        {CIUDADES_POR_PROVINCIA[orderDetails.cliente.direccion.provincia].map(c => <option key={c} value={c}>{c}</option>)}
                        <option value="Otra">Otra...</option>
                      </select>
                    ) : (
                      <div className="relative">
                        <input
                          type="text"
                          className={inputClasses}
                          placeholder={orderDetails.cliente?.direccion.provincia ? "Escribí tu ciudad" : "Primero seleccioná provincia"}
                          disabled={!orderDetails.cliente?.direccion.provincia}
                          value={orderDetails.cliente?.direccion.ciudad}
                          onChange={e => setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, direccion: { ...p.cliente!.direccion, ciudad: e.target.value } } }))}
                        />
                        {orderDetails.cliente?.direccion.provincia && CIUDADES_POR_PROVINCIA[orderDetails.cliente.direccion.provincia] && (
                          <button
                            type="button"
                            onClick={() => {
                              setManualCityMode(false);
                              setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, direccion: { ...p.cliente!.direccion, ciudad: '' } } }));
                            }}
                            className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-primary font-bold hover:underline"
                          >
                            Ver lista
                          </button>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                <div className="grid sm:grid-cols-3 gap-3">
                  <div className="sm:col-span-2 space-y-0.5">
                    <label className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1">Dirección Completa</label>
                    <input type="text" className={inputClasses} placeholder="Av. Pellegrini 1234" value={orderDetails.cliente?.direccion.calle} onChange={e => setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, direccion: { ...p.cliente!.direccion, calle: e.target.value } } }))} />
                  </div>
                  <div className="space-y-0.5">
                    <label className="text-[9px] font-bold text-gray-500 uppercase tracking-widest ml-1">CP</label>
                    <input type="text" className={`${inputClasses} ${orderDetails.cliente?.direccion.cp && !/^\d{4}$/.test(orderDetails.cliente?.direccion.cp) ? 'border-red-400 bg-red-50' : ''}`} placeholder="2000" maxLength={4} value={orderDetails.cliente?.direccion.cp} onChange={e => setOrderDetails(p => ({ ...p, cliente: { ...p.cliente!, direccion: { ...p.cliente!.direccion, cp: e.target.value.replace(/\D/g, '').slice(0, 4) } } }))} />
                    {orderDetails.cliente?.direccion.cp && !/^\d{4}$/.test(orderDetails.cliente?.direccion.cp) && <span className="text-[9px] text-red-500 ml-1">4 dígitos</span>}
                  </div>
                </div>
              </div>
            </div>

            <div className="md:col-span-1">
              <div className="bg-white p-4 md:p-5 rounded-xl border border-gray-100 shadow-lg h-fit md:sticky md:top-24 space-y-3">
                <h3 className="font-display font-bold text-primary text-base">Tu Pedido</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400 text-xs">Modelo</span>
                    <span className="font-bold text-primary text-xs text-right">{selectedProduct?.nombre}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400 text-xs">Páginas</span>
                    <span className="font-bold text-primary text-xs">{orderDetails.paginasTotal}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400 text-xs">Envío</span>
                    <span className="font-bold text-primary text-xs">${priceBreakdown.shipping.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between border-t pt-2">
                    <span className="text-gray-500 font-bold uppercase text-[10px]">Total</span>
                    <span className="text-lg font-display font-bold text-primary">${priceBreakdown.total.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {step === 6 && (
          <div className="max-w-lg mx-auto animate-fade-in text-primary">
            <h2 className="text-xl md:text-2xl font-display font-bold text-center mb-4 md:mb-6">Finalizar Compra</h2>
            <div className="bg-white p-4 md:p-6 rounded-xl shadow-xl border border-gray-100 space-y-4">
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setOrderDetails(p => ({ ...p, metodoPago: 'mercadopago' }))}
                  className={`p-4 md:p-5 rounded-xl border-2 transition-all flex flex-col items-center gap-2 ${orderDetails.metodoPago === 'mercadopago' ? 'border-[#009EE3] bg-[#009EE3]/5' : 'border-gray-200 bg-white'}`}
                >
                  <svg viewBox="0 0 50 50" className="w-10 h-10">
                    <circle cx="25" cy="25" r="24" fill="#009EE3" />
                    <path d="M25 12c-7.2 0-13 5.8-13 13s5.8 13 13 13 13-5.8 13-13-5.8-13-13-13zm-1.5 19.5h-3v-9h3v9zm6 0h-3v-9h3v9zm-9-10.5c-.8 0-1.5-.7-1.5-1.5s.7-1.5 1.5-1.5 1.5.7 1.5 1.5-.7 1.5-1.5 1.5zm6 0c-.8 0-1.5-.7-1.5-1.5s.7-1.5 1.5-1.5 1.5.7 1.5 1.5-.7 1.5-1.5 1.5zm6 0c-.8 0-1.5-.7-1.5-1.5s.7-1.5 1.5-1.5 1.5.7 1.5 1.5-.7 1.5-1.5 1.5z" fill="white" />
                    <text x="25" y="30" textAnchor="middle" fill="white" fontSize="8" fontWeight="bold">MP</text>
                  </svg>
                  <span className="font-bold text-xs text-[#009EE3]">MercadoPago</span>
                </button>
                <button
                  onClick={() => setOrderDetails(p => ({ ...p, metodoPago: 'transferencia' }))}
                  className={`p-4 md:p-5 rounded-xl border-2 transition-all flex flex-col items-center gap-2 relative ${orderDetails.metodoPago === 'transferencia' ? 'border-green-500 bg-green-50' : 'border-gray-200 bg-white'}`}
                >
                  <span className="absolute -top-2 -right-2 bg-green-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-full shadow-md">15% OFF</span>
                  <svg viewBox="0 0 24 24" className="w-10 h-10" fill="none" stroke="currentColor" strokeWidth="1.5">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" className="text-primary" />
                  </svg>
                  <span className="font-bold text-xs text-primary">Transferencia</span>
                </button>
              </div>

              {orderDetails.metodoPago === 'transferencia' && (
                <div className="bg-green-50 p-3 md:p-4 rounded-xl border border-green-200 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="bg-green-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full">15% OFF</span>
                    <p className="font-bold text-green-700 text-xs">¡Ahorrás ${priceBreakdown.discount.toLocaleString()}!</p>
                  </div>
                  <p className="font-bold text-primary text-xs">Datos de la Cuenta:</p>
                  <div className="space-y-0.5">
                    <p className="text-[11px] text-primary font-medium"><strong>CBU:</strong> 0720000088000012345678</p>
                    <p className="text-[11px] text-primary font-medium"><strong>Alias:</strong> fotolibros.arg</p>
                  </div>
                  <p className="text-[9px] text-accent font-bold italic">"Se iniciará la producción tras validar el comprobante."</p>
                </div>
              )}

              <div className="pt-3 border-t">
                <div className="flex justify-between items-center">
                  <span className="text-primary/60 font-bold uppercase tracking-widest text-[10px]">Total a abonar</span>
                  <div className="text-right">
                    {priceBreakdown.discount > 0 ? (
                      <>
                        <span className="text-gray-400 line-through text-sm mr-2">${priceBreakdown.total.toLocaleString()}</span>
                        <span className="text-2xl md:text-3xl font-display font-bold text-green-600">${priceBreakdown.finalTotal.toLocaleString()}</span>
                      </>
                    ) : (
                      <span className="text-2xl md:text-3xl font-display font-bold text-primary">${priceBreakdown.total.toLocaleString()}</span>
                    )}
                  </div>
                </div>
              </div>

              {isSubmitting && (
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-500">{pedidoEstado}</span>
                    <span className="font-bold text-primary">{pedidoProgreso}%</span>
                  </div>
                  <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-accent transition-all duration-500"
                      style={{ width: `${pedidoProgreso}%` }}
                    />
                  </div>
                </div>
              )}

              {pedidoId && !isSubmitting && pedidoProgreso === 100 && (
                <div className="bg-green-50 border border-green-200 p-4 rounded-xl text-center">
                  <span className="text-2xl">🎉</span>
                  <p className="font-bold text-green-700 mt-2">¡Pedido completado!</p>
                  <p className="text-xs text-green-600 mt-1">ID: {pedidoId}</p>
                  <p className="text-xs text-green-600">Tu fotolibro está en producción</p>
                </div>
              )}

              <button
                onClick={enviarPedido}
                disabled={isSubmitting || !!(pedidoId && pedidoProgreso === 100)}
                className="w-full py-4 bg-accent text-white font-bold rounded-xl shadow-xl hover:scale-[1.01] transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSubmitting ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    Procesando...
                  </span>
                ) : pedidoId && pedidoProgreso === 100 ? (
                  '✓ Pedido Confirmado'
                ) : orderDetails.metodoPago === 'mercadopago' ? (
                  'Pagar con MercadoPago'
                ) : (
                  'Confirmar Pedido'
                )}
              </button>
            </div>
          </div>
        )}
      </main>

      {step < 6 && (
        <footer className="bg-white border-t p-2 md:p-3 flex items-center justify-between sticky bottom-0 z-50 shadow-2xl">
          <button onClick={prevStep} disabled={step === 1} className="px-3 md:px-6 py-1.5 md:py-2 font-bold text-gray-400 disabled:opacity-0 text-xs md:text-sm">← Atrás</button>
          <div className="text-center">
            <div className="text-primary font-bold text-sm md:text-base leading-none">${priceBreakdown.total.toLocaleString()}</div>
          </div>
          <button
            onClick={nextStep}
            disabled={(step === 1 && !orderDetails.productoCodigo) || (step === 4 && orderDetails.fotos!.length < 10) || (step === 5 && (!orderDetails.cliente?.nombre || !orderDetails.cliente?.direccion.provincia || !orderDetails.cliente?.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(orderDetails.cliente?.email)))}
            className="px-4 md:px-8 py-1.5 md:py-2 bg-primary text-white font-bold rounded-lg shadow-lg transition-all disabled:opacity-30 text-xs md:text-sm"
          >
            {step === 5 ? 'Ir a Pago →' : 'Siguiente →'}
          </button>
        </footer>
      )}

      {/* Modal de Consejos */}
      {isTipsModalOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-primary/40 backdrop-blur-sm animate-fade-in">
          <div className="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden animate-slide-up">
            <div className="bg-primary p-6 text-white flex justify-between items-center">
              <h3 className="font-display font-bold text-xl">Consejos para tu Fotolibro</h3>
              <button onClick={() => setIsTipsModalOpen(false)} className="text-white/60 hover:text-white">✕</button>
            </div>
            <div className="p-6 space-y-6 max-h-[70vh] overflow-y-auto">
              <div>
                <h4 className="font-bold text-primary flex items-center gap-2 mb-2">
                  <span className="text-xl">📸</span> Calidad y Resolución
                </h4>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Para que tus fotos se vean nítidas, usá archivos originales de tu cámara o celular. Evitá capturas de pantalla o fotos de WhatsApp, ya que pierden mucha resolución al imprimirse.
                </p>
              </div>

              <div>
                <h4 className="font-bold text-primary flex items-center gap-2 mb-2">
                  <span className="text-xl">🏺</span> Recuerdos en Papel
                </h4>
                <p className="text-sm text-gray-500 leading-relaxed">
                  ¿Tenés fotos antiguas? Escanealas a 300 DPI o más. Así capturarás cada detalle y se verán increíbles incluso si decidís agrandarlas en tu fotolibro.
                </p>
              </div>

              <div>
                <h4 className="font-bold text-primary flex items-center gap-2 mb-2">
                  <span className="text-xl">✨</span> El Secreto del Diseño
                </h4>
                <p className="text-sm text-gray-500 leading-relaxed">
                  Menos es más. Recomendamos colocar entre 2 y 4 fotos por página. Esto le da "aire" al diseño y hace que cada momento especial sea el protagonista.
                </p>
              </div>

              <div className="bg-blue-50 p-4 rounded-2xl border border-blue-100 italic">
                <p className="text-xs text-blue-800">
                  "Nuestras impresiones están diseñadas para durar décadas sin perder color. ¡Estás creando un objeto que pasará de generación en generación!"
                </p>
              </div>
            </div>
            <div className="p-4 bg-gray-50 border-t flex justify-end">
              <button
                onClick={() => setIsTipsModalOpen(false)}
                className="bg-primary text-white font-bold px-6 py-2 rounded-xl"
              >
                Entendido
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderWizard;
