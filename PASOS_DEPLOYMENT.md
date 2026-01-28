# 🚀 Pasos para Deployar - Fotolibros Argentina

## ✅ Archivos Listos

Ya tenés todo el proyecto preparado en:
```
C:\Users\Usuario\Downloads\fotolibros_argentina\fotolibros-vps-deploy\
```

---

## 📋 Paso a Paso

### PASO 1: Comprimir el Proyecto

En PowerShell (Windows):

```powershell
cd C:\Users\Usuario\Downloads\fotolibros_argentina\

Compress-Archive -Path fotolibros-vps-deploy\* -DestinationPath fotolibros-deploy.zip -Force
```

Esto crea `fotolibros-deploy.zip` (~2-5 MB)

---

### PASO 2: Subir al VPS

**Opción A - SCP (desde PowerShell):**

```powershell
scp fotolibros-deploy.zip usuario@168.231.98.115:/home/usuario/
```

**Opción B - WinSCP / FileZilla:**
1. Abrir WinSCP o FileZilla
2. Conectar a: `168.231.98.115`
3. Usuario: `usuario` (el que uses)
4. Subir `fotolibros-deploy.zip` a `/home/usuario/`

---

### PASO 3: Conectarse al VPS

```powershell
ssh usuario@168.231.98.115
```

---

### PASO 4: Descomprimir en el VPS

```bash
cd /home/usuario
unzip fotolibros-deploy.zip -d fotolibros-vps-deploy
cd fotolibros-vps-deploy
```

---

### PASO 5: Dar Permisos a Scripts

```bash
chmod +x scripts/*.sh
```

---

### PASO 6: Ejecutar Instalación

```bash
./scripts/install.sh
```

Esto instalará:
- PostgreSQL y Redis
- Python 3.11 + dependencias
- Creará base de datos
- Creará servicios systemd
- Copiará archivos de Clawdbot

**Tiempo estimado:** 5-10 minutos

---

### PASO 7: Configurar Variables de Entorno

```bash
nano backend/.env
```

**Editar estos valores:**

```bash
# Clawdbot
CLAWDBOT_HOOK_TOKEN=genera_un_token_secreto_aqui    # ej: clawdbot-hook-2026-secret-xyz

# OpenRouter (para AGNO)
OPENROUTER_API_KEY=sk-or-v1-TU_API_KEY_AQUI

# Telegram
TELEGRAM_ADMIN_CHAT=@tu_usuario_telegram            # ej: @juanperez

# FDF
FDF_USER=tu_usuario_fdf
FDF_PASS=tu_password_fdf
```

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### PASO 8: Actualizar Configuración de Clawdbot

```bash
nano ~/.clawdbot/clawdbot.json
```

**Agregar/actualizar esta sección:**

```json
{
  "agents": {
    "defaults": {
      "model": "anthropic/claude-opus-4-5",
      "thinking": "high"
    },
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "~/clawd",
        "identity": {
          "name": "Clawd",
          "emoji": "🦞"
        }
      },
      {
        "id": "fotolibros",
        "workspace": "~/clawd-fotolibros",
        "identity": {
          "name": "FotoBot",
          "emoji": "📚"
        }
      }
    ]
  },
  
  "hooks": {
    "enabled": true,
    "token": "EL_MISMO_TOKEN_DEL_PASO_7",
    "path": "/hooks"
  },
  
  "browser": {
    "enabled": true,
    "headless": true,
    "noSandbox": true
  }
  
  // ... el resto de tu configuración
}
```

**Importante:** El `hooks.token` debe ser IGUAL al `CLAWDBOT_HOOK_TOKEN` del `.env`

**Guardar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

### PASO 9: Reiniciar Clawdbot

```bash
# Si Clawdbot corre como servicio
sudo systemctl restart clawdbot

# O si lo tenés corriendo manual, detenerlo y volverlo a iniciar
# Ctrl+C y luego:
clawdbot gateway --port 18789
```

---

### PASO 10: Iniciar Servicios

```bash
./scripts/start.sh
```

