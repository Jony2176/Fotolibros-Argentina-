#!/bin/bash
# Script de instalación completa en VPS Ubuntu 24.04

set -e  # Exit on error

echo "=================================="
echo "  FOTOLIBROS ARGENTINA - INSTALL"
echo "=================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar que estamos en Ubuntu
if ! grep -q "Ubuntu" /etc/os-release; then
    echo "⚠️  Este script está diseñado para Ubuntu 24.04"
    exit 1
fi

echo -e "${GREEN}✓${NC} Sistema operativo verificado"

# 2. Actualizar sistema
echo ""
echo "📦 Actualizando sistema..."
sudo apt update
sudo apt upgrade -y

# 3. Instalar dependencias del sistema
echo ""
echo "📦 Instalando dependencias..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    redis-server \
    nginx \
    git

echo -e "${GREEN}✓${NC} Dependencias instaladas"

# 4. Crear usuario de base de datos
echo ""
echo "🗄️  Configurando PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE fotolibros;" || echo "BD ya existe"
sudo -u postgres psql -c "CREATE USER fotolibros WITH PASSWORD 'fotolibros';" || echo "Usuario ya existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE fotolibros TO fotolibros;"

echo -e "${GREEN}✓${NC} PostgreSQL configurado"

# 5. Iniciar Redis
echo ""
echo "🔴 Iniciando Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo -e "${GREEN}✓${NC} Redis iniciado"

# 6. Crear directorio de fotos
echo ""
echo "📁 Creando directorio de almacenamiento..."
sudo mkdir -p /var/fotolibros/pedidos
sudo chown -R $USER:$USER /var/fotolibros

echo -e "${GREEN}✓${NC} Directorio creado"

# 7. Crear entorno virtual Python
echo ""
echo "🐍 Creando entorno virtual Python..."
cd "$(dirname "$0")/.."
python3.11 -m venv backend/venv
source backend/venv/bin/activate

echo -e "${GREEN}✓${NC} Entorno virtual creado"

# 8. Instalar dependencias Python
echo ""
echo "📦 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo -e "${GREEN}✓${NC} Dependencias Python instaladas"

# 9. Copiar archivos de Clawdbot
echo ""
echo "🦞 Configurando Clawdbot..."

# Copiar SOUL.md
cp clawdbot/SOUL.md ~/clawd-fotolibros/SOUL.md || mkdir -p ~/clawd-fotolibros && cp clawdbot/SOUL.md ~/clawd-fotolibros/SOUL.md

# Copiar skill
mkdir -p ~/.clawdbot/skills/fotolibros-fdf
cp clawdbot/skills/fotolibros-fdf/SKILL.md ~/.clawdbot/skills/fotolibros-fdf/SKILL.md

echo -e "${GREEN}✓${NC} Archivos de Clawdbot copiados"

# 10. Crear archivo .env
echo ""
echo "⚙️  Configurando variables de entorno..."

if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}⚠️  Copiando .env.example a .env${NC}"
    cp backend/.env.example backend/.env
    echo ""
    echo -e "${YELLOW}⚠️  IMPORTANTE: Edita backend/.env con tus credenciales:${NC}"
    echo "   - CLAWDBOT_HOOK_TOKEN"
    echo "   - OPENROUTER_API_KEY"
    echo "   - TELEGRAM_ADMIN_CHAT"
    echo "   - FDF_USER / FDF_PASS"
    echo ""
    echo "   nano backend/.env"
    echo ""
fi

# 11. Crear servicios systemd
echo ""
echo "🔧 Creando servicios systemd..."

# Servicio del backend
sudo tee /etc/systemd/system/fotolibros-backend.service > /dev/null <<EOF
[Unit]
Description=Fotolibros Argentina Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/backend
Environment="PATH=$(pwd)/backend/venv/bin"
ExecStart=$(pwd)/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Servicio del worker
sudo tee /etc/systemd/system/fotolibros-worker.service > /dev/null <<EOF
[Unit]
Description=Fotolibros Argentina Worker
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)/backend
Environment="PATH=$(pwd)/backend/venv/bin"
ExecStart=$(pwd)/backend/venv/bin/python app/worker.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload

echo -e "${GREEN}✓${NC} Servicios creados"

# 12. Resumen
echo ""
echo "=================================="
echo "  ✅ INSTALACIÓN COMPLETADA"
echo "=================================="
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Editar configuración:"
echo "   nano backend/.env"
echo ""
echo "2. Actualizar Clawdbot config:"
echo "   nano ~/.clawdbot/clawdbot.json"
echo "   (Agregar configuración de agente 'fotolibros')"
echo ""
echo "3. Iniciar servicios:"
echo "   ./scripts/start.sh"
echo ""
echo "4. Ver logs:"
echo "   journalctl -u fotolibros-backend -f"
echo "   journalctl -u fotolibros-worker -f"
echo ""
