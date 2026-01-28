#!/bin/bash
# Instalación evitando puertos ocupados
# Backend: 8001 (8000 ocupado)
# Nginx: 8080 (80/443 ocupados por Docker)

set -e

echo "=========================================="
echo "  FOTOLIBROS - Puertos Libres"
echo "  Backend: 8001 | Nginx: 8080"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. Actualizar sistema
echo -e "${BLUE}📦 Actualizando sistema...${NC}"
apt update
apt upgrade -y

# 2. Instalar dependencias
echo ""
echo -e "${BLUE}📦 Instalando dependencias...${NC}"
apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nodejs \
    nginx \
    git \
    curl

# Node 20
if ! node --version | grep -q "v2[0-9]"; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | -E bash -
    apt install -y nodejs
fi

echo -e "${GREEN}✓${NC} Dependencias instaladas"

# 3. Directorios
echo ""
echo -e "${BLUE}📁 Creando directorios...${NC}"
mkdir -p /var/fotolibros/pedidos
chown -R root:root /var/fotolibros

# 4. Backend (Puerto 8001)
echo ""
echo -e "${BLUE}🐍 Backend (Puerto 8001)...${NC}"
cd "$(dirname "$0")/.."

python3.11 -m venv backend/venv
source backend/venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
python3.11 backend/app/db.py

echo -e "${GREEN}✓${NC} Backend configurado"

# 5. Frontend
echo ""
echo -e "${BLUE}⚛️  Frontend...${NC}"
cd frontend
npm install
npm run build
cd ..

mkdir -p /var/www/fotolibros
cp -r frontend/dist/* /var/www/fotolibros/
chown -R www-data:www-data /var/www/fotolibros

echo -e "${GREEN}✓${NC} Frontend built"

# 6. Clawdbot
echo ""
echo -e "${BLUE}🦞 Clawdbot...${NC}"
mkdir -p /root/clawd-fotolibros
cp clawdbot/SOUL.md /root/clawd-fotolibros/SOUL.md
mkdir -p /root/.clawdbot/skills/fotolibros-fdf
cp clawdbot/skills/fotolibros-fdf/SKILL.md /root/.clawdbot/skills/fotolibros-fdf/SKILL.md

echo -e "${GREEN}✓${NC} Clawdbot files copiados"

# 7. Nginx (Puerto 8080)
echo ""
echo -e "${BLUE}🌐 Nginx (Puerto 8080)...${NC}"

cat > /etc/nginx/sites-available/fotolibros <<'EOF'
server {
    listen 8080;
    server_name _;
    
    location / {
        root /var/www/fotolibros;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # Backend en puerto 8001
    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_bypass $http_upgrade;
    }
    
    location /health {
        proxy_pass http://localhost:8001/health;
    }
}
EOF

ln -sf /etc/nginx/sites-available/fotolibros /etc/nginx/sites-enabled/fotolibros
nginx -t
systemctl reload nginx

echo -e "${GREEN}✓${NC} Nginx en puerto 8080"

# 8. Servicios (Backend en 8001)
echo ""
echo -e "${BLUE}🔧 Servicios systemd...${NC}"

cat > /etc/systemd/system/fotolibros-backend.service <<EOF
[Unit]
Description=Fotolibros Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)/backend
Environment="PATH=$(pwd)/backend/venv/bin"
ExecStart=$(pwd)/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/fotolibros-worker.service <<EOF
[Unit]
Description=Fotolibros Worker
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$(pwd)/backend
Environment="PATH=$(pwd)/backend/venv/bin"
ExecStart=$(pwd)/backend/venv/bin/python app/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload

echo -e "${GREEN}✓${NC} Servicios creados"

# 9. .env
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
fi

# Resumen
echo ""
echo "=========================================="
echo -e "  ${GREEN}✅ INSTALACIÓN COMPLETADA${NC}"
echo "=========================================="
echo ""
echo "Puertos utilizados:"
echo "  • Frontend (Nginx): 8080"
echo "  • Backend (FastAPI): 8001"
echo "  • Clawdbot: 18789 (existente)"
echo ""
echo "URLs:"
echo "  • App: http://168.231.98.115:8080"
echo "  • API: http://168.231.98.115:8080/api/"
echo "  • Health: http://168.231.98.115:8080/health"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Configurar backend/.env:"
echo "   nano backend/.env"
echo "   (Agregar CLAWDBOT_HOOK_TOKEN, OPENROUTER_API_KEY, etc)"
echo ""
echo "2. Configurar Clawdbot:"
echo "   nano /root/.clawdbot/clawdbot.json"
echo "   (Agregar agente fotolibros y hooks)"
echo ""
echo "3. Reiniciar Clawdbot:"
echo "   systemctl restart clawdbot"
echo ""
echo "4. Iniciar servicios:"
echo "   systemctl start fotolibros-backend"
echo "   systemctl start fotolibros-worker"
echo "   systemctl enable fotolibros-backend"
echo "   systemctl enable fotolibros-worker"
echo ""
echo "5. Verificar:"
echo "   curl http://localhost:8080/health"
echo "   journalctl -u fotolibros-backend -f"
echo ""
