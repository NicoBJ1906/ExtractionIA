"""Esquema de datos de la factura extraída.

Este es el contrato que separa la etapa de IA (que solo llena estos campos)
de la etapa de validación (que decide qué hacer con ellos). Ningún dato sale
de este proceso sin pasar por este esquema.
"""
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, Field, field_validator


class LineaFactura(BaseModel):
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal


class Factura(BaseModel):
    proveedor_nit: str
    fecha_emision: str = Field(description="Fecha en formato ISO-8601 (AAAA-MM-DD)")
    total: Decimal
    lineas: list[LineaFactura] = Field(default_factory=list)
    confianza: float = Field(ge=0.0, le=1.0, description="Confianza del extractor, 0 a 1")

    @field_validator("proveedor_nit")
    @classmethod
    def nit_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("proveedor_nit no puede estar vacío")
        return v.strip()

    @field_validator("total", "confianza", mode="before")
    @classmethod
    def numero_valido(cls, v):
        try:
            return v
        except InvalidOperation as exc:
            raise ValueError("valor numérico inválido") from exc


class ResultadoExtraccion(BaseModel):
    documento_id: int
    factura: Factura
    decision: str
    motivo: str
    modo: str  # "claude" | "mock"
