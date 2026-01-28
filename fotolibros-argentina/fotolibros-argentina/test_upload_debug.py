import httpx
import asyncio

async def test():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Crear pedido dummy
        print("1. Creando pedido...")
        try:
            r = await client.post("http://localhost:8000/pedidos", json={
                "producto_codigo": "test-debug",
                "cliente": {
                    "nombre": "Debug User",
                    "email": "debug@test.com",
                    "direccion": {
                        "calle": "Test 123",
                        "ciudad": "CABA",
                        "provincia": "BA",
                        "cp": "1000"
                    }
                }
            })
            if r.status_code != 200:
                print(f"❌ Error creando pedido: {r.status_code} {r.text}")
                return
            
            pedido_id = r.json()["id"]
            print(f"✅ Pedido creado: {pedido_id}")
        except Exception as e:
            print(f"❌ Excepción conectando al backend: {e}")
            return

        # 2. Subir comprobante dummy
        print("2. Subiendo comprobante...")
        files = {'comprobante': ('test.txt', b'pixel negro dummy', 'text/plain')}
        data = {'monto_esperado': '10500.50'}
        
        try:
            r = await client.post(
                f"http://localhost:8000/pedidos/{pedido_id}/comprobante",
                files=files,
                data=data
            )
            print(f"Retorno: {r.status_code}")
            print("Cuerpo respuesta:")
            print(r.text)
        except Exception as e:
            print(f"❌ Excepción subiendo archivo: {e}")

if __name__ == "__main__":
    asyncio.run(test())
