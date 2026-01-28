# 📸 Fotolibros Argentina

Sistema completo para venta y gestión de fotolibros personalizados con verificación automática de pagos.

## 🎯 Características

- ✅ **Catálogo dinámico** con 12 productos y 3 paquetes predefinidos
- ✅ **Márgenes de ganancia configurables** (50%, 70%, 100%)
- ✅ **Verificación de pagos con IA** (NVIDIA Nemotron VL - GRATIS)
- ✅ **Gestión de pedidos** con estados y historial
- ✅ **Cálculo automático de envíos** por zona
- ✅ **Notificaciones** por Discord y Email
- ✅ **API REST** con FastAPI
- ✅ **Agente AGNO** orquestador

## 📦 Modelo de Negocio

```
┌─────────────────────────────────────────────────────────────────┐
│                     FLUJO DE PEDIDO                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Cliente paga → Verificación con IA (Nemotron VL)            │
│  2. Pago OK → Pedido a Fábrica de Fotolibros                    │
│  3. Gráfica produce (4-5 días) → Envío a tu domicilio           │
│  4. Recibís el producto → Enviás al cliente final               │
│                                                                 │
│  ⏱️ TIEMPO TOTAL AL CLIENTE: 12-18 días hábiles                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 💰 Márgenes de Ganancia

| Tipo | Margen | Uso |
|------|--------|-----|
| **Penetración** | 50% | Cliente trae diseño listo |
| **Estándar** | 70% | Clientes particulares |
| **Premium** | 100% | Incluye diseño y armado |

## 🚀 Instalación

### 1. Clonar/Descomprimir

```bash
cd /opt
unzip fotolibros-argentina.zip
cd fotolibros-argentina
```

### 2. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configurar variables de entorno

```bash
cp .env.example .env
nano .env  # Editar con tus valores
```

**Variables obligatorias:**
- `OPENROUTER_API_KEY` - Tu API key de OpenRouter
- `CUENTA_ALIAS` - Tu alias de MercadoPago/banco
- `DISCORD_WEBHOOK_URL` - Webhook para notificaciones

### 4. Ejecutar

```bash
# Desarrollo
python main.py

# Producción con Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:7777
```

## 📚 API Endpoints

### Catálogo

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/productos` | Lista todos los productos |
| GET | `/api/productos/{id}` | Detalle de un producto |
| GET | `/api/paquetes` | Lista paquetes predefinidos |
| GET | `/api/zonas-envio` | Zonas de envío y costos |
| GET | `/api/tiempos-entrega` | Tiempos estimados |

### Pedidos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/pedidos` | Crear nuevo pedido |
| GET | `/api/pedidos` | Listar pedidos |
| GET | `/api/pedidos/{id}` | Detalle de pedido |
| POST | `/api/pedidos/{id}/cliente` | Guardar datos cliente |
| POST | `/api/pedidos/{id}/estado` | Actualizar estado |

### Pagos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/pedidos/{id}/comprobante` | Subir comprobante |
| POST | `/api/pedidos/{id}/verificar-pago` | Verificar pago |

### Otros

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/calcular-precio` | Calculadora de precios |
| GET | `/api/estadisticas` | Estadísticas del sistema |
| POST | `/api/agent` | Interactuar con agente |

## 🔧 Estructura del Proyecto

```
fotolibros-argentina/
├── main.py                    # API FastAPI
├── requirements.txt           # Dependencias
├── .env.example              # Template de variables
├── agents/
│   └── orquestador.py        # Agente AGNO principal
├── models/
│   ├── __init__.py
│   ├── catalogo.py           # Productos, precios, zonas
│   └── pedido.py             # Estados, flujos
├── toolkits/
│   ├── __init__.py
│   ├── sqlite_toolkit.py     # Base de datos
│   ├── payment_toolkit.py    # Verificación de pagos
│   └── notification_toolkit.py # Discord + Email
├── static/                   # Archivos estáticos
├── uploads/                  # Comprobantes y fotos
│   ├── comprobantes/
│   └── fotos/
└── data/                     # Base de datos SQLite
    └── fotolibros.db
```

## 🛠️ Systemd Service (Producción)

```bash
# Crear archivo de servicio
sudo nano /etc/systemd/system/fotolibros.service
```

```ini
[Unit]
Description=Fotolibros Argentina API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/fotolibros-argentina
Environment=PATH=/opt/fotolibros-argentina/.venv/bin
ExecStart=/opt/fotolibros-argentina/.venv/bin/gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:7777
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable fotolibros
sudo systemctl start fotolibros

# Ver logs
sudo journalctl -u fotolibros -f
```

## 📊 Estados de Pedido

| Estado | Descripción | Acción |
|--------|-------------|--------|
| `pendiente_pago` | Pedido creado | Esperar comprobante |
| `verificando_pago` | Comprobante subido | IA verificando |
| `pago_aprobado` | Pago OK | Enviar a gráfica |
| `en_produccion` | En la gráfica | Esperar 4-5 días |
| `producido` | Gráfica terminó | Recibir en domicilio |
| `en_mi_domicilio` | Lo recibiste | Preparar envío |
| `enviado_cliente` | Despachado | Seguimiento |
| `entregado` | ✅ Finalizado | - |
| `cancelado` | ❌ Cancelado | - |
| `rechazado` | ❌ Pago inválido | - |

## 💳 Verificación de Pagos

El sistema usa **NVIDIA Nemotron Nano 12B VL** (GRATIS via OpenRouter) para:

1. Detectar el banco/app del comprobante
2. Extraer monto, fecha y datos de la transferencia
3. Verificar que el destino coincide con tu cuenta
4. Validar que el monto es correcto (±5% tolerancia)
5. Verificar que el comprobante no es muy antiguo

**Bancos soportados:** BBVA, Santander, Galicia, Brubank, Ualá, Prex, MercadoPago, Naranja X, y más.

## 🔔 Notificaciones

**Discord:** Todos los cambios de estado, nuevos pedidos, errores.

**Email:** Confirmación de pedido, pago verificado, envío despachado.

## 📈 Próximas Mejoras

- [ ] Frontend React para clientes
- [ ] Integración con Browserbase para automatizar pedidos a la gráfica
- [ ] Dashboard admin completo
- [ ] Webhooks para n8n
- [ ] Integración con MercadoPago checkout

## 📞 Proveedor

**Fábrica de Fotolibros**
- 📍 Concepción Arenal 4501, Chacarita, CABA
- 📞 011.5217.8188
- 📧 info@fabricadefotolibros.com
- 🌐 www.fabricadefotolibros.com

---

*Desarrollado para NEXUM Labs - Enero 2026*
