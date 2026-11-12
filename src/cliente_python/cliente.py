"""Cliente Python de la API REST de la tienda online (usa la librería requests).

Es independiente de la aplicación FastAPI: NO importa TiendaService, ni los
modelos, ni nada del servidor. Toda la comunicación es por HTTP.

Uso:
    python cliente.py                              -> usa BASE_URL (localhost)
    python cliente.py http://192.168.1.34:8000     -> usa la IP de otro equipo
"""
import json
import sys
import time

import requests

# Dirección base de la API. Cámbiala aquí (o pásala como argumento) para probar
# contra otro equipo de la red, p. ej. "http://192.168.1.34:8000".
BASE_URL = "http://localhost:8000"
TIMEOUT = 10  # segundos


def peticion(metodo: str, ruta: str, esperado: int, **kwargs):
    """Hace una petición HTTP, comprueba el código de estado y devuelve el JSON.

    - metodo:   "GET", "POST", ...
    - ruta:     ruta del endpoint, p. ej. "/usuarios"
    - esperado: código de estado HTTP que se espera (200, 201, ...)
    - kwargs:   se pasan a requests (json=... para el cuerpo)
    """
    url = f"{BASE_URL}{ruta}"
    print(f"\n>>> {metodo} {url}")
    if "json" in kwargs:
        print(f"    cuerpo: {json.dumps(kwargs['json'], ensure_ascii=False)}")

    try:
        respuesta = requests.request(metodo, url, timeout=TIMEOUT, **kwargs)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: no se pudo conectar con la API en {BASE_URL}\n       ({e.__class__.__name__})")
        print("       ¿Está arrancado el servidor? ¿Es correcta la IP/puerto? ¿El firewall permite el puerto?")
        sys.exit(1)

    print(f"<<< código HTTP: {respuesta.status_code}")

    if respuesta.status_code != esperado:
        print(f"ERROR: se esperaba el código {esperado}.")
        try:
            print(f"       respuesta: {json.dumps(respuesta.json(), ensure_ascii=False)}")
        except ValueError:
            print(f"       respuesta: {respuesta.text[:200]}")
        sys.exit(1)

    # Procesar la respuesta JSON (las respuestas 204 no tienen cuerpo)
    if not respuesta.content:
        return None
    datos = respuesta.json()
    print(json.dumps(datos, indent=2, ensure_ascii=False))
    return datos


def comprobar_docs():
    """Comprueba que la documentación interactiva /docs es accesible."""
    url = f"{BASE_URL}/docs"
    print(f"\n>>> GET {url}")
    try:
        respuesta = requests.get(url, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        print(f"ERROR: no se pudo conectar con la API en {BASE_URL} ({e.__class__.__name__})")
        sys.exit(1)
    print(f"<<< código HTTP: {respuesta.status_code}")
    if respuesta.status_code != 200:
        print("ERROR: /docs no está accesible")
        sys.exit(1)


def main():
    global BASE_URL
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip("/")

    print(f"Usando la API en: {BASE_URL}")
    comprobar_docs()

    # El email debe ser único, así que se añade una marca de tiempo para poder
    # ejecutar el script varias veces sin que falle por email repetido.
    marca = int(time.time())

    print("\n=== 1. Crear un usuario ===")
    usuario = peticion(
        "POST",
        "/usuarios",
        201,
        json={
            "nombre": "Ana García",
            "email": f"ana{marca}@example.com",
            "tipo": "cliente",
            "direccion": "C/ Mayor 1, Madrid",
        },
    )
    usuario_id = usuario["id"]

    print("\n=== 2. Consultar la lista de usuarios ===")
    usuarios = peticion("GET", "/usuarios", 200)
    print(f"\nHay {len(usuarios)} usuario(s) registrado(s).")

    print("\n=== 3. Crear productos (genérico, electrónico y ropa) ===")
    libreta = peticion(
        "POST", "/productos", 201,
        json={"tipo": "generico", "nombre": "Libreta", "precio": 3.5, "stock": 20},
    )
    auriculares = peticion(
        "POST", "/productos", 201,
        json={"tipo": "electronico", "nombre": "Auriculares", "precio": 29.99,
              "stock": 10, "meses_garantia": 24},
    )
    camiseta = peticion(
        "POST", "/productos", 201,
        json={"tipo": "ropa", "nombre": "Camiseta", "precio": 15.0,
              "stock": 5, "talla": "M", "color": "Azul"},
    )

    print("\n=== 4. Consultar la lista de productos ===")
    productos = peticion("GET", "/productos", 200)
    print(f"\nHay {len(productos)} producto(s) en la tienda.")

    print("\n=== 5. Crear un pedido para el usuario ===")
    pedido = peticion(
        "POST", "/pedidos", 201,
        json={
            "cliente_id": usuario_id,
            "items": [
                {"producto_id": libreta["id"], "cantidad": 2},
                {"producto_id": auriculares["id"], "cantidad": 1},
            ],
        },
    )
    print(f"\nPedido #{pedido['id']} creado. Total: {pedido['total']:.2f} EUR")

    print("\n=== 6. Consultar los pedidos del usuario ===")
    pedidos = peticion("GET", f"/usuarios/{usuario_id}/pedidos", 200)
    print(f"\nEl usuario {usuario_id} tiene {len(pedidos)} pedido(s).")

    print("\n=== 7. (Extra) Comprobar que la API rechaza un pedido sin stock ===")
    # Aquí se espera un 409: es un error esperado, no un fallo del cliente.
    peticion(
        "POST", "/pedidos", 409,
        json={"cliente_id": usuario_id,
              "items": [{"producto_id": camiseta["id"], "cantidad": 999}]},
    )

    print("\nFlujo completado correctamente.")


if __name__ == "__main__":
    main()
