import React, { useState, useEffect } from 'react';
import { ArrowLeft, ChevronRight, Check, Sparkles } from 'lucide-react';
import { PRODUCTS } from '../constants';
import Book3D from '../components/Book3D';

interface DesignItem {
    id: string;
    name: string;
    category: string;
    image: string;
    openBookImage: string;
    productCode: string;
    description: string;
    features: string[];
    titleFont?: string;
    titleColor?: string;
}

const DESIGNS_DATA: DesignItem[] = [
    // DÍA DE LA MADRE
    {
        id: 'mama-1',
        name: 'Mamá Flores',
        category: 'día de la madre',
        image: '/gallery/blanda-vertical.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'VE-22x28-BLANDA',
        description: 'Un homenaje visual lleno de delicadeza. Diseño estilo revista fino y elegante.',
        features: ['Tapa blanda estilo revista', 'Tipografías manuscritas', 'Ideal para fotos familiares'],
        titleFont: "'Caveat', cursive",
        titleColor: '#ff69b4'
    },
    {
        id: 'mama-2',
        name: 'Recuerdos Familia',
        category: 'día de la madre',
        image: '/gallery/bebe-vertical.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'AP-28x22-DURA',
        description: 'Tapa dura premium para los momentos más especiales con mamá.',
        features: ['Tapa dura resistente', 'Formato grande apaisado', 'Ideal para muchas fotos'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#333'
    },
    // VIAJES
    {
        id: 'viaje-1',
        name: 'Verano 2024',
        category: 'viajes',
        image: '/gallery/verano-2024.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'AP-21x15-DURA',
        description: 'Collage colorido para tus mejores vacaciones. Formato apaisado ideal para paisajes.',
        features: ['Diseño collage moderno', 'Colores vibrantes', 'Perfecto para vacaciones'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: 'white'
    },
    {
        id: 'viaje-2',
        name: 'Summer Memories',
        category: 'viajes',
        image: '/gallery/blanda-apaisado.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'AP-21x15-BLANDA',
        description: 'Tapa blanda estilo revista. Ligero y práctico para llevar a todos lados.',
        features: ['Tapa blanda fina', 'Formato pocket', 'Económico y elegante'],
        titleFont: "'Caveat', cursive",
        titleColor: '#0077be'
    },
    {
        id: 'viaje-3',
        name: 'Aventuras Scrapbook',
        category: 'viajes',
        image: '/gallery/img-02.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'CU-29x29-DURA',
        description: 'Estilo scrapbook con mapas y sellos postales. Gran formato cuadrado.',
        features: ['Estilo scrapbook', 'Formato grande 29x29', 'Gráficos de viaje'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#2c3e50'
    },
    // BODA
    {
        id: 'boda-1',
        name: 'Nuestra Boda',
        category: 'boda',
        image: '/gallery/img-03.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'CU-21x21-DURA',
        description: 'El clásico elegante para el día más importante.',
        features: ['Diseño clásico', 'Tipografía elegante', 'Formato cuadrado'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#d4af37'
    },
    {
        id: 'boda-2',
        name: 'Premium Cuero',
        category: 'boda',
        image: '/gallery/premium-cuero-negro.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'CU-29x29-CUERO',
        description: 'Lujo y sofisticación. Encuadernación símil cuero negro premium.',
        features: ['Tapa símil cuero', 'Hasta 160 páginas', 'Acabado premium'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#d4af37'
    },
    {
        id: 'boda-3',
        name: 'Love Story',
        category: 'boda',
        image: '/gallery/blanda-cuadrado.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'CU-21x21-BLANDA',
        description: 'Romántico y delicado. Tapa blanda estilo revista.',
        features: ['Tapa blanda fina', 'Diseño romántico', 'Económico'],
        titleFont: "'Caveat', cursive",
        titleColor: '#e0115f'
    },
    // NIÑOS
    {
        id: 'ninos-1',
        name: 'Mi Primer Añito',
        category: 'niños',
        image: '/gallery/primer-anito.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'CU-21x21-DURA',
        description: 'Diseño tierno y colorido para el primer año del bebé.',
        features: ['Colores pasteles', 'Diseño infantil', 'Tapa dura resistente'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#ff69b4'
    },
    {
        id: 'ninos-2',
        name: 'Graduación',
        category: 'niños',
        image: '/gallery/graduacion-vertical.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'VE-22x28-DURA',
        description: 'Para celebrar los logros de los más pequeños.',
        features: ['Formato vertical A4', 'Tapa dura', 'Diseño formal'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#2c3e50'
    },
    {
        id: 'ninos-3',
        name: 'Souvenir Pack x12',
        category: 'niños',
        image: '/gallery/souvenir-pack.jpg',
        openBookImage: '/gallery/souvenir-pack.jpg',
        productCode: 'SV-10x10-PACK12',
        description: '12 libritos iguales para regalar a los invitados.',
        features: ['Pack de 12 unidades', 'Tamaño bolsillo 10x10', 'Ideal para eventos'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#4a90d9'
    },
    // ENAMORADOS
    {
        id: 'enamorados-1',
        name: 'Caro y Berni',
        category: 'día de los enamorados',
        image: '/gallery/img-01.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'CU-21x21-DURA',
        description: 'Para celebrar cada capítulo de su historia de amor.',
        features: ['Foto de portada completa', 'Formato cuadrado', 'Diseño moderno'],
        titleFont: "'Caveat', cursive",
        titleColor: '#e0115f'
    },
    {
        id: 'enamorados-2',
        name: 'Our Love Story',
        category: 'día de los enamorados',
        image: '/gallery/blanda-cuadrado.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'CU-21x21-BLANDA',
        description: 'Tapa blanda romántica estilo revista.',
        features: ['Tapa blanda fina', 'Diseño romántico', 'Precio accesible'],
        titleFont: "'Caveat', cursive",
        titleColor: '#e0115f'
    },
    // FAMILIA
    {
        id: 'familia-1',
        name: 'Nuestros Recuerdos',
        category: 'familia',
        image: '/gallery/bebe-vertical.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'AP-28x22-DURA',
        description: 'Un libro robusto para pasar de generación en generación.',
        features: ['Gran formato apaisado', 'Tapa dura premium', 'Para muchas fotos'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#1a365d'
    },
    {
        id: 'amigos-1',
        name: 'Amigas Forever',
        category: 'amigos',
        image: '/gallery/amigas-abierto.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'AP-41x29-DURA',
        description: 'Formato Maxi para ver cada detalle de los momentos especiales.',
        features: ['Tamaño máximo 41x29', 'Tapa dura', 'Impresión espectacular'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#333'
    },
    // DÍA DEL PADRE
    {
        id: 'padre-1',
        name: 'Papá Premium',
        category: 'día del padre',
        image: '/gallery/premium-cuero-apaisado.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'AP-41x29-CUERO',
        description: 'Elegante símil cuero negro. El regalo perfecto para papá.',
        features: ['Símil cuero negro', 'Formato Maxi apaisado', 'Hasta 160 páginas'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#2c3e50'
    },
    {
        id: 'padre-2',
        name: 'Momentos con Papá',
        category: 'día del padre',
        image: '/gallery/verano-2024.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'AP-21x15-DURA',
        description: 'Colorido y alegre para los mejores recuerdos.',
        features: ['Formato pocket apaisado', 'Tapa dura', 'Diseño collage'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: 'white'
    },
    // CUMPLEAÑOS
    {
        id: 'cumple-1',
        name: 'My 1st Birthday',
        category: 'cumpleaños',
        image: '/gallery/souvenir-pack.jpg',
        openBookImage: '/gallery/souvenir-pack.jpg',
        productCode: 'SV-10x10-PACK12',
        description: 'Pack de souvenirs para el primer añito.',
        features: ['12 libritos iguales', 'Tamaño mini 10x10', 'Perfecto para regalar'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#4a90d9'
    },
    {
        id: 'cumple-2',
        name: 'Fiesta',
        category: 'cumpleaños',
        image: '/gallery/primer-anito.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'CU-21x21-DURA',
        description: 'Diseño festivo y colorido para cualquier edad.',
        features: ['Colores alegres', 'Formato cuadrado', 'Tapa dura'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#9b59b6'
    },
    // POSTALES
    {
        id: 'postales-1',
        name: 'Viajes Elegante',
        category: 'viajes',
        image: '/gallery/img-05.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'AP-28x22-DURA',
        description: 'Diseño minimalista con ventana en la tapa.',
        features: ['Ventana en portada', 'Estilo elegante', 'Formato grande'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#666'
    },
    {
        id: 'postales-2',
        name: 'Urban Vertical',
        category: 'postales',
        image: '/gallery/blanda-vertical.jpg',
        openBookImage: '/gallery/amigas-abierto.jpg',
        productCode: 'VE-22x28-BLANDA',
        description: 'Tus mejores fotos en formato revista vertical.',
        features: ['Tapa blanda fina', 'Formato A4 vertical', 'Estilo moderno'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: 'white'
    }
];

const CATEGORIES = [
    { id: 'amigos', name: 'Amigos', emoji: '👯', image: 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&q=80', description: 'Los mejores momentos con tus amigos.' },
    { id: 'día de la madre', name: 'Día de la Madre', emoji: '👩‍👧‍👦', image: 'https://images.unsplash.com/photo-1476703993599-0035a21b17a9?w=600&q=80', description: 'Regalos llenos de amor y recuerdos.' },
    { id: 'viajes', name: 'Viajes', emoji: '✈️', image: 'https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&q=80', description: 'Tus aventuras merecen ser contadas.' },
    { id: 'boda', name: 'Boda', emoji: '💒', image: 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=600&q=80', description: 'El comienzo de su historia juntos.' },
    { id: 'niños', name: 'Niños', emoji: '🧸', image: 'https://images.unsplash.com/photo-1621468635836-494461c17b64?w=600&q=80', description: 'Crecen muy rápido, guardá cada momento.' },
    { id: 'día de los enamorados', name: 'Enamorados', emoji: '❤️', image: 'https://images.unsplash.com/photo-1518568814500-bf0f8d125f46?w=600&q=80', description: 'Celebra el amor todos los días.' },
    { id: 'familia', name: 'Familia', emoji: '🏡', image: 'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=600&q=80', description: 'La historia de tu legado.' },
    { id: 'día del padre', name: 'Día del Padre', emoji: '🧔', image: 'https://images.unsplash.com/photo-1484515991647-c5760fcecfc7?w=600&q=80', description: 'Para el mejor papá del mundo.' },
    { id: 'cumpleaños', name: 'Cumpleaños', emoji: '🎂', image: 'https://images.unsplash.com/photo-1530103043960-ef38714abb15?w=600&q=80', description: 'Celebra un año más de vida.' },
    { id: 'postales', name: 'Estilo Postal', emoji: '📮', image: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=600&q=80', description: 'Tus fotos con un toque urbano.' },
];

interface DesignsProps {
    onBack: () => void;
    onSelectDesign: (productCode: string) => void;
}

const Designs: React.FC<DesignsProps> = ({ onBack, onSelectDesign }) => {
    const [viewMode, setViewMode] = useState<'categories' | 'designs'>('categories');
    const [selectedCategory, setSelectedCategory] = useState<string>('');
    const [isScrolled, setIsScrolled] = useState(false);

    useEffect(() => {
        const handleScroll = () => setIsScrolled(window.scrollY > 20);
        window.addEventListener('scroll', handleScroll);
        return () => window.removeEventListener('scroll', handleScroll);
    }, []);

    const filteredDesigns = DESIGNS_DATA.filter(d => d.category === selectedCategory);
    const activeCategory = CATEGORIES.find(c => c.id === selectedCategory);

    const handleSelectCategory = (id: string) => {
        setSelectedCategory(id);
        setViewMode('designs');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleBackToCategories = () => {
        setViewMode('categories');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900 selection:bg-primary/20">
            {/* Header Glassmorphism - Same as Landing */}
            <header className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${isScrolled
                ? 'bg-white/80 backdrop-blur-md shadow-lg border-b border-white/20 py-3'
                : 'bg-transparent py-5'
            }`}>
                <div className="max-w-7xl mx-auto px-4 md:px-6 flex justify-between items-center">
                    <button
                        onClick={viewMode === 'designs' ? handleBackToCategories : onBack}
                        className="group flex items-center gap-2 text-slate-600 hover:text-primary transition-all p-2 rounded-lg hover:bg-slate-100/50 min-h-[44px]"
                    >
                        <ArrowLeft className="w-5 h-5 transform group-hover:-translate-x-1 transition-transform" />
                        <span className="font-medium">{viewMode === 'designs' ? 'Galería' : 'Inicio'}</span>
                    </button>

                    <button onClick={onBack} className="flex items-center gap-2 group cursor-pointer leading-none focus:outline-none">
                        <img src="/logo.png" alt="Piksy" className="h-8 md:h-10 transition-transform duration-300 group-hover:scale-105" />
                    </button>

                    <div className="w-24 flex justify-end">
                        <button
                            onClick={onBack}
                            className="px-6 py-2.5 bg-primary text-white font-semibold rounded-xl shadow-lg shadow-primary/30 hover:shadow-xl hover:shadow-primary/40 hover:-translate-y-0.5 transition-all duration-300 active:scale-95 text-sm"
                        >
                            Comenzar
                        </button>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <section className="pt-32 pb-16 md:pt-40 md:pb-20 px-4 relative overflow-hidden">
                {/* Background Gradients */}
                <div className="absolute top-0 right-0 w-[50vw] h-[50vw] bg-purple-500/5 rounded-full blur-[120px] -translate-y-1/2 translate-x-1/2 -z-10"></div>
                <div className="absolute bottom-0 left-0 w-[40vw] h-[40vw] bg-primary/5 rounded-full blur-[100px] translate-y-1/2 -translate-x-1/2 -z-10"></div>

                <div className="max-w-7xl mx-auto text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white border border-primary/10 rounded-full text-xs font-bold tracking-wider uppercase shadow-sm text-primary mb-8">
                        <Sparkles className="w-4 h-4" />
                        Colecciones Exclusivas
                    </div>

                    <h1 className="text-5xl md:text-7xl font-display font-bold leading-[1.1] text-slate-900 tracking-tight mb-6">
                        {viewMode === 'categories' ? (
                            <>
                                Historias{' '}
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600">
                                    hechas libro
                                </span>
                            </>
                        ) : (
                            <>
                                {activeCategory?.name}{' '}
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary to-purple-600">
                                    Collection
                                </span>
                            </>
                        )}
                    </h1>

                    <p className="text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto font-light">
                        {viewMode === 'categories'
                            ? "Cada momento merece un diseño único. Explorá nuestras colecciones temáticas y encontrá la inspiración perfecta."
                            : activeCategory?.description
                        }
                    </p>
                </div>
            </section>

            <main className="max-w-7xl mx-auto px-4 pb-20">
                {/* CATEGORIES GRID */}
                {viewMode === 'categories' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 animate-fade-in-up">
                        {CATEGORIES.map((cat, index) => (
                            <div
                                key={cat.id}
                                onClick={() => handleSelectCategory(cat.id)}
                                className="group relative cursor-pointer rounded-3xl overflow-hidden aspect-[3/4] shadow-xl hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 bg-white"
                                style={{ animationDelay: `${index * 80}ms` }}
                            >
                                <img
                                    src={cat.image}
                                    alt={cat.name}
                                    className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-[1.2s] ease-out"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-slate-900/90 via-slate-900/30 to-transparent"></div>

                                <div className="absolute bottom-0 left-0 right-0 p-8">
                                    <span className="text-5xl mb-4 block filter drop-shadow-lg">{cat.emoji}</span>
                                    <h3 className="text-white font-display font-bold text-3xl mb-2 tracking-tight">{cat.name}</h3>
                                    <p className="text-white/70 font-light text-sm mb-6 line-clamp-2">{cat.description}</p>
                                    <span className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md text-white px-5 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider border border-white/20 group-hover:bg-white group-hover:text-slate-900 transition-all">
                                        Ver Colección
                                        <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* DESIGNS DETAIL VIEW */}
                {viewMode === 'designs' && (
                    <div className="space-y-32 animate-fade-in">
                        {filteredDesigns.length > 0 ? (
                            filteredDesigns.map((design, index) => {
                                const isOdd = index % 2 !== 0;
                                const product = PRODUCTS.find(p => p.codigo === design.productCode);
                                const sizeMatch = product?.tamanio.match(/(\d+(?:,\d+)?)\s*×\s*(\d+(?:,\d+)?)/);
                                const bookWidth = sizeMatch ? parseFloat(sizeMatch[1].replace(',', '.')) : 21;
                                const bookHeight = sizeMatch ? parseFloat(sizeMatch[2].replace(',', '.')) : 21;

                                return (
                                    <div key={design.id} className={`flex flex-col md:flex-row items-center gap-12 md:gap-20 ${isOdd ? 'md:flex-row-reverse' : ''}`}>
                                        {/* VISUALS */}
                                        <div className="w-full md:w-1/2 relative group">
                                            <div className="relative z-10 rounded-3xl overflow-hidden shadow-2xl border border-slate-100">
                                                <img
                                                    src={design.openBookImage}
                                                    alt={`${design.name} interior`}
                                                    className="w-full h-auto object-cover transform group-hover:scale-105 transition-transform duration-700"
                                                />
                                                <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-md text-xs font-bold uppercase tracking-wider px-4 py-2 rounded-full shadow-lg text-slate-700 flex items-center gap-2">
                                                    <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                                                    Vista Interior
                                                </div>
                                            </div>

                                            <div className={`absolute -bottom-8 w-48 shadow-2xl z-20 transform transition-all duration-500 hover:scale-105 ${isOdd ? '-left-6 rotate-3' : '-right-6 -rotate-3'}`}>
                                                <div className="aspect-[3/4]">
                                                    <Book3D
                                                        width={bookWidth}
                                                        height={bookHeight}
                                                        coverType={product?.tapa as any || 'Dura'}
                                                        imageUrl={design.image}
                                                        title={design.name}
                                                        titleFont={design.titleFont}
                                                        titleColor={design.titleColor}
                                                        className="h-full"
                                                    />
                                                </div>
                                            </div>
                                        </div>

                                        {/* TEXT */}
                                        <div className="w-full md:w-1/2 space-y-6">
                                            <div className="flex items-center gap-3 mb-4">
                                                <span className="px-3 py-1.5 bg-primary/10 text-primary rounded-full text-xs font-bold uppercase tracking-wider">
                                                    Destacado
                                                </span>
                                            </div>

                                            <h2 className="text-4xl md:text-5xl font-display font-bold text-slate-900 tracking-tight">
                                                {design.name}
                                            </h2>

                                            <p className="text-slate-600 text-lg leading-relaxed font-light">
                                                {design.description}
                                            </p>

                                            <ul className="space-y-3 py-4">
                                                {design.features.map((feature, i) => (
                                                    <li key={i} className="flex items-center gap-3 text-slate-600">
                                                        <span className="w-6 h-6 rounded-full bg-green-50 text-green-600 flex items-center justify-center border border-green-100">
                                                            <Check className="w-3.5 h-3.5" />
                                                        </span>
                                                        {feature}
                                                    </li>
                                                ))}
                                            </ul>

                                            <div className="pt-6 border-t border-slate-200 flex flex-col sm:flex-row gap-4">
                                                <button
                                                    onClick={() => onSelectDesign(design.productCode)}
                                                    className="flex-1 bg-primary hover:bg-primary/90 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 flex items-center justify-center gap-2 active:scale-95"
                                                >
                                                    Empezar Diseño
                                                    <ChevronRight className="w-4 h-4" />
                                                </button>
                                                <div className="px-6 py-4 rounded-xl border border-slate-200 bg-white flex flex-col justify-center">
                                                    <span className="text-xs text-slate-400 uppercase font-bold tracking-wider">Formato</span>
                                                    <span className="text-slate-900 font-semibold">{product?.tamanio} {product?.tapa}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })
                        ) : (
                            <div className="text-center py-32">
                                <h3 className="text-2xl font-bold text-slate-400 mb-2">Próximamente más diseños</h3>
                                <p className="text-slate-500 mb-8">Estamos preparando nuevas colecciones para {activeCategory?.name}.</p>
                                <button 
                                    onClick={handleBackToCategories} 
                                    className="text-primary font-semibold hover:underline flex items-center gap-2 mx-auto"
                                >
                                    <ArrowLeft className="w-4 h-4" />
                                    Volver al catálogo
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </main>

            {/* Footer */}
            <footer className="bg-slate-900 text-white py-12">
                <div className="max-w-7xl mx-auto px-4 text-center">
                    <img src="/logo.png" alt="PIKSY" className="h-8 mx-auto mb-4 brightness-0 invert" />
                    <p className="text-slate-400 text-sm">© 2026 PIKSY - Tus recuerdos impresos</p>
                </div>
            </footer>
        </div>
    );
};

export default Designs;
