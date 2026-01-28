"""
Analizador de Fotos con IA (Gemini Vision)
===========================================
Analiza las fotos del cliente para:
- Detectar tipo de evento (boda, cumpleaños, viaje, etc.)
- Evaluar calidad de las fotos
- Identificar orientación y composición
- Sugerir el estilo de diseño más apropiado
"""

import os
import base64
import json
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
import httpx
from pathlib import Path


# Configuración
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAWNg1r-6NkqOib6ma8nJN3PVNTQCresu4")
GEMINI_MODEL = "gemini-2.0-flash"


class TipoEvento(Enum):
    BODA = "boda"
    CUMPLEANOS = "cumpleaños"
    VIAJE = "viaje"
    BEBE = "bebé"
    GRADUACION = "graduación"
    MASCOTA = "mascota"
    FAMILIA = "familia"
    PAISAJE = "paisaje"
    ANIVERSARIO = "aniversario"
    QUINCEANOS = "quinceañera"
    OTRO = "otro"


class CalidadFoto(Enum):
    EXCELENTE = "excelente"
    BUENA = "buena"
    REGULAR = "regular"
    BAJA = "baja"


@dataclass
class AnalisisFoto:
    """Resultado del análisis de una foto individual"""
    indice: int
    orientacion: str  # horizontal, vertical, cuadrada
    calidad: CalidadFoto
    tiene_rostros: bool
    cantidad_personas: int
    es_paisaje: bool
    es_retrato: bool
    colores_dominantes: List[str] = field(default_factory=list)
    descripcion_corta: str = ""
    score_portada: float = 0.0  # 0-1, qué tan buena es para portada


@dataclass
class AnalisisColeccion:
    """Resultado del análisis de toda la colección de fotos"""
    total_fotos: int
    evento_detectado: TipoEvento
    confianza_evento: float  # 0-1
    estilo_sugerido: str  # ID del estilo recomendado
    razon_sugerencia: str
    
    fotos_analizadas: List[AnalisisFoto] = field(default_factory=list)
    mejores_para_portada: List[int] = field(default_factory=list)  # Índices
    
    distribucion_orientacion: Dict[str, int] = field(default_factory=dict)
    promedio_calidad: float = 0.0
    tiene_fotos_grupales: bool = False


# Mapeo de eventos a estilos sugeridos
EVENTO_A_ESTILO = {
    TipoEvento.BODA: "clasico",
    TipoEvento.CUMPLEANOS: "divertido",
    TipoEvento.VIAJE: "minimalista",
    TipoEvento.BEBE: "divertido",
    TipoEvento.GRADUACION: "clasico",
    TipoEvento.MASCOTA: "divertido",
    TipoEvento.FAMILIA: "clasico",
    TipoEvento.PAISAJE: "minimalista",
    TipoEvento.ANIVERSARIO: "premium",
    TipoEvento.QUINCEANOS: "premium",
    TipoEvento.OTRO: "clasico",
}


