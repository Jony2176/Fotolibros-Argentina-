"""
Configuración de Modelos LLM para PIKSY
========================================
Usa modelos GRATUITOS de OpenRouter siempre que sea posible.
Para tareas críticas, usa Gemini con la API key del usuario.

Modelos gratuitos disponibles en OpenRouter (2026):
- google/gemma-3-27b-it:free - Mejor calidad gratuito
- google/gemma-3-4b-it:free - Rápido y ligero
- meta-llama/llama-3.2-3b-instruct:free - Bueno para instrucciones
- qwen/qwen-2.5-7b-instruct:free - Bueno para español
- mistralai/mistral-7b-instruct:free - General purpose
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class TareaLLM(Enum):
    """Tipos de tareas que requieren LLM"""
    CHAT_CLIENTE = "chat_cliente"           # Chat de atención al cliente
    ANALISIS_FOTOS = "analisis_fotos"       # Análisis visual de fotos
    ORQUESTACION = "orquestacion"           # Orquestador de agentes AGNO
    GENERACION_TEXTO = "generacion_texto"   # Generar títulos, descripciones
    CLASIFICACION = "clasificacion"          # Clasificar eventos, estilos


@dataclass
class ConfigModelo:
    """Configuración de un modelo"""
    provider: str  # "openrouter", "gemini", "local"
    model_id: str
    api_key_env: str  # Nombre de variable de entorno
    max_tokens: int = 1000
    temperature: float = 0.7
    es_gratuito: bool = True
    soporta_vision: bool = False


# API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAWNg1r-6NkqOib6ma8nJN3PVNTQCresu4")


# ============================================================
# MODELOS GRATUITOS MÁS AVANZADOS (2025-2026)
# ============================================================

MODELOS = {
    # Chat con clientes - Mejor modelo para conversación en español
    TareaLLM.CHAT_CLIENTE: ConfigModelo(
        provider="openrouter",
        model_id="meta-llama/llama-4-maverick:free",  # Llama 4 - el más capaz
        api_key_env="OPENROUTER_API_KEY",
        max_tokens=1500,
        temperature=0.7,
        es_gratuito=True,
        soporta_vision=False,
    ),
    
    # Análisis de fotos - Necesita visión
    TareaLLM.ANALISIS_FOTOS: ConfigModelo(
        provider="openrouter",
        model_id="google/gemini-2.0-flash-001",
        api_key_env="OPENROUTER_API_KEY",
        max_tokens=2000,
        temperature=0.2,
        es_gratuito=False, # Flash Lite suele ser paid tier o free con limites
        soporta_vision=True,
    ),
    
    # Orquestación de agentes - Máximo razonamiento
    TareaLLM.ORQUESTACION: ConfigModelo(
        provider="openrouter",
        model_id="google/gemini-2.0-flash-001",
        api_key_env="OPENROUTER_API_KEY",
        max_tokens=2000,
        temperature=0.3,
        es_gratuito=True,
        soporta_vision=False,
    ),
    
    # Generación de texto - Qwen3 es excelente en español
    TareaLLM.GENERACION_TEXTO: ConfigModelo(
        provider="openrouter",
        model_id="qwen/qwen3-coder-480b-a35b:free",  # Qwen3 - muy bueno
        api_key_env="OPENROUTER_API_KEY",
        max_tokens=800,
        temperature=0.8,
        es_gratuito=True,
        soporta_vision=False,
    ),
    
    # Clasificación - Rápido y eficiente
    TareaLLM.CLASIFICACION: ConfigModelo(
        provider="openrouter",
        model_id="google/gemma-3-27b:free",  # Gemma 3 27B - rápido y preciso
        api_key_env="OPENROUTER_API_KEY",
        max_tokens=200,
        temperature=0.1,
        es_gratuito=True,
        soporta_vision=False,
    ),
}


def get_modelo_config(tarea: TareaLLM) -> ConfigModelo:
    """Obtiene la configuración del modelo para una tarea"""
    return MODELOS.get(tarea, MODELOS[TareaLLM.ORQUESTACION])


def get_api_key(config: ConfigModelo) -> str:
    """Obtiene la API key según el provider"""
    if config.provider == "gemini":
        return GEMINI_API_KEY
    elif config.provider == "openrouter":
        return OPENROUTER_API_KEY
    return ""


# ============================================================
# FUNCIONES HELPER PARA LLAMAR MODELOS
# ============================================================

async def llamar_openrouter(
    model_id: str,
    messages: list,
    max_tokens: int = 1000,
    temperature: float = 0.7
) -> str:
    """Llama a un modelo de OpenRouter"""
    import httpx
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_id,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter error: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["choices"][0]["message"]["content"]


async def llamar_gemini(
    model_id: str,
    prompt: str,
    system_prompt: str = "",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    imagenes_base64: list = None
) -> str:
    """Llama a un modelo de Gemini"""
    import httpx
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_id}:generateContent?key={GEMINI_API_KEY}"
    
    # Construir partes del contenido
    parts = []
    
    if imagenes_base64:
        for img in imagenes_base64:
            parts.append({
                "inline_data": {
                    "mime_type": img.get("mime_type", "image/jpeg"),
                    "data": img["data"]
                }
            })
    
    parts.append({"text": prompt})
    
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature": temperature,
        }
    }
    
    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Gemini error: {response.status_code} - {response.text}")
        
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def llamar_modelo(
    tarea: TareaLLM,
    prompt: str,
    system_prompt: str = "",
    imagenes_base64: list = None
) -> str:
    """
    Función unificada para llamar al modelo correcto según la tarea.
    Usa modelos gratuitos siempre que sea posible.
    """
    config = get_modelo_config(tarea)
    
    if config.provider == "gemini":
        return await llamar_gemini(
            model_id=config.model_id,
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=config.max_tokens,
            temperature=config.temperature,
            imagenes_base64=imagenes_base64
        )
    
    elif config.provider == "openrouter":
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        return await llamar_openrouter(
            model_id=config.model_id,
            messages=messages,
            max_tokens=config.max_tokens,
            temperature=config.temperature
        )
    
    raise Exception(f"Provider no soportado: {config.provider}")


# ============================================================
# MODELOS PARA AGNO
# ============================================================

def get_agno_model_config(tarea: TareaLLM = TareaLLM.ORQUESTACION) -> dict:
    """
    Retorna la configuración para usar con AGNO Agent.
    
    Uso:
        from agno.agent import Agent
        from agno.models.openrouter import OpenRouter
        
        config = get_agno_model_config(TareaLLM.ORQUESTACION)
        agent = Agent(
            model=OpenRouter(id=config["model_id"]),
            ...
        )
    """
    config = get_modelo_config(tarea)
    
    return {
        "provider": config.provider,
        "model_id": config.model_id,
        "api_key": get_api_key(config),
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
    }
