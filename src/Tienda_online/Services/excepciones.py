"""Excepciones de negocio. main.py las traduce a códigos HTTP."""


class TiendaError(Exception):
    """Error base de la tienda."""


class ValorInvalidoError(TiendaError):
    """Datos que no cumplen las reglas de negocio -> 400."""


class NoEncontradoError(TiendaError):
    """El usuario / producto solicitado no existe -> 404."""


class ConflictoError(TiendaError):
    """Conflicto con el estado actual (email repetido, sin stock...) -> 409."""
