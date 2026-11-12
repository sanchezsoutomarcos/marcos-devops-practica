"""Modelos de dominio: pedidos."""
from datetime import datetime
from typing import List

from models.Usuario import Usuario


class LineaPedido:
    """Una línea de pedido. Guarda el nombre y el precio del producto en el
    momento de la compra, de modo que un pedido no cambia si el producto se
    modifica o se elimina después."""

    def __init__(self, producto_id: int, nombre_producto: str, cantidad: int, precio_unitario: float):
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0")
        self.producto_id = producto_id
        self.nombre_producto = nombre_producto
        self.cantidad = cantidad
        self.precio_unitario = precio_unitario

    @property
    def subtotal(self) -> float:
        return round(self.precio_unitario * self.cantidad, 2)


class Pedido:
    def __init__(self, id: int, cliente: Usuario, items: List[LineaPedido]):
        if not items:
            raise ValueError("Un pedido necesita al menos una línea")
        self.id = id
        self.cliente = cliente
        self.items = items
        self.fecha = datetime.now()

    @property
    def total(self) -> float:
        return round(sum(linea.subtotal for linea in self.items), 2)
