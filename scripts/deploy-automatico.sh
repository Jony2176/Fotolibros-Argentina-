#!/bin/bash
# DEPLOYMENT AUTOMÁTICO - Fotolibros Argentina
# Ejecutar DESPUÉS de subir el proyecto al VPS

set -e

echo "=========================================="
echo "  DEPLOYMENT AUTOMÁTICO"
echo "  Fotolibros Argentina"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Verificar que estamos en el directorio correcto
if [ ! -f "scripts/install.sh" ]; then
    echo -e "${RED}❌ Error: Ejecuta este script desde fotolibros-vps-deploy/${NC}"
    echo "   cd fotolibros-vps-deploy && ./scripts/deploy-automatico.sh"
    exit 1
fi

# 1. Permisos a scripts
echo -e "${BLUE}📝 Dando permisos a scripts...${NC}"
chmod +x scripts/*.sh
echo -e "${GREEN}✓${NC} Permisos asignados"

# 2. Ejecutar instalación
echo ""
echo -e "${BLUE}📦 Ejecutando instalación...${NC}"
./scripts/install.sh

# 3. Configurar .env
echo ""
echo -e "${YELLOW}⚙️  CONFIGURACIÓN REQUERIDA${NC}"
echo ""

if [ ! -f backend/.env ]; then
    cp backend/.env.example backend/.env
    echo -e "${YELLOW}Se creó backend/.env${NC}"
    echo ""
    echo "Edita estos valores:"
    echo "  nano backend/.env"
    echo ""
    echo "Configurar:"
    echo "  - CLAWDBOT_HOOK_TOKEN (generar un token secreto)"
    echo "  - OPENROUTER_API_KEY"
    echo "  - TELEGRAM_ADMIN_CHAT"
    echo "  - FDF_USER"
    echo "  - FDF_PASS"
    echo ""
    read -p "Presiona Enter cuando hayas editado .env..."
fi

# 4. Actualizar Clawdbot config
echo ""
echo -e "${BLUE}🦞 Configurando Clawdbot...${NC}"

HOOK_TOKEN=$(grep CLAWDBOT_HOOK_TOKEN backend/.env | cut -d '=' -f2)

if [ -z "$HOOK_TOKEN" ]; then
    echo -e "${RED}❌ Error: CLAWDBOT_HOOK_TOKEN no configurado en .env${NC}"
    exit 1
fi

echo "Hook token detectado: ${HOOK_TOKEN:0:10}..."

echo ""
echo -e "${YELLOW}Ahora edita ~/.clawdbot/clawdbot.json${NC}"
echo ""
echo "Agrega esta sección:"
echo ""
cat << EOF
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
    "token": "$HOOK_TOKEN"
  },
  "browser": {
    "enabled": true,
    "headless": true
  }
}
EOF

echo ""
read -p "¿Ya editaste clawdbot.json? (s/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}Edita ~/.clawdbot/clawdbot.json y vuelve a ejecutar este script${NC}"
    exit 1
fi

# 5. Reiniciar Clawdbot
echo ""
echo -e "${BLUE}🔄 Reiniciando Clawdbot...${NC}"

if systemctl is-active --quiet clawdbot; then
    sudo systemctl restart clawdbot
    echo -e "${GREEN}✓${NC} Clawdbot reiniciado"
else
    echo -e "${YELLOW}⚠${NC}  Clawdbot no corre como servicio"
    echo "   Reinícialo manualmente"
fi

# 6. Iniciar servicios
echo ""
echo -e "${BLUE}🚀 Iniciando servicios...${NC}"
./scripts/start.sh

# 7. Verificaciones
echo ""
echo "=========================================="
echo "  VERIFICANDO INSTALACIÓN"
echo "=========================================="
echo ""

# Health check
echo -n "Backend... "
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Redis
echo -n "Redis... "
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# PostgreSQL
echo -n "PostgreSQL... "
if sudo -u postgres psql -c "\l" | grep -q fotolibros; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Clawdbot
echo -n "Clawdbot... "
if netstat -tulpn 2>/dev/null | grep -q 18789; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "=========================================="
echo -e "  ${GREEN}✅ DEPLOYMENT COMPLETADO${NC}"
echo "=========================================="
echo ""
echo "Comandos útiles:"
echo ""
echo "  Ver logs backend:"
echo "    journalctl -u fotolibros-backend -f"
echo ""
echo "  Ver logs worker:"
echo "    journalctl -u fotolibros-worker -f"
echo ""
echo "  Ver cola:"
echo "    redis-cli LLEN fotolibros:cola"
echo ""
echo "  Health check:"
echo "    curl http://localhost:8000/health"
echo ""
