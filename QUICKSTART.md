# Quick Start - Fotolibros Argentina

## Resumen del Sistema

**Arquitectura híbrida: AGNO (análisis) + Clawdbot (ejecución)**

```
Cliente → FastAPI → AGNO ($0.10) → Clawdbot ($0 con Claude Max) → FDF
                      ↓
                   PostgreSQL + Redis (cola)
```

## Instalación Rápida

### 1. En tu PC (preparar)

```bash
cd C:\Users\Usuario\Downloads\fotolibros_argentina\

# Copiar AGNO al proyecto
xcopy fotolibros-argentina-v2\fotolibros-agno-backend\agents fotolibros-vps-deploy\backend\agno\agents\ /E /I
copy fotolibros-argentina-v2\fotolibros-agno-backend\team.py fotolibros-vps-deploy\backend\agno\
copy fotolibros-argentina-v2\fotolibros-agno-backend\__init__.py fotolibros-vps-deploy\backend\agno\

# Comprimir
Compress-Archive -Path fotolibros-vps-deploy\* -DestinationPath fotolibros-deploy.zip

# Subir al VPS
scp fotolibros-deploy.zip usuario@168.231.98.115:/home/usuario/
```

### 2. En el VPS (instalar)

```bash
ssh usuario@168.231.98.115

cd /home/usuario
unzip fotolibros-deploy.zip -d fotolibros-vps-deploy
cd fotolibros-vps-deploy
chmod +x scripts/*.sh

# Ejecutar instalación
./scripts/install.sh

# Editar configuración
nano backend/.env
# Configurar: CLAWDBOT_HOOK_TOKEN, OPENROUTER_API_KEY, TELEGRAM_ADMIN_CHAT, FDF_USER, FDF_PASS

# Actualizar Clawdbot
nano ~/.clawdbot/clawdbot.json
# Agregar agente "fotolibros" (ver clawdbot/clawdbot.json.example)

# Reiniciar Clawdbot
sudo systemctl restart clawdbot

# Iniciar servicios
./scripts/start.sh
```

### 3. Verificar

```bash
# Health check
curl http://localhost:8000/health

# Logs backend
journalctl -u fotolibros-backend -f

# Logs worker
journalctl -u fotolibros-worker -f

# Cola Redis
redis-cli LLEN fotolibros:cola
```

## Flujo del Sistema

1. **Cliente** completa wizard web y paga
2. **Backend** recibe pedido, guarda fotos en `/var/fotolibros/pedidos/{id}/`
3. **Backend** encola pedido en Redis
4. **Worker** toma pedido de la cola
5. **Worker** llama a **AGNO** (5 agentes Python):
   - PhotoAnalyzer → analiza fotos
   - MotifDetector → detecta ocasión
   - ChronologySpecialist → ordena cronológicamente
   - StoryGenerator → genera textos
   - DesignCurator → decide diseño
6. **AGNO** retorna JSON completo
7. **Worker** formatea JSON y envía webhook a **Clawdbot**
8. **Clawdbot** (agente "fotolibros"):
   - Abre editor FDF
   - Login
   - Crea proyecto
   - Sube fotos EN ORDEN
   - Aplica template
   - Inserta textos
   - Notifica por Telegram (narrativo)
9. **Vos** apruebas o rechazas por Telegram
10. **Clawdbot** finaliza en FDF
11. **Backend** actualiza estado

## Configuración Clave

### Clawdbot (`~/.clawdbot/clawdbot.json`)

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "~/clawd"
      },
      {
        "id": "fotolibros",
        "workspace": "~/clawd-fotolibros"
      }
    ]
  },
  "hooks": {
    "enabled": true,
    "token": "TU_TOKEN_SECRETO"
  },
  "browser": {
    "enabled": true,
    "headless": true
  }
}
```

### Backend (`.env`)

```bash
CLAWDBOT_URL=http://127.0.0.1:18789
CLAWDBOT_HOOK_TOKEN=EL_MISMO_TOKEN_DE_ARRIBA
OPENROUTER_API_KEY=sk-or-v1-xxx
TELEGRAM_ADMIN_CHAT=@tu_usuario
FDF_USER=tu_usuario_fdf
FDF_PASS=tu_password_fdf
```

## Costos por Pedido

| Componente | Costo |
|------------|-------|
| AGNO (GPT-4o-mini) | ~$0.10 |
| Clawdbot (Claude Max) | **$0** (incluido en tu plan) |
| **Total** | **~$0.10 USD** |

## Endpoints API

```bash
# Crear pedido
POST /api/pedidos

# Subir fotos
POST /api/pedidos/{id}/fotos

# Procesar (encolar)
POST /api/pedidos/{id}/procesar

# Ver estado
GET /api/pedidos/{id}/estado

# Health check
GET /health
```

## Comandos Útiles

```bash
# Ver cola
redis-cli LLEN fotolibros:cola

# Ver procesando
redis-cli GET fotolibros:procesando

# Ver completados
redis-cli LRANGE fotolibros:completados 0 -1

# Ver errores
redis-cli LRANGE fotolibros:errores 0 -1

# Reiniciar servicios
sudo systemctl restart fotolibros-backend fotolibros-worker

# Ver logs
journalctl -u fotolibros-backend -f
journalctl -u fotolibros-worker -f
```

## Documentación Completa

- `README.md` - Descripción general del proyecto
- `DEPLOYMENT.md` - Guía completa de deployment y troubleshooting
- `backend/app/` - Código del backend FastAPI
- `clawdbot/` - Archivos de configuración de Clawdbot
- `scripts/` - Scripts de instalación y deployment

## Soporte

- Logs del backend: `/tmp/fotolibros/backend.log`
- Logs de Clawdbot: `/tmp/clawdbot/clawdbot.log`
- Fotos procesadas: `/var/fotolibros/pedidos/`

---

**Creado para Fotolibros Argentina - 2026**