def imagen_a_base64(ruta_archivo: str) -> str:
    """Convierte una imagen a base64"""
    with open(ruta_archivo, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def obtener_mime_type(ruta_archivo: str) -> str:
    """Obtiene el MIME type de la imagen"""
    extension = Path(ruta_archivo).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_types.get(extension, "image/jpeg")


async def analizar_fotos_con_gemini(
    rutas_fotos: List[str],
    max_fotos_analizar: int = 20
) -> AnalisisColeccion:
    """
    Analiza una colección de fotos usando Gemini Vision.
    
    Args:
        rutas_fotos: Lista de rutas a los archivos de imagen
        max_fotos_analizar: Máximo de fotos a analizar (para optimizar costos)
    
    Returns:
        AnalisisColeccion con los resultados
    """
    
    # Seleccionar fotos a analizar (distribuidas uniformemente)
    total = len(rutas_fotos)
    if total > max_fotos_analizar:
        # Tomar fotos distribuidas uniformemente
        paso = total // max_fotos_analizar
        fotos_seleccionadas = rutas_fotos[::paso][:max_fotos_analizar]
        indices_seleccionados = list(range(0, total, paso))[:max_fotos_analizar]
    else:
        fotos_seleccionadas = rutas_fotos
        indices_seleccionados = list(range(total))
    
    # Preparar las imágenes para Gemini
    partes_imagenes = []
    for ruta in fotos_seleccionadas:
        try:
            b64 = imagen_a_base64(ruta)
            mime = obtener_mime_type(ruta)
            partes_imagenes.append({
                "inline_data": {
                    "mime_type": mime,
                    "data": b64
                }
            })
        except Exception as e:
            print(f"Error leyendo imagen {ruta}: {e}")
            continue
    
    if not partes_imagenes:
        # Si no hay imágenes, devolver análisis por defecto
        return AnalisisColeccion(
            total_fotos=total,
            evento_detectado=TipoEvento.OTRO,
            confianza_evento=0.0,
            estilo_sugerido="clasico",
            razon_sugerencia="No se pudieron analizar las fotos"
        )
    
    # Prompt para Gemini
    prompt = """Analiza esta colección de fotos y responde en JSON con esta estructura exacta:

{
    "evento_detectado": "boda|cumpleaños|viaje|bebé|graduación|mascota|familia|paisaje|aniversario|quinceañera|otro",
    "confianza_evento": 0.0-1.0,
    "razon_deteccion": "explicación corta de por qué detectaste este evento",
    "fotos_analisis": [
        {
            "indice": 0,
            "orientacion": "horizontal|vertical|cuadrada",
            "calidad": "excelente|buena|regular|baja",
            "tiene_rostros": true/false,
            "cantidad_personas": 0,
            "es_paisaje": true/false,
            "descripcion_corta": "descripción de 10 palabras max",
            "score_portada": 0.0-1.0
        }
    ],
    "mejores_para_portada": [0, 5, 12],
    "tiene_fotos_grupales": true/false,
    "colores_predominantes": ["#color1", "#color2"]
}

Criterios para score_portada alto:
- Buena composición y enfoque
- Sin elementos cortados
- Representa bien el tema/evento
- Apela visualmente

Responde SOLO el JSON, sin texto adicional."""

    # Llamar a Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt},
                    *partes_imagenes
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 2000,
        }
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        
        if response.status_code != 200:
            print(f"Error en Gemini API: {response.status_code} - {response.text}")
            return AnalisisColeccion(
                total_fotos=total,
                evento_detectado=TipoEvento.OTRO,
                confianza_evento=0.0,
                estilo_sugerido="clasico",
                razon_sugerencia=f"Error en análisis: {response.status_code}"
            )
        
        data = response.json()
        
    # Parsear respuesta
    try:
        texto_respuesta = data["candidates"][0]["content"]["parts"][0]["text"]
        # Limpiar posibles caracteres extra
        texto_respuesta = texto_respuesta.strip()
        if texto_respuesta.startswith("```"):
            texto_respuesta = texto_respuesta.split("```")[1]
            if texto_respuesta.startswith("json"):
                texto_respuesta = texto_respuesta[4:]
        
        resultado_json = json.loads(texto_respuesta)
    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parseando respuesta de Gemini: {e}")
        return AnalisisColeccion(
            total_fotos=total,
            evento_detectado=TipoEvento.OTRO,
            confianza_evento=0.0,
            estilo_sugerido="clasico",
            razon_sugerencia="Error procesando análisis"
        )
    
    # Construir resultado
    evento_str = resultado_json.get("evento_detectado", "otro").lower()
    try:
        evento = TipoEvento(evento_str)
    except ValueError:
        evento = TipoEvento.OTRO
    
    estilo_sugerido = EVENTO_A_ESTILO.get(evento, "clasico")
    
    # Analizar distribución de orientación
    fotos_analizadas = []
    orientaciones = {"horizontal": 0, "vertical": 0, "cuadrada": 0}
    calidades = []
    
    for foto_data in resultado_json.get("fotos_analisis", []):
        orientacion = foto_data.get("orientacion", "horizontal")
        orientaciones[orientacion] = orientaciones.get(orientacion, 0) + 1
        
        calidad_str = foto_data.get("calidad", "buena")
        try:
            calidad = CalidadFoto(calidad_str)
        except ValueError:
            calidad = CalidadFoto.BUENA
        
        calidad_score = {"excelente": 4, "buena": 3, "regular": 2, "baja": 1}
        calidades.append(calidad_score.get(calidad_str, 2))
        
        fotos_analizadas.append(AnalisisFoto(
            indice=foto_data.get("indice", 0),
            orientacion=orientacion,
            calidad=calidad,
            tiene_rostros=foto_data.get("tiene_rostros", False),
            cantidad_personas=foto_data.get("cantidad_personas", 0),
            es_paisaje=foto_data.get("es_paisaje", False),
            es_retrato=not foto_data.get("es_paisaje", True),
            descripcion_corta=foto_data.get("descripcion_corta", ""),
            score_portada=foto_data.get("score_portada", 0.5),
        ))
    
    promedio_calidad = sum(calidades) / len(calidades) if calidades else 2.5
    
    return AnalisisColeccion(
        total_fotos=total,
        evento_detectado=evento,
        confianza_evento=resultado_json.get("confianza_evento", 0.5),
        estilo_sugerido=estilo_sugerido,
        razon_sugerencia=resultado_json.get("razon_deteccion", ""),
        fotos_analizadas=fotos_analizadas,
        mejores_para_portada=resultado_json.get("mejores_para_portada", [0]),
        distribucion_orientacion=orientaciones,
        promedio_calidad=promedio_calidad,
        tiene_fotos_grupales=resultado_json.get("tiene_fotos_grupales", False),
    )


def sugerir_estilo_simple(evento: TipoEvento) -> str:
    """Sugiere un estilo basado solo en el tipo de evento (sin IA)"""
    return EVENTO_A_ESTILO.get(evento, "clasico")


async def analizar_fotos_rapido(rutas_fotos: List[str]) -> Dict[str, Any]:
    """
    Versión simplificada del análisis para respuesta rápida.
    Solo analiza 5 fotos para detectar el evento.
    
    Returns:
        Dict con evento_detectado, estilo_sugerido y mejores_para_portada
    """
    if not rutas_fotos:
        return {
            "evento_detectado": "otro",
            "estilo_sugerido": "clasico",
            "mejores_para_portada": [],
            "confianza": 0.0
        }
    
    # Analizar solo 5 fotos distribuidas
    resultado = await analizar_fotos_con_gemini(rutas_fotos, max_fotos_analizar=5)
    
    return {
        "evento_detectado": resultado.evento_detectado.value,
        "estilo_sugerido": resultado.estilo_sugerido,
        "mejores_para_portada": resultado.mejores_para_portada[:3],
        "confianza": resultado.confianza_evento,
        "razon": resultado.razon_sugerencia
    }
