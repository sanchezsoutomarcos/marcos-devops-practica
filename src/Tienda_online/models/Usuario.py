"""Modelos de dominio: usuarios."""
import re

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Usuario:
    """Usuario base de la tienda."""

    tipo = "usuario"
    es_admin = False

    def __init__(self, id: int, nombre: str, email: str, direccion: str = None):
        if not nombre or not str(nombre).strip():
            raise ValueError("El nombre no puede estar vacío")
        if not email or not _EMAIL_RE.match(str(email).strip()):
            raise ValueError("El email no es válido")
        self.id = id
        self.nombre = str(nombre).strip()
        self.email = str(email).strip().lower()
        self.direccion = str(direccion).strip() if direccion else None

    def __str__(self) -> str:
        return f"[{self.id}] {self.nombre} <{self.email}> ({self.tipo})"


class Cliente(Usuario):
    tipo = "cliente"

    def __init__(self, id: int, nombre: str, email: str, direccion: str):
        super().__init__(id, nombre, email, direccion)
        if not self.direccion:
            raise ValueError("Un cliente necesita una dirección postal")


class Administrador(Usuario):
    tipo = "administrador"
    es_admin = True