Esto inicia:
- `fotolibros-backend` (FastAPI en puerto 8000)
- `fotolibros-worker` (procesa cola)

---

### PASO 11: Verificar que Todo Funciona

```bash
# 1. Health check del backend
curl http://localhost:8000/health

# Deberías ver algo como:
# {"status":"healthy","queue":{"en_cola":0,...}}

# 2. Ver logs del backend
journalctl -u fotolibros-backend -f
# Ctrl+C para salir

# 3. Ver logs del worker
journalctl -u fotolibros-worker -f
# Ctrl+C para salir

# 4. Verificar Redis
redis-cli ping
# Debería responder: PONG

# 5. Verificar PostgreSQL
sudo -u postgres psql -c "\l" | grep fotolibros
# Debería mostrar la base de datos

# 6. Verificar que Clawdbot está escuchando
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"test","name":"Test","sessionKey":"test:1"}'

# Debería retornar status 202
```

---

### PASO 12: Test Completo (Opcional)

```bash
# 1. Crear directorio de fotos de prueba
mkdir -p /var/fotolibros/pedidos/PED-TEST-001

# 2. Subir algunas fotos de prueba
# (scp desde tu PC o usar fotos de ejemplo)

# 3. Crear pedido de prueba vía API
curl -X POST http://localhost:8000/api/pedidos/PED-TEST-001/procesar

# 4. Ver en logs
journalctl -u fotolibros-worker -f

# Deberías ver:
# - AGNO analizando fotos
# - Webhook enviándose a Clawdbot
# - Clawdbot procesando

# 5. Verificar en Telegram
# Deberías recibir notificaciones de FotoBot
```

---

## 🎯 Resumen de Puertos

| Servicio | Puerto | Acceso |
|----------|--------|--------|
| Backend FastAPI | 8000 | localhost |
| Clawdbot Gateway | 18789 | localhost |
| PostgreSQL | 5432 | localhost |
| Redis | 6379 | localhost |

---

## 📊 Comandos Útiles

### Ver Estado de Servicios
```bash
sudo systemctl status fotolibros-backend
sudo systemctl status fotolibros-worker
```

### Reiniciar Servicios
```bash
sudo systemctl restart fotolibros-backend
sudo systemctl restart fotolibros-worker
```

### Ver Cola Redis
```bash
redis-cli LLEN fotolibros:cola
redis-cli GET fotolibros:procesando
```

### Ver Logs en Tiempo Real
```bash
# Backend
journalctl -u fotolibros-backend -f

# Worker
journalctl -u fotolibros-worker -f

# Clawdbot
tail -f /tmp/clawdbot/clawdbot.log
```

---

## ⚠️ Troubleshooting

### Backend no inicia
```bash
journalctl -u fotolibros-backend -n 50 --no-pager
# Ver el error específico
```

### Worker no procesa
```bash
journalctl -u fotolibros-worker -n 50 --no-pager
```

### Clawdbot no recibe webhooks
```bash
# Verificar que está corriendo
ps aux | grep clawdbot

# Verificar puerto
netstat -tulpn | grep 18789
```

### Skill no se carga
```bash
ls -la ~/.clawdbot/skills/fotolibros-fdf/
cat ~/.clawdbot/skills/fotolibros-fdf/SKILL.md
```

---

## ✅ Checklist Final

- [ ] Archivo comprimido
- [ ] Subido al VPS
- [ ] Descomprimido
- [ ] Scripts con permisos
- [ ] Instalación ejecutada
- [ ] `.env` configurado
- [ ] `clawdbot.json` actualizado
- [ ] Clawdbot reiniciado
- [ ] Servicios iniciados
- [ ] Health check OK
- [ ] Logs sin errores
- [ ] Webhook test OK

---

## 🎉 ¡Listo!

Si todo está ✅, ya tenés el sistema corriendo.

**Próximo paso:** Integrar con tu frontend web para que los clientes puedan crear pedidos.

---

**Documentación completa:**
- `QUICKSTART.md` - Guía rápida
- `DEPLOYMENT.md` - Troubleshooting detallado
- `README.md` - Arquitectura del sistema
