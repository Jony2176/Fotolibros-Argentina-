"""
Test Stagehand con OpenRouter
"""
import os
import sys

# Configurar OpenRouter
os.environ["OPENAI_BASE_URL"] = "https://openrouter.ai/api/v1"
os.environ["MODEL_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = os.environ["MODEL_API_KEY"]

# Dummy values para modo local (no se usan realmente)
os.environ["BROWSERBASE_API_KEY"] = "dummy"
os.environ["BROWSERBASE_PROJECT_ID"] = "dummy"

from stagehand import Stagehand

def main():
    print("🚀 Iniciando Stagehand en modo local con OpenRouter...")
    
    client = Stagehand(
        server="local",
        local_openai_api_key=os.environ["MODEL_API_KEY"],
        local_ready_timeout_s=60.0,
    )
    
    session_id = None
    
    try:
        print("⏳ Iniciando sesión de browser...")
        session = client.sessions.start(
            model_name="openai/gpt-4o-mini",
            browser={
                "type": "local",
                "launchOptions": {
                    "headless": True,
                    "args": ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
                },
            },
        )
        session_id = session.data.session_id
        print(f"✅ Sesión iniciada: {session_id}")
        
        print("🌐 Navegando a example.com...")
        client.sessions.navigate(
            id=session_id,
            url="https://www.example.com",
        )
        print("✅ Navegación completa")
        
        print("🔍 Probando extract()...")
        extract_response = client.sessions.extract(
            id=session_id,
            instruction="Extract the main heading text from this page",
        )
        print(f"📄 Resultado: {extract_response.data.result}")
        
        print("\n✅ ¡TEST EXITOSO! Stagehand + OpenRouter funciona")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        if session_id:
            print("🛑 Cerrando sesión...")
            client.sessions.end(id=session_id)
        client.close()
        print("✅ Limpieza completa")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
