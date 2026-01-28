
import React, { useState } from 'react';
import { 
  Package, Search, ArrowLeft, Palette, Sparkles, 
  Send, Check, Clock, AlertCircle, Mail, ChevronRight
} from 'lucide-react';

interface OrderTrackingProps {
    onBack: () => void;
}

interface TrackingData {
    id: string;
    producto: string;
    estado: string;
    progreso: number;
    mensaje: string;
    timeline: Array<{
        estado: string;
        label: string;
        done: boolean;
        current: boolean;
    }>;
    created_at: string;
    updated_at: string;
}

const OrderTracking: React.FC<OrderTrackingProps> = ({ onBack }) => {
    const [email, setEmail] = useState('');
    const [pedidoId, setPedidoId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [trackingData, setTrackingData] = useState<TrackingData | null>(null);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setTrackingData(null);

        try {
            const response = await fetch(`http://168.231.98.115:8002/tracking?email=${encodeURIComponent(email)}&pedido_id=${encodeURIComponent(pedidoId)}`, {
                method: 'POST'
            });

            if (!response.ok) {
                if (response.status === 404) {
                    throw new Error('Pedido no encontrado. Verificá el ID ingresado.');
                } else if (response.status === 403) {
                    throw new Error('El email no coincide con el pedido. Usá el mismo email con el que hiciste la compra.');
                }
                throw new Error('Error al buscar el pedido.');
            }

            const data = await response.json();
            setTrackingData(data);
        } catch (err: any) {
            setError(err.message || 'Error de conexión');
        } finally {
            setLoading(false);
        }
    };

    const getStatusIcon = (estado: string): React.ReactNode => {
        const iconClass = "w-12 h-12";
        const icons: Record<string, React.ReactNode> = {
            'pendiente': <Clock className={iconClass} />,
            'procesando': <Search className={iconClass} />,
            'creando_proyecto': <Palette className={iconClass} />,
            'aplicando_diseño': <Sparkles className={iconClass} />,
            'enviando_grafica': <Send className={iconClass} />,
            'completado': <Package className={iconClass} />,
        };
        return icons[estado] || <Package className={iconClass} />;
    };

    const getStatusColor = (estado: string) => {
        const colors: Record<string, string> = {
            'pendiente': 'bg-yellow-500',
            'procesando': 'bg-blue-500',
            'creando_proyecto': 'bg-orange-500',
            'aplicando_diseño': 'bg-purple-500',
            'enviando_grafica': 'bg-indigo-500',
            'completado': 'bg-green-500',
        };
        return colors[estado] || 'bg-gray-500';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-cream via-white to-cream flex flex-col">
            {/* Header */}
            <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100 shadow-sm">
                <div className="max-w-4xl mx-auto px-4 h-16 flex items-center justify-between">
                    <button onClick={onBack} className="text-gray-500 hover:text-primary transition-colors flex items-center gap-2">
                        <ArrowLeft className="w-4 h-4" /> Volver al inicio
                    </button>
                    <img src="/logo.png" alt="Fotolibros Argentina" className="h-8" />
                    <div className="w-20"></div>
                </div>
            </header>

            <main className="flex-grow flex items-center justify-center p-6">
                <div className="w-full max-w-lg">
                    {!trackingData ? (
                        /* Search Form */
                        <div className="bg-white rounded-3xl shadow-xl p-8 border border-gray-100">
                            <div className="text-center mb-8">
                                <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <Package className="w-10 h-10 text-primary" />
                                </div>
                                <h1 className="text-2xl font-display font-bold text-primary">Estado de tu Pedido</h1>
                                <p className="text-gray-500 mt-2">Ingresá tus datos para ver el progreso de tu fotolibro</p>
                            </div>

                            <form onSubmit={handleSearch} className="space-y-4">
                                <div>
                                    <label className="text-sm font-bold text-gray-600 block mb-1">Email de la compra</label>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={e => setEmail(e.target.value)}
                                        placeholder="tu@email.com"
                                        required
                                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                                    />
                                </div>

                                <div>
                                    <label className="text-sm font-bold text-gray-600 block mb-1">ID del Pedido</label>
                                    <input
                                        type="text"
                                        value={pedidoId}
                                        onChange={e => setPedidoId(e.target.value)}
                                        placeholder="Ej: a1b2c3d4-e5f6-..."
                                        required
                                        className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all font-mono text-sm"
                                    />
                                    <p className="text-xs text-gray-400 mt-1">Lo recibiste en el email de confirmación</p>
                                </div>

                                {error && (
                                    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
                                        {error}
                                    </div>
                                )}

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-4 bg-primary text-white font-bold rounded-xl hover:bg-opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                                            Buscando...
                                        </>
                                    ) : (
                                        <>
                                            <Search className="w-5 h-5" />
                                            Buscar Pedido
                                        </>
                                    )}
                                </button>
                            </form>

                            <div className="mt-8 pt-6 border-t text-center">
                                <p className="text-sm text-gray-400">¿No encontrás tu pedido?</p>
                                <a
                                    href="mailto:hola@fotolibros-argentina.com?subject=Ayuda con mi pedido"
                                    className="text-accent font-bold text-sm hover:underline inline-flex items-center gap-1"
                                >
                                    Contactanos por email <ChevronRight className="w-4 h-4" />
                                </a>
                            </div>
                        </div>
                    ) : (
                        /* Tracking Result */
                        <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-gray-100">
                            {/* Header */}
                            <div className={`${getStatusColor(trackingData.estado)} p-6 text-white`}>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <div className="text-sm opacity-80">Pedido</div>
                                        <div className="font-mono font-bold text-lg">{trackingData.id.slice(0, 8).toUpperCase()}</div>
                                    </div>
                                    <div className="text-white">{getStatusIcon(trackingData.estado)}</div>
                                </div>
                                <div className="mt-4">
                                    <div className="text-2xl font-bold">{trackingData.mensaje}</div>
                                    <div className="text-sm opacity-80 mt-1">Producto: {trackingData.producto}</div>
                                </div>
                            </div>

                            {/* Progress Bar */}
                            <div className="px-6 py-4 bg-gray-50">
                                <div className="flex justify-between text-xs text-gray-500 mb-2">
                                    <span>Progreso</span>
                                    <span className="font-bold">{trackingData.progreso}%</span>
                                </div>
                                <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${getStatusColor(trackingData.estado)} transition-all duration-500`}
                                        style={{ width: `${trackingData.progreso}%` }}
                                    ></div>
                                </div>
                            </div>

                            {/* Timeline */}
                            <div className="p-6">
                                <h3 className="font-bold text-primary mb-4">Historial del Pedido</h3>
                                <div className="space-y-4">
                                    {trackingData.timeline.map((step, index) => (
                                        <div key={step.estado} className="flex items-center gap-4">
                                            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${step.done ? 'bg-green-500 text-white' :
                                                step.current ? 'bg-primary text-white animate-pulse' :
                                                    'bg-gray-200 text-gray-400'
                                                }`}>
                                                {step.done ? <Check className="w-4 h-4" /> : index + 1}
                                            </div>
                                            <div className={`flex-grow ${step.current ? 'font-bold text-primary' : step.done ? 'text-gray-600' : 'text-gray-400'}`}>
                                                {step.label}
                                            </div>
                                            {step.current && (
                                                <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full font-bold">
                                                    Actual
                                                </span>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Dates */}
                            <div className="px-6 py-4 bg-gray-50 flex justify-between text-sm">
                                <div>
                                    <span className="text-gray-400">Creado:</span>{' '}
                                    <span className="font-medium">{new Date(trackingData.created_at).toLocaleDateString('es-AR')}</span>
                                </div>
                                <div>
                                    <span className="text-gray-400">Actualizado:</span>{' '}
                                    <span className="font-medium">{new Date(trackingData.updated_at).toLocaleDateString('es-AR')}</span>
                                </div>
                            </div>

                            {/* Actions */}
                            <div className="p-6 border-t flex gap-3">
                                <button
                                    onClick={() => setTrackingData(null)}
                                    className="flex-grow py-3 border-2 border-gray-200 text-gray-600 font-bold rounded-xl hover:bg-gray-50 transition-all flex items-center justify-center gap-2"
                                >
                                    <ArrowLeft className="w-4 h-4" /> Buscar otro pedido
                                </button>
                                <a
                                    href={`mailto:hola@fotolibros-argentina.com?subject=Consulta pedido ${trackingData.id.slice(0, 8).toUpperCase()}`}
                                    className="flex-grow py-3 bg-primary text-white font-bold rounded-xl hover:bg-opacity-90 transition-all text-center inline-flex items-center justify-center gap-2"
                                >
                                    <Mail className="w-4 h-4" /> Contactar
                                </a>
                            </div>
                        </div>
                    )}
                </div>
            </main>

            {/* Footer */}
            <footer className="py-6 text-center text-sm text-gray-400">
                Fotolibros Argentina © 2024 - Todos los derechos reservados
            </footer>
        </div>
    );
};

export default OrderTracking;
