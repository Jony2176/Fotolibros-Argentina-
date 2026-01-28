#!/bin/bash

# Test Rápido del Backend con AGNO Team
# ======================================
# Script para probar todo el flujo en un solo comando

echo "======================================================================"
echo "  TEST RAPIDO - Backend con AGNO Team"
echo "======================================================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar que el backend está corriendo
echo -e "${YELLOW}[1/5] Verificando backend...${NC}"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health 2>/dev/null)

if [ "$response" = "200" ]; then
    echo -e "${GREEN}✓ Backend corriendo en http://localhost:8000${NC}"
else
    echo -e "${RED}✗ Backend NO está corriendo${NC}"
    echo ""
    echo "Inicia el backend primero:"
    echo "  cd fotolibros-argentina && python main.py"
    exit 1
fi

# 2. Listar pedidos existentes
echo ""
echo -e "${YELLOW}[2/5] Listando pedidos en la base de datos...${NC}"
cd fotolibros-argentina
pedidos=$(sqlite3 data/fotolibros.db "SELECT id, cliente_nombre, estado, created_at FROM pedidos ORDER BY created_at DESC LIMIT 5;" 2>/dev/null)

if [ -z "$pedidos" ]; then
    echo -e "${RED}✗ No hay pedidos en la base de datos${NC}"
    echo ""
    echo "Opciones:"
    echo "  1. Crear pedido desde el frontend (http://localhost:3000)"
    echo "  2. Crear pedido con cURL (ver GUIA_PRUEBA_COMPLETA.md)"
    exit 1
else
    echo -e "${GREEN}✓ Pedidos encontrados:${NC}"
    echo "$pedidos" | while IFS='|' read -r id nombre estado fecha; do
        echo "  - ID: ${id:0:8}... | Cliente: $nombre | Estado: $estado | Fecha: $fecha"
    done
fi

# 3. Obtener el último pedido
echo ""
echo -e "${YELLOW}[3/5] Obteniendo último pedido...${NC}"
ultimo_pedido=$(sqlite3 data/fotolibros.db "SELECT id FROM pedidos ORDER BY created_at DESC LIMIT 1;" 2>/dev/null)

if [ -z "$ultimo_pedido" ]; then
    echo -e "${RED}✗ No se pudo obtener el pedido${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Pedido seleccionado: ${ultimo_pedido:0:8}...${NC}"

# Verificar si tiene fotos
num_fotos=$(sqlite3 data/fotolibros.db "SELECT COUNT(*) FROM fotos WHERE pedido_id='$ultimo_pedido';" 2>/dev/null)
echo "  Fotos: $num_fotos"

if [ "$num_fotos" -eq "0" ]; then
    echo -e "${YELLOW}⚠ Este pedido no tiene fotos. Necesitas subir fotos primero.${NC}"
    exit 1
fi

cd ..

# 4. Procesar con AGNO Team
echo ""
echo -e "${YELLOW}[4/5] Procesando con AGNO Team...${NC}"
echo ""

# Verificar si ya existe la configuración
config_file="fotolibros-argentina/data/agno_config_${ultimo_pedido:0:8}.json"
if [ -f "$config_file" ]; then
    echo -e "${YELLOW}⚠ Ya existe una configuración AGNO para este pedido${NC}"
    echo "  Archivo: $config_file"
    echo ""
    read -p "¿Quieres volver a procesarlo? (s/n): " respuesta
    if [ "$respuesta" != "s" ]; then
        echo "Saltando procesamiento..."
    else
        echo "Procesando..."
        python procesar_pedido_agno.py
    fi
else
    python procesar_pedido_agno.py
fi

# 5. Visualizar resultado
echo ""
echo -e "${YELLOW}[5/5] Visualizando resultado...${NC}"
echo ""

if [ -f "$config_file" ]; then
    python visualizar_agno_config.py "$ultimo_pedido"
    
    echo ""
    echo -e "${GREEN}======================================================================"
    echo -e "  ✓ TEST COMPLETADO EXITOSAMENTE"
    echo -e "======================================================================${NC}"
    echo ""
    echo "Archivo generado: $config_file"
    echo ""
    echo "Próximos pasos:"
    echo "  1. Revisar el diseño generado (arriba)"
    echo "  2. Ejecutar en FDF: python ejecutar_fdf_con_agno.py $ultimo_pedido"
    echo ""
else
    echo -e "${RED}✗ No se generó la configuración AGNO${NC}"
    echo "Revisa los errores arriba"
    exit 1
fi
