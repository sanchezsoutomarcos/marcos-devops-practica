"""Esquemas Pydantic: validan lo que llega del cliente y definen lo que se devuelve.
FastAPI los usa también para generar la documentación OpenAPI (/docs)."""
from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


# ------------------------------------------------------------------- Usuario
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Ana García"])
    email: str = Field(
        ...,
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        examples=["ana@example.com"],
    )
    tipo: Literal["cliente", "administrador"] = "cliente"
    direccion: Optional[str] = Field(None, max_length=200, examples=["C/ Mayor 1, Madrid"])

    @model_validator(mode="after")
    def cliente_necesita_direccion(self):
        if self.tipo == "cliente" and not (self.direccion and self.direccion.strip()):
            raise ValueError("Un cliente necesita una dirección postal")
        return self


class UsuarioRead(BaseModel):
    id: int
    nombre: str
    email: str
    es_admin: bool


# ------------------------------------------------------------------ Producto
class ProductoCreate(BaseModel):
    tipo: Literal["generico", "electronico", "ropa"] = "generico"
    nombre: str = Field(..., min_length=1, max_length=100, examples=["Auriculares"])
    precio: float = Field(..., gt=0, examples=[29.99])
    stock: int = Field(..., ge=0, examples=[10])
    # Solo electrónicos
    meses_garantia: Optional[int] = Field(None, ge=0, examples=[24])
    # Solo ropa
    talla: Optional[str] = Field(None, max_length=10, examples=["M"])
    color: Optional[str] = Field(None, max_length=30, examples=["Azul"])

    @model_validator(mode="after")
    def validar_atributos_segun_tipo(self):
        if self.tipo == "electronico":
            if self.meses_garantia is None:
                raise ValueError("Un producto electrónico necesita 'meses_garantia'")
            if self.talla is not None or self.color is not None:
                raise ValueError("Un producto electrónico no admite 'talla' ni 'color'")
        elif self.tipo == "ropa":
            if not self.talla or not self.color:
                raise ValueError("Un producto de ropa necesita 'talla' y 'color'")
            if self.meses_garantia is not None:
                raise ValueError("Un producto de ropa no admite 'meses_garantia'")
        else:  # generico
            if self.meses_garantia is not None or self.talla is not None or self.color is not None:
                raise ValueError(
                    "Un producto genérico no admite 'meses_garantia', 'talla' ni 'color'"
                )
        return self


class ProductoRead(BaseModel):
    id: int
    tipo: str
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None


# -------------------------------------------------------------------- Pedido
class PedidoItemCreate(BaseModel):
    producto_id: int = Field(..., ge=1)
    cantidad: int = Field(..., gt=0, examples=[2])


class PedidoCreate(BaseModel):
    cliente_id: int = Field(..., ge=1)
    items: List[PedidoItemCreate] = Field(..., min_length=1)


class PedidoItemRead(BaseModel):
    producto_id: int
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoRead(BaseModel):
    id: int
    fecha: datetime
    cliente: UsuarioRead
    total: float
    items: List[PedidoItemRead]
