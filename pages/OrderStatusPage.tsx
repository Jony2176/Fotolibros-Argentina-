
import React, { useState } from 'react';
import { OrderStatus, STATUS_CONFIG } from '../types';

interface OrderStatusPageProps {
  onBack: () => void;
}

const OrderStatusPage: React.FC<OrderStatusPageProps> = ({ onBack }) => {
  const [orderId, setOrderId] = useState('');
  const [email, setEmail] = useState('');
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = () => {
    setLoading(true);
    // Simulation
    setTimeout(() => {
      setOrder({
        id: orderId || 'FL-12345',
        producto: 'Fotolibro 21x21 Tapa Dura',
        estado: OrderStatus.EN_PRODUCCION,
        fecha: '2024-03-20',
        ciudad: 'Córdoba Capital',
        paginas: 44,
        history: [
          { status: OrderStatus.PENDIENTE_PAGO, date: '2024-03-20 10:30', done: true },
          { status: OrderStatus.VERIFICANDO_PAGO, date: '2024-03-20 11:15', done: true },
          { status: OrderStatus.PAGO_APROBADO, date: '2024-03-20 14:00', done: true },
          { status: OrderStatus.EN_PRODUCCION, date: 'En proceso', done: false, current: true },
          { status: OrderStatus.EN_DEPOSITO, date: null, done: false },
          { status: OrderStatus.ENVIADO, date: null, done: false },
        ]
      });
      setLoading(false);
    }, 1000);
  };

  return (
    <div className="bg-cream min-h-screen flex flex-col">
      <header className="bg-white border-b px-4 py-6 shadow-sm">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <button onClick={onBack} className="text-gray-400 hover:text-primary transition-colors">← Volver</button>
          <div className="font-display font-bold text-primary tracking-widest uppercase">Consultar Estado</div>
          <div className="w-10"></div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto w-full p-4 py-12 flex-grow">
        {!order ? (
          <div className="max-w-md mx-auto bg-white p-10 rounded-3xl shadow-xl border border-gray-100">
            <div className="text-center mb-8">
               <span className="text-4xl mb-4 block">📦</span>
               <h2 className="text-2xl font-display font-bold text-primary">Seguimiento de Pedido</h2>
               <p className="text-sm text-gray-500 mt-2">Ingresá los datos para localizar tu fotolibro.</p>
            </div>
            
            <div className="space-y-6">
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Número de Pedido</label>
                <input 
                  type="text" 
                  placeholder="Ej: FL-12345" 
                  className="w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-2xl focus:ring-4 focus:ring-primary/5 focus:border-primary outline-none transition-all placeholder:text-gray-300"
                  value={orderId}
                  onChange={(e) => setOrderId(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-bold text-gray-400 uppercase tracking-widest ml-1">Email de compra</label>
                <input 
                  type="email" 
                  placeholder="tu@email.com" 
                  className="w-full p-4 bg-white border border-gray-200 text-primary font-medium rounded-2xl focus:ring-4 focus:ring-primary/5 focus:border-primary outline-none transition-all placeholder:text-gray-300"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <button 
                onClick={handleSearch}
                disabled={loading}
                className="w-full py-5 bg-primary text-white font-bold rounded-2xl shadow-lg hover:bg-opacity-95 disabled:opacity-50 mt-4 transition-all active:scale-[0.98]"
              >
                {loading ? 'Buscando historia...' : 'Consultar Pedido →'}
              </button>
            </div>
            <p className="mt-10 text-center text-xs text-gray-400 leading-relaxed italic">
              ¿No encontrás tu número de pedido?<br/>Revisá tu casilla de SPAM o contactanos por <a href="#" className="text-primary font-bold underline">WhatsApp</a>.
            </p>
          </div>
        ) : (
          <div className="space-y-8 animate-fade-in max-w-2xl mx-auto">
            <div className="bg-white p-8 rounded-3xl shadow-lg border border-gray-100 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
              <div>
                <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Pedido #{order.id}</div>
                <h2 className="text-2xl font-display font-bold text-primary">{order.producto}</h2>
                <div className="text-sm text-gray-500 mt-1">Enviando a {order.ciudad} • {order.paginas} páginas</div>
              </div>
              <div className={`px-5 py-2 rounded-full font-bold text-xs uppercase tracking-widest ${STATUS_CONFIG[order.estado].color}`}>
                {STATUS_CONFIG[order.estado].label}
              </div>
            </div>

            <div className="bg-white p-10 rounded-3xl shadow-lg border border-gray-100">
              <h3 className="font-display font-bold text-primary mb-10 text-lg border-b pb-4">Línea de tiempo de producción</h3>
              <div className="space-y-10 relative">
                <div className="absolute left-[15px] top-2 bottom-2 w-0.5 bg-gray-100"></div>
                {order.history.map((step: any, idx: number) => (
                  <div key={idx} className="flex gap-6 relative">
                    <div className={`w-8 h-8 rounded-full z-10 flex items-center justify-center transition-all ${
                      step.done ? 'bg-success text-white' : step.current ? 'bg-primary ring-4 ring-primary/20 scale-110 shadow-lg' : 'bg-gray-100'
                    }`}>
                      {step.done ? '✓' : ''}
                    </div>
                    <div className="flex-grow pt-1">
                      <div className={`font-bold tracking-tight ${step.done || step.current ? 'text-primary' : 'text-gray-300'}`}>
                        {STATUS_CONFIG[step.status as OrderStatus].label}
                      </div>
                      <div className="text-xs text-gray-400 mt-0.5">
                        {step.date || 'Próximamente'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="text-center">
              <button 
                onClick={() => setOrder(null)}
                className="text-xs font-bold text-gray-400 hover:text-primary transition-all uppercase tracking-widest"
              >
                Realizar otra búsqueda
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default OrderStatusPage;
