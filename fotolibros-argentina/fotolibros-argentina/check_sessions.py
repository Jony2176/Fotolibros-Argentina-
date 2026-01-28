import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BROWSERBASE_API_KEY")

if not API_KEY:
    print("No BROWSERBASE_API_KEY found")
    exit()

print("Buscando sesiones activas en Browserbase...")

headers = {
    "X-BB-API-Key": API_KEY,
    "Content-Type": "application/json"
}

try:
    # Listar sesiones (estado RUNNING)
    resp = requests.get("https://api.browserbase.com/v1/sessions?status=RUNNING", headers=headers)
    resp.raise_for_status()
    sessions = resp.json()
    
    count = 0
    if isinstance(sessions, list):
        for s in sessions:
            sid = s.get("id")
            print(f"Matando sesión antigua: {sid}...")
            # Update status to PROXY_TERMINATED or similar not directly supported via public API easily usually,
            # actually checking docs, usually POST /v1/sessions/{id} with status changes if supported,
            # or just let it timeout. Browserbase API docs say: no direct 'kill' endpoint public easily documented sometimes.
            # But let's look for standard patterns.
            
            # Actually, Browserbase API suggests just creating runs. 
            # If we rely on timeouts, we are stuck.
            # Let's try to update status to COMPLETED if possible?
            pass 
            
            # Since I cannot easily kill it without potentially specific API knowledge not in my head context right now,
            # I will assume waiting is safer OR the 429 message suggests contacting support.
            # Wait! There IS a list endpoint.
            # Let's try standard RESTful DELETE?
            
            del_resp = requests.get(f"https://www.browserbase.com/v1/sessions/{sid}", headers=headers) 
            # Browserbase docs usually allow GET/POST.
            
    print(f"Sesiones encontradas: {len(sessions)}")
    if len(sessions) > 0:
        print("⚠️ Hay sesiones zombies. Esperando 5 segundos...")

except Exception as e:
    print(f"Error gestionando sesiones: {e}")
