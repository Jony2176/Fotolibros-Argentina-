# 🚀 Deployment Completo - Todo el Stack

## Sistema Completo Incluido

```
fotolibros-vps-deploy/
├── frontend/          ✅ React + Vite (tu frontend existente)
├── backend/           ✅ FastAPI + AGNO + Worker
├── clawdbot/          ✅ Configuración Clawdbot
└── scripts/           ✅ Scripts de instalación
```

---

## Arquitectura Final en el VPS

```
┌────────────────────────────────────────────────────────────────┐
│                    VPS Ubuntu 24.04                            │
│                   168.231.98.115                               │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Internet → NGINX (Puerto 80)                                  │
│                │                                               │
│       ┌────────┴────────┐                                      │
│       ▼                 ▼                                      │
│  /var/www/fotolibros  FastAPI:8000                             │
│  (React build)         (Backend API)                           │
│                            │                                   │
│                            ▼                                   │
│                     SQLite + Worker                            │
│                            │                                   │
│                     ┌──────┴──────┐                            │
│                     ▼             ▼                            │
│                   AGNO        CLAWDBOT                          │
│                                    │                           │
│                                    ▼                           │
│                            Chrome Headless                     │
│                                    │                           │
└────────────────────────────────────┼───────────────────────────┘
                                     │
                                     ▼
                              FDF Editor
```

---

## Paso a Paso - Deployment Completo

### PASO 1: En tu PC - Preparar el Proyecto

```powershell
cd C:\Users\Usuario\Downloads\fotolibros_argentina\

# Comprimir TODO el proyecto
Compress-Archive -Path fotolibros-vps-deploy\* -DestinationPath fotolibros-completo.zip -Force
```

El archivo será ~10-20 MB (sin node_modules).

---

### PASO 2: Subir al VPS

```powershell
# Opción A: SCP
scp fotolibros-completo.zip usuario@168.231.98.115:/home/usuario/

# Opción B: WinSCP / FileZilla
# Subir fotolibros-completo.zip a /home/usuario/
```

---

### PASO 3: En el VPS - Descomprimir

```bash
ssh usuario@168.231.98.115

cd /home/usuario
unzip fotolibros-completo.zip -d fotolibros-app
cd fotolibros-app
```

---

### PASO 4: Ejecutar Instalación Completa

```bash
chmod +x scripts/*.sh
./scripts/install-full.sh
```

Este script instala:
- ✅ Python + FastAPI
- ✅ Node.js + npm
- ✅ Frontend (build + deploy a nginx)
- ✅ Backend + Worker
- ✅ SQLite
- ✅ Nginx
- ✅ Servicios systemd

**Tiempo estimado: 10-15 minutos**

---

### PASO 5: Configurar Variables de Entorno

#### Backend

```bash
nano backend/.env
```

Configurar:
```bash
CLAWDBOT_HOOK_TOKEN=genera_token_secreto_123
OPENROUTER_API_KEY=sk-or-v1-tu_key
TELEGRAM_ADMIN_CHAT=@tu_usuario
FDF_USER=tu_usuario_fdf
FDF_PASS=tu_password_fdf
```

#### Frontend (si es necesario)

El frontend ya está configurado para usar `/api/` (nginx lo routea al backend).

---

### PASO 6: Configurar Clawdbot

```bash
nano ~/.clawdbot/clawdbot.json
```

Agregar:

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
    "token": "EL_MISMO_TOKEN_DEL_BACKEND_ENV"
  },
  "browser": {
    "enabled": true,
    "headless": true,
    "noSandbox": true
  }
}
```

---

### PASO 7: Reiniciar Clawdbot

```bash
sudo systemctl restart clawdbot
```

---

### PASO 8: Iniciar Servicios

```bash
sudo systemctl start fotolibros-backend
sudo systemctl start fotolibros-worker
sudo systemctl enable fotolibros-backend
sudo systemctl enable fotolibros-worker
```

---

### PASO 9: Verificar que Todo Funciona

```bash
# 1. Backend health check
curl http://localhost:8000/health

# 2. Frontend
curl http://localhost/

# 3. Ver logs backend
journalctl -u fotolibros-backend -f

# 4. Ver logs worker
journalctl -u fotolibros-worker -f

# 5. Ver servicios
sudo systemctl status fotolibros-backend
sudo systemctl status fotolibros-worker
sudo systemctl status nginx
```

---

### PASO 10: Acceder desde el Navegador

```
http://168.231.98.115
```

Deberías ver tu frontend de React funcionando.

---

## Configurar Dominio (Opcional)

Si tenés un dominio (ej: `fotolibros.com.ar`):

### 1. DNS

Agregar registro A:
```
A    @    168.231.98.115
A    www  168.231.98.115
```

### 2. Actualizar Nginx

```bash
sudo nano /etc/nginx/sites-available/fotolibros
```

Cambiar:
```nginx
server_name fotolibros.com.ar www.fotolibros.com.ar;
```

### 3. SSL con Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d fotolibros.com.ar -d www.fotolibros.com.ar
```

