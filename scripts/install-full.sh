#!/bin/bash
# Instalación COMPLETA: Frontend + Backend + Clawdbot
# Todo en un solo VPS con SQLite

set -e

echo "=========================================="
echo "  FOTOLIBROS ARGENTINA"
echo "  Instalación Completa"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ==========================================
# 1. VERIFICACIONES
# ==========================================

if ! grep -q "Ubuntu" /etc/os-release; then
    echo "⚠️  Este script está diseñado para Ubuntu 24.04"
    exit 1
fi

echo -e "${GREEN}✓${NC} Sistema: Ubuntu"

# ==========================================
# 2. ACTUALIZAR SISTEMA
# ==========================================

echo ""
echo -e "${BLUE}📦 Actualizando sistema...${NC}"
sudo apt update
sudo apt upgrade -y

# ==========================================
# 3. INSTALAR DEPENDENCIAS
# ==========================================

echo ""
echo -e "${BLUE}📦 Instalando dependencias...${NC}"
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nodejs \
    npm \
    nginx \
    git \
    curl

echo -e "${GREEN}✓${NC} Dependencias instaladas"

# Instalar Node 20 LTS si es necesario
if ! node --version | grep -q "v2[0-9]"; then
    echo ""
    echo -e "${BLUE}📦 Instalando Node.js 20 LTS...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
fi

echo -e "${GREEN}✓${NC} Node.js $(node --version)"
echo -e "${GREEN}✓${NC} npm $(npm --version)"

# ==========================================
# 4. CREAR DIRECTORIOS
# ==========================================

echo ""
echo -e "${BLUE}📁 Creando directorios...${NC}"
sudo mkdir -p /var/fotolibros/pedidos
sudo chown -R $USER:$USER /var/fotolibros

echo -e "${GREEN}✓${NC} Directorio: /var/fotolibros/"

# ==========================================
# 5. BACKEND - Python
# ==========================================

echo ""
echo "=========================================="
echo "  BACKEND (FastAPI + AGNO)"
echo "=========================================="

cd "$(dirname "$0")/.."

# Crear venv
echo ""
echo -e "${BLUE}🐍 Creando entorno virtual Python...${NC}"
python3.11 -m venv backend/venv
source backend/venv/bin/activate

# Instalar dependencias
echo ""
echo -e "${BLUE}📦 Instalando dependencias Python...${NC}"
pip install --upgrade pip
pip install -r backend/requirements.txt

echo -e "${GREEN}✓${NC} Backend dependencies instaladas"

# Inicializar DB
echo ""
echo -e "${BLUE}🗄️  Inicializando SQLite...${NC}"
python3.11 backend/app/db.py

echo -e "${GREEN}✓${NC} Base de datos: /var/fotolibros/fotolibros.db"

# Configurar .env
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  Configura backend/.env:${NC}"
    echo "   nano backend/.env"
    echo ""
fi

# ==========================================
# 6. FRONTEND - React + Vite
# ==========================================

echo ""
echo "=========================================="
echo "  FRONTEND (React + Vite)"
echo "=========================================="

cd frontend

# Instalar dependencias
echo ""
echo -e "${BLUE}📦 Instalando dependencias npm...${NC}"
npm install

echo -e "${GREEN}✓${NC} Frontend dependencies instaladas"

# Build para producción
echo ""
echo -e "${BLUE}🔨 Building frontend...${NC}"
npm run build

echo -e "${GREEN}✓${NC} Frontend build: frontend/dist/"

cd ..

# ==========================================
# 7. CLAWDBOT
# ==========================================

echo ""
echo "=========================================="
echo "  CLAWDBOT"
echo "=========================================="

# Copiar SOUL.md
mkdir -p ~/clawd-fotolibros
cp clawdbot/SOUL.md ~/clawd-fotolibros/SOUL.md

# Copiar skill
mkdir -p ~/.clawdbot/skills/fotolibros-fdf
cp clawdbot/skills/fotolibros-fdf/SKILL.md ~/.clawdbot/skills/fotolibros-fdf/SKILL.md

echo -e "${GREEN}✓${NC} Archivos Clawdbot copiados"

# ==========================================
# 8. NGINX
# ==========================================

echo ""
echo "=========================================="
echo "  NGINX (Reverse Proxy)"
echo "=========================================="

# Configuración de nginx
sudo tee /etc/nginx/sites-available/fotolibros > /dev/null <<'EOF'
# Frontend (React app estático)
server {
    listen 80;
    server_name _;
    
    # Servir frontend
    location / {
        root /var/www/fotolibros;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
EOF

# Copiar frontend build a /var/www
sudo mkdir -p /var/www/fotolibros
sudo cp -r frontend/dist/* /var/www/fotolibros/
sudo chown -R www-data:www-data /var/www/fotolibros

# Habilitar sitio
sudo ln -sf /etc/nginx/sites-available/fotolibros /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test y reload nginx
sudo nginx -t
sudo systemctl reload nginx

echo -e "${GREEN}✓${NC} Nginx configurado"

# ==========================================
# 9. SERVICIOS SYSTEMD
# ==========================================

echo ""
echo "=========================================="
echo "  SERVICIOS SYSTEMD"
echo "=========================================="

# Backend service
sudo tee /etc/systemd/system/fotolibros-backend.service > /dev/null <<EOF
[Unit]
Description=Fotolibros Backend (FastAPI)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/backend
Environment="PATH=$(pwd)/backend/venv/bin"
ExecStart=$(pwd)/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Worker service
sudo tee /etc/systemd/system/fotolibros-worker.service > /dev/null <<EOF
[Unit]
Description=Fotolibros Worker (Cola de procesamiento)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/backend
Environment="PATH=$(pwd)/backend/venv/bin"
ExecStart=$(pwd)/backend/venv/bin/python app/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo -e "${GREEN}✓${NC} Servicios creados"

# ==========================================
# 10. RESUMEN
# ==========================================

echo ""
echo "=========================================="
echo -e "  ${GREEN}✅ INSTALACIÓN COMPLETADA${NC}"
echo "=========================================="
echo ""
echo "Stack instalado:"
echo "  • Frontend: React + Vite → /var/www/fotolibros"
echo "  • Backend: FastAPI → Puerto 8000"
echo "  • Worker: Procesador de cola"
echo "  • DB: SQLite → /var/fotolibros/fotolibros.db"
echo "  • Nginx: Reverse proxy → Puerto 80"
echo "  • Clawdbot: Agente FotoBot"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Configurar backend/.env:"
echo "   nano backend/.env"
echo ""
echo "2. Configurar ~/.clawdbot/clawdbot.json"
echo "   (Agregar agente 'fotolibros' y hooks)"
echo ""
echo "3. Reiniciar Clawdbot:"
echo "   sudo systemctl restart clawdbot"
echo ""
echo "4. Iniciar servicios:"
echo "   sudo systemctl start fotolibros-backend"
echo "   sudo systemctl start fotolibros-worker"
echo "   sudo systemctl enable fotolibros-backend"
echo "   sudo systemctl enable fotolibros-worker"
echo ""
echo "5. Verificar:"
echo "   curl http://localhost/health"
echo "   curl http://localhost"
echo ""
echo "Tu app estará en: http://TU_IP_VPS"
echo ""
