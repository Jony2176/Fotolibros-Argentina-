
import React, { useState } from 'react';
import { PRODUCTS } from '../constants';
import Book3D from '../components/Book3D';

interface DesignItem {
    id: string;
    name: string;
    category: string;
    image: string; // Cover image for 3D
    openBookImage: string; // Internal spread view
    productCode: string;
    description: string;
    features: string[];
    titleFont?: string;
    titleColor?: string;
}

// Datos enriquecidos con imágenes de "Interior" (Open Book) y features
const DESIGNS_DATA: DesignItem[] = [
    // DÍA DE LA MADRE
    {
        id: 'mama-1',
        name: 'Mamá Flores',
        category: 'día de la madre',
        image: 'https://images.unsplash.com/photo-1490750967868-88aa35a14010?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=800&q=80',
        productCode: 'CU-21x21-DURA',
        description: 'Un homenaje visual lleno de delicadeza. Este diseño combina ilustraciones florales estilo acuarela con espacios amplios para textos emotivos.',
        features: ['Fondos estilo papel texturado', 'Tipografías manuscritas', 'Ideal para fotos familiares espontáneas'],
        titleFont: "'Caveat', cursive",
        titleColor: '#ff69b4'
    },
    {
        id: 'mama-2',
        name: 'Mamá Minimal',
        category: 'día de la madre',
        image: 'https://images.unsplash.com/photo-1491438590914-bc09fcaaf77a?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=800&q=80',
        productCode: 'AP-21x15-DURA',
        description: 'La belleza de lo simple. Un diseño donde tus fotos son las absolutas protagonistas, sin distracciones.',
        features: ['Diseño limpio y aireado', 'Marcos finos en gris plomo', 'Elegancia atemporal'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#333'
    },

    // VIAJES
    {
        id: 'viaje-1',
        name: 'Aventuras',
        category: 'viajes',
        image: 'https://images.unsplash.com/photo-1527631746610-bca00a040d60?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1452421822248-d4c2b47f0c81?w=800&q=80',
        productCode: 'AP-28x22-DURA',
        description: 'Tu bitácora de viaje definitiva. Incluye gráficos de mapas, sellos postales y layouts tipo collage.',
        features: ['Gráficos de brújulas y mapas', 'Espacio para crónicas de viaje', 'Layouts dinámicos'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: 'white'
    },
    {
        id: 'viaje-2',
        name: 'Playa Soul',
        category: 'viajes',
        image: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1519681393784-d120267933ba?w=800&q=80',
        productCode: 'CU-29x29-DURA',
        description: 'Reviví el verano eterno. Tonos cálidos, arenas y azules profundos para tus fotos de mar.',
        features: ['Paleta de colores cálida', 'Filtros solares suaves', 'Perfecto para paisajes'],
        titleFont: "'Caveat', cursive",
        titleColor: '#0077be'
    },

    // BODA
    {
        id: 'boda-1',
        name: 'Eternidad',
        category: 'boda',
        image: 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1537905569824-f89f14cceb68?w=800&q=80',
        productCode: 'CU-29x29-CUERO',
        description: 'Lujo y sofisticación para el día más importante. Encuadernación con detalles premium y layouts clásicos.',
        features: ['Estilo editorial de revista', 'Tipografía Serif clásica', 'Márgenes generosos'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#d4af37'
    },

    // NIÑOS
    {
        id: 'ninos-1',
        name: 'Mundo Mágico',
        category: 'niños',
        image: 'https://images.unsplash.com/photo-1621468635836-494461c17b64?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1603504381735-8b83526786a3?w=800&q=80',
        productCode: 'CU-21x21-BLANDA',
        description: 'Un diseño lleno de color y fantasía para capturar esos momentos de risas y juegos.',
        features: ['Colores vibrantes', 'Elementos gráficos divertidos', 'Resistente y alegre'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#ff4500'
    },

    // ENAMORADOS
    {
        id: 'enamorados-1',
        name: 'Love Story',
        category: 'día de los enamorados',
        image: 'https://images.unsplash.com/photo-1518568814500-bf0f8d125f46?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1518134261730-8d5c41253509?w=800&q=80',
        productCode: 'CU-21x21-DURA',
        description: 'Para celebrar cada capítulo de su historia de amor.',
        features: ['Romántico y sutil', 'Detalles de corazón', 'Perfecto para aniversarios'],
        titleFont: "'Caveat', cursive",
        titleColor: '#e0115f'
    },

    // FAMILIA
    {
        id: 'familia-1',
        name: 'Legado',
        category: 'familia',
        image: 'https://images.unsplash.com/photo-1511895426328-dc8714191300?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1574895058862-233bb3294025?w=800&q=80',
        productCode: 'AP-28x22-DURA',
        description: 'Un libro robusto para pasar de generación en generación.',
        features: ['Diseño clásico y sobrio', 'Cuidada maquetación', 'Ideal para árboles genealógicos'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#fff'
    },

    // POSTALES
    {
        id: 'postales-1',
        name: 'Urban Life',
        category: 'postales',
        image: 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1502472584811-0a2f2ca8f6cf?w=800&q=80',
        productCode: 'VE-22x28-BLANDA',
        description: 'Tus mejores fotos callejeras merecen este formato.',
        features: ['Estilo moderno', 'Papel mate', 'Ideal para blanco y negro'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: 'white'
    },

    // DÍA DEL PADRE
    {
        id: 'padre-1',
        name: 'Papá Héroe',
        category: 'día del padre',
        image: 'https://images.unsplash.com/photo-1484515991647-c5760fcecfc7?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1549633030-89d0743bad01?w=800&q=80',
        productCode: 'VE-22x28-DURA',
        description: 'Elegante, sobrio y con carácter. El regalo perfecto para papá.',
        features: ['Colores oscuros y masculinos', 'Tipografías fuertes', 'Acabado premium'],
        titleFont: "'Playfair Display', serif",
        titleColor: '#2c3e50'
    },

    // CUMPLEAÑOS
    {
        id: 'cumple-1',
        name: 'Fiesta',
        category: 'cumpleaños',
        image: 'https://images.unsplash.com/photo-1530103043960-ef38714abb15?w=800&q=80',
        openBookImage: 'https://images.unsplash.com/photo-1513151233558-d860c5398176?w=800&q=80',
        productCode: 'CU-21x21-DURA',
        description: '¡Que los cumplas feliz! Un diseño tan alegre como el festejo.',
        features: ['Colorido festivo', 'Diseños de globos y tortas', 'Ideal para todas las edades'],
        titleFont: "'Montserrat', sans-serif",
        titleColor: '#9b59b6'
    },
];

const CATEGORIES = [
    { id: 'día de la madre', name: 'Día de la Madre', emoji: '👩‍👧‍👦', image: 'https://images.unsplash.com/photo-1490750967868-88aa35a14010?w=600&q=80', description: 'Regalos llenos de amor y recuerdos.' },
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
        <div className="min-h-screen bg-cream animate-fade-in pb-20 font-sans">
            {/* Navigation & Header */}
            <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100/50">
                <div className="max-w-7xl mx-auto px-4 h-20 flex items-center justify-between">
                    <button
                        onClick={viewMode === 'designs' ? handleBackToCategories : onBack}
                        className="group flex items-center gap-2 text-gray-500 hover:text-primary transition-all p-2 rounded-lg hover:bg-gray-50"
                    >
                        <span className="text-xl transform group-hover:-translate-x-1 transition-transform">←</span>
                        <span className="font-medium tracking-wide">{viewMode === 'designs' ? 'Galería' : 'Inicio'}</span>
                    </button>

                    {/* LOGO CLICKABLE */}
                    <button onClick={onBack} className="focus:outline-none transition-opacity hover:opacity-80">
                        <img src="/logo.png" alt="PIKSY" className="h-10 cursor-pointer" />
                    </button>

                    <div className="w-24"></div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-4 py-8">

                {/* HERO TEXT */}
                <div className="text-center mb-20 mt-8">
                    <h1 className="text-5xl md:text-7xl font-display font-bold text-primary mb-6 tracking-tight">
                        {viewMode === 'categories' ? (
                            <>Historias <span className="text-secondary font-serif italic font-normal">hechas libro</span></>
                        ) : (
                            <>{activeCategory?.name} <span className="text-secondary font-serif italic font-normal">Collection</span></>
                        )}
                    </h1>
                    <p className="text-gray-500 text-lg md:text-xl max-w-2xl mx-auto font-light leading-relaxed">
                        {viewMode === 'categories'
                            ? "Cada momento merece un diseño único. Explorá nuestras colecciones temáticas y encontrá la inspiración perfecta."
                            : activeCategory?.description
                        }
                    </p>
                </div>

                {/* CATEGORIES GRID (Main View) */}
                {viewMode === 'categories' && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 px-2 md:px-8 animate-fade-in-up">
                        {CATEGORIES.map((cat, index) => (
                            <div
                                key={cat.id}
                                onClick={() => handleSelectCategory(cat.id)}
                                className="group relative cursor-pointer rounded-[2rem] overflow-hidden aspect-[3/4] shadow-sm hover:shadow-2xl transition-all duration-700"
                                style={{ animationDelay: `${index * 100}ms` }}
                            >
                                <img
                                    src={cat.image}
                                    alt={cat.name}
                                    className="w-full h-full object-cover transform group-hover:scale-110 transition-transform duration-[1.5s] ease-out"
                                />
                                <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent opacity-80 group-hover:opacity-90 transition-opacity"></div>

                                <div className="absolute bottom-0 left-0 right-0 p-8 transform translate-y-2 group-hover:translate-y-0 transition-transform duration-500">
                                    <span className="text-4xl mb-3 block transform group-hover:scale-110 transition-transform origin-left">{cat.emoji}</span>
                                    <h3 className="text-white font-display font-bold text-3xl mb-2">{cat.name}</h3>
                                    <p className="text-white/80 font-light text-sm mb-4 line-clamp-2 max-w-[80%]">{cat.description}</p>
                                    <span className="inline-block border border-white/30 text-white px-5 py-2 rounded-full text-xs font-bold uppercase tracking-widest backdrop-blur-sm hover:bg-white hover:text-black transition-all">
                                        Ver Colección
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* EDITORIAL DETAIL VIEW (Zig-Zag) */}
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
                                    <div key={design.id} className={`flex flex-col md:flex-row items-center gap-12 md:gap-24 ${isOdd ? 'md:flex-row-reverse' : ''}`}>

                                        {/* VISUALS SIDE */}
                                        <div className="w-full md:w-1/2 relative group perspective-1000">
                                            {/* Open Book (Background/Main) */}
                                            <div className="relative z-10 rounded-2xl overflow-hidden shadow-2xl rotate-1 hover:rotate-0 transition-transform duration-700">
                                                <img
                                                    src={design.openBookImage}
                                                    alt={`${design.name} interior`}
                                                    className="w-full h-auto object-cover"
                                                />
                                                {/* Overlay Text hint */}
                                                <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur text-xs px-3 py-1 rounded-full shadow-sm text-gray-500 font-medium">
                                                    Vista Interior
                                                </div>
                                            </div>

                                            {/* 3D Cover (Floating Overlay) */}
                                            <div className={`absolute -bottom-10 w-48 shadow-2xl z-20 transform transition-transform duration-700 hover:scale-105 ${isOdd ? '-left-8 rotate-3' : '-right-8 -rotate-3'}`}>
                                                <div className="aspect-[3/4] bg-transparent">
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

                                        {/* TEXT SIDE */}
                                        <div className="w-full md:w-1/2 space-y-8">
                                            <div>
                                                <span className="text-secondary font-bold uppercase tracking-widest text-xs mb-2 block font-heading">
                                                    Estilo Destacado
                                                </span>
                                                <h2 className="text-4xl md:text-5xl font-display font-bold text-primary mb-6">
                                                    {design.name}
                                                </h2>
                                                <p className="text-gray-600 text-lg leading-relaxed font-light mb-8">
                                                    {design.description}
                                                </p>

                                                <ul className="space-y-3 mb-8">
                                                    {design.features && design.features.map((feature, i) => (
                                                        <li key={i} className="flex items-center gap-3 text-gray-500 font-medium">
                                                            <span className="w-6 h-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-xs">✓</span>
                                                            {feature}
                                                        </li>
                                                    ))}
                                                </ul>
                                            </div>

                                            {/* SOFT CTA */}
                                            <div className="pt-6 border-t border-gray-100">
                                                <p className="text-sm text-gray-400 mb-3 font-bold uppercase tracking-wider">Te gusta este formato?</p>
                                                <button
                                                    onClick={() => onSelectDesign(design.productCode)}
                                                    className="group bg-primary hover:bg-gray-800 text-white px-8 py-4 rounded-full font-bold transition-all shadow-lg hover:shadow-xl flex items-center gap-3 active:scale-95 w-full md:w-auto justify-center"
                                                >
                                                    Empezar en {product?.tamanio} {product?.tapa}
                                                    <span className="group-hover:translate-x-1 transition-transform">→</span>
                                                </button>
                                                <p className="text-xs text-gray-400 mt-2 text-center md:text-left">
                                                    Se aplicará el formato {product?.codigo.split('-')[0]} {product?.tamanio}. Elegí tu estilo en el siguiente paso.
                                                </p>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })
                        ) : (
                            <div className="text-center py-32 opacity-50">
                                <h3 className="text-2xl font-bold text-gray-300 mb-2">Próximamente más diseños</h3>
                                <p className="text-gray-400">Estamos fotografiando nuevas colecciones para {activeCategory?.name}.</p>
                                <button onClick={handleBackToCategories} className="mt-8 text-primary font-bold hover:underline">← Volver al catálogo</button>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
};

export default Designs;