---

## Estructura de Archivos en el VPS

```
/home/usuario/fotolibros-app/
├── frontend/
│   ├── dist/                    → Copiado a /var/www/fotolibros
│   ├── src/
│   └── package.json
├── backend/
│   ├── venv/                    → Entorno Python
│   ├── app/
│   │   ├── main.py
│   │   ├── worker.py
│   │   ├── db.py
│   │   └── ...
│   └── agno/
└── clawdbot/

/var/fotolibros/
├── fotolibros.db                → Base de datos SQLite
└── pedidos/
    ├── PED-001/
    └── PED-002/

/var/www/fotolibros/             → Frontend servido por nginx
├── index.html
├── assets/
└── ...

~/.clawdbot/
├── clawdbot.json
└── skills/
    └── fotolibros-fdf/

~/clawd-fotolibros/
└── SOUL.md
```

---

## Puertos Utilizados

| Servicio | Puerto | Acceso |
|----------|--------|--------|
| Nginx | 80 | Público (frontend + API) |
| Backend FastAPI | 8000 | localhost (via nginx) |
| Clawdbot | 18789 | localhost |
| SQLite | - | archivo local |

---

## Flujo de una Request

```
Cliente → http://tu-vps/
         ↓
      Nginx:80
         ↓
   /var/www/fotolibros/index.html (React)
         ↓
   JavaScript hace fetch('/api/pedidos')
         ↓
      Nginx proxy_pass → localhost:8000/api/pedidos
         ↓
      FastAPI Backend
         ↓
      SQLite
```

---

## Comandos Útiles

### Ver Logs

```bash
# Backend
journalctl -u fotolibros-backend -f

# Worker
journalctl -u fotolibros-worker -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Clawdbot
tail -f /tmp/clawdbot/clawdbot.log
```

### Reiniciar Servicios

```bash
sudo systemctl restart fotolibros-backend
sudo systemctl restart fotolibros-worker
sudo systemctl restart nginx
```

### Ver Cola

```bash
sqlite3 /var/fotolibros/fotolibros.db \
  "SELECT pedido_id, estado, fecha_encolado FROM cola ORDER BY fecha_encolado"
```

### Backup

```bash
# Backup completo
cd /var/fotolibros
tar -czf backup-$(date +%Y%m%d).tar.gz fotolibros.db pedidos/

# Solo DB
cp fotolibros.db fotolibros-backup-$(date +%Y%m%d).db
```

---

## Troubleshooting

### Frontend no carga

```bash
# Verificar nginx
sudo nginx -t
sudo systemctl status nginx

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

### API no responde

```bash
# Ver backend
journalctl -u fotolibros-backend -n 50

# Health check
curl http://localhost:8000/health
```

### Worker no procesa

```bash
# Ver worker
journalctl -u fotolibros-worker -n 50

# Ver cola
sqlite3 /var/fotolibros/fotolibros.db "SELECT * FROM cola"
```

---

## Actualizar el Sistema

```bash
cd /home/usuario/fotolibros-app

# Frontend
cd frontend
npm run build
sudo cp -r dist/* /var/www/fotolibros/
cd ..

# Backend
sudo systemctl restart fotolibros-backend
sudo systemctl restart fotolibros-worker
```

---

## ✅ Checklist Final

- [ ] Archivo comprimido creado
- [ ] Subido al VPS
- [ ] Descomprimido en `/home/usuario/fotolibros-app`
- [ ] `install-full.sh` ejecutado
- [ ] `backend/.env` configurado
- [ ] `~/.clawdbot/clawdbot.json` configurado
- [ ] Clawdbot reiniciado
- [ ] Servicios backend y worker iniciados
- [ ] Nginx funcionando
- [ ] Frontend visible en navegador
- [ ] API health check OK
- [ ] Test de pedido exitoso

---

## 🎉 Sistema Completo Funcionando

Cuando todo esté ✅:

1. **Frontend**: `http://TU_IP_VPS`
2. **API**: `http://TU_IP_VPS/api/health`
3. **Cliente** puede crear pedidos
4. **Worker** los procesa automáticamente
5. **Clawdbot** ejecuta en FDF
6. **Vos** recibís notificación en Telegram

---

**Stack Final:**
- Frontend: React + Vite
- Backend: FastAPI
- DB: SQLite
- Cola: SQLite
- Análisis: AGNO (Python)
- Ejecución: Clawdbot (Claude Max)
- Servidor: Nginx
- Costo por pedido: ~$0.10 USD

**TODO en un solo VPS Ubuntu 24.04** 🚀
