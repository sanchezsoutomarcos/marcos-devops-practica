"""Modelos de dominio: productos."""


class Producto:
    """Producto genérico de la tienda."""

    tipo = "generico"

    def __init__(self, id: int, nombre: str, precio: float, stock: int):
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre del producto no puede estar vacío")
        if precio <= 0:
            raise ValueError("El precio debe ser mayor que 0")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo")
        self.id = id
        self.nombre = str(nombre).strip()
        self.precio = float(precio)
        self.stock = int(stock)

    def hay_stock(self, cantidad: int) -> bool:
        return 0 < cantidad <= self.stock

    def reducir_stock(self, cantidad: int) -> None:
        if cantidad <= 0:
            raise ValueError("La cantidad debe ser mayor que 0")
        if cantidad > self.stock:
            raise ValueError(
                f"Stock insuficiente de '{self.nombre}': "
                f"disponible {self.stock}, solicitado {cantidad}"
            )
        self.stock -= cantidad

    def atributos_extra(self) -> dict:
        """Atributos propios de cada subtipo (vacío en el producto genérico)."""
        return {}

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} - {self.precio:.2f} EUR (stock: {self.stock})"


class ProductoElectronico(Producto):
    tipo = "electronico"

    def __init__(self, id: int, nombre: str, precio: float, stock: int, meses_garantia: int):
        super().__init__(id, nombre, precio, stock)
        if meses_garantia < 0:
            raise ValueError("Los meses de garantía no pueden ser negativos")
        self.meses_garantia = int(meses_garantia)

    def atributos_extra(self) -> dict:
        return {"meses_garantia": self.meses_garantia}


class ProductoRopa(Producto):
    tipo = "ropa"

    def __init__(self, id: int, nombre: str, precio: float, stock: int, talla: str, color: str):
        super().__init__(id, nombre, precio, stock)
        if not talla or not str(talla).strip():
            raise ValueError("La talla no puede estar vacía")
        if not color or not str(color).strip():
            raise ValueError("El color no puede estar vacío")
        self.talla = str(talla).strip()
        self.color = str(color).strip()

    def atributos_extra(self) -> dict:
        return {"talla": self.talla, "color": self.color}
