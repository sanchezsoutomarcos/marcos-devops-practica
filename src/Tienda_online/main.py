"""Punto de entrada de la aplicación y capa de exposición del servicio (API REST).

Arrancar:
    uvicorn main:app --host 0.0.0.0 --port 8000      (accesible desde otros equipos)
    uvicorn main:app --host 127.0.0.1 --port 8000    (solo accesible desde este equipo)
    python main.py                                    (equivale a la primera opción)

Documentación interactiva: http://localhost:8000/docs
"""
import os
from typing import List

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from schemas import (
    PedidoCreate,
    PedidoItemRead,
    PedidoRead,
    ProductoCreate,
    ProductoRead,
    UsuarioCreate,
    UsuarioRead,
)
from Services.excepciones import ConflictoError, NoEncontradoError, ValorInvalidoError
from Services.Tienda_service import TiendaService

app = FastAPI(
    title="Tienda online API",
    description="API REST de la tienda online (usuarios, productos y pedidos).",
    version="1.0.0",
)

# CORS: permite que el frontend (otra página/origen en el navegador) llame a la API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Única instancia del servicio: todos los clientes trabajan sobre los mismos datos.
servicio = TiendaService()


# ------------------------------------------------- errores de negocio -> HTTP
# Todos los errores se devuelven con el mismo formato: {"detail": "mensaje"}
@app.exception_handler(ValorInvalidoError)
async def valor_invalido_handler(request, exc: ValorInvalidoError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(exc)})


@app.exception_handler(NoEncontradoError)
async def no_encontrado_handler(request, exc: NoEncontradoError):
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(exc)})


@app.exception_handler(ConflictoError)
async def conflicto_handler(request, exc: ConflictoError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(exc)})


# --------------------------------------------- conversión dominio -> esquemas
def usuario_a_read(u) -> UsuarioRead:
    return UsuarioRead(id=u.id, nombre=u.nombre, email=u.email, es_admin=u.es_admin)


def producto_a_read(p) -> ProductoRead:
    return ProductoRead(
        id=p.id,
        tipo=p.tipo,
        nombre=p.nombre,
        precio=p.precio,
        stock=p.stock,
        **p.atributos_extra(),
    )


def pedido_a_read(p) -> PedidoRead:
    return PedidoRead(
        id=p.id,
        fecha=p.fecha,
        cliente=usuario_a_read(p.cliente),
        total=p.total,
        items=[
            PedidoItemRead(
                producto_id=i.producto_id,
                nombre_producto=i.nombre_producto,
                cantidad=i.cantidad,
                precio_unitario=i.precio_unitario,
                subtotal=i.subtotal,
            )
            for i in p.items
        ],
    )


# ------------------------------------------------------------------ USUARIOS
@app.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_usuario(datos: UsuarioCreate):
    """Crea un nuevo usuario (cliente o administrador). El email debe ser único."""
    usuario = servicio.crear_usuario(datos.nombre, datos.email, datos.tipo, datos.direccion)
    return usuario_a_read(usuario)


@app.get("/usuarios", response_model=List[UsuarioRead], tags=["Usuarios"])
def listar_usuarios():
    """Devuelve la lista de usuarios registrados."""
    return [usuario_a_read(u) for u in servicio.listar_usuarios()]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead, tags=["Usuarios"])
def obtener_usuario(usuario_id: int):
    """Devuelve un usuario concreto (404 si no existe)."""
    return usuario_a_read(servicio.obtener_usuario(usuario_id))


# ----------------------------------------------------------------- PRODUCTOS
@app.post("/productos", response_model=ProductoRead, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def crear_producto(datos: ProductoCreate):
    """Crea un producto genérico, electrónico (meses_garantia) o de ropa (talla y color)."""
    producto = servicio.crear_producto(
        datos.tipo,
        datos.nombre,
        datos.precio,
        datos.stock,
        meses_garantia=datos.meses_garantia,
        talla=datos.talla,
        color=datos.color,
    )
    return producto_a_read(producto)


@app.get("/productos", response_model=List[ProductoRead], tags=["Productos"])
def listar_productos():
    """Devuelve la lista de productos."""
    return [producto_a_read(p) for p in servicio.listar_productos()]


@app.get("/productos/{producto_id}", response_model=ProductoRead, tags=["Productos"])
def obtener_producto(producto_id: int):
    """Devuelve un producto concreto (404 si no existe)."""
    return producto_a_read(servicio.obtener_producto(producto_id))


@app.delete("/productos/{producto_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Productos"])
def eliminar_producto(producto_id: int):
    """Elimina un producto (404 si no existe)."""
    servicio.eliminar_producto(producto_id)


# ------------------------------------------------------------------- PEDIDOS
@app.post("/pedidos", response_model=PedidoRead, status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
def crear_pedido(datos: PedidoCreate):
    """Crea un pedido. Verifica que existan el cliente y los productos y que haya stock
    suficiente (404 si algo no existe, 409 si falta stock)."""
    pedido = servicio.crear_pedido(
        datos.cliente_id, [(i.producto_id, i.cantidad) for i in datos.items]
    )
    return pedido_a_read(pedido)


@app.get("/usuarios/{cliente_id}/pedidos", response_model=List[PedidoRead], tags=["Pedidos"])
def listar_pedidos_cliente(cliente_id: int):
    """Devuelve el historial de pedidos de un cliente (404 si el cliente no existe)."""
    return [pedido_a_read(p) for p in servicio.listar_pedidos_cliente(cliente_id)]


if __name__ == "__main__":
    # host 0.0.0.0 -> escucha en todas las interfaces (accesible desde otros equipos).
    # Con host 127.0.0.1 solo se podría acceder desde el propio equipo.
    uvicorn.run(
        app,
        host=os.environ.get("HOST", "0.0.0.0"),
        port=int(os.environ.get("PORT", "8000")),
    )
