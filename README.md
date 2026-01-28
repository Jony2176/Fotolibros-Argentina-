# Fotolibros Argentina - Sistema Completo VPS

Sistema automatizado de creacion de fotolibros artisticos usando AGNO + Clawdbot.

## Arquitectura

```
Cliente Web --> FastAPI Backend --> AGNO (analisis) --> Clawdbot (ejecucion) --> FDF
                     |
                     v
               PostgreSQL + Redis (cola)
```

## Requisitos del VPS

- Ubuntu 24.04
- Python 3.11+
- Node.js 22+
- PostgreSQL 15+
- Redis 7+
- Clawdbot ya instalado y corriendo

## Estructura del Proyecto

```
fotolibros-vps-deploy/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Entry point FastAPI
│   │   ├── config.py          # Configuracion
│   │   ├── models.py          # Modelos SQLAlchemy
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── routers/
│   │   │   ├── pedidos.py     # Endpoints de pedidos
│   │   │   └── webhooks.py    # Webhooks internos
│   │   ├── services/
│   │   │   ├── agno_service.py    # Bridge a AGNO
│   │   │   ├── clawdbot_service.py # Bridge a Clawdbot
│   │   │   ├── queue_service.py    # Cola de pedidos
│   │   │   └── notification_service.py
│   │   └── worker.py          # Worker de procesamiento
│   ├── agno/                   # Sistema AGNO (copiado)
│   │   ├── agents/
│   │   ├── team.py
│   │   └── ...
│   ├── requirements.txt
│   └── .env.example
├── clawdbot/                   # Archivos para Clawdbot
│   ├── SOUL.md                # Personalidad del agente
│   ├── skills/
│   │   └── fotolibros-fdf/
│   │       └── SKILL.md       # Instrucciones del editor
│   └── clawdbot.json.example  # Config de referencia
├── scripts/
│   ├── install.sh             # Instalacion completa
│   ├── start.sh               # Iniciar servicios
│   └── deploy.sh              # Deploy desde PC local
├── docker-compose.yml          # Opcional: PostgreSQL + Redis
└── README.md                   # Este archivo
```

## Instalacion Rapida

### 1. En tu PC local (preparar archivos)

```bash
# Clonar/copiar este directorio al VPS
scp -r fotolibros-vps-deploy/ usuario@168.231.98.115:/home/usuario/
```

### 2. En el VPS

```bash
cd /home/usuario/fotolibros-vps-deploy
chmod +x scripts/*.sh
./scripts/install.sh
```

### 3. Configurar

```bash
# Copiar y editar configuracion
cp backend/.env.example backend/.env
nano backend/.env

# Copiar archivos de Clawdbot
cp clawdbot/SOUL.md ~/clawd/SOUL.md
cp -r clawdbot/skills/* ~/.clawdbot/skills/
```

### 4. Iniciar

```bash
./scripts/start.sh
```

## Variables de Entorno

```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@localhost/fotolibros
REDIS_URL=redis://localhost:6379/0
CLAWDBOT_URL=http://127.0.0.1:18789
CLAWDBOT_HOOK_TOKEN=tu_token_secreto
OPENROUTER_API_KEY=sk-or-xxx
TELEGRAM_ADMIN_CHAT=@tu_usuario
FDF_USER=tu_usuario_fdf
FDF_PASS=tu_password_fdf
```

## Flujo de Procesamiento

1. Cliente completa wizard en la web y paga
2. Backend guarda pedido en PostgreSQL
3. Backend encola pedido en Redis
4. Worker toma pedido de la cola
5. Worker llama a AGNO para analisis (5 agentes)
6. AGNO genera `fotolibro_config.json`
7. Worker envia webhook a Clawdbot con el config
8. Clawdbot ejecuta en FDF (browser headless)
9. Clawdbot notifica por Telegram (narrativo)
10. Vos aprobas o rechazas
11. Clawdbot finaliza en FDF
12. Backend actualiza estado

## Endpoints Principales

- `POST /api/pedidos` - Crear nuevo pedido
- `GET /api/pedidos/{id}` - Obtener estado de pedido
- `POST /api/pedidos/{id}/fotos` - Subir fotos
- `POST /api/webhooks/clawdbot-result` - Callback de Clawdbot

## Comandos Utiles

```bash
# Ver logs del backend
journalctl -u fotolibros-backend -f

# Ver logs del worker
journalctl -u fotolibros-worker -f

# Ver estado de la cola
redis-cli LLEN fotolibros:cola

# Reiniciar servicios
sudo systemctl restart fotolibros-backend fotolibros-worker
```

## Costos Estimados por Pedido

| Componente | Costo |
|------------|-------|
| AGNO (GPT-4o-mini) | ~$0.10 |
| Clawdbot (Opus 4.5) | ~$0.30-0.50 |
| **Total** | **~$0.40-0.60 USD** |

## Soporte

Creado para Fotolibros Argentina - 2026
