"""
Prueba rápida de AGNO + Browserbase con página simple
"""

import os
os.environ["BROWSERBASE_API_KEY"] = "bb_live_uyHSRbZ7_5XT0kNvltt1xJfxfcQ"
os.environ["BROWSERBASE_PROJECT_ID"] = "35743d70-110d-427b-adad-1e8fb780bfd3"
os.environ["OPENROUTER_API_KEY"] = "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"

from agno.agent import Agent
from agno.models.openrouter import OpenRouter
from agno.tools.browserbase import BrowserbaseTools

agent = Agent(
    name="Web Scraper",
    model=OpenRouter(id="google/gemini-2.5-flash"),
    tools=[BrowserbaseTools()],
    instructions=["Extract information from web pages."],
    markdown=True,
)

if __name__ == "__main__":
    print("🚀 Prueba rápida con quotes.toscrape.com...")
    
    agent.print_response("""
        Visit https://quotes.toscrape.com and extract the first 3 quotes with their authors.
    """)
