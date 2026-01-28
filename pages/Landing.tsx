
import React from 'react';
import { 
  Package, Gem, Shield, Palette, Rocket, Camera, Sparkles, Gift, 
  Star, ChevronRight, ChevronDown, ArrowRight
} from 'lucide-react';
import { PACKAGES, PRODUCTS } from '../constants';

interface LandingProps {
  onStart: () => void;
  onCheckStatus: () => void;
  onAdmin: () => void;
  onViewDesigns: () => void;
}

const Landing: React.FC<LandingProps> = ({ onStart, onCheckStatus, onAdmin, onViewDesigns }) => {
  const [isScrolled, setIsScrolled] = React.useState(false);
  const [showAllFormats, setShowAllFormats] = React.useState(false);

  React.useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navigate = (page: string) => {
    window.scrollTo(0, 0);
  };

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-primary/20">
      {/* Header Glassmorphism */}
      <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
        ? 'bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20 py-3'
        : 'bg-transparent py-5'
        }`}>
        <div className="max-w-7xl mx-auto px-4 md:px-6 flex justify-between items-center">
          <div className="flex items-center gap-2 group cursor-pointer leading-none" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            <img src="/logo.png" alt="Piksy" className="h-8 md:h-10 transition-transform duration-300 group-hover:scale-105" />
          </div>

          <div className="hidden md:flex gap-8 items-center">
            <a href="#como-funciona" className="text-sm font-medium text-slate-600 hover:text-primary transition-colors relative after:content-[''] after:absolute after:bottom-[-4px] after:left-0 after:w-0 after:h-0.5 after:bg-primary after:transition-all hover:after:w-full">Cómo funciona</a>
            <a href="#precios" className="text-sm font-medium text-slate-600 hover:text-primary transition-colors relative after:content-[''] after:absolute after:bottom-[-4px] after:left-0 after:w-0 after:h-0.5 after:bg-primary after:transition-all hover:after:w-full">Precios</a>
            <a href="#faq" className="text-sm font-medium text-slate-600 hover:text-primary transition-colors relative after:content-[''] after:absolute after:bottom-[-4px] after:left-0 after:w-0 after:h-0.5 after:bg-primary after:transition-all hover:after:w-full">Preguntas</a>
          </div>

          <div className="flex gap-3 items-center">
            <button
              onClick={onCheckStatus}
              className="hidden lg:flex items-center gap-2 px-4 py-2 text-slate-500 hover:text-primary transition-colors text-sm font-medium min-h-[44px]"
              aria-label="Ver estado del pedido"
            >
              <Package className="w-5 h-5" />
              Estado de Pedido
            </button>
            <button
              onClick={onViewDesigns}
              className="hidden md:block px-6 py-2.5 bg-white text-slate-700 font-semibold rounded-xl border border-slate-200 hover:border-primary hover:text-primary hover:shadow-lg transition-all duration-300 active:scale-95 text-sm"
            >
              Ver Diseños
            </button>
            <button
              onClick={onStart}
              className="px-6 py-2.5 bg-primary text-white font-semibold rounded-xl shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 hover:-translate-y-0.5 transition-all duration-300 active:scale-95 flex items-center gap-2 text-sm"
            >
              Comenzar
              <ArrowRight className="w-4 h-4 hidden sm:inline" />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section - Premium & Emotional */}
      <section className="pt-32 pb-20 md:pt-48 md:pb-32 px-4 relative overflow-hidden">
        {/* Background Gradients */}
        <div className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-purple-500/5 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/2 -z-10"></div>
        <div className="absolute bottom-0 left-0 w-[40vw] h-[40vw] bg-primary/5 rounded-full blur-[100px] translate-y-1/2 -translate-x-1/2 -z-10"></div>

        <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center relative z-10">
          <div className="space-y-8 animate-fade-in-up">
            <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white border border-primary/10 rounded-full text-xs font-bold tracking-wider uppercase shadow-sm text-primary">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              Calidad Premium Certificada
            </div>

            <h1 className="text-5xl md:text-7xl font-display font-bold leading-[1.1] text-slate-900 tracking-tight">
              Tus fotos no son <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600 relative inline-block">
                solo pixeles
                <svg className="absolute -bottom-2 left-0 w-full h-3 text-primary/20" viewBox="0 0 100 10" preserveAspectRatio="none">
                  <path d="M0 5 Q 50 10 100 5" stroke="currentColor" strokeWidth="8" fill="none" />
                </svg>
              </span>
            </h1>

            <p className="text-xl text-slate-600 leading-relaxed max-w-lg font-light">
              Transformamos tu galería digital en <strong className="font-semibold text-slate-800">obras de arte tangibles</strong>. Calidad de galería, papel premium e impresión digital profesional.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <button
                onClick={onStart}
                className="px-8 py-4 bg-primary text-white text-lg font-bold rounded-2xl shadow-xl shadow-primary/25 hover:shadow-2xl hover:shadow-primary/40 hover:-translate-y-1 transition-all duration-300 flex items-center justify-center gap-3 group cursor-pointer min-h-[56px]"
              >
                Crear mi Fotolibro
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button
                onClick={onViewDesigns}
                className="px-8 py-4 bg-white text-slate-700 text-lg font-semibold rounded-2xl border-2 border-slate-100 hover:border-primary/20 hover:bg-slate-50 transition-all duration-300 flex items-center justify-center gap-2 group cursor-pointer min-h-[56px]"
              >
                <Palette className="w-5 h-5 text-primary group-hover:scale-110 transition-transform duration-300" />
                Explorar Disenos
              </button>
            </div>

            <div className="flex items-center gap-6 pt-6 text-sm text-slate-500 font-medium border-t border-slate-100 mt-8 w-fit">
              <div className="flex items-center gap-2">
                <div className="flex -space-x-3">
                  {[1, 2, 3, 4].map(i => (
                    <div key={i} className="w-10 h-10 rounded-full border-2 border-white flex items-center justify-center bg-slate-100 overflow-hidden shadow-sm">
                      <img src={`https://i.pravatar.cc/100?img=${i + 10}`} alt="user" className="w-full h-full object-cover" />
                    </div>
                  ))}
                </div>
                <span className="ml-2">+5000 clientes felices</span>
              </div>
              <div className="h-4 w-px bg-slate-200"></div>
              <div className="flex items-center gap-1">
                <div className="flex gap-0.5">
                  {[1,2,3,4,5].map(i => <Star key={i} className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />)}
                </div>
                <span className="text-slate-500 ml-1 font-normal">4.9/5</span>
              </div>
            </div>
          </div>

          <div className="relative animate-fade-in-right delay-200 perspective-1000">
            {/* Abstract background blobs */}
            <div className="absolute top-0 right-0 w-72 h-72 bg-purple-200 rounded-full blur-[80px] opacity-40 mix-blend-multiply animate-blob"></div>
            <div className="absolute bottom-0 left-10 w-72 h-72 bg-primary/20 rounded-full blur-[80px] opacity-40 mix-blend-multiply animate-blob animation-delay-2000"></div>

            {/* 3D Book Preview Container - Floating Effect */}
            <div className="relative transform rotate-y-[-5deg] rotate-x-[5deg] hover:rotate-y-[0deg] hover:rotate-x-[0deg] transition-transform duration-700 ease-out-back cursor-pointer group">
              <div className="absolute inset-0 bg-gradient-to-tr from-black/20 to-transparent rounded-[40px] blur-xl transform translate-y-10 scale-90 opacity-60"></div>
              <img
                src="/gallery/amigas-abierto.jpg"
                alt="Fotolibro Premium Abierto"
                className="relative rounded-[32px] shadow-[0_20px_50px_-12px_rgba(0,0,0,0.15)] border-[6px] border-white z-10 w-full object-cover aspect-[4/3] group-hover:scale-[1.02] transition-transform duration-500"
              />

              {/* Floating Quality Badge */}
              <div className="absolute -bottom-6 -left-6 bg-white p-4 rounded-2xl shadow-xl z-20 flex items-center gap-3 border border-slate-50 animate-float">
                <div className="w-12 h-12 bg-indigo-50 rounded-full flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-indigo-500" />
                </div>
                <div>
                  <p className="font-bold text-slate-800 leading-tight text-sm">Garantia<br />de Calidad</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Badges - Clean & Minimal */}
      <section className="py-12 border-y border-slate-100 bg-white">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8">
          {[
            { icon: Gem, title: 'Papel Premium', desc: '170g Importado', color: 'text-violet-500' },
            { icon: Shield, title: 'Blindaje', desc: 'Anti-huella y roce', color: 'text-emerald-500' },
            { icon: Palette, title: 'Color Real', desc: 'Impresión profesional', color: 'text-orange-500' },
            { icon: Rocket, title: 'Envio Rapido', desc: 'Todo el pais', color: 'text-blue-500' }
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-4 justify-center md:justify-start">
              <div className="w-12 h-12 bg-slate-50 rounded-full flex items-center justify-center shadow-inner border border-slate-100">
                <item.icon className={`w-5 h-5 ${item.color}`} />
              </div>
              <div>
                <h4 className="font-bold text-slate-800 text-sm">{item.title}</h4>
                <p className="text-xs text-slate-500">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section id="como-funciona" className="py-24 bg-slate-50 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <div className="text-center mb-20">
            <span className="text-secondary font-bold uppercase tracking-widest text-xs mb-2 block font-heading">Simple y Rápido</span>
            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 mb-6">Tu libro en 3 pasos</h2>
            <p className="text-slate-600 max-w-2xl mx-auto text-lg font-light">
              Nuestra tecnología se encarga del diseño difícil. Vos solo elegí tus fotos favoritas.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12 relative">
            {/* Connector Line */}
            <div className="hidden md:block absolute top-12 left-[16%] right-[16%] h-0.5 bg-slate-200 -z-10 bg-[linear-gradient(to_right,transparent_0%,#e2e8f0_50%,transparent_100%)]"></div>

            {[
              { icon: Camera, title: '1. Subi tus fotos', text: 'Desde tu celu o compu. Nuestro sistema las ordena cronologicamente.', color: 'text-blue-500' },
              { icon: Sparkles, title: '2. Personaliza', text: 'Elegi un diseno de nuestra coleccion. Agrega titulos y dedicatorias.', color: 'text-purple-500' },
              { icon: Gift, title: '3. Recibi felicidad', text: 'Imprimimos en alta calidad y te lo enviamos listo para regalar(te).', color: 'text-rose-500' },
            ].map((step, idx) => (
              <div key={idx} className="relative group cursor-default">
                <div className="w-24 h-24 bg-white shadow-xl shadow-slate-200/50 rounded-[2rem] flex items-center justify-center mx-auto mb-8 border border-slate-100 group-hover:-translate-y-2 transition-transform duration-300 relative z-10">
                  <step.icon className={`w-10 h-10 ${step.color}`} />
                  <div className="absolute -top-3 -right-3 w-8 h-8 bg-primary text-white rounded-full flex items-center justify-center font-bold text-sm border-2 border-white shadow-md">
                    {idx + 1}
                  </div>
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-3 text-center">{step.title}</h3>
                <p className="text-slate-500 leading-relaxed text-center px-4 font-light">{step.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Formats (Toggleable) */}
      <section id="precios" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-end mb-16 gap-6">
            <div>
              <h2 className="text-4xl font-display font-bold text-slate-900 mb-2">Nuestros Formatos</h2>
              <p className="text-slate-500 text-lg font-light">
                {showAllFormats ? 'Todos los tamaños disponibles' : 'Los favoritos de nuestros clientes'}
              </p>
            </div>
            <div className="flex gap-4">
              <button onClick={onViewDesigns} className="px-6 py-2 rounded-full border border-slate-200 text-slate-600 font-medium hover:border-primary hover:text-primary transition-colors text-sm">
                Ver Diseños
              </button>
            </div>
          </div>

          <div className={`grid md:grid-cols-3 ${showAllFormats ? 'lg:grid-cols-4' : 'lg:grid-cols-3'} gap-12 transition-all duration-500 items-end`}>
            {(showAllFormats ? PRODUCTS : PRODUCTS.filter(p => ['AP-21x15-DURA', 'CU-21x21-DURA', 'VE-22x28-DURA'].includes(p.codigo))).map((prod, idx) => {
              // Parse dimensions from string like "21 × 14,8 cm"
              const dims = prod.tamanio.split('×').map(s => parseFloat(s.replace(',', '.').replace('cm', '').trim()));
              const width = dims[0];
              const height = dims[1];
              const isVertical = height > width;

              // Scale factor: 41cm (Max XL) = 100%
              const scaleWidth = (width / 41) * 100;
              const aspectRatio = width / height;

              return (
                <div key={idx} className="group flex flex-col items-center">
                  {/* Physical Scale Simulation Container */}
                  <div className="w-full h-64 flex items-end justify-center mb-8 relative">
                    {/* Shadow/Reflections stage */}
                    <div className="absolute bottom-0 w-3/4 h-4 bg-slate-900/5 blur-xl rounded-full"></div>

                    {/* The Book Object */}
                    <div
                      className="relative z-10 bg-white shadow-[0_10px_30px_-5px_rgba(0,0,0,0.15)] group-hover:shadow-[0_20px_50px_-10px_rgba(0,0,0,0.25)] transition-all duration-500 overflow-hidden border border-slate-100 group-hover:-translate-y-2 cursor-pointer"
                      style={{
                        width: `${scaleWidth * 2}%`, // Multiplier to make it look decent in the card
                        aspectRatio: `${aspectRatio}`,
                        maxHeight: '100%',
                        borderRadius: '4px 12px 12px 4px', // Hardcover look
                      }}
                      onClick={onStart}
                    >
                      {/* Spine detail */}
                      <div className="absolute left-0 top-0 bottom-0 w-[4%] bg-slate-900/10 z-20 border-r border-black/5"></div>

                      {/* Image Preview */}
                      <img
                        src={prod.imagen}
                        alt={prod.nombre}
                        className="w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-700"
                      />

                      {/* Premium Overlay for DURA */}
                      {prod.tapa === 'Dura' && (
                        <div className="absolute inset-0 bg-gradient-to-tr from-white/10 to-transparent opacity-50 pointer-events-none"></div>
                      )}

                      {/* Dynamic Badge */}
                      {prod.badge && (
                        <div className="absolute top-2 right-2 z-20">
                          <span className="bg-secondary text-white text-[8px] font-bold py-0.5 px-2 rounded-full uppercase tracking-tighter">
                            {prod.badge}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Info Card */}
                  <div className="text-center w-full">
                    <h3 className="text-xl font-bold text-slate-900 mb-1">{prod.nombre}</h3>
                    <p className="text-slate-400 text-xs font-medium uppercase tracking-widest mb-3">{prod.tamanio}</p>
                    <p className="text-slate-500 text-sm leading-relaxed mb-6 h-10 line-clamp-2 px-4">{prod.descripcion}</p>

                    <div className="flex flex-col items-center gap-4">
                      {/* Specs */}
                      <div className="flex gap-3 text-xs text-slate-500 mb-2">
                        <span className="bg-slate-100 px-2 py-1 rounded-full">{prod.paginasBase} págs</span>
                        <span className={`px-2 py-1 rounded-full ${prod.tapa === 'Dura' ? 'bg-amber-100 text-amber-700' : prod.tapa === 'Simil Cuero' ? 'bg-purple-100 text-purple-700' : 'bg-slate-100 text-slate-600'}`}>Tapa {prod.tapa}</span>
                      </div>
                      
                      <div className="flex items-baseline gap-1">
                        <span className="text-3xl font-bold text-slate-900">${prod.precioBase.toLocaleString()}</span>
                        <span className="text-slate-400 text-xs font-semibold">desde</span>
                      </div>

                      <button
                        onClick={onStart}
                        className="w-full max-w-[200px] py-3.5 bg-slate-900 text-white text-sm font-bold rounded-2xl hover:bg-primary transition-all duration-300 shadow-lg shadow-slate-200 hover:shadow-primary/25 flex justify-center items-center gap-2 group/btn min-h-[48px]"
                      >
                        Comenzar
                        <ChevronRight className="w-4 h-4 group-hover/btn:translate-x-1 transition-transform" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-16 text-center">
            <button
              onClick={() => setShowAllFormats(!showAllFormats)}
              className="inline-flex items-center gap-2 px-8 py-4 bg-slate-100 text-slate-900 font-bold rounded-full hover:bg-slate-200 transition-colors shadow-sm min-h-[56px]"
              aria-expanded={showAllFormats}
            >
              {showAllFormats ? 'Ver menos formatos' : 'Ver todos los formatos'}
              <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${showAllFormats ? 'rotate-180' : ''}`} />
            </button>
          </div>
        </div>
      </section>

      {/* Emotional CTA */}
      <section className="py-32 relative overflow-hidden flex items-center justify-center">
        <div className="absolute inset-0 bg-slate-900">
          <img src="https://images.unsplash.com/photo-1621468635836-494461c17b64?q=80&w=2000&auto=format&fit=crop" className="w-full h-full object-cover opacity-20 mix-blend-overlay" alt="Background" />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-slate-900"></div>
        </div>

        <div className="relative z-10 text-center max-w-3xl px-4">
          <h2 className="text-4xl md:text-6xl font-display font-bold text-white mb-6 tracking-tight">
            No dejes que tus fotos<br />se pierdan en la nube
          </h2>
          <p className="text-xl text-slate-300 mb-10 font-light">
            El mejor momento para imprimir tus recuerdos es ahora. Mañana te vas a agradecer haberlo hecho.
          </p>
          <button
            onClick={onStart}
            className="px-10 py-5 bg-white text-slate-900 text-xl font-bold rounded-full shadow-2xl hover:scale-105 transition-transform flex items-center gap-3 mx-auto min-h-[64px]"
          >
            Comenzar mi libro
            <Sparkles className="w-5 h-5 text-amber-500" />
          </button>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonios" className="py-24 bg-slate-50 relative overflow-hidden">
        <div className="absolute top-1/2 left-0 w-64 h-64 bg-secondary/5 rounded-full blur-[80px] -translate-y-1/2 -translate-x-1/2"></div>
        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <div className="text-center mb-16">
            <span className="text-secondary font-bold uppercase tracking-widest text-xs mb-2 block font-heading">Experiencias Reales</span>
            <h2 className="text-4xl font-display font-bold text-slate-900 mb-4">Lo que dicen nuestros clientes</h2>
            <p className="text-slate-500 max-w-2xl mx-auto font-light">
              Más de 5.000 familias ya eligieron PIKSY para atesorar sus momentos más importantes.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { name: 'María García', location: 'Buenos Aires', quote: 'El fotolibro de mi boda quedó espectacular. La calidad del papel y la impresión superaron todas mis expectativas.', stars: 5, avatar: 'https://i.pravatar.cc/100?img=1' },
              { name: 'Carlos López', location: 'Córdoba', quote: 'Regalé un fotolibro a mis viejos con fotos de toda la familia. ¡Lloraron de emoción! Muy recomendable.', stars: 5, avatar: 'https://i.pravatar.cc/100?img=3' },
              { name: 'Laura Fernández', location: 'Rosario', quote: 'Super fácil de armar. Subí las fotos, elegí el estilo y en 10 días lo tenía en casa. ¡Perfecto!', stars: 5, avatar: 'https://i.pravatar.cc/100?img=5' },
            ].map((t, idx) => (
              <div key={idx} className="bg-white p-8 rounded-3xl shadow-sm border border-slate-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group">
                <div className="flex gap-0.5 mb-4">
                  {Array(t.stars).fill(0).map((_, i) => <Star key={i} className="w-4 h-4 text-amber-400 fill-amber-400" />)}
                </div>
                <p className="text-slate-600 mb-6 leading-relaxed font-light italic">"{t.quote}"</p>
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-slate-100">
                    <img src={t.avatar} alt={t.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                  </div>
                  <div>
                    <h4 className="font-bold text-slate-900 text-sm">{t.name}</h4>
                    <p className="text-slate-400 text-xs">{t.location}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Gallery / Inspiration */}
      <section id="galeria" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center mb-12">
            <span className="text-secondary font-bold uppercase tracking-widest text-xs mb-2 block font-heading">Inspiración</span>
            <h2 className="text-4xl font-display font-bold text-slate-900 mb-4">Nuestros Trabajos</h2>
            <p className="text-slate-500 max-w-2xl mx-auto">Mirá algunos de los fotolibros que creamos para nuestros clientes</p>
          </div>
          
          {/* Category Filters */}
          <div className="flex flex-wrap justify-center gap-3 mb-12">
            {['Todos', 'Viajes', 'Bodas', 'Bebés', 'Familia', 'Cumpleaños'].map((cat) => (
              <button
                key={cat}
                className="px-5 py-2 rounded-full text-sm font-medium transition-all border border-slate-200 hover:border-primary hover:text-primary first:bg-primary first:text-white first:border-primary"
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Masonry Grid */}
          <div className="columns-1 sm:columns-2 lg:columns-3 gap-4 space-y-4">
            {[
              { src: '/gallery/amigas-abierto.jpg', cat: 'Amigas', title: 'Recuerdos Juntas' },
              { src: '/gallery/img-03.jpg', cat: 'Bodas', title: 'Nuestra Boda' },
              { src: '/gallery/primer-anito.jpg', cat: 'Bebés', title: 'Mi Primer Añito' },
              { src: '/gallery/img-02.jpg', cat: 'Viajes', title: 'Miami - NY - Washington' },
              { src: '/gallery/familia-horizontal.jpg', cat: 'Familia', title: 'Nuestros Recuerdos' },
              { src: '/gallery/cuadrado-gris.jpg', cat: 'Premium', title: 'Edición Elegante' },
              { src: '/gallery/girasoles-paz.jpg', cat: 'Familia', title: 'Momentos de Paz' },
              { src: '/gallery/img-01.jpg', cat: 'Viajes', title: 'Nuestros Viajes' },
              { src: '/gallery/pareja-boda.jpg', cat: 'Parejas', title: 'Caro y Berni' },
            ].map((item, idx) => (
              <div key={idx} className="break-inside-avoid group cursor-pointer">
                <div className="relative overflow-hidden rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300">
                  <img 
                    src={item.src} 
                    alt={item.title}
                    className="w-full object-cover group-hover:scale-105 transition-transform duration-500"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <div className="absolute bottom-4 left-4 text-white">
                      <span className="text-xs font-medium bg-white/20 backdrop-blur-sm px-2 py-1 rounded-full">{item.cat}</span>
                      <h4 className="text-lg font-bold mt-2">{item.title}</h4>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <button className="px-8 py-4 bg-slate-100 text-slate-700 font-bold rounded-full hover:bg-slate-200 transition-colors">
              Ver más trabajos
            </button>
          </div>
        </div>
      </section>

      {/* FAQ Enhanced */}
      <section id="faq" className="py-24 bg-slate-50">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-16">
            <span className="text-secondary font-bold uppercase tracking-widest text-xs mb-2 block font-heading">¿Tenés dudas?</span>
            <h2 className="text-3xl font-display font-bold text-slate-900 mb-4">Preguntas Frecuentes</h2>
            <p className="text-slate-500">Todo lo que necesitás saber antes de imprimir tu historia</p>
          </div>
          <div className="space-y-4">
            {[
              { q: '¿Cuánto tarda el envío?', a: 'Entre 10 y 14 días hábiles a todo el país. Te enviamos el código de seguimiento por email para que sepas dónde está tu pedido en todo momento.' },
              { q: '¿Puedo editar después de pagar?', a: 'Tenés 24 horas para solicitar cambios enviándonos un email. Después de ese plazo, el libro entra en proceso de impresión y encuadernación.' },
              { q: '¿Qué garantía tengo?', a: 'Ofrecemos garantía total de satisfacción. Si tu fotolibro tiene algún defecto de fabricación o impresión, lo reimprimimos sin costo alguno para vos.' },
              { q: '¿Cómo envío mis fotos?', a: 'Es muy fácil. Podés subirlas desde tu celular, computadora, Instagram o Google Photos directamente en nuestro editor online. El sistema las ordena automáticamente.' },
              { q: '¿Hacen descuentos por cantidad?', a: 'Si, ofrecemos descuentos especiales para fotógrafos o si pedís más de 3 copias del mismo libro (ideal para regalos familiares).' },
            ].map((faq, idx) => (
              <details key={idx} open={idx < 2} className="bg-white rounded-2xl border border-slate-200 group overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                <summary className="flex items-center justify-between p-6 cursor-pointer font-bold text-slate-800 text-lg select-none min-h-[72px]">
                  {faq.q}
                  <span className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 group-open:bg-primary group-open:text-white transition-all group-open:rotate-180">
                    <ChevronDown className="w-4 h-4" />
                  </span>
                </summary>
                <div className="px-6 pb-6 text-slate-600 leading-relaxed font-light border-t border-slate-50 pt-4">
                  {faq.a}
                </div>
              </details>
            ))}
          </div>
        </div>
      </section>

      {/* Footer Minimal */}
      {/* Footer Pro */}
      <footer className="bg-slate-900 text-white py-20 relative overflow-hidden">
        {/* Decorative Background */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary/5 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/2"></div>
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/5 rounded-full blur-[80px] translate-y-1/2 -translate-x-1/2"></div>

        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <div className="grid md:grid-cols-4 gap-12 mb-16">
            {/* Brand */}
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <img src="/logo.png" alt="PIKSY" className="h-8 brightness-0 invert" />
                <span className="font-display font-bold text-xl tracking-tight">PIKSY</span>
              </div>
              <p className="text-slate-400 text-sm leading-relaxed max-w-xs font-light">
                Transformando galerías digitales en recuerdos tangibles de calidad premium. Guardá tus momentos para siempre.
              </p>
              <div className="flex gap-4">
                {/* Instagram */}
                <a href="https://instagram.com/fotolibrosarg" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-white/5 hover:bg-gradient-to-tr hover:from-purple-500 hover:to-pink-500 rounded-full flex items-center justify-center transition-all duration-300 group">
                  <svg className="w-5 h-5 text-white/70 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                  </svg>
                </a>
                {/* Facebook */}
                <a href="https://facebook.com/fotolibrosarg" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-white/5 hover:bg-[#1877F2] rounded-full flex items-center justify-center transition-all duration-300 group">
                  <svg className="w-5 h-5 text-white/70 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                  </svg>
                </a>
                {/* Whatsapp */}
                <a href="https://wa.me/" target="_blank" rel="noopener noreferrer" className="w-10 h-10 bg-white/5 hover:bg-[#25D366] rounded-full flex items-center justify-center transition-all duration-300 group">
                  <svg className="w-5 h-5 text-white/70 group-hover:text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487 2.155.931 2.593.931 3.056.883 1.137-.118 2.451-1.017 2.898-2.181.446-1.164.446-2.157.322-2.356z" />
                  </svg>
                </a>
              </div>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider text-xs">Navegación</h4>
              <ul className="space-y-3 text-slate-400 text-sm">
                <li><button onClick={onStart} className="hover:text-primary transition-colors flex items-center gap-2 group"><span className="w-1.5 h-1.5 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></span>Crear Fotolibro</button></li>
                <li><button onClick={onViewDesigns} className="hover:text-primary transition-colors flex items-center gap-2 group"><span className="w-1.5 h-1.5 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></span>Ver Diseños</button></li>
                <li><button onClick={onCheckStatus} className="hover:text-primary transition-colors flex items-center gap-2 group"><span className="w-1.5 h-1.5 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></span>Estado de Pedido</button></li>
                <li><a href="#como-funciona" className="hover:text-primary transition-colors flex items-center gap-2 group"><span className="w-1.5 h-1.5 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></span>Cómo Funciona</a></li>
                <li><a href="#precios" className="hover:text-primary transition-colors flex items-center gap-2 group"><span className="w-1.5 h-1.5 rounded-full bg-primary opacity-0 group-hover:opacity-100 transition-opacity"></span>Precios</a></li>
              </ul>
            </div>

            {/* Policies */}
            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider text-xs">Legales</h4>
              <ul className="space-y-3 text-slate-400 text-sm">
                <li><button className="hover:text-primary transition-colors text-left">Términos y Condiciones</button></li>
                <li><button className="hover:text-primary transition-colors text-left">Política de Privacidad</button></li>
                <li><button className="hover:text-primary transition-colors text-left">Política de Envíos</button></li>
                <li><button className="hover:text-primary transition-colors text-left">Cambios y Devoluciones</button></li>
              </ul>
            </div>

            {/* Payments */}
            <div>
              <h4 className="font-bold text-white mb-6 uppercase tracking-wider text-xs">Medios de Pago</h4>
              <div className="space-y-3">
                <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl p-3 hover:bg-white/10 transition-colors cursor-default">
                  <div className="bg-green-500/20 text-green-400 p-1.5 rounded-lg">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0012 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18" />
                    </svg>
                  </div>
                  <div>
                    <span className="text-sm font-bold block text-white">Transferencia</span>
                    <span className="text-[10px] text-green-400 font-bold bg-green-900/40 px-2 py-0.5 rounded-full">15% OFF</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 bg-white/5 border border-white/10 rounded-xl p-3 hover:bg-white/10 transition-colors cursor-default">
                  <div className="bg-[#00B4E5]/20 text-[#00B4E5] p-1.5 rounded-lg">
                    <svg viewBox="0 0 40 20" className="w-5 h-5">
                      <rect width="40" height="20" rx="4" fill="currentColor" />
                      <text x="20" y="14" textAnchor="middle" fill="rgba(255,255,255,0.2)" fontSize="10" fontWeight="800">MODO</text>
                    </svg>
                  </div>
                  <span className="text-sm font-bold block text-white">Pago con QR</span>
                </div>
              </div>
            </div>
          </div>

          <div className="pt-8 border-t border-white/10 flex flex-col md:flex-row justify-between items-center gap-4 text-xs text-slate-500 font-medium">
            <p>© 2026 PIKSY - Piksy.</p>
            <div className="flex items-center gap-6">
              <span className="flex items-center gap-2 text-slate-600"><span className="w-2 h-2 rounded-full bg-green-500"></span> Sistema Operativo</span>
              <button onClick={onAdmin} className="hover:text-white transition-colors">Acceso Admin</button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;

