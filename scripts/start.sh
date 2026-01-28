#!/bin/bash
# Script para iniciar servicios

set -e

echo "=================================="
echo "  INICIANDO SERVICIOS"
echo "=================================="
echo ""

# Iniciar backend
echo "🚀 Iniciando backend..."
sudo systemctl start fotolibros-backend
sudo systemctl enable fotolibros-backend

# Iniciar worker
echo "🔄 Iniciando worker..."
sudo systemctl start fotolibros-worker
sudo systemctl enable fotolibros-worker

# Mostrar estado
echo ""
echo "📊 Estado de servicios:"
sudo systemctl status fotolibros-backend --no-pager
sudo systemctl status fotolibros-worker --no-pager

echo ""
echo "✅ Servicios iniciados"
echo ""
echo "Ver logs:"
echo "  journalctl -u fotolibros-backend -f"
echo "  journalctl -u fotolibros-worker -f"
echo ""
