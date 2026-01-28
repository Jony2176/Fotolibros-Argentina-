# Configuración de n8n para PIKSY

## Importar el Workflow

1. Abrir n8n (http://localhost:5678)
2. Ir a **Workflows** → **Import from File**
3. Seleccionar el archivo `piksy_workflow.json`
4. Click en **Import**

## Configurar Credenciales

### Email (para notificaciones)

1. Ir a **Settings** → **Credentials**
2. Click en **Add Credential** → **SMTP**
3. Configurar:
   - **Host**: smtp.gmail.com (o tu proveedor)
   - **Port**: 587
   - **User**: tu-email@gmail.com
   - **Password**: tu-app-password
   - **SSL/TLS**: STARTTLS
4. Guardar y conectar al nodo "Email Pedido Completado"

## URLs del Workflow

Una vez importado, el webhook estará disponible en:

```
POST http://localhost:5678/webhook/nuevo-pedido
```

### Payload esperado:

```json
{
  "producto_codigo": "CU-21x21-DURA",
  "estilo_diseno": "clasico",
  "paginas_total": 22,
  "cliente": {
    "nombre": "Juan Pérez",
    "email": "juan@email.com",
    "telefono": "1155667788",
    "direccion": {
      "calle": "Av. Corrientes 1234",
      "ciudad": "Buenos Aires",
      "provincia": "CABA",
      "cp": "1043"
    }
  },
  "metodo_pago": "mercadopago",
  "titulo_tapa": "Nuestros Recuerdos",
  "texto_lomo": "2025"
}
```

## Flujo del Workflow

```
[Webhook] → [Crear Pedido en Backend] → [¿Éxito?]
                                             ↓
                              [Guardar ID] → [Esperar 5s] → [Consultar Estado]
                                                                    ↓
                                                            [¿Completado?]
                                                                    ↓
                                                        [Email Confirmación]
```

## Activar el Workflow

1. Abrir el workflow importado
2. Click en el toggle **Active** (arriba a la derecha)
3. El webhook estará listo para recibir pedidos

## Probar el Workflow

```bash
curl -X POST http://localhost:5678/webhook/nuevo-pedido \
  -H "Content-Type: application/json" \
  -d '{
    "producto_codigo": "CU-21x21-DURA",
    "estilo_diseno": "clasico",
    "paginas_total": 22,
    "cliente": {
      "nombre": "Test",
      "email": "test@test.com",
      "direccion": {
        "calle": "Test 123",
        "ciudad": "CABA",
        "provincia": "Buenos Aires",
        "cp": "1000"
      }
    },
    "metodo_pago": "transferencia"
  }'
```

## Notas

- El backend debe estar corriendo en `http://localhost:8000`
- El workflow hace polling cada 2 segundos hasta que el pedido esté completado
- El email se envía automáticamente cuando el pedido termina
