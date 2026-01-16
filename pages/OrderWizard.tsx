
import React, { useState, useEffect, useRef } from 'react';
import { PRODUCTS, PACKAGES, PROVINCIAS_MAPPING, SHIPPING_COSTS } from '../constants';
import { OrderDetails, Product, OrderStatus } from '../types';

interface OrderWizardProps {
  onBack: () => void;
}

const OrderWizard: React.FC<OrderWizardProps> = ({ onBack }) => {
  const [step, setStep] = useState(1);
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
      // We don't save File objects, so handle that
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

  return (
    <div className="bg-cream min-h-screen flex flex-col">
      {/* Wizard Header */}
      <header className="bg-white border-b px-4 py-6 shadow-sm sticky top-0 z-50">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <button onClick={onBack} className="text-gray-400 hover:text-primary flex items-center gap-1">
              ← Volver
            </button>
            <div className="font-display font-bold text-primary">NUEVO PEDIDO</div>
            <div className="text-xs text-gray-400">Paso {step} de 5</div>
          </div>
          
          {/* Progress Bar */}
          <div className="flex items-center justify-between relative">
            <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-100 -translate-y-1/2 -z-10"></div>
            <div className="absolute top-1/2 left-0 h-1 bg-primary -translate-y-1/2 -z-10 transition-all duration-500" style={{ width: `${((step - 1) / 4) * 100}%` }}></div>
            {[1, 2, 3, 4, 5].map((s) => (
              <div 
                key={s} 
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                  step === s ? 'step-active' : step > s ? 'step-done' : 'step-pending'
                }`}
              >
                {step > s ? '✓' : s}
              </div>
            ))}
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto w-full p-4 py-10 flex-grow">
        
        {/* Step 1: Producto */}
        {step === 1 && (
          <div className="animate-fade-in">
            <h2 className="text-2xl font-display font-bold text-primary mb-2">Elegí tu fotolibro</h2>
            <p className="text-gray-500 mb-10">Seleccioná el tamaño y tipo de tapa que prefieras</p>
            
            <div className="mb-12">
              <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6">Paquetes Recomendados</h3>
              <div className="grid md:grid-cols-3 gap-6">
                {PACKAGES.map((pkg) => (
                  <button 
                    key={pkg.nombre}
                    onClick={() => {
                      setOrderDetails(prev => ({ ...prev, productoCodigo: pkg.productoCodigo, paginasTotal: pkg.paginas }));
                      nextStep();
                    }}
                    className={`text-left p-6 rounded-2xl border-2 transition-all ${
                      orderDetails.productoCodigo === pkg.productoCodigo && orderDetails.paginasTotal === pkg.paginas
                      ? 'border-primary bg-primary/5' : 'border-gray-100 bg-white hover:border-accent/50'
                    }`}
                  >
                    <div className="text-sm font-bold text-secondary mb-2 uppercase tracking-wide">{pkg.badge || 'PROMO'}</div>
                    <div className="text-xl font-bold text-primary mb-1">{pkg.nombre}</div>
                    <div className="text-sm text-gray-500 mb-4">{pkg.descripcion}</div>
                    <div className="text-2xl font-bold text-primary">${pkg.precio.toLocaleString()}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="relative mb-8 text-center">
              <div className="absolute top-1/2 left-0 w-full h-px bg-gray-200 -z-10"></div>
              <span className="bg-cream px-6 text-sm text-gray-400 font-medium">o elegí un formato base</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {PRODUCTS.map((prod) => (
                <div 
                  key={prod.codigo}
                  onClick={() => setOrderDetails(prev => ({ ...prev, productoCodigo: prod.codigo, paginasTotal: prod.paginasBase }))}
                  className={`cursor-pointer group bg-white p-4 rounded-2xl border-2 transition-all ${
                    orderDetails.productoCodigo === prod.codigo ? 'border-primary' : 'border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <img src={prod.imagen} alt={prod.nombre} className="w-full aspect-square object-cover rounded-lg mb-4" />
                  <div className="text-xs font-bold text-accent uppercase mb-1">{prod.tipo}</div>
                  <h4 className="font-bold text-primary mb-2">{prod.nombre}</h4>
                  <div className="flex justify-between items-end">
                    <span className="text-xl font-bold text-primary">${prod.precioBase.toLocaleString()}</span>
                    <button 
                      onClick={(e) => { e.stopPropagation(); setOrderDetails(prev => ({ ...prev, productoCodigo: prod.codigo, paginasTotal: prod.paginasBase })); nextStep(); }}
                      className="bg-gray-100 group-hover:bg-primary group-hover:text-white p-2 rounded-lg transition-colors"
                    >
                      →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Step 2: Páginas */}
        {step === 2 && selectedProduct && (
          <div className="animate-fade-in max-w-xl mx-auto">
             <h2 className="text-2xl font-display font-bold text-primary mb-2">¿Cuántas páginas necesitás?</h2>
             <p className="text-gray-500 mb-8">El fotolibro base incluye {selectedProduct.paginasBase} páginas.</p>

             <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 mb-8">
                <div className="flex items-center gap-4 mb-8">
                  <img src={selectedProduct.imagen} className="w-20 h-20 rounded-xl object-cover" />
                  <div>
                    <h3 className="font-bold text-primary">{selectedProduct.nombre}</h3>
                    <p className="text-sm text-gray-400">Formato {selectedProduct.tipo}</p>
                  </div>
                </div>

                <div className="flex items-center justify-between mb-8 bg-cream p-4 rounded-2xl">
                  <button 
                    onClick={() => setOrderDetails(prev => ({ ...prev, paginasTotal: Math.max(selectedProduct.paginasBase, (prev.paginasTotal || 0) - 2) }))}
                    className="w-12 h-12 rounded-xl bg-white shadow-sm flex items-center justify-center text-2xl hover:bg-primary hover:text-white transition-colors"
                  >-</button>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-primary">{orderDetails.paginasTotal}</div>
                    <div className="text-xs font-medium text-gray-400 uppercase tracking-widest">Páginas</div>
                  </div>
                  <button 
                    onClick={() => setOrderDetails(prev => ({ ...prev, paginasTotal: Math.min(100, (prev.paginasTotal || 0) + 2) }))}
                    className="w-12 h-12 rounded-xl bg-white shadow-sm flex items-center justify-center text-2xl hover:bg-primary hover:text-white transition-colors"
                  >+</button>
                </div>

                <div className="space-y-4 border-t pt-6">
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>Producto Base ({selectedProduct.paginasBase} págs)</span>
                    <span>${selectedProduct.precioBase.toLocaleString()}</span>
                  </div>
                  {orderDetails.paginasTotal! > selectedProduct.paginasBase && (
                    <div className="flex justify-between text-sm text-gray-500">
                      <span>Páginas Extra ({(orderDetails.paginasTotal! - selectedProduct.paginasBase)})</span>
                      <span>${((orderDetails.paginasTotal! - selectedProduct.paginasBase) * selectedProduct.precioPaginaExtra).toLocaleString()}</span>
                    </div>
                  )}
                  <div className="flex justify-between text-xl font-bold text-primary border-t pt-4">
                    <span>Subtotal</span>
                    <span>${calculateTotal().toLocaleString()}</span>
                  </div>
                </div>
             </div>

             <div className="bg-blue-50 p-4 rounded-2xl flex gap-3 text-sm text-blue-700 mb-8">
               <span>💡</span>
               <p>Recomendamos un promedio de 2 a 3 fotos por página para un diseño elegante y espacioso.</p>
             </div>

             <button onClick={nextStep} className="w-full py-4 bg-primary text-white font-bold rounded-2xl hover:bg-opacity-95 shadow-lg">Continuar →</button>
          </div>
        )}

        {/* Step 3: Fotos */}
        {step === 3 && (
          <div className="animate-fade-in">
             <h2 className="text-2xl font-display font-bold text-primary mb-2">Subí tus fotos</h2>
             <p className="text-gray-500 mb-8">Podés subir hasta 200 fotos. Nosotros las organizaremos por vos.</p>

             <div 
               onClick={() => fileInputRef.current?.click()}
               className="border-4 border-dashed border-gray-200 rounded-3xl p-12 text-center hover:border-primary transition-colors cursor-pointer bg-white group"
             >
               <div className="text-5xl mb-4 group-hover:scale-110 transition-transform">☁️</div>
               <h3 className="text-xl font-bold text-primary mb-1">Arrastrá tus fotos aquí</h3>
               <p className="text-gray-400">o hacé click para seleccionar desde tu dispositivo</p>
               <p className="mt-4 text-xs font-medium text-gray-300">Formatos JPG, PNG • Máximo 10MB por foto</p>
               <input 
                 type="file" 
                 multiple 
                 hidden 
                 ref={fileInputRef} 
                 onChange={handleFileUpload} 
                 accept="image/*"
               />
             </div>

             <div className="mt-10">
                <div className="flex justify-between items-end mb-6">
                  <h3 className="font-bold text-primary">Fotos seleccionadas ({orderDetails.fotos?.length || 0})</h3>
                  {orderDetails.fotos && orderDetails.fotos.length > 0 && (
                    <button onClick={() => setOrderDetails(prev => ({ ...prev, fotos: [] }))} className="text-xs font-bold text-error">Eliminar todas</button>
                  )}
                </div>

                <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-4">
                  {orderDetails.fotos?.map((file, idx) => (
                    <div key={idx} className="relative group aspect-square rounded-xl overflow-hidden shadow-sm">
                      <img src={URL.createObjectURL(file)} className="w-full h-full object-cover" />
                      <button 
                        onClick={() => removePhoto(idx)}
                        className="absolute top-1 right-1 bg-white/80 backdrop-blur rounded-full w-6 h-6 flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                      >✕</button>
                    </div>
                  ))}
                </div>
             </div>

             <div className="mt-12 sticky bottom-4">
                <button 
                  disabled={(orderDetails.fotos?.length || 0) < 10}
                  onClick={nextStep} 
                  className={`w-full py-4 font-bold rounded-2xl shadow-xl transition-all ${
                    (orderDetails.fotos?.length || 0) >= 10 
                    ? 'bg-primary text-white hover:bg-opacity-95' 
                    : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {(orderDetails.fotos?.length || 0) < 10 ? `Faltan ${(10 - (orderDetails.fotos?.length || 0))} fotos para continuar` : 'Continuar →'}
                </button>
             </div>
          </div>
        )}

        {/* Step 4: Envío */}
        {step === 4 && (
          <div className="animate-fade-in grid md:grid-cols-3 gap-8">
            <div className="md:col-span-2">
              <h2 className="text-2xl font-display font-bold text-primary mb-2">¿A dónde lo enviamos?</h2>
              <p className="text-gray-500 mb-8">Completá tus datos para el envío con Correo Argentino.</p>

              <form className="space-y-6">
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-sm font-bold text-gray-700">Nombre completo</label>
                    <input 
                      type="text" 
                      className="w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 ring-primary/20 outline-none"
                      value={orderDetails.cliente?.nombre}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, nombre: e.target.value } }))}
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-bold text-gray-700">Email</label>
                    <input 
                      type="email" 
                      className="w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 ring-primary/20 outline-none"
                      value={orderDetails.cliente?.email}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, email: e.target.value } }))}
                    />
                  </div>
                </div>

                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-1">
                    <label className="text-sm font-bold text-gray-700">Provincia</label>
                    <select 
                      className="w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 ring-primary/20 outline-none"
                      value={orderDetails.cliente?.direccion.provincia}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, direccion: { ...prev.cliente!.direccion, provincia: e.target.value } } }))}
                    >
                      <option value="">Seleccionar...</option>
                      {Object.keys(PROVINCIAS_MAPPING).map(p => <option key={p} value={p}>{p}</option>)}
                    </select>
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-bold text-gray-700">Ciudad</label>
                    <input 
                      type="text" 
                      className="w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 ring-primary/20 outline-none"
                      value={orderDetails.cliente?.direccion.ciudad}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, direccion: { ...prev.cliente!.direccion, ciudad: e.target.value } } }))}
                    />
                  </div>
                </div>

                <div className="grid sm:grid-cols-3 gap-4">
                  <div className="sm:col-span-2 space-y-1">
                    <label className="text-sm font-bold text-gray-700">Calle y Número</label>
                    <input 
                      type="text" 
                      className="w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 ring-primary/20 outline-none"
                      value={orderDetails.cliente?.direccion.calle}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, direccion: { ...prev.cliente!.direccion, calle: e.target.value } } }))}
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-bold text-gray-700">Código Postal</label>
                    <input 
                      type="text" 
                      className="w-full p-3 bg-white border border-gray-200 rounded-xl focus:ring-2 ring-primary/20 outline-none"
                      value={orderDetails.cliente?.direccion.cp}
                      onChange={(e) => setOrderDetails(prev => ({ ...prev, cliente: { ...prev.cliente!, direccion: { ...prev.cliente!.direccion, cp: e.target.value } } }))}
                    />
                  </div>
                </div>
              </form>
            </div>

            <div className="bg-white p-6 rounded-3xl border border-gray-100 shadow-sm h-fit space-y-6">
              <h3 className="font-bold text-primary">Resumen</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-400">Producto</span>
                  <span className="text-primary font-medium text-right">{selectedProduct?.nombre}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Páginas</span>
                  <span className="text-primary font-medium">{orderDetails.paginasTotal}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Envío</span>
                  <span className="text-primary font-medium">
                    {orderDetails.cliente?.direccion.provincia ? `$${SHIPPING_COSTS[PROVINCIAS_MAPPING[orderDetails.cliente.direccion.provincia]].toLocaleString()}` : 'Pendiente'}
                  </span>
                </div>
                <div className="border-t pt-4 flex justify-between text-lg font-bold text-primary">
                  <span>Total</span>
                  <span>${calculateTotal().toLocaleString()}</span>
                </div>
              </div>
              <div className="p-3 bg-cream rounded-xl text-xs text-orange-800 flex items-center gap-2">
                <span>⏱️</span>
                Entrega estimada: 12-18 días hábiles
              </div>
              <button 
                onClick={nextStep} 
                className="w-full py-4 bg-primary text-white font-bold rounded-2xl shadow-lg hover:bg-opacity-95"
              >
                Ir al Pago →
              </button>
            </div>
          </div>
        )}

        {/* Step 5: Pago */}
        {step === 5 && (
          <div className="animate-fade-in max-w-2xl mx-auto">
             <h2 className="text-2xl font-display font-bold text-primary mb-2">Completá tu pedido</h2>
             <p className="text-gray-500 mb-8">Elegí el método de pago que prefieras.</p>

             <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm mb-8 space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <button 
                    onClick={() => setOrderDetails(prev => ({ ...prev, metodoPago: 'mercadopago' }))}
                    className={`p-6 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${
                      orderDetails.metodoPago === 'mercadopago' ? 'border-primary bg-primary/5' : 'border-gray-100'
                    }`}
                  >
                    <span className="text-3xl">💳</span>
                    <span className="font-bold text-sm">MercadoPago</span>
                  </button>
                  <button 
                    onClick={() => setOrderDetails(prev => ({ ...prev, metodoPago: 'transferencia' }))}
                    className={`p-6 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${
                      orderDetails.metodoPago === 'transferencia' ? 'border-primary bg-primary/5' : 'border-gray-100'
                    }`}
                  >
                    <span className="text-3xl">🏦</span>
                    <span className="font-bold text-sm">Transferencia</span>
                  </button>
                </div>

                {orderDetails.metodoPago === 'transferencia' ? (
                  <div className="bg-cream p-6 rounded-2xl border border-orange-100">
                    <h4 className="font-bold text-primary mb-4">Datos Bancarios</h4>
                    <div className="space-y-3 text-sm">
                      <div className="flex justify-between"><span className="text-gray-400">Banco:</span><span className="font-medium">Santander Río</span></div>
                      <div className="flex justify-between"><span className="text-gray-400">CBU:</span><span className="font-medium">0720123456789012345678</span></div>
                      <div className="flex justify-between"><span className="text-gray-400">Alias:</span><span className="font-medium">fotolibros.arg</span></div>
                      <div className="flex justify-between"><span className="text-gray-400">Titular:</span><span className="font-medium">Fotolibros Argentina SRL</span></div>
                    </div>
                    <div className="mt-6 p-4 bg-white rounded-xl border border-orange-200">
                      <div className="text-xs text-gray-400 uppercase font-bold mb-1">Tu Referencia:</div>
                      <div className="text-2xl font-display font-bold text-primary tracking-widest">FL-98231</div>
                    </div>
                  </div>
                ) : (
                  <div className="p-6 bg-blue-50 rounded-2xl text-blue-800 text-sm flex gap-3">
                    <span>✨</span>
                    <p>Serás redirigido de forma segura a MercadoPago para completar el pago con tarjeta de crédito, débito o saldo en cuenta.</p>
                  </div>
                )}

                <div className="pt-6 border-t">
                  <div className="flex justify-between items-center mb-6">
                    <div className="text-sm text-gray-400">Total a pagar:</div>
                    <div className="text-3xl font-bold text-primary">${calculateTotal().toLocaleString()}</div>
                  </div>
                  <button 
                    className="w-full py-4 bg-accent text-white font-bold rounded-2xl shadow-lg hover:bg-orange-600 transition-colors"
                    onClick={() => alert('¡Pedido creado! Esta es una demo.')}
                  >
                    Confirmar y Finalizar Pedido
                  </button>
                  <p className="mt-4 text-center text-xs text-gray-400">
                    Al confirmar, aceptás los términos y condiciones de servicio.
                  </p>
                </div>
             </div>
          </div>
        )}

      </main>

      {/* Navigation Footer */}
      {step < 5 && (
        <footer className="bg-white border-t p-4 flex items-center justify-between">
          <button 
            onClick={prevStep}
            disabled={step === 1}
            className={`px-6 py-3 font-bold rounded-xl transition-colors ${step === 1 ? 'text-gray-200 cursor-not-allowed' : 'text-gray-400 hover:text-primary'}`}
          >
            ← Atrás
          </button>
          
          {/* Mobile small summary */}
          <div className="md:hidden text-center">
            <div className="text-[10px] text-gray-400 uppercase font-bold">Subtotal</div>
            <div className="text-primary font-bold">${calculateTotal().toLocaleString()}</div>
          </div>

          <div className="flex gap-4">
            {step < 5 && step !== 4 && step !== 3 && (
              <button 
                onClick={nextStep}
                disabled={!orderDetails.productoCodigo}
                className={`px-8 py-3 bg-primary text-white font-bold rounded-xl shadow-lg transition-all ${!orderDetails.productoCodigo ? 'opacity-50 cursor-not-allowed' : 'hover:scale-105'}`}
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
