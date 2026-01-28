# Arquitectura Completa - Todo en el VPS

## Stack Completo en un Solo Servidor

```
┌─────────────────────────────────────────────────────────────────┐
│                   VPS Ubuntu 24.04                              │
│                  168.231.98.115                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    NGINX (Reverse Proxy)                  │  │
│  │                    Puerto 80/443                          │  │
│  └──────────────┬──────────────────┬────────────────────────┘  │
│                 │                  │                            │
│                 ▼                  ▼                            │
│  ┌──────────────────┐   ┌──────────────────┐                   │
│  │   FRONTEND       │   │   BACKEND        │                   │
│  │   (React/Next)   │   │   (FastAPI)      │                   │
│  │   Puerto 3000    │   │   Puerto 8000    │                   │
│  └──────────────────┘   └────────┬─────────┘                   │
│                                  │                              │
│                    ┌─────────────┴─────────────┐               │
│                    ▼                           ▼               │
│         ┌──────────────────┐        ┌──────────────────┐       │
│         │   PostgreSQL     │        │     Redis        │       │
│         │   Puerto 5432    │        │   Puerto 6379    │       │
│         └──────────────────┘        └──────────────────┘       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 WORKER (Procesador)                       │  │
│  └──────────────┬───────────────────────────────────────────┘  │
│                 │                                              │
│      ┌──────────┴────────────┐                                 │
│      ▼                       ▼                                 │
│  ┌─────────┐         ┌──────────────┐                          │
│  │  AGNO   │ ──JSON─►│  CLAWDBOT    │                          │
│  │(Python) │         │  (Ejecutor)  │                          │
│  └─────────┘         └──────┬───────┘                          │
│                             │                                  │
│                             ▼                                  │
│                    Chrome Headless                             │
│                             │                                  │
└─────────────────────────────┼──────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │  online.fabricadefotolibros.com │
              └───────────────────────────────┘
```

---

## Opciones de Frontend

### Opción 1: Next.js (Recomendado)
- Framework React moderno
- SSR + API routes integradas
- Deploy simple

### Opción 2: React + Vite
- SPA puro
- Más ligero
- Sirve como archivos estáticos

### Opción 3: HTML/JS vanilla
- Más simple
- Sin build process
- Directo con nginx

---

## Estructura de Archivos Actualizada

```
/home/usuario/
├── fotolibros-app/                    # Todo el proyecto
│   ├── frontend/                      # Frontend (Next.js/React)
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── .env.local
│   │
│   ├── backend/                       # Backend FastAPI
│   │   ├── app/
│   │   ├── agno/
│   │   ├── requirements.txt
│   │   └── .env
│   │
│   ├── nginx/                         # Config Nginx
│   │   └── fotolibros.conf
│   │
│   └── scripts/
│       ├── install-full.sh           # Instalación completa
│       ├── start-all.sh              # Iniciar todo
│       └── deploy.sh                 # Deploy updates
│
├── .clawdbot/                         # Clawdbot
├── clawd/                             # Workspace main
├── clawd-fotolibros/                  # Workspace fotolibros
└── /var/fotolibros/                   # Storage fotos
```

---

## Configuración de NGINX

```nginx
# /etc/nginx/sites-available/fotolibros

# Frontend
server {
    listen 80;
    server_name tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Backend API
server {
    listen 80;
    server_name api.tu-dominio.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Servicios Systemd

### Frontend (Next.js)
```ini
[Unit]
Description=Fotolibros Frontend
After=network.target

[Service]
Type=simple
User=usuario
WorkingDirectory=/home/usuario/fotolibros-app/frontend
Environment="NODE_ENV=production"
ExecStart=/usr/bin/npm start
Restart=always

[Install]
WantedBy=multi-user.target
```

### Backend (ya creado)
```ini
# Ya existe en scripts/install.sh
```

### Worker (ya creado)
```ini
# Ya existe en scripts/install.sh
```

---

## Variables de Entorno

### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
# O en producción:
NEXT_PUBLIC_API_URL=https://api.tu-dominio.com
```

### Backend (.env)
```bash
# Ya configurado
DATABASE_URL=postgresql://...
CORS_ORIGINS=["http://localhost:3000","https://tu-dominio.com"]
```

---

## Flujo Completo del Usuario

```
1. Cliente → https://tu-dominio.com (Frontend)
2. Wizard de pedido:
   - Datos personales
   - Sube fotos
   - Elige tamaño/estilo
3. Pago con MercadoPago
4. Frontend → POST /api/pedidos (Backend)
5. Backend → Guarda en PostgreSQL
6. Backend → Guarda fotos en /var/fotolibros/
7. Backend → Encola en Redis
8. Worker → Procesa cola
9. Worker → AGNO (análisis)
10. Worker → Clawdbot (ejecución)
11. Clawdbot → FDF
12. Notificación a vos por Telegram
13. Vos aprobás
14. Estado actualizado en BD
15. Cliente ve estado en frontend
```

---

## Próximos Pasos

### ¿Qué frontend preferís?

1. **Next.js** - Completo, moderno, SSR
2. **React + Vite** - SPA simple
3. **HTML/JS** - Lo más simple

### ¿Tenés ya diseñado el frontend?

- Si ya tenés código: lo integramos
- Si no: te creo uno básico con:
  - Wizard de pedido
  - Upload de fotos
  - Integración MercadoPago
  - Dashboard de estado

---

¿Qué preferís que haga ahora?

A) Crear un frontend básico Next.js desde cero
B) Crear estructura para que integres tu frontend existente
C) Crear solo landing + form simple HTML
