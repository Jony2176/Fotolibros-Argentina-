# Guía de Deployment - Fotolibros Argentina

## Desde tu PC local al VPS

### Paso 1: Preparar el proyecto

En tu PC (Windows):

```bash
cd C:\Users\Usuario\Downloads\fotolibros_argentina\
```

### Paso 2: Copiar AGNO al proyecto

Necesitamos copiar los archivos de AGNO al proyecto:

```bash
# Copiar agentes de AGNO
xcopy fotolibros-argentina-v2\fotolibros-agno-backend\agents fotolibros-vps-deploy\backend\agno\agents\ /E /I

# Copiar archivos principales de AGNO
copy fotolibros-argentina-v2\fotolibros-agno-backend\team.py fotolibros-vps-deploy\backend\agno\
copy fotolibros-argentina-v2\fotolibros-agno-backend\__init__.py fotolibros-vps-deploy\backend\agno\
```

### Paso 3: Comprimir el proyecto

```bash
# En PowerShell
Compress-Archive -Path fotolibros-vps-deploy\* -DestinationPath fotolibros-deploy.zip
```

### Paso 4: Subir al VPS

```bash
# Usando SCP (desde PowerShell o WSL)
scp fotolibros-deploy.zip usuario@168.231.98.115:/home/usuario/

# O usar FileZilla, WinSCP, etc.
```

### Paso 5: En el VPS

```bash
# Conectarse por SSH
ssh usuario@168.231.98.115

# Descomprimir
cd /home/usuario
unzip fotolibros-deploy.zip -d fotolibros-vps-deploy

# Dar permisos a scripts
cd fotolibros-vps-deploy
chmod +x scripts/*.sh

# Ejecutar instalación
./scripts/install.sh
```

### Paso 6: Configurar

```bash
# Editar .env
nano backend/.env
```

Configurar:
- `CLAWDBOT_HOOK_TOKEN` - Token para webhooks
- `OPENROUTER_API_KEY` - Tu API key de OpenRouter
- `TELEGRAM_ADMIN_CHAT` - Tu ID de Telegram (ej: @tu_usuario)
- `FDF_USER` - Usuario de FDF
- `FDF_PASS` - Password de FDF

### Paso 7: Actualizar Clawdbot config

```bash
nano ~/.clawdbot/clawdbot.json
```

Agregar la configuración del ejemplo:
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
    "token": "EL_MISMO_TOKEN_DEL_.ENV"
  }
  // ... resto de tu config
}
```

### Paso 8: Reiniciar Clawdbot

```bash
# Si Clawdbot corre como servicio
sudo systemctl restart clawdbot

# O si corre manualmente
# Ctrl+C para detener
# clawdbot gateway --port 18789
```

### Paso 9: Iniciar servicios

```bash
cd /home/usuario/fotolibros-vps-deploy
./scripts/start.sh
```

### Paso 10: Verificar

```bash
# Ver logs del backend
journalctl -u fotolibros-backend -f

# Ver logs del worker
journalctl -u fotolibros-worker -f

# Ver estado de la cola
redis-cli LLEN fotolibros:cola

# Health check
curl http://localhost:8000/health
```

## Testing

### Test manual del flujo completo

```bash
# 1. Crear pedido de prueba
curl -X POST http://localhost:8000/api/pedidos \
  -H "Content-Type: application/json" \
  -d '{
    "cliente": {
      "nombre": "Test Cliente",
      "email": "test@example.com",
      "telefono": "+5491123456789"
    },
    "libro": {
      "codigo_producto": "CU-21x21-DURA",
      "tamano": "21x21",
      "tapa": "Dura",
      "estilo": "minimalista",
      "ocasion": "cumpleaños"
    },
    "modo_confirmacion": true
  }'

# 2. Subir fotos de prueba (preparar algunas fotos antes)
curl -X POST http://localhost:8000/api/pedidos/PED-XXX/fotos \
  -F "files=@foto1.jpg" \
  -F "files=@foto2.jpg"

# 3. Procesar pedido
curl -X POST http://localhost:8000/api/pedidos/PED-XXX/procesar

# 4. Ver estado
curl http://localhost:8000/api/pedidos/PED-XXX/estado

# 5. Monitorear Telegram
# Deberías recibir notificaciones de FotoBot
```

## Troubleshooting

### Backend no inicia

```bash
# Ver logs detallados
journalctl -u fotolibros-backend -n 100 --no-pager

# Verificar .env
cat backend/.env

# Verificar PostgreSQL
sudo systemctl status postgresql

# Verificar Redis
redis-cli ping
```

### Worker no procesa

```bash
# Ver logs del worker
journalctl -u fotolibros-worker -n 100 --no-pager

# Ver cola de Redis
redis-cli LRANGE fotolibros:cola 0 -1

# Verificar que AGNO funciona
cd backend
source venv/bin/activate
python -c "from agno.team import process_fotolibro; print('OK')"
```

### Clawdbot no recibe webhook

```bash
# Verificar que Clawdbot corre
ps aux | grep clawdbot

# Verificar puerto
netstat -tulpn | grep 18789

# Test webhook manual
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"test","name":"Test","sessionKey":"test:1"}'
```

### Skills no se cargan

```bash
# Verificar que el skill existe
ls -la ~/.clawdbot/skills/fotolibros-fdf/

# Ver logs de Clawdbot
tail -f /tmp/clawdbot/clawdbot.log

# Reiniciar Clawdbot
sudo systemctl restart clawdbot
```

## Mantenimiento

### Actualizar código

```bash
# En tu PC: hacer cambios, comprimir, subir

# En el VPS:
cd /home/usuario/fotolibros-vps-deploy

# Backup
cp -r backend backend.backup

# Actualizar archivos
# (subir nuevo zip y descomprimir)

# Reiniciar servicios
./scripts/start.sh
```

### Limpiar cola

```bash
# Vaciar cola de pedidos
redis-cli DEL fotolibros:cola

# Ver completados
redis-cli LRANGE fotolibros:completados 0 -1

# Ver errores
redis-cli LRANGE fotolibros:errores 0 -1
```

### Backup de base de datos

```bash
# Backup
pg_dump -U fotolibros fotolibros > fotolibros_backup.sql

# Restore
psql -U fotolibros fotolibros < fotolibros_backup.sql
```

## Estructura final en el VPS

```
/home/usuario/
├── fotolibros-vps-deploy/
│   ├── backend/
│   │   ├── venv/
│   │   ├── app/
│   │   ├── agno/
│   │   ├── .env
│   │   └── requirements.txt
│   ├── clawdbot/
│   ├── scripts/
│   └── README.md
├── .clawdbot/
│   ├── clawdbot.json
│   └── skills/
│       └── fotolibros-fdf/
├── clawd/              # Agente main
│   └── SOUL.md
├── clawd-fotolibros/   # Agente fotolibros
│   └── SOUL.md
└── /var/fotolibros/
    └── pedidos/
        ├── PED-2026-001/
        ├── PED-2026-002/
        └── ...
```
