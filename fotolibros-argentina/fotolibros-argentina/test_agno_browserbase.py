"""
Script de prueba para AGNO + Browserbase
Siguiendo la documentación oficial de AGNO
"""

import os
os.environ["BROWSERBASE_API_KEY"] = "bb_live_uyHSRbZ7_5XT0kNvltt1xJfxfcQ"
os.environ["BROWSERBASE_PROJECT_ID"] = "35743d70-110d-427b-adad-1e8fb780bfd3"
os.environ["OPENROUTER_API_KEY"] = "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"

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.browserbase import BrowserbaseTools

agent = Agent(
    name="Web Automation Assistant",
    model=OpenRouter(id="google/gemini-2.5-flash"),
    tools=[BrowserbaseTools()],
    instructions=[
        "You are a web automation assistant that can help with:",
        "1. Capturing screenshots of websites",
        "2. Extracting content from web pages",
        "3. Navigating between pages",
    ],
    markdown=True,
)

if __name__ == "__main__":
    print("🚀 Probando AGNO + Browserbase...")
    print("=" * 50)
    
    agent.print_response("""
        Visita https://online.fabricadefotolibros.com y:
        1. Describe qué ves en la página principal
        2. Indica si hay un formulario de login
        3. Lista las opciones de fotolibros disponibles si las hay
    """)
