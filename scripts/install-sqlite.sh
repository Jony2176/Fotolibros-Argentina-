#!/bin/bash
# Script de instalación con SQLite (sin PostgreSQL ni Redis)

set -e

echo "=================================="
echo "  FOTOLIBROS ARGENTINA - INSTALL"
echo "  Versión SQLite Simplificada"
echo "=================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Verificar Ubuntu
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

# 3. Instalar dependencias (SIN PostgreSQL ni Redis)
echo ""
echo "📦 Instalando dependencias..."
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    nginx \
    git

echo -e "${GREEN}✓${NC} Dependencias instaladas"

# 4. Crear directorio de datos
echo ""
echo "📁 Creando directorios..."
sudo mkdir -p /var/fotolibros/pedidos
sudo chown -R $USER:$USER /var/fotolibros

echo -e "${GREEN}✓${NC} Directorios creados"

# 5. Inicializar base de datos SQLite
echo ""
echo "🗄️  Inicializando base de datos SQLite..."
cd "$(dirname "$0")/.."
python3.11 backend/app/db.py

echo -e "${GREEN}✓${NC} Base de datos SQLite creada en /var/fotolibros/fotolibros.db"

# 6. Crear entorno virtual Python
echo ""
echo "🐍 Creando entorno virtual..."
python3.11 -m venv backend/venv
source backend/venv/bin/activate

echo -e "${GREEN}✓${NC} Entorno virtual creado"

# 7. Instalar dependencias Python
echo ""
echo "📦 Instalando dependencias Python..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo -e "${GREEN}✓${NC} Dependencias Python instaladas"

# 8. Copiar archivos Clawdbot
echo ""
echo "🦞 Configurando Clawdbot..."
cp clawdbot/SOUL.md ~/clawd-fotolibros/SOUL.md || mkdir -p ~/clawd-fotolibros && cp clawdbot/SOUL.md ~/clawd-fotolibros/SOUL.md
mkdir -p ~/.clawdbot/skills/fotolibros-fdf
cp clawdbot/skills/fotolibros-fdf/SKILL.md ~/.clawdbot/skills/fotolibros-fdf/SKILL.md

echo -e "${GREEN}✓${NC} Archivos Clawdbot copiados"

# 9. Crear .env
echo ""
echo "⚙️  Configurando variables de entorno..."
if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}⚠️  Edita backend/.env con tus credenciales:${NC}"
    echo "   nano backend/.env"
    echo ""
fi

# 10. Crear servicios systemd
echo ""
echo "🔧 Creando servicios..."

sudo tee /etc/systemd/system/fotolibros-backend.service > /dev/null <<EOF
[Unit]
Description=Fotolibros Backend
After=network.target

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

sudo tee /etc/systemd/system/fotolibros-worker.service > /dev/null <<EOF
[Unit]
Description=Fotolibros Worker
After=network.target

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

# 11. Resumen
echo ""
echo "=================================="
echo "  ✅ INSTALACIÓN COMPLETADA"
echo "=================================="
echo ""
echo "Stack instalado:"
echo "  • Python 3.11 + FastAPI"
echo "  • SQLite (base de datos única)"
echo "  • Nginx (reverse proxy)"
echo ""
echo "NO instalado (no necesario):"
echo "  ✗ PostgreSQL"
echo "  ✗ Redis"
echo ""
echo "Ventajas:"
echo "  • Cero mantenimiento de servicios"
echo "  • Backup = copiar un solo archivo"
echo "  • SQLite es ACID compliant"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Editar .env:"
echo "   nano backend/.env"
echo ""
echo "2. Actualizar ~/.clawdbot/clawdbot.json"
echo ""
echo "3. Iniciar:"
echo "   ./scripts/start.sh"
echo ""
