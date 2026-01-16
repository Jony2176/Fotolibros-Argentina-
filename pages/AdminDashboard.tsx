
import React, { useState } from 'react';
import { OrderStatus, STATUS_CONFIG } from '../types';

interface AdminDashboardProps {
  onLogout: () => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('all');

  const stats = [
    { label: 'Pendiente Pago', count: 12, color: 'bg-yellow-500', status: OrderStatus.PENDIENTE_PAGO },
    { label: 'Verificando', count: 5, color: 'bg-blue-500', status: OrderStatus.VERIFICANDO_PAGO },
    { label: 'Pago OK', count: 28, color: 'bg-green-500', status: OrderStatus.PAGO_APROBADO },
    { label: 'Producción', count: 42, color: 'bg-orange-500', status: OrderStatus.EN_PRODUCCION },
    { label: 'En Domicilio', count: 3, color: 'bg-purple-500', status: OrderStatus.EN_DEPOSITO, urgent: true },
    { label: 'Enviados', count: 156, color: 'bg-indigo-500', status: OrderStatus.ENVIADO },
  ];

  const mockOrders = [
    { id: 'FL-98231', client: 'Juan Pérez', product: '21x21 Tapa Dura', total: 61000, status: OrderStatus.EN_PRODUCCION, date: 'Hoy, 10:30' },
    { id: 'FL-98230', client: 'María López', product: '30x30 Tapa Dura', total: 95000, status: OrderStatus.VERIFICANDO_PAGO, date: 'Hoy, 09:15' },
    { id: 'FL-98229', client: 'Carlos Ruiz', product: 'Mini 10x10', total: 14300, status: OrderStatus.EN_DEPOSITO, date: 'Ayer' },
    { id: 'FL-98228', client: 'Ana García', product: '21x21 Tapa Dura', total: 40800, status: OrderStatus.PENDIENTE_PAGO, date: 'Ayer' },
    { id: 'FL-98227', client: 'Pedro Gómez', product: 'Horizontal Blanda', total: 26500, status: OrderStatus.ENVIADO, date: '15 Mar' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white border-b h-16 px-6 flex items-center justify-between sticky top-0 z-40">
        <div className="flex items-center gap-4">
          <span className="text-2xl">📸</span>
          <span className="font-display font-bold text-primary">ADMIN PANEL</span>
        </div>
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center text-white text-xs font-bold">A</div>
            <span className="text-sm font-medium text-gray-700 hidden sm:block">Administrator</span>
          </div>
          <button onClick={onLogout} className="text-gray-400 hover:text-error transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
          </button>
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto w-full space-y-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          {stats.map((stat) => (
            <div 
              key={stat.label} 
              className={`bg-white p-4 rounded-2xl shadow-sm border border-gray-100 relative overflow-hidden cursor-pointer hover:-translate-y-1 transition-all ${stat.urgent ? 'ring-2 ring-error/50' : ''}`}
            >
              <div className="text-xs font-bold text-gray-400 uppercase mb-2">{stat.label}</div>
              <div className="text-3xl font-display font-bold text-primary">{stat.count}</div>
              <div className={`absolute bottom-0 left-0 h-1 w-full ${stat.color}`}></div>
              {stat.urgent && <span className="absolute top-2 right-2 flex h-2 w-2"><span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-error opacity-75"></span><span className="relative inline-flex rounded-full h-2 w-2 bg-error"></span></span>}
            </div>
          ))}
        </div>

        {/* Orders Table */}
        <div className="bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 border-b flex flex-col md:flex-row justify-between items-center gap-4">
            <h2 className="font-display font-bold text-primary text-xl">Gestión de Pedidos</h2>
            <div className="flex bg-gray-100 p-1 rounded-xl">
              <button onClick={() => setActiveTab('all')} className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'all' ? 'bg-white shadow-sm text-primary' : 'text-gray-500'}`}>Todos</button>
              <button onClick={() => setActiveTab('action')} className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'action' ? 'bg-white shadow-sm text-primary' : 'text-gray-500'}`}>Pendientes Acción</button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="bg-gray-50 text-[10px] uppercase tracking-widest text-gray-400 font-bold">
                  <th className="px-6 py-4">Pedido ID</th>
                  <th className="px-6 py-4">Cliente</th>
                  <th className="px-6 py-4">Producto</th>
                  <th className="px-6 py-4">Total</th>
                  <th className="px-6 py-4">Estado</th>
                  <th className="px-6 py-4">Fecha</th>
                  <th className="px-6 py-4 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {mockOrders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50/50 transition-colors group">
                    <td className="px-6 py-4 font-bold text-primary">{order.id}</td>
                    <td className="px-6 py-4 text-sm text-gray-600 font-medium">{order.client}</td>
                    <td className="px-6 py-4 text-sm text-gray-400">{order.product}</td>
                    <td className="px-6 py-4 font-bold text-primary">${order.total.toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <div className={`px-3 py-1 rounded-full text-[10px] font-bold inline-flex items-center gap-1.5 ${STATUS_CONFIG[order.status].color}`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${STATUS_CONFIG[order.status].dot}`}></div>
                        {STATUS_CONFIG[order.status].label}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-xs text-gray-400">{order.date}</td>
                    <td className="px-6 py-4 text-right">
                      <button className="p-2 text-gray-400 hover:text-primary transition-colors">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="p-4 bg-gray-50 border-t flex items-center justify-center">
            <button className="text-xs font-bold text-gray-400 hover:text-primary transition-colors">Ver todos los pedidos →</button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default AdminDashboard;
