# 🔒 Deployment Seguro - Sin Romper Servicios Existentes

## Plan de Deployment Paso a Paso

Vamos a deployar **sin tocar** tus servicios existentes.

---

## PASO 1: Comprimir en tu PC

```powershell
cd C:\Users\Usuario\Downloads\fotolibros_argentina\

# Comprimir proyecto
Compress-Archive -Path fotolibros-vps-deploy\* -DestinationPath fotolibros.zip -Force
```

---

## PASO 2: Subir al VPS

```powershell
# Reemplaza 'usuario' con tu usuario real
scp fotolibros.zip usuario@168.231.98.115:/home/usuario/
```

O usar WinSCP/FileZilla si preferís interfaz gráfica.

---

## PASO 3: Conectarse al VPS y Verificar Estado Actual

```bash
ssh usuario@168.231.98.115

# Descargar e ir al proyecto
cd /home/usuario
unzip fotolibros.zip -d fotolibros-app
cd fotolibros-app
chmod +x scripts/*.sh

# IMPORTANTE: Verificar qué está corriendo
./scripts/check-vps.sh
```

**Compartí el output de este comando** y ajustaremos los puertos si hay conflictos.

---

## PASO 4: Instalación con Verificación de Puertos

El script `install-full.sh` está configurado para:

| Servicio | Puerto Default | Configurable |
|----------|---------------|--------------|
| Nginx | 80 | ✅ Sí (puede usar 8080) |
| Backend | 8000 | ✅ Sí (puede usar 8001, 8002...) |
| Clawdbot | 18789 | ✅ Ya existe (no tocar) |
| Frontend | Via Nginx | - |

### Opción A: Puertos por defecto disponibles

Si el puerto 80 y 8000 están libres:

```bash
./scripts/install-full.sh
```

### Opción B: Ajustar puertos (si hay conflictos)

Edita antes de instalar:

```bash
# Backend en puerto diferente
nano backend/app/config.py
# Cambiar PORT = 8000 → PORT = 8001

# Nginx en puerto diferente
nano scripts/install-full.sh
# Buscar "listen 80" y cambiar a "listen 8080"
```

---

## PASO 5: Configurar Variables

```bash
nano backend/.env
```

Completar:
```bash
CLAWDBOT_URL=http://127.0.0.1:18789  # Puerto donde YA corre Clawdbot
CLAWDBOT_HOOK_TOKEN=genera_un_token_secreto
OPENROUTER_API_KEY=sk-or-v1-xxx
TELEGRAM_ADMIN_CHAT=@tu_usuario
FDF_USER=tu_usuario_fdf
FDF_PASS=tu_password_fdf
```

---

## PASO 6: Actualizar Clawdbot SIN Reiniciarlo

En lugar de editar el config principal, podemos usar el endpoint de config:

```bash
# Ver config actual (sin modificar)
curl http://127.0.0.1:18789/config
```

Luego agregamos la configuración de fotolibros via código (más seguro).

O editamos con cuidado:

```bash
# Backup del config
cp ~/.clawdbot/clawdbot.json ~/.clawdbot/clawdbot.json.backup

# Editar
nano ~/.clawdbot/clawdbot.json
```

Agregar SOLO estas líneas (sin tocar el resto):

```json
{
  // ... tu config existente ...
  
  "agents": {
    "list": [
      // ... tus agentes existentes ...
      {
        "id": "fotolibros",
        "workspace": "~/clawd-fotolibros"
      }
    ]
  },
  
  "hooks": {
    "enabled": true,
    "token": "EL_TOKEN_DEL_ENV"
  }
}
```

**Reiniciar Clawdbot:**

```bash
# Si corre como servicio
sudo systemctl restart clawdbot

# Si corre manual
# Ctrl+C y volver a iniciar
```

---

## PASO 7: Iniciar Solo los Servicios Nuevos

```bash
# Backend
sudo systemctl start fotolibros-backend
sudo systemctl enable fotolibros-backend

# Worker
sudo systemctl start fotolibros-worker
sudo systemctl enable fotolibros-worker

# Verificar que iniciaron
sudo systemctl status fotolibros-backend
sudo systemctl status fotolibros-worker
```

