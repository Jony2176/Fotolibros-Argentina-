
import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print(f"🔑 Token length: {len(TOKEN) if TOKEN else 0}")
print(f"🆔 Chat ID: {CHAT_ID}")

async def send_test():
    if not TOKEN or not CHAT_ID:
        print("❌ Faltan credenciales en .env")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": "🧪 Prueba de Telegram desde Fotolibros Argentina",
        "parse_mode": "HTML"
    }
    
    print(f"📡 Enviando a {url}...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload)
            print(f"📥 Status: {resp.status_code}")
            print(f"📥 Body: {resp.text}")
            
            if resp.status_code == 200:
                print("✅ Mensaje enviado con éxito.")
            else:
                print("❌ Error enviando mensaje.")
    except Exception as e:
        print(f"❌ Excepción: {e}")

if __name__ == "__main__":
    asyncio.run(send_test())
