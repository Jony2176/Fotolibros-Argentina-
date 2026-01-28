
import React, { useState, useEffect } from 'react';
import { 
  Camera, Package, Users, CreditCard, Settings, LogOut,
  LayoutDashboard, Clock, CheckCircle, DollarSign, Download,
  Building2, ChevronRight, Check, AlertTriangle, Truck, Percent,
  Smartphone, KeyRound, Save, Inbox, Circle
} from 'lucide-react';
import { OrderStatus, STATUS_CONFIG } from '../types';

interface AdminDashboardProps {
  onLogout: () => void;
}

// Types
interface Order {
  id: string;
  fullId: string;
  client: string;
  email: string;
  telefono: string;
  product: string;
  total: number;
  status: OrderStatus;
  rawStatus: string;
  date: string;
  ciudad: string;
  provincia: string;
}

interface Client {
  email: string;
  nombre: string;
  telefono: string;
  direccion: any;
  ordersCount: number;
  totalSpent: number;
  lastOrder: string;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ onLogout }) => {
  // Navigation
  const [activeSection, setActiveSection] = useState<'dashboard' | 'orders' | 'clients' | 'config' | 'payments'>('dashboard');
  const [activeTab, setActiveTab] = useState('all');

  // Data
  const [orders, setOrders] = useState<Order[]>([]);
  const [clients, setClients] = useState<Client[]>([]);
  const [stats, setStats] = useState<any>({});
  const [loading, setLoading] = useState(true);

  // Config State
  const [config, setConfig] = useState({
    precios: {
      envio_caba: 3500,
      envio_gba: 5500,
      envio_interior: 8500,
      descuento_transferencia: 15,
    },
    contacto: {
      whatsapp: '5491155554444',
      email: 'ventas@fotolibros.com.ar',
      instagram: '@fotolibrosargentina',
    },
    bancos: {
      bbva_cbu: '0170099340000012345678',
      bbva_alias: 'FOTOLIBROS.BBVA',
      prex_cvu: '0000076500000012345678',
      prex_alias: 'FOTOLIBROS.PREX',
      uala_cvu: '0000000000000012345678',
      uala_alias: 'FOTOLIBROS.UALA',
    }
  });

  // Fetch data
  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await fetch('http://168.231.98.115:8002/admin/pedidos');
      const data = await response.json();

      const transformed: Order[] = data.pedidos.map((p: any) => ({
        id: p.id.slice(0, 8).toUpperCase(),
        fullId: p.id,
        client: p.cliente?.nombre || 'Sin nombre',
        email: p.cliente?.email || '',
        telefono: p.cliente?.telefono || '-',
        product: p.producto_codigo,
        total: p.total_precio || 0,
        status: mapStatus(p.estado),
        rawStatus: p.estado,
        date: new Date(p.created_at).toLocaleDateString('es-AR'),
        ciudad: p.cliente?.direccion?.ciudad || '',
        provincia: p.cliente?.direccion?.provincia || '',
      }));

      setOrders(transformed);
      setStats(data.stats || {});

      // Extract unique clients
      const clientMap = new Map<string, Client>();
      transformed.forEach(o => {
        const existing = clientMap.get(o.email);
        if (existing) {
          existing.ordersCount++;
          existing.totalSpent += o.total;
        } else {
          clientMap.set(o.email, {
            email: o.email,
            nombre: o.client,
            telefono: o.telefono,
            direccion: { ciudad: o.ciudad, provincia: o.provincia },
            ordersCount: 1,
            totalSpent: o.total,
            lastOrder: o.date
          });
        }
      });
      setClients(Array.from(clientMap.values()));

    } catch (error) {
      console.error('Error loading orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const mapStatus = (estado: string): OrderStatus => {
    const map: Record<string, OrderStatus> = {
      'pendiente': OrderStatus.PENDIENTE_PAGO,
      'procesando': OrderStatus.VERIFICANDO_PAGO,
      'creando_proyecto': OrderStatus.EN_PRODUCCION,
      'completado': OrderStatus.ENVIADO,
      'error': OrderStatus.PENDIENTE_PAGO
    };
    return map[estado] || OrderStatus.EN_PRODUCCION;
  };

  const handleChangeStatus = async (fullId: string, newStatus: string) => {
    const tracking = newStatus === 'completado' ? prompt('Código de seguimiento (opcional):') : null;
    try {
      const url = `http://168.231.98.115:8002/admin/pedidos/${fullId}/estado?nuevo_estado=${newStatus}${tracking ? `&codigo_seguimiento=${tracking}` : ''}`;
      const response = await fetch(url, { method: 'PATCH' });
      if (response.ok) {
        fetchOrders();
      }
    } catch (error) {
      alert('Error actualizando estado');
    }
  };

  const handleExport = () => {
    window.open('http://168.231.98.115:8002/admin/export', '_blank');
  };

  const saveConfig = () => {
    localStorage.setItem('piksy_config', JSON.stringify(config));
    alert('Configuración guardada localmente');
  };

  // Sidebar items
  const menuItems = [
    { id: 'dashboard', icon: <LayoutDashboard className="w-5 h-5" />, label: 'Dashboard' },
    { id: 'orders', icon: <Package className="w-5 h-5" />, label: 'Pedidos' },
    { id: 'clients', icon: <Users className="w-5 h-5" />, label: 'Clientes' },
    { id: 'payments', icon: <CreditCard className="w-5 h-5" />, label: 'Pagos' },
    { id: 'config', icon: <Settings className="w-5 h-5" />, label: 'Configuración' },
  ];

  const totalRevenue = orders.reduce((sum, o) => sum + (o.total || 0), 0);
  const pendingOrders = orders.filter(o => o.rawStatus === 'pendiente').length;
  const completedOrders = orders.filter(o => o.rawStatus === 'completado').length;

  return (
    <div className="min-h-screen bg-gray-100 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-primary text-white flex flex-col fixed h-full">
        <div className="p-6 border-b border-white/10">
          <div className="flex items-center gap-3">
            <Camera className="w-8 h-8" />
            <div>
              <div className="font-display font-bold text-lg">PIKSY</div>
              <div className="text-[10px] text-white/60 uppercase tracking-widest">Admin Panel</div>
            </div>
          </div>
        </div>

        <nav className="flex-grow py-6">
          {menuItems.map(item => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id as any)}
              className={`w-full px-6 py-3 flex items-center gap-3 text-left transition-all ${activeSection === item.id
                ? 'bg-white/20 border-l-4 border-accent'
                : 'hover:bg-white/10 border-l-4 border-transparent'
                }`}
            >
              {item.icon}
              <span className="font-medium">{item.label}</span>
            </button>
          ))}
        </nav>

        <div className="p-6 border-t border-white/10">
          <button
            onClick={onLogout}
            className="w-full py-2 px-4 bg-white/10 hover:bg-white/20 rounded-lg flex items-center justify-center gap-2 transition-all"
          >
            <LogOut className="w-4 h-4" /> Cerrar Sesión
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-grow ml-64 p-8">
        {/* Dashboard Section */}
        {activeSection === 'dashboard' && (
          <div className="space-y-8">
            <div className="flex justify-between items-center">
              <h1 className="text-3xl font-display font-bold text-primary">Dashboard</h1>
              <div className="text-sm text-gray-500">Última actualización: {new Date().toLocaleTimeString('es-AR')}</div>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center">
                    <Package className="w-7 h-7 text-blue-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Total Pedidos</div>
                    <div className="text-2xl font-bold text-primary">{orders.length}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-yellow-100 rounded-2xl flex items-center justify-center">
                    <Clock className="w-7 h-7 text-yellow-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Pendientes</div>
                    <div className="text-2xl font-bold text-yellow-600">{pendingOrders}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-green-100 rounded-2xl flex items-center justify-center">
                    <CheckCircle className="w-7 h-7 text-green-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Completados</div>
                    <div className="text-2xl font-bold text-green-600">{completedOrders}</div>
                  </div>
                </div>
              </div>

              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="flex items-center gap-4">
                  <div className="w-14 h-14 bg-purple-100 rounded-2xl flex items-center justify-center">
                    <DollarSign className="w-7 h-7 text-purple-600" />
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Ingresos Totales</div>
                    <div className="text-2xl font-bold text-purple-600">${totalRevenue.toLocaleString('es-AR')}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recent Orders */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <div className="p-6 border-b flex justify-between items-center">
                <h2 className="font-bold text-lg text-primary">Pedidos Recientes</h2>
                <button onClick={() => setActiveSection('orders')} className="text-sm text-accent hover:underline">Ver todos →</button>
              </div>
              <table className="w-full">
                <thead className="bg-gray-50 text-[10px] uppercase tracking-widest text-gray-400">
                  <tr>
                    <th className="px-6 py-3 text-left">ID</th>
                    <th className="px-6 py-3 text-left">Cliente</th>
                    <th className="px-6 py-3 text-left">Producto</th>
                    <th className="px-6 py-3 text-left">Estado</th>
                    <th className="px-6 py-3 text-left">Fecha</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {orders.slice(0, 5).map(order => (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-bold text-primary">{order.id}</td>
                      <td className="px-6 py-4">{order.client}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{order.product}</td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${order.rawStatus === 'completado' ? 'bg-green-100 text-green-800' :
                          order.rawStatus === 'pendiente' ? 'bg-yellow-100 text-yellow-800' :
                            order.rawStatus === 'error' ? 'bg-red-100 text-red-800' :
                              'bg-blue-100 text-blue-800'
                          }`}>{order.rawStatus}</span>
                      </td>
                      <td className="px-6 py-4 text-gray-500">{order.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Orders Section */}
        {activeSection === 'orders' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h1 className="text-3xl font-display font-bold text-primary">Gestión de Pedidos</h1>
              <button onClick={handleExport} className="px-4 py-2 bg-green-500 text-white font-bold rounded-lg hover:bg-green-600 transition-all flex items-center gap-2">
                <Download className="w-4 h-4" /> Exportar CSV
              </button>
            </div>

            {/* Filters */}
            <div className="flex gap-2 bg-white p-2 rounded-xl shadow-sm w-fit">
              {['all', 'pendiente', 'procesando', 'completado', 'error'].map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === tab ? 'bg-primary text-white' : 'text-gray-500 hover:bg-gray-100'
                    }`}
                >
                  {tab === 'all' ? 'Todos' : tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Orders Table */}
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 text-[10px] uppercase tracking-widest text-gray-400">
                  <tr>
                    <th className="px-6 py-4 text-left">ID</th>
                    <th className="px-6 py-4 text-left">Cliente</th>
                    <th className="px-6 py-4 text-left">Producto</th>
                    <th className="px-6 py-4 text-left">Total</th>
                    <th className="px-6 py-4 text-left">Estado</th>
                    <th className="px-6 py-4 text-left">Fecha</th>
                    <th className="px-6 py-4 text-right">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {loading ? (
                    <tr><td colSpan={7} className="px-6 py-8 text-center text-gray-400">Cargando pedidos...</td></tr>
                  ) : orders
                    .filter(o => activeTab === 'all' || o.rawStatus === activeTab)
                    .map(order => (
                      <tr key={order.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-bold text-primary">{order.id}</td>
                        <td className="px-6 py-4">
                          <div>{order.client}</div>
                          <div className="text-xs text-gray-400">{order.email}</div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-500">{order.product}</td>
                        <td className="px-6 py-4 font-bold">${order.total?.toLocaleString('es-AR') || '-'}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded-full text-[10px] font-bold ${order.rawStatus === 'completado' ? 'bg-green-100 text-green-800' :
                            order.rawStatus === 'pendiente' ? 'bg-yellow-100 text-yellow-800' :
                              order.rawStatus === 'error' ? 'bg-red-100 text-red-800' :
                                'bg-blue-100 text-blue-800'
                            }`}>{order.rawStatus}</span>
                        </td>
                        <td className="px-6 py-4 text-gray-500">{order.date}</td>
                        <td className="px-6 py-4 text-right">
                          <select
                            className="text-xs border rounded-lg px-2 py-1 bg-white cursor-pointer"
                            value={order.rawStatus}
                            onChange={(e) => handleChangeStatus(order.fullId, e.target.value)}
                          >
                            <option value="pendiente">Pendiente</option>
                            <option value="procesando">Procesando</option>
                            <option value="creando_proyecto">En Producción</option>
                            <option value="completado">Completado</option>
                            <option value="error">Error</option>
                          </select>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Clients Section */}
        {activeSection === 'clients' && (
          <div className="space-y-6">
            <h1 className="text-3xl font-display font-bold text-primary">Clientes</h1>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="text-sm text-gray-500">Total Clientes</div>
                <div className="text-3xl font-bold text-primary">{clients.length}</div>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="text-sm text-gray-500">Clientes Recurrentes</div>
                <div className="text-3xl font-bold text-green-600">{clients.filter(c => c.ordersCount > 1).length}</div>
              </div>
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100">
                <div className="text-sm text-gray-500">Ticket Promedio</div>
                <div className="text-3xl font-bold text-purple-600">
                  ${clients.length > 0 ? Math.round(totalRevenue / orders.length).toLocaleString('es-AR') : 0}
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50 text-[10px] uppercase tracking-widest text-gray-400">
                  <tr>
                    <th className="px-6 py-4 text-left">Cliente</th>
                    <th className="px-6 py-4 text-left">Email</th>
                    <th className="px-6 py-4 text-left">Teléfono</th>
                    <th className="px-6 py-4 text-left">Ubicación</th>
                    <th className="px-6 py-4 text-left">Pedidos</th>
                    <th className="px-6 py-4 text-left">Total Gastado</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {clients.map(client => (
                    <tr key={client.email} className="hover:bg-gray-50">
                      <td className="px-6 py-4 font-bold">{client.nombre}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{client.email}</td>
                      <td className="px-6 py-4 text-sm">{client.telefono}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{client.direccion.ciudad}, {client.direccion.provincia}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-bold">{client.ordersCount}</span>
                      </td>
                      <td className="px-6 py-4 font-bold text-green-600">${client.totalSpent.toLocaleString('es-AR')}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Payments Section */}
        {activeSection === 'payments' && (
          <div className="space-y-6">
            <h1 className="text-3xl font-display font-bold text-primary">Gestión de Pagos</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                <h3 className="font-bold text-lg text-primary flex items-center gap-2">
                  <Building2 className="w-5 h-5" /> Cuentas Bancarias Activas
                </h3>
                <p className="text-sm text-gray-500">Cuentas disponibles para recibir pagos por transferencia.</p>

                {/* BBVA */}
                <div className="p-4 rounded-xl border-2 border-blue-200 bg-blue-50/50">
                  <div className="flex items-center gap-2 mb-2">
                    <Building2 className="w-5 h-5 text-blue-800" />
                    <span className="font-bold text-blue-800">Banco BBVA</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div><span className="text-gray-500">CBU:</span> <span className="font-mono font-bold">0170099340000012345678</span></div>
                    <div><span className="text-gray-500">Alias:</span> <span className="font-mono font-bold">FOTOLIBROS.BBVA</span></div>
                  </div>
                </div>

                {/* Prex */}
                <div className="p-4 rounded-xl border-2 border-purple-200 bg-purple-50/50">
                  <div className="flex items-center gap-2 mb-2">
                    <CreditCard className="w-5 h-5 text-purple-800" />
                    <span className="font-bold text-purple-800">Prex</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div><span className="text-gray-500">CVU:</span> <span className="font-mono font-bold">0000076500000012345678</span></div>
                    <div><span className="text-gray-500">Alias:</span> <span className="font-mono font-bold">FOTOLIBROS.PREX</span></div>
                  </div>
                </div>

                {/* Uala */}
                <div className="p-4 rounded-xl border-2 border-red-200 bg-red-50/50">
                  <div className="flex items-center gap-2 mb-2">
                    <Circle className="w-5 h-5 text-red-600 fill-red-600" />
                    <span className="font-bold text-red-700">Uala</span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div><span className="text-gray-500">CVU:</span> <span className="font-mono font-bold">0000000000000012345678</span></div>
                    <div><span className="text-gray-500">Alias:</span> <span className="font-mono font-bold">FOTOLIBROS.UALA</span></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
              <h3 className="font-bold text-lg text-primary mb-4">Pagos Pendientes de Verificación</h3>
              <div className="text-center py-8 text-gray-400">
                <Inbox className="w-10 h-10 mx-auto mb-2" />
                <p>No hay comprobantes pendientes de verificar.</p>
                <p className="text-sm">Los clientes que paguen por transferencia enviaran su comprobante aqui.</p>
              </div>
            </div>
          </div>
        )}

        {/* Config Section */}
        {activeSection === 'config' && (
          <div className="space-y-6">
            <h1 className="text-3xl font-display font-bold text-primary">Configuración General</h1>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Precios de Envío */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                <h3 className="font-bold text-lg text-primary flex items-center gap-2">
                  <Truck className="w-5 h-5" /> Costos de Envio
                </h3>

                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-500">CABA</label>
                    <input
                      type="number"
                      value={config.precios.envio_caba}
                      onChange={e => setConfig({ ...config, precios: { ...config.precios, envio_caba: +e.target.value } })}
                      className="w-full mt-1 px-4 py-2 border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">GBA</label>
                    <input
                      type="number"
                      value={config.precios.envio_gba}
                      onChange={e => setConfig({ ...config, precios: { ...config.precios, envio_gba: +e.target.value } })}
                      className="w-full mt-1 px-4 py-2 border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Interior</label>
                    <input
                      type="number"
                      value={config.precios.envio_interior}
                      onChange={e => setConfig({ ...config, precios: { ...config.precios, envio_interior: +e.target.value } })}
                      className="w-full mt-1 px-4 py-2 border rounded-lg"
                    />
                  </div>
                </div>
              </div>

              {/* Descuentos */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                <h3 className="font-bold text-lg text-primary flex items-center gap-2">
                  <Percent className="w-5 h-5" /> Descuentos
                </h3>

                <div>
                  <label className="text-sm text-gray-500">Descuento por Transferencia (%)</label>
                  <input
                    type="number"
                    value={config.precios.descuento_transferencia}
                    onChange={e => setConfig({ ...config, precios: { ...config.precios, descuento_transferencia: +e.target.value } })}
                    className="w-full mt-1 px-4 py-2 border rounded-lg"
                  />
                </div>
              </div>

              {/* Contacto */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                <h3 className="font-bold text-lg text-primary flex items-center gap-2">
                  <Smartphone className="w-5 h-5" /> Datos de Contacto
                </h3>

                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-500">WhatsApp</label>
                    <input
                      type="text"
                      value={config.contacto.whatsapp}
                      onChange={e => setConfig({ ...config, contacto: { ...config.contacto, whatsapp: e.target.value } })}
                      className="w-full mt-1 px-4 py-2 border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Email de Ventas</label>
                    <input
                      type="email"
                      value={config.contacto.email}
                      onChange={e => setConfig({ ...config, contacto: { ...config.contacto, email: e.target.value } })}
                      className="w-full mt-1 px-4 py-2 border rounded-lg"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-gray-500">Instagram</label>
                    <input
                      type="text"
                      value={config.contacto.instagram}
                      onChange={e => setConfig({ ...config, contacto: { ...config.contacto, instagram: e.target.value } })}
                      className="w-full mt-1 px-4 py-2 border rounded-lg"
                    />
                  </div>
                </div>
              </div>

              {/* API Keys */}
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 space-y-4">
                <h3 className="font-bold text-lg text-primary flex items-center gap-2">
                  <KeyRound className="w-5 h-5" /> Integraciones
                </h3>
                <p className="text-sm text-gray-500">Las API keys se configuran en el archivo .env del servidor.</p>

                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                    <span>Browserbase</span>
                    <span className="text-green-600 font-bold flex items-center gap-1">
                      <Check className="w-4 h-4" /> Configurado
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                    <span>OpenRouter (IA)</span>
                    <span className="text-green-600 font-bold flex items-center gap-1">
                      <Check className="w-4 h-4" /> Configurado
                    </span>
                  </div>
                  <div className="flex items-center justify-between py-2 px-3 bg-gray-50 rounded-lg">
                    <span>Google Gemini</span>
                    <span className="text-yellow-600 font-bold flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" /> Revisar
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={saveConfig}
              className="px-6 py-3 bg-primary text-white font-bold rounded-xl hover:bg-opacity-90 transition-all flex items-center gap-2"
            >
              <Save className="w-5 h-5" /> Guardar Configuracion
            </button>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;
