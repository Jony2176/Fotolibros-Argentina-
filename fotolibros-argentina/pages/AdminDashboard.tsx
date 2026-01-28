
import React, { useState, useEffect } from 'react';
import { OrderStatus, STATUS_CONFIG } from '../types';
import { GoogleGenAI, Type } from "@google/genai";

interface AdminDashboardProps {
  onLogout: () => void;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  const [activeTab, setActiveTab] = useState('all');
  const [verifyingId, setVerifyingId] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [orders, setOrders] = useState<any[]>([]);
  const [stats, setStats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Cargar pedidos del backend
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await fetch('http://localhost:8000/admin/pedidos');
        const data = await response.json();

        // Transformar pedidos
        const transformed = data.pedidos.map((p: any) => ({
          id: p.id.slice(0, 8).toUpperCase(),
          fullId: p.id,
          client: p.cliente?.nombre || 'Sin nombre',
          email: p.cliente?.email || '',
          product: p.producto_codigo,
          total: p.total_precio || 0,
          status: p.estado === 'pendiente' ? OrderStatus.PENDIENTE_PAGO :
            p.estado === 'procesando' ? OrderStatus.VERIFICANDO_PAGO :
              p.estado === 'creando_proyecto' ? OrderStatus.EN_PRODUCCION :
                p.estado === 'completado' ? OrderStatus.ENVIADO :
                  OrderStatus.EN_PRODUCCION,
          date: new Date(p.created_at).toLocaleDateString('es-AR'),
          rawStatus: p.estado
        }));

        setOrders(transformed);

        // Stats
        const s = data.stats || {};
        setStats([
          { label: 'Pendiente', count: s.pendiente || 0, color: 'bg-yellow-500', status: OrderStatus.PENDIENTE_PAGO },
          { label: 'Procesando', count: s.procesando || 0, color: 'bg-blue-500', status: OrderStatus.VERIFICANDO_PAGO },
          { label: 'En Producción', count: (s.creando_proyecto || 0) + (s.subiendo_fotos || 0), color: 'bg-orange-500', status: OrderStatus.EN_PRODUCCION },
          { label: 'Completados', count: s.completado || 0, color: 'bg-green-500', status: OrderStatus.ENVIADO },
          { label: 'Errores', count: s.error || 0, color: 'bg-red-500', status: OrderStatus.PENDIENTE_PAGO, urgent: (s.error || 0) > 0 },
        ]);

      } catch (error) {
        console.error('Error loading orders:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  // Exportar CSV
  const handleExport = () => {
    window.open('http://localhost:8000/admin/export', '_blank');
  };

  // Cambiar estado de pedido
  const handleChangeStatus = async (orderId: string, fullId: string, newStatus: string) => {
    const tracking = newStatus === 'completado' ? prompt('Código de seguimiento (opcional):') : null;

    try {
      const response = await fetch(`http://localhost:8000/admin/pedidos/${fullId}/estado?nuevo_estado=${newStatus}${tracking ? `&codigo_seguimiento=${tracking}` : ''}`, {
        method: 'PATCH'
      });

      if (response.ok) {
        alert(`Estado actualizado a: ${newStatus}`);
        // Recargar
        window.location.reload();
      }
    } catch (error) {
      alert('Error actualizando estado');
    }
  };

  const MY_BANK_DATA = {
    cbu: "0720000088000012345678",
    alias: "fotolibros.arg"
  };

  const handleVerifyAI = async (order: any) => {
    setIsAnalyzing(true);
    setVerifyingId(order.id);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      // In a real app, we'd convert the URL to base64. Here we simulate multimodal input with a placeholder description as it's a mock URL.
      // But let's assume we fetch it and convert to base64.
      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: [
          {
            parts: [
              { text: `Analiza este comprobante de transferencia para el pedido ${order.id}. El monto esperado es $${order.total}. Mis datos destino son CBU: ${MY_BANK_DATA.cbu} y Alias: ${MY_BANK_DATA.alias}. Extrae: monto, fecha, banco_origen, cbu_destino, referencia. Devuelve JSON.` }
            ]
          }
        ],
        config: {
          responseMimeType: 'application/json',
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              monto: { type: Type.NUMBER },
              fecha: { type: Type.STRING },
              banco_origen: { type: Type.STRING },
              cbu_destino: { type: Type.STRING },
              referencia: { type: Type.STRING },
              confianza: { type: Type.NUMBER, description: '0 to 1' }
            },
            required: ['monto', 'fecha', 'cbu_destino']
          }
        }
      });

      const result = JSON.parse(response.text);
      setAnalysisResult({
        ...result,
        coincideMonto: Math.abs(result.monto - order.total) < 1,
        cbuCorrecto: result.cbu_destino.includes("12345678") || result.cbu_destino === MY_BANK_DATA.cbu
      });
    } catch (error) {
      console.error(error);
      alert("Error analizando el comprobante con IA.");
    } finally {
      setIsAnalyzing(false);
    }
  };

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
            <div className="flex items-center gap-4">
              <div className="flex bg-gray-100 p-1 rounded-xl">
                <button onClick={() => setActiveTab('all')} className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'all' ? 'bg-white shadow-sm text-primary' : 'text-gray-500'}`}>Todos</button>
                <button onClick={() => setActiveTab('action')} className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'action' ? 'bg-white shadow-sm text-primary' : 'text-gray-500'}`}>Pendientes</button>
              </div>
              <button onClick={handleExport} className="px-4 py-2 bg-green-500 text-white text-sm font-bold rounded-lg hover:bg-green-600 transition-all">
                📥 Exportar CSV
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-primary">
              <thead>
                <tr className="bg-gray-50 text-[10px] uppercase tracking-widest text-gray-400 font-bold">
                  <th className="px-6 py-4">Pedido ID</th>
                  <th className="px-6 py-4">Cliente</th>
                  <th className="px-6 py-4">Producto</th>
                  <th className="px-6 py-4">Total</th>
                  <th className="px-6 py-4">Estado</th>
                  <th className="px-6 py-4 text-right">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {loading ? (
                  <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-400">Cargando pedidos...</td></tr>
                ) : orders.length === 0 ? (
                  <tr><td colSpan={6} className="px-6 py-8 text-center text-gray-400">No hay pedidos aún</td></tr>
                ) : orders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50/50 transition-colors group">
                    <td className="px-6 py-4 font-bold">{order.id}</td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-600 font-medium">{order.client}</div>
                      <div className="text-xs text-gray-400">{order.email}</div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-400">{order.product}</td>
                    <td className="px-6 py-4 font-bold">{order.date}</td>
                    <td className="px-6 py-4">
                      <div className={`px-3 py-1 rounded-full text-[10px] font-bold inline-flex items-center gap-1.5 ${STATUS_CONFIG[order.status]?.color || 'bg-gray-100 text-gray-600'}`}>
                        {order.rawStatus}
                      </div>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <select
                        className="text-xs border rounded-lg px-2 py-1 bg-white"
                        value={order.rawStatus}
                        onChange={(e) => handleChangeStatus(order.id, order.fullId, e.target.value)}
                      >
                        <option value="pendiente">Pendiente</option>
                        <option value="procesando">Procesando</option>
                        <option value="creando_proyecto">En Producción</option>
                        <option value="completado">Enviado/Completado</option>
                        <option value="error">Error</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Analysis Overlay */}
        {verifyingId && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-primary/20 backdrop-blur-sm">
            <div className="bg-white w-full max-w-lg rounded-3xl shadow-2xl overflow-hidden animate-fade-in border border-gray-100">
              <div className="p-6 border-b flex justify-between items-center bg-gray-50">
                <h3 className="font-display font-bold text-primary">🔍 Verificación de Pago Inteligente</h3>
                <button onClick={() => setVerifyingId(null)} className="text-gray-400">✕</button>
              </div>
              <div className="p-8">
                {isAnalyzing ? (
                  <div className="text-center py-10 space-y-4">
                    <div className="w-16 h-16 border-4 border-accent border-t-transparent rounded-full animate-spin mx-auto"></div>
                    <p className="font-bold text-primary">Gemini analizando el comprobante...</p>
                    <p className="text-sm text-gray-400">Extrayendo datos y validando con el pedido.</p>
                  </div>
                ) : analysisResult ? (
                  <div className="space-y-6">
                    <div className="flex gap-4 p-4 bg-cream rounded-2xl border border-orange-100">
                      <div className="w-20 h-28 bg-gray-200 rounded-lg flex-shrink-0 overflow-hidden">
                        <img src="https://picsum.photos/seed/receipt1/400/600" alt="Comprobante" className="w-full h-full object-cover" />
                      </div>
                      <div className="flex-grow space-y-1">
                        <p className="text-[10px] font-bold text-gray-400 uppercase">Referencia</p>
                        <p className="font-bold text-primary">{analysisResult.referencia || 'N/A'}</p>
                        <p className="text-[10px] font-bold text-gray-400 uppercase mt-2">Banco Origen</p>
                        <p className="text-sm font-medium text-primary">{analysisResult.banco_origen}</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 gap-3">
                      <div className={`p-4 rounded-xl flex items-center justify-between ${analysisResult.coincideMonto ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                        <span className="text-sm font-bold">{analysisResult.coincideMonto ? '✅' : '❌'} Monto: ${analysisResult.monto}</span>
                        <span className="text-[10px] font-bold uppercase">{analysisResult.coincideMonto ? 'Coincide' : 'Diferente'}</span>
                      </div>
                      <div className={`p-4 rounded-xl flex items-center justify-between ${analysisResult.cbuCorrecto ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                        <span className="text-sm font-bold">{analysisResult.cbuCorrecto ? '✅' : '❌'} CBU Destino</span>
                        <span className="text-[10px] font-bold uppercase">{analysisResult.cbuCorrecto ? 'Correcto' : 'Inválido'}</span>
                      </div>
                      <div className="p-4 bg-blue-50 text-blue-800 rounded-xl flex items-center justify-between">
                        <span className="text-sm font-bold">📅 Fecha: {analysisResult.fecha}</span>
                        <span className="text-[10px] font-bold uppercase">Válida</span>
                      </div>
                    </div>

                    <div className="pt-6 flex gap-3">
                      <button className="flex-grow py-4 bg-success text-white font-bold rounded-2xl shadow-lg hover:opacity-90 transition-all">Aprobar Pago ✓</button>
                      <button className="flex-grow py-4 bg-error/10 text-error font-bold rounded-2xl hover:bg-error hover:text-white transition-all">Rechazar ✗</button>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;
