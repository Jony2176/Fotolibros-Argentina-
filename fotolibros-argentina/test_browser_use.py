import os
import asyncio
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser
from pydantic import ConfigDict

# Cargar variables de entorno
load_dotenv()

# Configuración
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GRAFICA_EMAIL = os.getenv("GRAFICA_EMAIL")
GRAFICA_PASSWORD = os.getenv("GRAFICA_PASSWORD")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY no encontrada en .env")

# Subclase para añadir el campo 'provider' requerido por browser-use 0.11.3
# y permitir monkey-patching (ainvoke)
class PatchedChatOpenAI(ChatOpenAI):
    provider: str = "openai"
    model_config = ConfigDict(extra='allow')

    @property
    def model(self):
        return self.model_name

# Inicializar LLM con OpenRouter
llm = PatchedChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    model="google/gemini-2.0-flash-exp:free",
    temperature=0
)
# Monkey patch adicional por si acaso (aunque la clase ya lo tiene)
# llm.provider = "openai" 


async def main():
    print("🚀 Iniciando prueba de Browser-Use con Gemini 2.0 Flash (vía OpenRouter)...")
    
    task = f"""
    1. Ve a https://www.fabricadefotolibros.com/software_home.php?home=online.fabricadefotolibros.com
    2. Haz login con el email '{GRAFICA_EMAIL}' y la contraseña '{GRAFICA_PASSWORD}'.
    3. Una vez logueado, haz clic en la categoría 'Fotolibros'.
    4. Busca y selecciona el producto 'Cuadrado 21x21 Tapa Dura'.
    5. Haz clic en 'Crear Proyecto' o 'Crear'.
    6. Confirma que se ha abierto el editor (puede tardar unos segundos).
    """
    
    # Inicializar navegador (headless=False para ver la acción)
    browser = Browser(headless=False)
    
    agent = Agent(
        task=task,
        llm=llm,
        browser=browser
    )
    
    try:
        result = await agent.run()
        print("\n✅ Resultado:", result)
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cerrar navegador al finalizar
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
