"""Lógica de negocio de la tienda online.

La clase TiendaService guarda los datos en memoria y es la única que conoce
las reglas de negocio. main.py (la capa de exposición) solo traduce entre
HTTP y estos métodos.
"""
from typing import Dict, List, Optional, Tuple

from models import (
    Administrador,
    Cliente,
    LineaPedido,
    Pedido,
    Producto,
    ProductoElectronico,
    ProductoRopa,
    Usuario,
)
from Services.excepciones import ConflictoError, NoEncontradoError, ValorInvalidoError


class TiendaService:
    def __init__(self):
        self._usuarios: Dict[int, Usuario] = {}
        self._productos: Dict[int, Producto] = {}
        self._pedidos: List[Pedido] = []
        self._sig_usuario = 1
        self._sig_producto = 1
        self._sig_pedido = 1

    # ------------------------------------------------------------------ usuarios
    def crear_usuario(self, nombre: str, email: str, tipo: str, direccion: Optional[str] = None) -> Usuario:
        email_norm = (email or "").strip().lower()
        if any(u.email == email_norm for u in self._usuarios.values()):
            raise ConflictoError(f"Ya existe un usuario con el email '{email_norm}'")
        try:
            if tipo == "cliente":
                usuario = Cliente(self._sig_usuario, nombre, email, direccion)
            elif tipo == "administrador":
                usuario = Administrador(self._sig_usuario, nombre, email, direccion)
            else:
                raise ValueError("El tipo de usuario debe ser 'cliente' o 'administrador'")
        except ValueError as e:
            raise ValorInvalidoError(str(e))
        self._usuarios[usuario.id] = usuario
        self._sig_usuario += 1
        return usuario

    def obtener_usuario(self, usuario_id: int) -> Usuario:
        usuario = self._usuarios.get(usuario_id)
        if usuario is None:
            raise NoEncontradoError(f"No existe el usuario con id {usuario_id}")
        return usuario

    def listar_usuarios(self) -> List[Usuario]:
        return list(self._usuarios.values())

    # ----------------------------------------------------------------- productos
    def crear_producto(
        self,
        tipo: str,
        nombre: str,
        precio: float,
        stock: int,
        meses_garantia: Optional[int] = None,
        talla: Optional[str] = None,
        color: Optional[str] = None,
    ) -> Producto:
        pid = self._sig_producto
        try:
            if tipo == "generico":
                producto = Producto(pid, nombre, precio, stock)
            elif tipo == "electronico":
                if meses_garantia is None:
                    raise ValueError("Un producto electrónico necesita 'meses_garantia'")
                producto = ProductoElectronico(pid, nombre, precio, stock, meses_garantia)
            elif tipo == "ropa":
                if talla is None or color is None:
                    raise ValueError("Un producto de ropa necesita 'talla' y 'color'")
                producto = ProductoRopa(pid, nombre, precio, stock, talla, color)
            else:
                raise ValueError("El tipo de producto debe ser 'generico', 'electronico' o 'ropa'")
        except ValueError as e:
            raise ValorInvalidoError(str(e))
        self._productos[pid] = producto
        self._sig_producto += 1
        return producto

    def obtener_producto(self, producto_id: int) -> Producto:
        producto = self._productos.get(producto_id)
        if producto is None:
            raise NoEncontradoError(f"No existe el producto con id {producto_id}")
        return producto

    def listar_productos(self) -> List[Producto]:
        return list(self._productos.values())

    def eliminar_producto(self, producto_id: int) -> None:
        self.obtener_producto(producto_id)  # lanza NoEncontradoError si no existe
        del self._productos[producto_id]

    # ------------------------------------------------------------------- pedidos
    def crear_pedido(self, cliente_id: int, items: List[Tuple[int, int]]) -> Pedido:
        """Crea un pedido. `items` es una lista de (producto_id, cantidad).

        Se valida TODO antes de tocar el stock: si cualquier línea falla,
        no se descuenta nada.
        """
        cliente = self.obtener_usuario(cliente_id)
        if not items:
            raise ValorInvalidoError("El pedido necesita al menos un producto")

        # Si el mismo producto aparece en varias líneas, se suman las cantidades.
        cantidades: Dict[int, int] = {}
        for producto_id, cantidad in items:
            if cantidad <= 0:
                raise ValorInvalidoError("Las cantidades deben ser mayores que 0")
            cantidades[producto_id] = cantidades.get(producto_id, 0) + cantidad

        # 1) Validar existencia y stock
        for producto_id, cantidad in cantidades.items():
            producto = self.obtener_producto(producto_id)
            if not producto.hay_stock(cantidad):
                raise ConflictoError(
                    f"Stock insuficiente de '{producto.nombre}': "
                    f"disponible {producto.stock}, solicitado {cantidad}"
                )

        # 2) Todo correcto: descontar stock y crear las líneas
        lineas: List[LineaPedido] = []
        for producto_id, cantidad in cantidades.items():
            producto = self._productos[producto_id]
            producto.reducir_stock(cantidad)
            lineas.append(LineaPedido(producto.id, producto.nombre, cantidad, producto.precio))

        pedido = Pedido(self._sig_pedido, cliente, lineas)
        self._pedidos.append(pedido)
        self._sig_pedido += 1
        return pedido

    def listar_pedidos_cliente(self, cliente_id: int) -> List[Pedido]:
        self.obtener_usuario(cliente_id)  # 404 si el cliente no existe
        return [p for p in self._pedidos if p.cliente.id == cliente_id]