**NO reinicies nginx aún** si ya tenés sitios corriendo.

---

## PASO 8: Configurar Nginx Sin Romper Sitios Existentes

### Opción A: Subdirectorio

Tu sitio actual: `http://tu-vps/`
Fotolibros: `http://tu-vps/fotolibros/`

```bash
sudo nano /etc/nginx/sites-available/fotolibros-subdirectory
```

```nginx
# Agregar a tu server block existente
location /fotolibros {
    alias /var/www/fotolibros;
    index index.html;
    try_files $uri $uri/ /fotolibros/index.html;
}

location /api/fotolibros/ {
    proxy_pass http://localhost:8000/api/;
    proxy_set_header Host $host;
}
```

### Opción B: Subdominio

Crear `fotolibros.tu-dominio.com`:

```bash
sudo nano /etc/nginx/sites-available/fotolibros
```

```nginx
server {
    listen 80;
    server_name fotolibros.tu-dominio.com;
    
    location / {
        root /var/www/fotolibros;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/fotolibros /etc/nginx/sites-enabled/
```

### Opción C: Puerto alternativo

Nginx en otro puerto (ej: 8080):

```bash
sudo nano /etc/nginx/sites-available/fotolibros-alt-port
```

```nginx
server {
    listen 8080;
    server_name _;
    
    location / {
        root /var/www/fotolibros;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/api/;
    }
}
```

**Testear antes de aplicar:**

```bash
sudo nginx -t

# Si está OK:
sudo systemctl reload nginx
```

---

## PASO 9: Verificar que Todo Funciona

```bash
# Backend health
curl http://localhost:8000/health

# Ver logs backend
journalctl -u fotolibros-backend -f

# Ver logs worker
journalctl -u fotolibros-worker -f

# Acceder al frontend
# http://TU_IP:8080  (si usaste puerto alt)
# o http://TU_IP/fotolibros  (si usaste subdirectorio)
# o http://fotolibros.tu-dominio.com  (si usaste subdominio)
```

---

## PASO 10: Rollback si Algo Sale Mal

```bash
# Detener servicios nuevos
sudo systemctl stop fotolibros-backend
sudo systemctl stop fotolibros-worker

# Restaurar Clawdbot config
cp ~/.clawdbot/clawdbot.json.backup ~/.clawdbot/clawdbot.json
sudo systemctl restart clawdbot

# Quitar config de nginx
sudo rm /etc/nginx/sites-enabled/fotolibros
sudo systemctl reload nginx
```

---

## Troubleshooting Común

### Puerto 8000 ya en uso

```bash
# Ver qué lo usa
sudo netstat -tulpn | grep :8000

# Cambiar backend a 8001
nano backend/app/main.py
# En la última línea cambiar: --port 8001
```

### Puerto 80 ya en uso

Usar Opción B (subdominio) u Opción C (puerto alternativo).

### Clawdbot no acepta webhooks

```bash
# Verificar token
grep CLAWDBOT_HOOK_TOKEN backend/.env
cat ~/.clawdbot/clawdbot.json | grep token

# Deben coincidir!
```

### Nginx no recarga

```bash
# Ver error
sudo nginx -t

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

---

## Checklist Pre-Deployment

- [ ] Backup de config de Clawdbot
- [ ] Verificar puertos disponibles (`check-vps.sh`)
- [ ] Decidir estrategia nginx (subdirectorio/subdominio/puerto)
- [ ] Comprimir proyecto
- [ ] Subir al VPS
- [ ] Descomprimir
- [ ] Ejecutar instalación
- [ ] Configurar .env
- [ ] Actualizar Clawdbot config
- [ ] Iniciar servicios
- [ ] Configurar nginx
- [ ] Testear

---

## Próximo Paso

Ejecutá en el VPS:

```bash
./scripts/check-vps.sh
```

Y compartí el output para que ajustemos los puertos si es necesario.
