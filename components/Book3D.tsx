import React from 'react';

interface Book3DProps {
    width: number;  // ancho en cm
    height: number; // alto en cm
    coverType: 'Blanda' | 'Dura' | 'Simil Cuero';
    color?: string;
    imageUrl?: string;
    title?: string;
    className?: string;
}

/**
 * Componente que renderiza un libro 3D con proporciones reales.
 * El tamaño visual se escala proporcionalmente manteniendo la relación de aspecto.
 */
const Book3D: React.FC<Book3DProps> = ({
    width,
    height,
    coverType,
    color = '#1a365d',
    imageUrl,
    title,
    className = ''
}) => {
    // Escala fija base: 4.5px por cm
    let scale = 4.5;

    // Si el libro es muy grande (ej: > 35cm de ancho), reducimos un poco la escala 
    // para que quepa en la tarjeta sin perder la proporción relativa
    if (width > 30 || height > 30) {
        scale = 3.5;
    }

    // Limitamos el ancho máximo visual para evitar desbordes excesivos
    const MAX_VISUAL_WIDTH = 140;
    let bookWidth = width * scale;
    let bookHeight = height * scale;

    if (bookWidth > MAX_VISUAL_WIDTH) {
        const reductionFactor = MAX_VISUAL_WIDTH / bookWidth;
        bookWidth = MAX_VISUAL_WIDTH;
        bookHeight = bookHeight * reductionFactor;
    }

    // Grosor del lomo basado en tipo de tapa
    const spineThickness = coverType === 'Blanda' ? 6 : coverType === 'Dura' ? 14 : 16;

    // Determinar estilos de tapa según tipo
    const isLeather = coverType === 'Simil Cuero';
    const isSoft = coverType === 'Blanda';

    // Si es simil cuero, forzamos color negro/gris oscuro. Si no, usamos el color o imagen
    const baseColor = isLeather ? '#1a1a1a' : color;

    // Tapa blanda: Lomo continuo. Tapa dura: Lomo más oscuro
    const coverGradient = `linear-gradient(135deg, ${baseColor} 0%, ${adjustBrightness(baseColor, -30)} 100%)`;
    const spineGradient = isSoft
        ? `linear-gradient(90deg, ${adjustBrightness(baseColor, -10)} 0%, ${baseColor} 40%, ${adjustBrightness(baseColor, -20)} 100%)`
        : `linear-gradient(90deg, ${adjustBrightness(baseColor, -40)} 0%, ${adjustBrightness(baseColor, -20)} 50%, ${adjustBrightness(baseColor, -40)} 100%)`;
    const pagesColor = '#f5f5f5';

    // Tapa dura: Esquinas rectas y lomo definido. 
    // Tapa blanda: Puede tener mínima curvatura pero ahora se pide rectas también.
    const borderRadius = '1px'; // Esquinas filosas, casi 0

    return (
        <div
            className={`relative ${className}`}
            style={{
                width: `${bookWidth + spineThickness + 4}px`,
                height: `${bookHeight + 4}px`,
                perspective: '1000px', // Perspectiva más lejana para menos distorsión tipo "lente de pez"
                transformStyle: 'preserve-3d',
            }}
        >
            {/* Contenedor 3D */}
            <div
                style={{
                    width: '100%',
                    height: '100%',
                    position: 'relative',
                    transformStyle: 'preserve-3d',
                    transform: 'rotateY(-25deg) rotateX(10deg)',
                    transition: 'transform 0.4s cubic-bezier(0.25, 1, 0.5, 1)', // Movimiento más pesado/realista
                }}
                className="group-hover:!transform group-hover:!rotate-y-[0deg] group-hover:!rotate-x-[0deg]"
            >
                {/* Tapa frontal */}
                <div
                    style={{
                        position: 'absolute',
                        width: `${bookWidth}px`,
                        height: `${bookHeight}px`,
                        background: imageUrl && !isLeather ? 'white' : coverGradient,
                        // Tapa blanda: Volvemos a bordes rectos (flexibilidad solo por rotación de apertura)
                        borderRadius: borderRadius,
                        // Sombra de oclusión
                        boxShadow: isSoft
                            ? '5px 5px 15px rgba(0,0,0,0.15)'
                            : '1px 1px 3px rgba(0,0,0,0.3)',
                        // Tapa blanda: Se abre visualmente de forma sutil (-6deg)
                        transform: `translateZ(${spineThickness / 2}px) ${isSoft ? 'rotateY(-6deg)' : ''}`,
                        transformOrigin: 'left center',
                        left: `${spineThickness}px`,
                        overflow: 'hidden',
                    }}
                >
                    {/* Imagen Ilustrativa */}
                    {imageUrl && !isLeather && (
                        <img
                            src={imageUrl}
                            alt="Tapa"
                            style={{
                                width: '100%',
                                height: '100%',
                                objectFit: 'cover',
                            }}

                        />
                    )}

                    {/* Título del libro (Estilo Manuscrito/Informal) */}
                    {title && !isLeather && (
                        <div
                            style={{
                                position: 'absolute',
                                top: '35%', // Centrado verticalmente más o menos
                                left: 0,
                                right: 0,
                                textAlign: 'center',
                                padding: '0 10px',
                                zIndex: 10,
                                transform: 'translateZ(1px)'
                            }}
                        >
                            <h3 style={{
                                fontFamily: "'Brush Script MT', 'Comic Sans MS', cursive", // Fuente manuscrita informal
                                fontSize: `${Math.max(14, bookWidth * 0.18)}px`, // Fuente más grande
                                color: 'white',
                                textShadow: '2px 2px 0px rgba(0,0,0,0.5)', // Sombra "pop" dura
                                margin: 0,
                                transform: 'rotate(-5deg)', // Ligera rotación para efecto divertido
                                lineHeight: 1.1
                            }}>
                                {title}
                            </h3>
                        </div>
                    )}

                    {/* Brillo especular sutil (Mate/Satinado) */}
                    <div
                        style={{
                            position: 'absolute',
                            // Gradiente complejo para simular la onda del papel flexible
                            background: isSoft
                                ? 'linear-gradient(90deg, rgba(0,0,0,0.05) 0%, rgba(255,255,255,0.2) 20%, rgba(0,0,0,0.05) 50%, rgba(0,0,0,0.2) 100%)'
                                : 'linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0) 50%, rgba(0,0,0,0.05) 100%)',
                            pointerEvents: 'none',
                            top: 0, left: 0, right: 0, bottom: 0,
                        }}
                    />

                    {/* Surco lateral (Charnela) - Típico de tapa dura, línea recta y definida */}
                    {coverType !== 'Blanda' && (
                        <div
                            style={{
                                position: 'absolute',
                                top: 0, bottom: 0, left: '8px',
                                width: '1px',
                                background: 'rgba(0,0,0,0.3)',
                                boxShadow: '1px 0 0 rgba(255,255,255,0.1)'
                            }}
                        />
                    )}

                    {/* Textura Simil Cuero Realista */}
                    {isLeather && (
                        <div
                            style={{
                                position: 'absolute',
                                inset: 0,
                                // Patrón de ruido para simular cuero
                                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.15'/%3E%3C/svg%3E")`,
                                backgroundSize: '100px 100px',
                                mixBlendMode: 'overlay',
                            }}
                        >
                            {/* Grabado dorado opcional para realismo si se quisiera */}
                        </div>
                    )}
                </div>

                {/* Lomo del libro (Recto) */}
                <div
                    style={{
                        position: 'absolute',
                        width: `${spineThickness}px`,
                        height: `${bookHeight}px`,
                        background: spineGradient,
                        transform: `rotateY(90deg) translateZ(${spineThickness / 2}px)`,
                        transformOrigin: 'left center',
                        borderRadius: '1px', // Filoso
                        overflow: 'hidden'
                    }}
                >
                    {isLeather && (
                        <div
                            style={{
                                position: 'absolute',
                                inset: 0,
                                backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.15'/%3E%3C/svg%3E")`,
                                backgroundSize: '50px 50px',
                                mixBlendMode: 'overlay',
                            }}
                        />
                    )}

                    {/* Nervios del lomo (solo tapa dura/cuero) */}
                    {coverType !== 'Blanda' && (
                        <>
                            <div style={{ position: 'absolute', top: '15%', left: 0, right: 0, height: '2px', background: 'rgba(0,0,0,0.3)', boxShadow: '0 1px 1px rgba(255,255,255,0.1)' }} />
                            <div style={{ position: 'absolute', bottom: '15%', left: 0, right: 0, height: '2px', background: 'rgba(0,0,0,0.3)', boxShadow: '0 1px 1px rgba(255,255,255,0.1)' }} />
                        </>
                    )}
                </div>

                {/* Páginas (Lado derecho - Simulando flexibilidad en tapa blanda) */}
                <div
                    style={{
                        position: 'absolute',
                        width: `${spineThickness - 2}px`,
                        height: `${bookHeight - 6}px`,
                        // Textura:
                        // Tapa blanda: Gradiente radial que simula la curvatura de las hojas (fanning)
                        // Tapa dura: Líneas rectas sólidas
                        background: isSoft
                            ? `linear-gradient(to right, #e0e0e0 0%, #fcfcfc 40%, #f0f0f0 100%)`
                            : `repeating-linear-gradient(to right, #fcfcfc 0px, #f0f0f0 1px, #fcfcfc 2px)`,
                        right: '3px',
                        top: '3px',
                        // Transformación:
                        transform: `rotateY(90deg) translateZ(${bookWidth - 2}px) translateX(-${spineThickness / 2}px)`,
                        transformOrigin: 'right center',
                        // FLEXIBILIDAD: Bordes rectos siempre, la flexibilidad la da la apertura de la tapa
                        borderRadius: '0 1px 1px 0',
                        boxShadow: isSoft
                            ? 'inset 3px 0 5px rgba(0,0,0,0.1)'
                            : 'inset 2px 0 5px rgba(0,0,0,0.1)',
                    }}
                />


                {/* Tapa trasera */}
                <div
                    style={{
                        position: 'absolute',
                        width: `${bookWidth}px`,
                        height: `${bookHeight}px`,
                        background: '#e0e0e0', // Color neutro trasera
                        borderRadius: borderRadius,
                        transform: `translateZ(-${spineThickness / 2}px)`,
                        left: `${spineThickness}px`,
                        boxShadow: '-5px 5px 20px rgba(0,0,0,0.3)', // Sombra principal hacia el suelo
                    }}
                />
            </div>

            {/* Sombra de suelo */}
            <div
                style={{
                    position: 'absolute',
                    bottom: '-10px',
                    left: '5%',
                    right: '5%',
                    height: '15px',
                    background: 'radial-gradient(ellipse at center, rgba(0,0,0,0.4) 0%, transparent 70%)',
                    filter: 'blur(5px)',
                    transform: 'rotateX(90deg) translateZ(-10px)',
                    zIndex: -1
                }}
            />
        </div>
    );
};

/**
 * Ajusta el brillo de un color hex
 */
function adjustBrightness(hex: string, percent: number): string {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent);
    const R = Math.max(0, Math.min(255, (num >> 16) + amt));
    const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amt));
    const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
    return `#${(0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1)}`;
}

// Colores predefinidos para los productos
export const BOOK_COLORS = {
    'Apaisado': '#1a365d',      // Azul marino
    'Cuadrado': '#744210',      // Marrón cálido
    'Vertical': '#2d3748',      // Gris oscuro
    'Mini': '#553c9a',          // Púrpura
};

export const COVER_COLORS = {
    'Blanda': '#4a5568',        // Gris
    'Dura': '#1a365d',          // Azul marino
    'Simil Cuero': '#1a1a1a',   // Negro cuero
};

export default Book3D;
