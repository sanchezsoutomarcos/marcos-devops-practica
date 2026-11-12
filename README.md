# marcos-devops-practica — Tienda online

**Autor:** Marcos Sánchez

**Asignatura:** Arquitectura del Software — Práctica 3 (control de versiones y Docker)

## Descripción

Aplicación Python de una **tienda online**. Es una API REST hecha con FastAPI que
permite gestionar usuarios, productos y pedidos, y que comprueba las reglas de
negocio (emails únicos, stock suficiente, etc.). Los datos se guardan en memoria.

El proyecto tiene tres partes separadas que trabajan sobre los mismos datos:

- **API REST** (`src/Tienda_online`): servidor FastAPI con la lógica de la tienda.
- **Cliente Python** (`src/cliente_python`): script que usa la API con la librería `requests`.
- **Frontend web** (`src/frontend`): página HTML que usa la API desde el navegador.

Este repositorio parte del código de la Práctica 2 y se usa para practicar el
trabajo con Git y GitHub (ramas, commits y Pull Requests) y con Docker
(imagen, contenedor y publicación en un registry).

## Estructura

```
marcos-devops-practica/
├── Dockerfile                ← imagen Docker de la API
├── .dockerignore             ← ficheros que no entran en la imagen
├── requirements.txt          ← dependencias con versiones fijadas
├── README.md
└── src/
    ├── Tienda_online/        ← API REST (FastAPI)
    │   ├── main.py           ← endpoints
    │   ├── schemas.py        ← esquemas Pydantic
    │   ├── models/           ← Producto, Usuario, Pedido
    │   └── Services/         ← lógica de negocio y excepciones
    ├── cliente_python/
    │   └── cliente.py        ← cliente con requests
    └── frontend/
        └── index.html        ← frontend web
```

## Docker

La imagen está publicada en Docker Hub:
[`sanchezsoutomarcos/tienda-online-api`](https://hub.docker.com/r/sanchezsoutomarcos/tienda-online-api)

### 1. Construir la imagen

Desde la raíz del repositorio:

```bash
docker build -t sanchezsoutomarcos/tienda-online-api:1.0.0 .
```

El `Dockerfile` parte de `python:3.12-slim`, instala las dependencias de
`requirements.txt`, copia el código de `src/` y arranca la API con un usuario
sin privilegios.

### 2. Ejecutar el contenedor

```bash
docker run -d --name tienda-api -p 8000:8000 sanchezsoutomarcos/tienda-online-api:1.0.0
```

- `-d`: el contenedor se queda funcionando en segundo plano.
- `--name tienda-api`: nombre del contenedor.
- `-p 8000:8000`: el puerto 8000 del equipo se conecta con el 8000 del contenedor.

Otro ejemplo, usando el puerto 9000:

```bash
docker run -d --name tienda-api -p 9000:9000 -e PORT=9000 sanchezsoutomarcos/tienda-online-api:1.0.0
```

Para ver los logs, parar y borrar el contenedor:

```bash
docker logs tienda-api
docker stop tienda-api
docker rm tienda-api
```

### 3. Variables de entorno

| Variable | Valor por defecto | Descripción |
|---|---|---|
| `HOST` | `0.0.0.0` | Dirección en la que escucha la API dentro del contenedor |
| `PORT` | `8000` | Puerto en el que escucha la API dentro del contenedor |

Se cambian con `-e`, por ejemplo `-e PORT=9000`. La aplicación no usa claves ni secretos.

### 4. Probar que funciona

Con el contenedor arrancado:

1. Abre <http://localhost:8000/docs>: debe aparecer la documentación interactiva de la API.
2. Lista los productos (al principio no hay ninguno):

   ```bash
   curl http://localhost:8000/productos
   ```

   Salida esperada: `[]`

3. Ejecuta el cliente Python dentro del contenedor. Crea un usuario y tres productos,
   hace un pedido y comprueba que un pedido sin stock devuelve un 409:

   ```bash
   docker exec tienda-api python /app/src/cliente_python/cliente.py
   ```

   La última línea debe ser: `Flujo completado correctamente.`

4. Vuelve a listar los productos: ahora aparecen los tres que ha creado el cliente.

   ```bash
   curl http://localhost:8000/productos
   ```

### 5. Publicar y descargar la imagen

Publicar en Docker Hub (hay que haber iniciado sesión con `docker login`):

```bash
docker push sanchezsoutomarcos/tienda-online-api:1.0.0
```

Descargar y ejecutar la imagen publicada en cualquier equipo con Docker:

```bash
docker pull sanchezsoutomarcos/tienda-online-api:1.0.0
docker run -d --name tienda-api -p 8000:8000 sanchezsoutomarcos/tienda-online-api:1.0.0
```

## Ejecutar sin Docker

```bash
pip install -r requirements.txt
cd src/Tienda_online
uvicorn main:app --host 0.0.0.0 --port 8000     # o: python main.py
```

Documentación interactiva: <http://localhost:8000/docs>

### Cliente Python

Con la API arrancada:

```bash
python src/cliente_python/cliente.py                           # contra localhost
python src/cliente_python/cliente.py http://192.168.1.34:8000  # contra otro equipo
```

### Frontend

Con la API arrancada, abre `src/frontend/index.html` en el navegador, o sírvelo con:

```bash
cd src/frontend
python -m http.server 5500
```

y entra en <http://localhost:5500>. En el campo **Servidor API** escribe
`http://localhost:8000` y pulsa *Conectar*.

## Endpoints

| Método | Ruta | Descripción | Códigos |
|---|---|---|---|
| POST | `/usuarios` | Crear usuario | 201, 409 (email repetido), 422 |
| GET | `/usuarios` | Listar usuarios | 200 |
| GET | `/usuarios/{usuario_id}` | Un usuario | 200, 404 |
| POST | `/productos` | Crear producto (genérico / electrónico / ropa) | 201, 422 |
| GET | `/productos` | Listar productos | 200 |
| GET | `/productos/{producto_id}` | Un producto | 200, 404 |
| DELETE | `/productos/{producto_id}` | Eliminar producto | 204, 404 |
| POST | `/pedidos` | Crear pedido (verifica cliente, producto y stock) | 201, 404, 409 (sin stock), 422 |
| GET | `/usuarios/{cliente_id}/pedidos` | Pedidos de un cliente | 200, 404 |

Los errores siempre tienen el mismo formato: `{"detail": "mensaje"}`.

## Flujo de trabajo con Git

- `main`: rama principal, con el código estable.
- `feature/<nombre>`: una rama por cada funcionalidad (por ejemplo `feature/docker`).
- Cada rama se integra en `main` mediante un Pull Request.
