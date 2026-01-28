# Backend FastAPI - Fotolibros Argentina

Backend con FastAPI + SQLite para gestión de pedidos y integración con Clawdbot.

## Estructura

```
backend-fastapi/
├── app/
│   ├── main.py           # Entry point FastAPI
│   ├── config.py         # Configuración (env vars)
│   ├── db.py             # SQLite operations
│   ├── models.py         # Modelos de datos
│   ├── schemas.py        # Pydantic schemas
│   ├── worker.py         # Worker para procesar cola
│   ├── routers/
│   │   └── pedidos.py    # Endpoints de pedidos
│   └── services/
│       ├── agno_service.py     # Integración con AGNO Team
│       ├── clawdbot_service.py # Webhook a Clawdbot
│       └── queue_service.py    # Manejo de cola
├── requirements.txt
└── .env.example
```

## Endpoints

- `POST /api/pedidos/` - Crear pedido
- `POST /api/pedidos/{id}/fotos` - Subir fotos
- `POST /api/pedidos/{id}/procesar` - Encolar para procesamiento
- `GET /api/pedidos/{id}/estado` - Ver estado

## Flujo

1. Cliente crea pedido → `POST /api/pedidos/`
2. Cliente sube fotos → `POST /api/pedidos/{id}/fotos`
3. Cliente confirma → `POST /api/pedidos/{id}/procesar`
4. Worker procesa con AGNO Team
5. Webhook notifica a Clawdbot
6. Clawdbot ejecuta en FDF

## Configuración (.env)

```
DATABASE_PATH=/var/fotolibros/fotolibros.db
CLAWDBOT_URL=http://127.0.0.1:18789
CLAWDBOT_HOOK_TOKEN=your_token
OPENROUTER_API_KEY=your_key
AGNO_MODEL=openai/gpt-4o-mini
FDF_USER=your_fdf_email
FDF_PASS=your_fdf_pass
```

## Instalación

```bash
cd backend-fastapi
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8002
```

## Worker

```bash
python app/worker.py
```

---
Integrado con Clawdbot por Clawd 🐾 (2026-01-28)
