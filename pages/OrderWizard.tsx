
import React, { useState, useEffect, useRef, useMemo } from 'react';
import { PRODUCTS, PACKAGES, PROVINCIAS_MAPPING, SHIPPING_COSTS } from '../constants';
import { OrderDetails, Product, OrderStatus } from '../types';

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
    estado: OrderStatus.PENDIENTE_PAGO
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Persistence
  useEffect(() => {
    const saved = localStorage.getItem('fl_draft');
    if (saved) {
      const parsed = JSON.parse(saved);
      setOrderDetails(prev => ({ ...prev, ...parsed, fotos: [] }));
    }
  }, []);

  useEffect(() => {
    const { fotos, ...toSave } = orderDetails;
    localStorage.setItem('fl_draft', JSON.stringify(toSave));
  }, [orderDetails]);

  const selectedProduct = PRODUCTS.find(p => p.codigo === orderDetails.productoCodigo);
  
  const calculateTotal = () => {
    if (!selectedProduct) return 0;
    const base = selectedProduct.precioBase;
    const extras = Math.max(0, (orderDetails.paginasTotal || 0) - selectedProduct.paginasBase);
    const paginasExtraCost = extras * selectedProduct.precioPaginaExtra;
    
    const prov = orderDetails.cliente?.direccion?.provincia;
    const zona = prov ? PROVINCIAS_MAPPING[prov] : null;
    const shipping = zona ? SHIPPING_COSTS[zona] : 0;
    
    return base + paginasExtraCost + shipping;
  };

  const filteredProducts = useMemo(() => {
    return PRODUCTS.filter(p => {
      const matchTipo = filterTipo === 'all' || p.tipo === filterTipo;
      const matchTapa = filterTapa === 'all' || p.tapa === filterTapa;
      return matchTipo && matchTapa;
    });
  }, [filterTipo, filterTapa]);

  const nextStep = () => setStep(s => Math.min(s + 1, 5));
  const prevStep = () => setStep(s => Math.max(s - 1, 1));

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setOrderDetails(prev => ({
        ...prev,
        fotos: [...(prev.fotos || []), ...newFiles].slice(0, 200)
      }));
    }
  };

  const removePhoto = (index: number) => {
    setOrderDetails(prev => ({
      ...prev,
      fotos: (prev.fotos || []).filter((_, i) => i !== index)
    }));
  };

  // Helper to format cover display name
  const formatTapa = (tapa: string) => {
    if (tapa === 'Simil Cuero' || tapa === 'all') return tapa;
    return `Tapa ${tapa}`;
  };

  return (
    <div className="bg-cream min-h-screen flex flex-col">
      {/* Wizard Header */}
      <header className="bg-white border-b px-4 py-6 shadow-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <button onClick={onBack} className="text-gray-400 hover:text-primary flex items-center gap-1">
              ← Volver
            </button>
            <div className="font-display font-bold text-primary tracking-widest uppercase">Fotolibros Argentina</div>
            <div className="text-xs text-gray-400 font-bold">PASO {step} / 5</div>
          </div>
          
          {/* Progress Bar */}
          <div className="flex items-center justify-between relative">
            <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-100 -translate-y-1/2 -z-10"></div>
            <div className="absolute top-1/2 left-0 h-1 bg-primary -translate-y-1/2 -z-10 transition-all duration-500" style={{ width: `${((step - 1) / 4) * 100}%` }}></div>
            {[1, 2, 3, 4, 5].map((s) => (
              <div 
                key={s} 
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300 ${
                  step === s ? 'step-active scale-110 shadow-lg' : step > s ? 'step-done' : 'step-pending'
                }`}
              >
                {step > s ? '✓' : s}
              </div>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto w-full p-4 py-10 flex-grow">
        
        {/* Step 1: Producto */}
        {step === 1 && (
          <div className="animate-fade-in">
            <div className="max-w-4xl mx-auto text-center mb-10">
              <h2 className="text-3xl font-display font-bold text-primary mb-3">Elegí tu fotolibro</h2>
              <p className="text-gray-500">Seleccioná entre nuestra variedad de tamaños reales y terminaciones de calidad.</p>
            </div>
            
            <div className="mb-14">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6 text-center">Paquetes en Oferta</h3>
              <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                {PACKAGES.map((pkg) => (
                  <button 
                    key={pkg.id}
                    onClick={() => {
                      setOrderDetails(prev => ({ ...prev, productoCodigo: pkg.productoCodigo, paginasTotal: pkg.paginas }));
                      nextStep();
                    }}
                    className={`text-left p-6 rounded-3xl border-2 transition-all hover:shadow-xl relative overflow-hidden group ${
                      orderDetails.productoCodigo === pkg.productoCodigo && orderDetails.paginasTotal === pkg.paginas
                      ? 'border-primary bg-primary/5' : 'border-gray-100 bg-white'
                    }`}
                  >
                    {pkg.badge && (
                      <div className="absolute top-0 right-0 bg-secondary text-white text-[10px] font-bold px-3 py-1 rounded-bl-xl">
                        {pkg.badge}
                      </div>
                    )}
                    <div className="text-lg font-bold text-primary mb-1">{pkg.nombre}</div>
                    <div className="text-xs text-gray-400 mb-4">{pkg.descripcion}</div>
                    <div className="flex items-baseline gap-2">
                      <span className="text-2xl font-bold text-primary">${pkg.precio.toLocaleString()}</span>
                      <span className="text-xs text-gray-400">/ {pkg.paginas} págs</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Filtros */}
            <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm mb-10 flex flex-wrap items-center justify-center gap-6">
               <div className="flex flex-col gap-2">
                 <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">Formato</label>
                 <div className="flex bg-gray-50 p-1 rounded-xl">
                    {['all', 'Apaisado', 'Cuadrado', 'Vertical', 'Mini'].map(t => (
                      <button 
                        key={t}
                        onClick={() => setFilterTipo(t)}
                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${filterTipo === t ? 'bg-white shadow-sm text-primary' : 'text-gray-500'}`}
                      >
                        {t === 'all' ? 'Todos' : t}
                      </button>
                    ))}
                 </div>
               </div>
               <div className="flex flex-col gap-2">
                 <label className="text-[10px] font-bold text-gray-400 uppercase tracking-widest ml-1">Tapa</label>
                 <div className="flex bg-gray-50 p-1 rounded-xl">
                    {['all', 'Blanda', 'Dura', 'Simil Cuero'].map(t => (
                      <button 
                        key={t}
                        onClick={() => setFilterTapa(t)}
                        className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${filterTapa === t ? 'bg-white shadow-sm text-primary' : 'text-gray-500'}`}
                      >
                        {t === 'all' ? 'Todas' : formatTapa(t)}
                      </button>
                    ))}
                 </div>
               </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredProducts.map((prod) => (
                <div 
                  key={prod.codigo}
                  onClick={() => setOrderDetails(prev => ({ ...prev, productoCodigo: prod.codigo, paginasTotal: prod.paginasBase }))}
                  className={`cursor-pointer group bg-white p-4 rounded-3xl border-2 transition-all flex flex-col hover:shadow-md ${
                    orderDetails.productoCodigo === prod.codigo ? 'border-primary' : 'border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <div className="relative mb-4">
                    <img src={prod.imagen} alt={prod.nombre} className="w-full aspect-[4/3] object-cover rounded-2xl" />
                    {prod.badge && (
                      <div className={`absolute top-2 left-2 px-3 py-1 rounded-lg text-[10px] font-bold text-white shadow-sm ${
                        prod.badge === 'POPULAR' ? 'bg-secondary' : prod.badge === 'PREMIUM' ? 'bg-primary' : 'bg-accent'
                      }`}>
                        {prod.badge}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col flex-grow">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-[10px] font-bold text-accent uppercase tracking-wider">{prod.tipo} • {formatTapa(prod.tapa)}</span>
                      <span className="text-[10px] font-medium text-gray-400">{prod.tamanio}</span>
                    </div>
                    <h4 className="font-bold text-primary mb-2 text-lg">{prod.nombre}</h4>
                    <p className="text-xs text-gray-400 mb-4 line-clamp-2 leading-relaxed">{prod.descripcion}</p>
                    <div className="mt-auto flex justify-between items-center">
                      <div className="flex flex-col">
                        <span className="text-sm text-gray-400 leading-none">Desde</span>
                        <span className="text-xl font-bold text-primary">${prod.precioBase.toLocaleString()}</span>
                      </div>
                      <button 
                        onClick={(e) => { e.stopPropagation(); setOrderDetails(prev => ({ ...prev, productoCodigo: prod.codigo, paginasTotal: prod.paginasBase })); nextStep(); }}
                        className="bg-primary/5 text-primary group-hover:bg-primary group-hover:text-white px-4 py-2 rounded-xl text-sm font-bold transition-all"
                      >
                        Elegir →
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            {filteredProducts.length === 0 && (
              <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-gray-200">
                <span className="text-4xl mb-4 block">🔍</span>
                <p className="text-gray-400 font-medium">No encontramos productos con esos filtros.</p>
                <button onClick={() => { setFilterTipo('all'); setFilterTapa('all'); }} className="text-primary font-bold underline mt-2">Limpiar filtros</button>
              </div>
            )}
          </div>
        )}

        {/* Step 2: Páginas */}
        {step === 2 && selectedProduct && (
          <div className="animate-fade-in max-w-xl mx-auto">
             <div className="text-center mb-10">
               <h2 className="text-3xl font-display font-bold text-primary mb-2">Configurá tus páginas</h2>
               <p className="text-gray-500">Mínimo {selectedProduct.paginasBase} - Máximo {selectedProduct.paginasMax} páginas.</p>
             </div>

             <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 mb-8">
                <div className="flex items-center gap-5 mb-8">
                  <div className="w-24 h-24 rounded-2xl overflow-hidden shadow-sm">
                    <img src={selectedProduct.imagen} className="w-full h-full object-cover" />
                  </div>
                  <div>
                    <h3 className="font-bold text-primary text-xl">{selectedProduct.nombre}</h3>
                    <div className="flex flex-wrap gap-2 mt-1">
                      <span className="text-[10px] font-bold bg-cream px-2 py-1 rounded text-primary">{selectedProduct.tipo}</span>
                      <span className="text-[10px] font-bold bg-cream px-2 py-1 rounded text-primary">{formatTapa(selectedProduct.tapa)}</span>
                      <span className="text-[10px] font-bold bg-cream px-2 py-1 rounded text-gray-500">{selectedProduct.tamanio}</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center justify-between mb-8 bg-cream p-5 rounded-2xl">
                  <button 
                    onClick={() => setOrderDetails(prev => ({ ...prev, paginasTotal: Math.max(selectedProduct.paginasBase, (prev.paginasTotal || 0) - 2) }))}
                    className="w-14 h-14 rounded-xl bg-white shadow-sm flex items-center justify-center text-3xl hover:bg-primary hover:text-white transition-all active:scale-95"
                  >-</button>
                  <div className="text-center">
                    <div className="text-5xl font-display font-bold text-primary">{orderDetails.paginasTotal}</div>
                    <div className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mt-1">PÁGINAS TOTALES</div>
                  </div>
                  <button 
                    onClick={() => setOrderDetails(prev => ({ ...prev, paginasTotal: Math.min(selectedProduct.paginasMax, (prev.paginasTotal || 0) + 2) }))}
                    className="w-14 h-14 rounded-xl bg-white shadow-sm flex items-center justify-center text-3xl hover:bg-primary hover:text-white transition-all active:scale-95"
                  >+</button>
                </div>

                <div className="space-y-4 border-t pt-6">
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>Producto Base ({selectedProduct.paginasBase} págs)</span>
                    <span className="font-medium text-primary">${selectedProduct.precioBase.toLocaleString()}</span>
                  </div>
                  {orderDetails.paginasTotal! > selectedProduct.paginasBase && (
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>Páginas Extra ({(orderDetails.paginasTotal! - selectedProduct.paginasBase)})</span>
                      <span className="font-medium text-primary">+ ${((orderDetails.paginasTotal! - selectedProduct.paginasBase) * selectedProduct.precioPaginaExtra).toLocaleString()}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-2xl font-display font-bold text-primary border-t pt-4">
                    <span>Subtotal</span>
                    <span>${calculateTotal().toLocaleString()}</span>
                  </div>
                </div>
             </div>

             <div className="bg-blue-50 p-5 rounded-2xl flex gap-4 text-sm text-blue-800 mb-8 border border-blue-100">
               <span className="text-xl">💡</span>
               <p className="leading-relaxed">Recomendamos un promedio de <b>2 a 3 fotos por página</b>. Con {orderDetails.paginasTotal} páginas podés incluir hasta unas {orderDetails.paginasTotal! * 3} fotos cómodamente.</p>
             </div>

             <button onClick={nextStep} className="w-full py-5 bg-primary text-white font-bold rounded-2xl hover:bg-opacity-95 shadow-xl transition-all">Continuar al diseño →</button>
          </div>
        )}

        {/* Step 3: Fotos */}
        {step === 3 && (
          <div className="animate-fade-in">
             <div className="max-w-4xl mx-auto text-center mb-10">
               <h2 className="text-3xl font-display font-bold text-primary mb-2">Subí tus fotos</h2>
               <p className="text-gray-500">Seleccioná entre 10 y 200 fotos para tu fotolibro.</p>
             </div>

             <div 
               onClick={() => fileInputRef.current?.click()}
               className="border-4 border-dashed border-gray-200 rounded-3xl p-16 text-center hover:border-primary hover:bg-white/50 transition-all cursor-pointer bg-white group shadow-sm"
             >
               <div className="text-6xl mb-6 group-hover:scale-110 transition-transform duration-500">☁️</div>
               <h3 className="text-2xl font-bold text-primary mb-2">Arrastrá tus fotos aquí</h3>
               <p className="text-gray-400">o hacé click para explorar archivos</p>
               <div className="mt-8 flex justify-center gap-4 text-[10px] font-bold uppercase tracking-widest text-gray-300">
                 <span>JPG • PNG</span>
                 <span>Máx 10MB</span>
               </div>
               <input 
                 type="file" 
                 multiple 
                 hidden 
                 ref={fileInputRef} 
                 onChange={handleFileUpload} 
                 accept="image/*"
               />
             </div>

             {orderDetails.fotos && orderDetails.fotos.length > 0 && (
               <div className="mt-12">
                  <div className="flex justify-between items-center mb-8 bg-white p-4 rounded-2xl border border-gray-100">
                    <div className="flex items-center gap-3">
                      <span className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold">{orderDetails.fotos?.length}</span>
                      <h3 className="font-bold text-primary">Fotos cargadas</h3>
                    </div>
                    <button onClick={() => setOrderDetails(prev => ({ ...prev, fotos: [] }))} className="text-xs font-bold text-error bg-red-50 hover:bg-red-100 px-4 py-2 rounded-xl transition-colors">Limpiar Galería</button>
                  </div>

                  <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4">
                    {orderDetails.fotos?.map((file, idx) => (
                      <div key={idx} className="relative group aspect-square rounded-2xl overflow-hidden shadow-sm border border-gray-100">
                        <img src={URL.createObjectURL(file)} className="w-full h-full object-cover" />
                        <button 
                          onClick={() => removePhoto(idx)}
                          className="absolute top-2 right-2 bg-white/90 backdrop-blur rounded-lg w-7 h-7 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-all hover:bg-error hover:text-white"
                        >✕</button>
                      </div>
                    ))}
                  </div>
               </div>
             )}

             <div className="mt-16 sticky bottom-6 z-10 flex justify-center">
                <button 
                  disabled={(orderDetails.fotos?.length || 0) < 10}
                  onClick={nextStep} 
                  className={`w-full max-w-md py-5 font-bold rounded-2xl shadow-2xl transition-all ${
                    (orderDetails.fotos?.length || 0) >= 10 
                    ? 'bg-primary text-white hover:scale-105' 
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {(orderDetails.fotos?.length || 0) < 10 ? `Faltan ${(10 - (orderDetails.fotos?.length || 0))} fotos para continuar` : 'Confirmar Selección →'}
                </button>
             </div>
          </div>
        )}

        {/* Step 4: Envío */}
        {step === 4 && (
          <div className="animate-fade-in grid md:grid-cols-3 gap-10">
            <div className="md:col-span-2">
              <h2 className="text-3xl font-display font-bold text-primary mb-2">Datos de Entrega</h2>
              <p className="text-gray-500 mb-10">Realizamos envíos a todo el país vía Correo Argentino.</p>

              <form className="space-y-8 bg-white p-10 rounded-3xl border border-gray-100 shadow-sm text-primary">
                <div className="grid sm:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Nombre completo</label>
                    <input 
                      type="text" 
                      placeholder="Ej: Juan Pérez"
                      className="w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-2xl focus:ring-4 focus:ring-primary/5 focus:border-primary outline-none transition-all placeholder:text-gray-300"
                      value={orderDetails.cliente?.nombre}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, nombre: e.target.value } }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Email</label>
                    <input 
                      type="email" 
                      placeholder="tu@email.com"
                      className="w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-2xl focus:ring-4 focus:ring-primary/5 focus:border-primary outline-none transition-all placeholder:text-gray-300"
                      value={orderDetails.cliente?.email}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, email: e.target.value } }))}
                    />
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Provincia</label>
                    <select 
                      className="w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-2xl focus:ring-4 focus:ring-primary/5 focus:border-primary outline-none cursor-pointer transition-all"
                      value={orderDetails.cliente?.direccion.provincia}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, direccion: { ...prev.cliente!.direccion, provincia: e.target.value } } }))}
                    >
                      <option value="">Seleccionar Provincia...</option>
                      {Object.keys(PROVINCIAS_MAPPING).map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Localidad / Ciudad</label>
                    <input 
                      type="text" 
                      className="w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-2xl focus:ring-4 focus:ring-primary/5 focus:border-primary outline-none transition-all"
                      value={orderDetails.cliente?.direccion.ciudad}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, direccion: { ...prev.cliente!.direccion, ciudad: e.target.value } } }))}
                    />
                  </div>
                </div>

                <div className="grid sm:grid-cols-3 gap-6">
                  <div className="sm:col-span-2 space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">Calle y Altura</label>
                    <input 
                      type="text" 
                      placeholder="Ej: Av. Rivadavia 1234"
                      className="w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-2xl focus:ring-4 focus:ring-primary/5 focus:border-primary outline-none transition-all placeholder:text-gray-300"
                      value={orderDetails.cliente?.direccion.calle}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, direccion: { ...prev.cliente!.direccion, calle: e.target.value } } }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-xs font-bold text-gray-500 uppercase tracking-widest ml-1">CP</label>
                    <input 
                      type="text" 
                      className="w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-2xl focus:ring-4 focus:ring-primary/5 focus:border-primary outline-none transition-all"
                      value={orderDetails.cliente?.direccion.cp}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, direccion: { ...prev.cliente!.direccion, cp: e.target.value } } }))}
                    />
                  </div>
                </div>
              </form>
            </div>

            <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-xl h-fit sticky top-32">
              <h3 className="font-display font-bold text-primary text-xl mb-6">Resumen del Pedido</h3>
              <div className="space-y-4 mb-8">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400 font-medium">Producto</span>
                  <span className="text-primary font-bold text-right ml-4">{selectedProduct?.nombre}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400 font-medium">Terminación</span>
                  <span className="text-primary font-bold">{selectedProduct ? formatTapa(selectedProduct.tapa) : ''}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400 font-medium">Páginas</span>
                  <span className="text-primary font-bold">{orderDetails.paginasTotal}</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-400 font-medium">Envío</span>
                  <span className="text-primary font-bold">
                    {orderDetails.cliente?.direccion.provincia ? `$${SHIPPING_COSTS[PROVINCIAS_MAPPING[orderDetails.cliente.direccion.provincia]].toLocaleString()}` : 'Pendiente'}
                  </span>
                </div>
                <div className="border-t border-dashed pt-4 flex justify-between items-baseline">
                  <span className="font-bold text-primary">Total</span>
                  <span className="text-3xl font-display font-bold text-primary">${calculateTotal().toLocaleString()}</span>
                </div>
              </div>
              <button 
                disabled={!orderDetails.cliente?.nombre || !orderDetails.cliente?.direccion.provincia}
                onClick={nextStep} 
                className="w-full py-5 bg-primary text-white font-bold rounded-2xl shadow-lg hover:bg-opacity-95 disabled:opacity-50 transition-all active:scale-[0.98]"
              >
                Pagar Ahora →
              </button>
            </div>
          </div>
        )}

        {/* Step 5: Pago */}
        {step === 5 && (
          <div className="animate-fade-in max-w-2xl mx-auto">
             <div className="text-center mb-10">
               <h2 className="text-3xl font-display font-bold text-primary mb-2">Finalizar Compra</h2>
               <p className="text-gray-500">Seleccioná tu método de pago para procesar el pedido.</p>
             </div>

             <div className="bg-white p-10 rounded-3xl border border-gray-100 shadow-xl space-y-8">
                <div className="grid grid-cols-2 gap-6">
                  <button 
                    onClick={() => setOrderDetails(prev => ({ ...prev, metodoPago: 'mercadopago' }))}
                    className={`p-8 rounded-3xl border-2 transition-all flex flex-col items-center gap-3 hover:shadow-md ${
                      orderDetails.metodoPago === 'mercadopago' ? 'border-primary bg-primary/5' : 'border-gray-50 bg-gray-50'
                    }`}
                  >
                    <span className="text-4xl">💳</span>
                    <span className="font-bold text-primary">MercadoPago</span>
                    <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Tarjeta / Dinero en cuenta</span>
                  </button>
                  <button 
                    onClick={() => setOrderDetails(prev => ({ ...prev, metodoPago: 'transferencia' }))}
                    className={`p-8 rounded-3xl border-2 transition-all flex flex-col items-center gap-3 hover:shadow-md ${
                      orderDetails.metodoPago === 'transferencia' ? 'border-primary bg-primary/5' : 'border-gray-50 bg-gray-50'
                    }`}
                  >
                    <span className="text-4xl">🏦</span>
                    <span className="font-bold text-primary">Transferencia</span>
                    <span className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Ahorrá tiempo de proceso</span>
                  </button>
                </div>

                {orderDetails.metodoPago === 'transferencia' && (
                  <div className="bg-cream p-8 rounded-3xl border border-orange-100 space-y-6 animate-fade-in">
                    <h4 className="font-display font-bold text-primary text-lg">Cuentas Bancarias</h4>
                    <div className="grid gap-4 text-primary">
                      <div className="bg-white p-5 rounded-2xl flex justify-between items-center shadow-sm border border-orange-50">
                        <div className="space-y-1">
                          <p className="text-[10px] font-bold text-gray-400 uppercase">CBU / Alias</p>
                          <p className="font-bold select-all">fotolibros.arg</p>
                        </div>
                        <button className="text-[10px] font-bold text-accent border border-accent/30 px-3 py-1 rounded-lg uppercase">Copiar</button>
                      </div>
                      <div className="bg-white p-5 rounded-2xl flex justify-between items-center shadow-sm border border-orange-50">
                        <div className="space-y-1">
                          <p className="text-[10px] font-bold text-gray-400 uppercase">CUIT Titular</p>
                          <p className="font-bold">30-71717171-8</p>
                        </div>
                      </div>
                    </div>
                    <div className="p-4 bg-orange-50 rounded-2xl text-xs text-orange-800 leading-relaxed italic">
                      "Por favor, una vez realizada la transferencia, envianos el comprobante por WhatsApp o Email indicando el número de referencia."
                    </div>
                  </div>
                )}

                <div className="pt-8 border-t border-gray-100">
                  <div className="flex justify-between items-center mb-10">
                    <div className="text-sm text-gray-400 font-bold uppercase tracking-widest">A PAGAR</div>
                    <div className="text-4xl font-display font-bold text-primary">${calculateTotal().toLocaleString()}</div>
                  </div>
                  
                  <button 
                    className="w-full py-6 bg-accent text-white font-bold rounded-2xl shadow-2xl hover:bg-orange-600 transition-all hover:scale-[1.02] active:scale-100"
                    onClick={() => alert('¡Muchas gracias! Esta es una demostración. Tu pedido sería procesado ahora.')}
                  >
                    {orderDetails.metodoPago === 'mercadopago' ? 'Pagar con MercadoPago' : 'Confirmar Pedido'}
                  </button>
                  
                  <p className="mt-6 text-center text-[10px] text-gray-400 uppercase tracking-widest font-bold">
                    Transacción Protegida • SSL Secured
                  </p>
                </div>
             </div>
          </div>
        )}

      </main>

      {/* Navigation Footer */}
      {step < 5 && (
        <footer className="bg-white border-t p-5 flex items-center justify-between sticky bottom-0 z-50 shadow-2xl">
          <button 
            onClick={prevStep}
            disabled={step === 1}
            className={`px-8 py-3 font-bold rounded-xl transition-colors ${step === 1 ? 'text-gray-200 cursor-not-allowed' : 'text-gray-400 hover:text-primary'}`}
          >
            ← Atrás
          </button>
          
          {/* Summary Preview */}
          <div className="flex flex-col items-center">
            <div className="text-[10px] text-gray-400 uppercase font-bold tracking-widest">SUBTOTAL</div>
            <div className="text-primary font-bold text-xl">${calculateTotal().toLocaleString()}</div>
          </div>

          <div className="flex gap-4">
            {step < 5 && step !== 4 && step !== 3 && (
              <button 
                onClick={nextStep}
                disabled={!orderDetails.productoCodigo}
                className={`px-10 py-3 bg-primary text-white font-bold rounded-xl shadow-lg transition-all ${!orderDetails.productoCodigo ? 'opacity-50 cursor-not-allowed' : 'hover:bg-opacity-95'}`}
              >
                Siguiente →
              </button>
            )}
          </div>
        </footer>
      )}
    </div>
  );
};

export default OrderWizard;
