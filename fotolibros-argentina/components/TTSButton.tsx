
import React, { useState } from 'react';
import { GoogleGenAI, Modality } from "@google/genai";

interface TTSButtonProps {
  text: string;
}

const TTSButton: React.FC<TTSButtonProps> = ({ text }) => {
  const [isPlaying, setIsPlaying] = useState(false);

  const playSpeech = async () => {
    if (isPlaying) return;
    setIsPlaying(true);

    try {
      const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });
      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash-preview-tts",
        contents: [{ parts: [{ text: `Lee pausadamente y con claridad: ${text}` }] }],
        config: {
          responseModalities: [Modality.AUDIO],
          speechConfig: {
            voiceConfig: {
              prebuiltVoiceConfig: { voiceName: 'Kore' },
            },
          },
        },
      });

      const base64Audio = response.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
      if (base64Audio) {
        const audioBlob = await fetch(`data:audio/pcm;base64,${base64Audio}`).then(r => r.blob());
        const audioUrl = URL.createObjectURL(audioBlob);
        
        // As standard browser Audio doesn't support raw PCM, we'd normally use AudioContext.
        // For simplicity in this UI component, we provide the visual feedback.
        // Real implementation as per guidelines:
        const ctx = new (window.AudioContext || (window as any).webkitAudioContext)({sampleRate: 24000});
        const bytes = atob(base64Audio);
        const len = bytes.length;
        const bytesArr = new Uint8Array(len);
        for(let i=0; i<len; i++) bytesArr[i] = bytes.charCodeAt(i);
        
        const dataInt16 = new Int16Array(bytesArr.buffer);
        const buffer = ctx.createBuffer(1, dataInt16.length, 24000);
        const channelData = buffer.getChannelData(0);
        for (let i = 0; i < dataInt16.length; i++) {
          channelData[i] = dataInt16[i] / 32768.0;
        }
        
        const source = ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(ctx.destination);
        source.onended = () => setIsPlaying(false);
        source.start();
      }
    } catch (error) {
      console.error("TTS Error:", error);
      setIsPlaying(false);
    }
  };

  return (
    <button 
      onClick={playSpeech}
      className={`p-2 rounded-lg transition-all ${isPlaying ? 'text-accent bg-accent/10 animate-pulse' : 'text-gray-400 hover:text-primary hover:bg-primary/5'}`}
      title="Leer en voz alta"
    >
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" /></svg>
    </button>
  );
};

export default TTSButton;
