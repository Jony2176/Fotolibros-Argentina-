#!/bin/bash
# Script de verificación pre-deployment
# Ejecutar PRIMERO en el VPS para ver qué hay

echo "=========================================="
echo "  VERIFICACIÓN PRE-DEPLOYMENT"
echo "=========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Puertos en uso
echo -e "${YELLOW}1. PUERTOS EN USO${NC}"
echo ""
echo "Servicios escuchando en puertos:"
sudo netstat -tulpn | grep LISTEN | awk '{print $4, $7}' | column -t
echo ""

# 2. Servicios systemd
echo -e "${YELLOW}2. SERVICIOS SYSTEMD${NC}"
echo ""
systemctl list-units --type=service --state=running | grep -E 'nginx|clawdbot|postgres|redis|node|python'
echo ""

# 3. Nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓${NC} Nginx está corriendo"
    echo "Sitios habilitados:"
    ls -la /etc/nginx/sites-enabled/
    echo ""
else
    echo -e "${YELLOW}⚠${NC}  Nginx no está corriendo"
fi

# 4. Bases de datos
echo -e "${YELLOW}3. BASES DE DATOS${NC}"
echo ""

if systemctl is-active --quiet postgresql; then
    echo -e "${GREEN}✓${NC} PostgreSQL está corriendo"
else
    echo "PostgreSQL: No"
fi

if systemctl is-active --quiet redis; then
    echo -e "${GREEN}✓${NC} Redis está corriendo"
else
    echo "Redis: No"
fi
echo ""

# 5. Clawdbot
echo -e "${YELLOW}4. CLAWDBOT${NC}"
echo ""
if pgrep -f clawdbot > /dev/null; then
    echo -e "${GREEN}✓${NC} Clawdbot está corriendo"
    ps aux | grep clawdbot | grep -v grep
    echo ""
    
    # Ver config
    if [ -f ~/.clawdbot/clawdbot.json ]; then
        echo "Config encontrada: ~/.clawdbot/clawdbot.json"
        echo "Puerto gateway:"
        cat ~/.clawdbot/clawdbot.json | grep -A2 "gateway" | grep port || echo "  (default: 18789)"
    fi
else
    echo -e "${YELLOW}⚠${NC}  Clawdbot no está corriendo"
fi
echo ""

# 6. Python/Node
echo -e "${YELLOW}5. PYTHON/NODE${NC}"
echo ""
python3 --version 2>/dev/null && echo -e "${GREEN}✓${NC} Python instalado" || echo "Python: No"
node --version 2>/dev/null && echo -e "${GREEN}✓${NC} Node instalado" || echo "Node: No"
npm --version 2>/dev/null && echo -e "${GREEN}✓${NC} npm instalado" || echo "npm: No"
echo ""

# 7. Espacio en disco
echo -e "${YELLOW}6. ESPACIO EN DISCO${NC}"
echo ""
df -h /
echo ""

# 8. Memoria
echo -e "${YELLOW}7. MEMORIA${NC}"
echo ""
free -h
echo ""

# Resumen
echo "=========================================="
echo "  RESUMEN"
echo "=========================================="
echo ""
echo "Puertos críticos a verificar:"
echo "  • 80  (HTTP)  → $(sudo netstat -tulpn | grep ':80 ' && echo 'EN USO' || echo 'LIBRE')"
echo "  • 443 (HTTPS) → $(sudo netstat -tulpn | grep ':443 ' && echo 'EN USO' || echo 'LIBRE')"
echo "  • 8000 (Backend) → $(sudo netstat -tulpn | grep ':8000 ' && echo 'EN USO' || echo 'LIBRE')"
echo "  • 3000 (Frontend dev) → $(sudo netstat -tulpn | grep ':3000 ' && echo 'EN USO' || echo 'LIBRE')"
echo "  • 18789 (Clawdbot) → $(sudo netstat -tulpn | grep ':18789 ' && echo 'EN USO' || echo 'LIBRE')"
echo ""
echo "Guarda este output y compartilo para ajustar la instalación."
echo ""
