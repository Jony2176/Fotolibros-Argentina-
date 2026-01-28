
import React from 'react';
import { PACKAGES } from '../constants';

interface LandingProps {
  onStart: () => void;
  onCheckStatus: () => void;
  onAdmin: () => void;
}

const Landing: React.FC<LandingProps> = ({ onStart, onCheckStatus, onAdmin }) => {
  return (
    <div className="flex flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <button onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })} className="transition-transform hover:scale-105 active:scale-95">
            <img src="/logo.png" alt="Fotolibros Argentina" className="h-8 md:h-10" />
          </button>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
            <button onClick={onCheckStatus} className="hover:text-primary transition-colors">Estado de Pedido</button>
            <button onClick={onStart} className="bg-primary text-white px-5 py-2 rounded-full hover:bg-opacity-90 transition-all">Crear Pedido</button>
          </nav>
          <button onClick={onStart} className="md:hidden text-primary font-bold">Empezar</button>
        </div>
      </header>

      {/* Hero */}
      <section className="relative h-[85vh] flex items-center justify-center overflow-hidden">
        <img
          src="https://picsum.photos/seed/hero/1920/1080"
          alt="Fotolibro"
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/40"></div>
        <div className="relative z-10 text-center px-4 max-w-4xl">
          <h1 className="text-4xl md:text-6xl font-display font-bold text-white mb-6 leading-tight">
            Tus recuerdos, <span className="text-secondary italic">impresos para siempre</span>
          </h1>
          <p className="text-xl text-gray-100 mb-10 max-w-2xl mx-auto">
            Creá tu fotolibro personalizado en minutos con la mejor calidad del país.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <button
              onClick={onStart}
              className="w-full sm:w-auto bg-accent hover:bg-orange-600 text-white text-lg font-bold px-10 py-4 rounded-xl shadow-xl transition-all transform hover:scale-105"
            >
              Crear mi Fotolibro →
            </button>
          </div>
          <div className="mt-8 flex items-center justify-center gap-2 text-white/90 text-sm bg-white/10 backdrop-blur-md rounded-full py-2 px-4 w-fit mx-auto">
            <span>⏱️</span>
            Entrega en 10-14 días hábiles a todo el país
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 bg-cream">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-display font-bold text-primary mb-4">¿Cómo funciona?</h2>
            <p className="text-gray-600">En solo 3 pasos tendrás tu historia en tus manos</p>
          </div>
          <div className="grid md:grid-cols-3 gap-12">
            {[
              { icon: '📸', title: 'Elegí tu fotolibro', text: 'Seleccioná el tamaño, tipo de tapa y la cantidad de páginas.' },
              { icon: '🖼️', title: 'Subí tus fotos', text: 'Arrastrá tus mejores momentos. Nosotros los organizamos por vos.' },
              { icon: '📬', title: 'Recibí en tu casa', text: 'Te lo enviamos listo para disfrutar en 10-14 días hábiles.' },
            ].map((step, idx) => (
              <div key={idx} className="text-center group">
                <div className="w-20 h-20 bg-white shadow-lg rounded-3xl flex items-center justify-center text-4xl mx-auto mb-6 group-hover:-translate-y-2 transition-transform duration-300">
                  {step.icon}
                </div>
                <h3 className="text-xl font-bold text-primary mb-3">{step.title}</h3>
                <p className="text-gray-500 leading-relaxed">{step.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Packages */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-end mb-12 gap-4">
            <div>
              <h2 className="text-3xl font-display font-bold text-primary mb-2">Paquetes destacados</h2>
              <p className="text-gray-500">Opciones pensadas para cada tipo de recuerdo</p>
            </div>
            <button onClick={onStart} className="text-primary font-bold hover:underline">Ver todos los productos →</button>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {PACKAGES.map((pkg, idx) => (
              <div key={idx} className="bg-cream border border-orange-100 rounded-3xl p-8 flex flex-col hover:shadow-xl transition-shadow relative overflow-hidden group">
                {pkg.badge && (
                  <div className="absolute top-4 right-[-35px] bg-secondary text-white text-[10px] font-bold py-1 px-10 rotate-45 shadow-sm">
                    {pkg.badge}
                  </div>
                )}
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-primary mb-2">{pkg.nombre}</h3>
                  <p className="text-gray-500 text-sm line-clamp-2">{pkg.descripcion}</p>
                </div>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-3xl font-bold text-primary">${pkg.precio.toLocaleString()}</span>
                  <span className="text-gray-400 text-sm">/ {pkg.paginas} págs</span>
                </div>
                <button
                  onClick={onStart}
                  className="mt-auto w-full py-4 bg-white border-2 border-primary text-primary font-bold rounded-xl hover:bg-primary hover:text-white transition-all"
                >
                  Seleccionar
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust */}
      <section className="py-20 bg-primary text-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { icon: '✨', title: 'Calidad Premium', text: 'Papel fotográfico de alta densidad' },
              { icon: '🇦🇷', title: 'Envío Nacional', text: 'Llegamos a cada rincón del país' },
              { icon: '💬', title: 'Soporte 24/7', text: 'Atención personalizada vía WhatsApp' },
              { icon: '🔒', title: 'Pago Seguro', text: 'MercadoPago y Transferencia (-15%)' },
            ].map((item, idx) => (
              <div key={idx} className="flex flex-col items-center text-center">
                <span className="text-3xl mb-4">{item.icon}</span>
                <h4 className="font-bold mb-2">{item.title}</h4>
                <p className="text-white/60 text-sm">{item.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-cream">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-display font-bold text-primary mb-4">Lo que dicen nuestros clientes</h2>
            <p className="text-gray-500">Más de 5.000 familias ya tienen sus recuerdos impresos</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { name: 'María García', location: 'Buenos Aires', quote: 'El fotolibro de mi boda quedó espectacular. La calidad del papel y la impresión superaron todas mis expectativas.', stars: 5, avatar: 'https://i.pravatar.cc/100?img=1' },
              { name: 'Carlos López', location: 'Córdoba', quote: 'Regalé un fotolibro a mis viejos con fotos de toda la familia. ¡Lloraron de emoción! Muy recomendable.', stars: 5, avatar: 'https://i.pravatar.cc/100?img=3' },
              { name: 'Laura Fernández', location: 'Rosario', quote: 'Super fácil de armar. Subí las fotos, elegí el estilo y en 10 días lo tenía en casa. ¡Perfecto!', stars: 5, avatar: 'https://i.pravatar.cc/100?img=5' },
            ].map((t, idx) => (
              <div key={idx} className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100">
                <div className="flex items-center gap-3 mb-4">
                  <img src={t.avatar} alt={t.name} className="w-12 h-12 rounded-full object-cover" />
                  <div>
                    <p className="font-bold text-primary">{t.name}</p>
                    <p className="text-xs text-gray-400">{t.location}</p>
                  </div>
                </div>
                <div className="flex gap-1 mb-3">
                  {Array(t.stars).fill('⭐').map((s, i) => <span key={i} className="text-sm">{s}</span>)}
                </div>
                <p className="text-gray-600 text-sm italic">"{t.quote}"</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 bg-white">
        <div className="max-w-3xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-display font-bold text-primary mb-4">Preguntas Frecuentes</h2>
          </div>
          <div className="space-y-4">
            {[
              { q: '¿Cuánto tarda el envío?', a: 'Entre 10 y 14 días hábiles a todo el país. Te enviamos el código de seguimiento por email.' },
              { q: '¿Puedo editar después de pagar?', a: 'Tenés 24 horas para solicitar cambios. Después de ese plazo, el libro entra en producción.' },
              { q: '¿Qué pasa si no me gusta el resultado?', a: 'Ofrecemos garantía de satisfacción. Si hay un defecto de impresión, lo reimprimimos sin costo.' },
              { q: '¿Aceptan cambios y devoluciones?', a: 'Por ser un producto personalizado, no aceptamos devoluciones. Pero garantizamos la calidad de impresión.' },
              { q: '¿Cómo funciona el descuento por transferencia?', a: 'Pagando por transferencia bancaria tenés un 15% de descuento automático sobre el total de tu pedido.' },
            ].map((faq, idx) => (
              <details key={idx} className="bg-cream rounded-xl border border-gray-200 group">
                <summary className="flex items-center justify-between p-4 cursor-pointer font-bold text-primary">
                  {faq.q}
                  <span className="text-xl group-open:rotate-45 transition-transform">+</span>
                </summary>
                <div className="px-4 pb-4 text-sm text-gray-600">{faq.a}</div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-primary text-white py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            {/* Brand */}
            <div className="space-y-4">
              <img src="/logo.png" alt="Fotolibros Argentina" className="h-10 brightness-0 invert" />
              <p className="text-white/60 text-sm">Transformamos tus mejores momentos en recuerdos que podés tocar.</p>
              <div className="flex gap-3">
                <a href="https://instagram.com/fotolibrosarg" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors">📷</a>
                <a href="https://facebook.com/fotolibrosarg" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors">👤</a>
                <a href="https://wa.me/5491155554444" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition-colors">💬</a>
              </div>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-bold mb-4">Navegación</h4>
              <ul className="space-y-2 text-white/70 text-sm">
                <li><button onClick={onStart} className="hover:text-white transition-colors">Crear Fotolibro</button></li>
                <li><button onClick={onCheckStatus} className="hover:text-white transition-colors">Estado de Pedido</button></li>
                <li><a href="#faq" className="hover:text-white transition-colors">Preguntas Frecuentes</a></li>
                <li><button onClick={() => window.open('https://wa.me/5491155554444')} className="hover:text-white transition-colors">Contacto</button></li>
              </ul>
            </div>

            {/* Políticas */}
            <div>
              <h4 className="font-bold mb-4">Políticas</h4>
              <ul className="space-y-2 text-white/70 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Términos y Condiciones</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Política de Privacidad</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Política de Envíos</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Cambios y Devoluciones</a></li>
              </ul>
            </div>

            {/* Pagos */}
            <div>
              <h4 className="font-bold mb-4">Medios de Pago</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-2 bg-white/10 rounded-lg p-3">
                  <span className="text-xl">💳</span>
                  <span className="text-sm">MercadoPago</span>
                </div>
                <div className="flex items-center gap-2 bg-green-500/20 border border-green-500/30 rounded-lg p-3">
                  <span className="text-xl">🏦</span>
                  <span className="text-sm">Transferencia</span>
                  <span className="ml-auto bg-green-500 text-white text-[9px] font-bold px-2 py-0.5 rounded-full">15% OFF</span>
                </div>
              </div>
            </div>
          </div>

          {/* Bottom */}
          <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-white/50 text-xs">© 2026 PIKSY - Fotolibros Argentina. Hecho con ❤️ para tus recuerdos.</p>
            <button onClick={onAdmin} className="text-white/30 hover:text-white/60 text-xs transition-colors">Acceso Admin</button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
