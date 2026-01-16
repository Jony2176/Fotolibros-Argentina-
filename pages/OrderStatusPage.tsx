
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
          <button onClick={onBack} className="text-gray-400 hover:text-primary">← Volver</button>
          <div className="font-display font-bold text-primary">CONSULTAR ESTADO</div>
          <div className="w-10"></div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto w-full p-4 py-12 flex-grow">
        {!order ? (
          <div className="max-w-md mx-auto bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
            <h2 className="text-2xl font-display font-bold text-primary mb-6 text-center">Seguimiento de Pedido</h2>
            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-sm font-bold text-gray-500">Número de Pedido</label>
                <input 
                  type="text" 
                  placeholder="Ej: FL-12345" 
                  className="w-full p-4 bg-cream border-none rounded-2xl focus:ring-2 ring-primary/20 outline-none"
                  value={orderId}
                  onChange={(e) => setOrderId(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <label className="text-sm font-bold text-gray-500">Email de compra</label>
                <input 
                  type="email" 
                  placeholder="juan@ejemplo.com" 
                  className="w-full p-4 bg-cream border-none rounded-2xl focus:ring-2 ring-primary/20 outline-none"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
              <button 
                onClick={handleSearch}
                disabled={loading}
                className="w-full py-4 bg-primary text-white font-bold rounded-2xl shadow-lg hover:bg-opacity-95 disabled:opacity-50 mt-4 transition-all"
              >
                {loading ? 'Buscando...' : 'Consultar →'}
              </button>
            </div>
            <p className="mt-8 text-center text-xs text-gray-400 leading-relaxed">
              ¿No encontrás tu número de pedido?<br/>Revisá tu casilla de SPAM o contactanos por <a href="#" className="text-primary font-bold underline">WhatsApp</a>.
            </p>
          </div>
        ) : (
          <div className="space-y-8 animate-fade-in">
            <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
              <div>
                <div className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1">Pedido #{order.id}</div>
                <h2 className="text-2xl font-bold text-primary">{order.producto}</h2>
                <div className="text-sm text-gray-500 mt-1">Enviando a {order.ciudad} • {order.paginas} páginas</div>
              </div>
              <div className={`px-4 py-2 rounded-full font-bold text-sm ${STATUS_CONFIG[order.estado].color}`}>
                {STATUS_CONFIG[order.estado].label}
              </div>
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-sm border border-gray-100">
              <h3 className="font-bold text-primary mb-8">Línea de tiempo</h3>
              <div className="space-y-8 relative">
                <div className="absolute left-[15px] top-2 bottom-2 w-0.5 bg-gray-100"></div>
                {order.history.map((step: any, idx: number) => (
                  <div key={idx} className="flex gap-6 relative">
                    <div className={`w-8 h-8 rounded-full z-10 flex items-center justify-center transition-all ${
                      step.done ? 'bg-success text-white' : step.current ? 'bg-primary ring-4 ring-primary/20' : 'bg-gray-100'
                    }`}>
                      {step.done ? '✓' : ''}
                    </div>
                    <div className="flex-grow pt-1">
                      <div className={`font-bold ${step.done || step.current ? 'text-primary' : 'text-gray-300'}`}>
                        {STATUS_CONFIG[step.status as OrderStatus].label}
                      </div>
                      <div className="text-xs text-gray-400 mt-0.5">
                        {step.date || 'Pendiente'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="text-center">
              <button 
                onClick={() => setOrder(null)}
                className="text-sm font-bold text-gray-400 hover:text-primary transition-colors"
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
