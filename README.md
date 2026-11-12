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
trabajo con Git y GitHub (ramas, commits y Pull Requests) y, después, Docker.

## Estructura

```
marcos-devops-practica/
├── README.md
└── src/
    ├── Tienda_online/        ← API REST (FastAPI)
    │   ├── main.py           ← endpoints
    │   ├── schemas.py        ← esquemas Pydantic
    │   ├── models/           ← Producto, Usuario, Pedido
    │   ├── Services/         ← lógica de negocio y excepciones
    │   └── requirements.txt
    ├── cliente_python/
    │   ├── cliente.py        ← cliente con requests
    │   └── requirements.txt
    └── frontend/
        └── index.html        ← frontend web
```

## Cómo ejecutar la API

```bash
cd src/Tienda_online
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000     # o: python main.py
```

Documentación interactiva: <http://localhost:8000/docs>

### Endpoints

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

## Cliente Python

Con la API arrancada:

```bash
cd src/cliente_python
pip install -r requirements.txt
python cliente.py                           # contra localhost
python cliente.py http://192.168.1.34:8000  # contra otro equipo
```

Crea un usuario y varios productos, hace un pedido, consulta los pedidos del
usuario y comprueba que un pedido sin stock devuelve un 409.

## Frontend

Con la API arrancada, abre `src/frontend/index.html` en el navegador, o sírvelo con:

```bash
cd src/frontend
python -m http.server 5500
```

y entra en <http://localhost:5500>. En el campo **Servidor API** escribe
`http://localhost:8000` y pulsa *Conectar*.

## Flujo de trabajo con Git

- `main`: rama principal, con el código estable.
- `feature/<nombre>`: una rama por cada funcionalidad (por ejemplo `feature/docker`).
- Cada rama se integra en `main` mediante un Pull Request.
