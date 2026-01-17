
import React, { useState, useRef, useEffect } from 'react';
import { GoogleGenAI } from "@google/genai";
import { PRODUCTS, PACKAGES, SHIPPING_COSTS, PROVINCIAS_MAPPING } from '../constants';

const AIChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ role: 'user' | 'model'; text: string }[]>([
    { role: 'model', text: '¡Hola! 👋 Soy tu asistente de Fotolibros Argentina. ¿En qué puedo ayudarte hoy?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isOpen]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userText = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setIsLoading(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const context = `
        Eres un asistente de ventas amigable para "Fotolibros Argentina".
        PRODUCTOS: ${JSON.stringify(PRODUCTS.map(p => ({ n: p.nombre, p: p.precioBase, t: p.tamanio, c: p.tapa })))}
        PAQUETES: ${JSON.stringify(PACKAGES)}
        ENVIOS: ${JSON.stringify(SHIPPING_COSTS)}
        POLITICAS:
        - Tiempo entrega: 10-14 días hábiles.
        - Recomendación: 2-4 fotos por página.
        - Máximo páginas: 80.
        - Pagos: MercadoPago y Transferencia.
        - Estilo: Amigable, servicial, usa emojis, respuestas cortas.
      `;

      const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: [...messages, { role: 'user', text: userText }].map(m => ({
          role: m.role === 'model' ? 'model' : 'user',
          parts: [{ text: m.text }]
        })),
        config: {
          systemInstruction: context,
        }
      });

      const aiText = response.text || "Lo siento, tuve un problema procesando tu consulta. ¿Podrías repetir?";
      setMessages(prev => [...prev, { role: 'model', text: aiText }]);
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { role: 'model', text: 'Ups, algo salió mal. ¿Podés intentar de nuevo?' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed bottom-24 right-4 md:right-8 z-[100] font-sans">
      {isOpen ? (
        <div className="bg-white w-[85vw] sm:w-[350px] h-[70vh] sm:h-[500px] rounded-3xl shadow-2xl flex flex-col border border-gray-100 overflow-hidden animate-fade-in mb-4">
          <header className="bg-primary p-4 text-white flex justify-between items-center shadow-md">
            <div className="flex items-center gap-2">
              <span className="text-xl">📸</span>
              <div>
                <h3 className="font-bold text-sm leading-none">Asistente Virtual</h3>
                <span className="text-[10px] text-white/70">En línea ahora</span>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="bg-white/10 hover:bg-white/20 w-8 h-8 rounded-full flex items-center justify-center transition-colors">✕</button>
          </header>
          
          <div ref={scrollRef} className="flex-grow p-4 overflow-y-auto space-y-4 bg-gray-50">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[85%] p-3 rounded-2xl text-sm shadow-sm leading-relaxed ${
                  m.role === 'user' ? 'bg-primary text-white rounded-tr-none' : 'bg-white text-gray-700 border border-gray-100 rounded-tl-none'
                }`}>
                  {m.text}
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white p-3 rounded-2xl shadow-sm border border-gray-100 flex gap-1">
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce"></span>
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce delay-75"></span>
                  <span className="w-1.5 h-1.5 bg-gray-300 rounded-full animate-bounce delay-150"></span>
                </div>
              </div>
            )}
          </div>

          <div className="p-4 bg-white border-t flex gap-2">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Escribí tu mensaje..."
              className="flex-grow text-sm p-3 bg-gray-50 border-none rounded-xl focus:ring-2 ring-primary/10 outline-none text-primary"
            />
            <button 
              onClick={sendMessage}
              disabled={!input.trim() || isLoading}
              className="bg-primary text-white p-3 rounded-xl hover:bg-opacity-90 transition-all disabled:opacity-50"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" /></svg>
            </button>
          </div>
        </div>
      ) : (
        <button 
          onClick={() => setIsOpen(true)}
          className="bg-primary text-white p-4 md:px-6 md:py-4 rounded-full shadow-2xl flex items-center gap-2 hover:scale-110 transition-all active:scale-95 group border-2 border-white/20"
        >
          <span className="text-2xl md:text-xl group-hover:rotate-12 transition-transform">💬</span>
          <span className="font-bold text-sm hidden md:inline">¿Necesitás ayuda?</span>
        </button>
      )}
    </div>
  );
};

export default AIChat;
